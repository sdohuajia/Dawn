import cv2
import numpy as np
import requests
import re
import json
import datetime
from PIL import Image
import pytesseract
from io import BytesIO
from loguru import logger
import base64

# URLs
KeepAliveURL = "https://www.aeropres.in/chromeapi/dawn/v1/userreward/keepalive"
GetPointURL = "https://www.aeropres.in/api/atom/v1/userreferral/getpoint"
LoginURL = "https://www.aeropres.in//chromeapi/dawn/v1/user/login/v2"
PuzzleID = "https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle"

# 创建一个请求会话
session = requests.Session()

# 设置通用请求头
headers = {
    "Content-Type": "application/json",
    "Origin": "chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Priority": "u=1, i",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
}

# 获取 Puzzle ID
def GetPuzzleID():
    r = session.get(PuzzleID, headers=headers, verify=False).json()
    puzzid = r['puzzle_id']
    return puzzid

# 检查验证码格式，6位字符、数字及部分特殊符号
def IsValidExpression(expression):
    pattern = r'^[A-Za-z0-9]{6}$'  # 简化为字母数字6位
    return bool(re.match(pattern, expression))

# 图像预处理与验证码识别
def ProcessCaptcha(base64_image):
    # 将Base64字符串解码为二进制数据
    image_data = base64.b64decode(base64_image)
    # 使用BytesIO将二进制数据转换为一个可读的文件对象
    image = Image.open(BytesIO(image_data))

    # 将图像转换为灰度
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

    # 使用二值化处理
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # 使用形态学操作去噪
    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    # 找到字符的轮廓
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 提取每个轮廓区域并进行OCR识别
    results = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        char_image = cleaned[y:y+h, x:x+w]
        # 使用Tesseract识别单个字符
        text = pytesseract.image_to_string(char_image, config='--psm 10')
        results.append(text.strip())

    captcha_result = ''.join(results)
    logger.debug(f'验证码识别结果: {captcha_result}')
    if IsValidExpression(captcha_result):
        return captcha_result

    return None

# 登录函数
def login(USERNAME, PASSWORD):
    puzzid = GetPuzzleID()
    current_time = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds').replace("+00:00", "Z")
    data = {
        "username": USERNAME,
        "password": PASSWORD,
        "logindata": {
            "_v": "1.0.7",
            "datetime": current_time
        },
        "puzzle_id": puzzid,
        "ans": "0"
    }
    
    # 获取验证码图片并识别
    refresh_image = session.get(f'https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle-image?puzzle_id={puzzid}', headers=headers, verify=False).json()
    code = ProcessCaptcha(refresh_image['imgBase64'])
    if code:
        logger.success(f'[√] 成功获取验证码结果: {code}')
        data['ans'] = str(code)
        login_data = json.dumps(data)
        logger.info(f'[2] 登录数据： {login_data}')
        try:
            r = session.post(LoginURL, login_data, headers=headers, verify=False).json()
            token = r['data']['token']
            logger.success(f'[√] 成功获取AuthToken: {token}')
            return token
        except Exception as e:
            logger.error(f'[x] 登录失败，验证码错误，错误信息: {e}')
    else:
        logger.error(f'[x] 无法识别验证码')

# 保持活动状态
def KeepAlive(USERNAME, TOKEN):
    data = {"username": USERNAME, "extensionid": "fpdkjdnhkakefebpekbdhillbhonfjjp", "numberoftabs": 0, "_v": "1.0.7"}
    json_data = json.dumps(data)
    headers['authorization'] = "Bearer " + str(TOKEN)
    r = session.post(KeepAliveURL, data=json_data, headers=headers, verify=False).json()
    logger.info(f'[3] 保持链接中... {r}')

# 获取 Point
def GetPoint(TOKEN):
    headers['authorization'] = "Bearer " + str(TOKEN)
    r = session.get(GetPointURL, headers=headers, verify=False).json()
    logger.success(f'[√] 成功获取Point: {r}')

# 主函数
def main(USERNAME, PASSWORD):
    TOKEN = ''
    if TOKEN == '':
        while True:
            TOKEN = login(USERNAME, PASSWORD)
            if TOKEN:
                break
    # 初始化计数器
    count = 0
    max_count = 200  # 每运行 200 次重新获取 TOKEN
    while True:
        try:
            KeepAlive(USERNAME, TOKEN)
            GetPoint(TOKEN)
            count += 1
            if count >= max_count:
                logger.debug(f'[√] 重新登录获取Token...')
                while True:
                    TOKEN = login(USERNAME, PASSWORD)
                    if TOKEN:
                        break
                count = 0
        except Exception as e:
            logger.error(e)

# 入口
if __name__ == '__main__':
    with open('password.txt', 'r') as f:
        username, password = f.readline().strip().split(':')
    main(username, password)
