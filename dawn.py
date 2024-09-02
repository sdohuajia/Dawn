import ast
import json
import re
import requests
import datetime
import urllib3
from PIL import Image
import base64
from io import BytesIO
import ddddocr
from loguru import logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 配置URL
KeepAliveURL = "https://www.aeropres.in/chromeapi/dawn/v1/userreward/keepalive"
GetPointURL = "https://www.aeropres.in/api/atom/v1/userreferral/getpoint"
LoginURL = "https://www.aeropres.in/chromeapi/dawn/v1/user/login/v2"
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

def GetPuzzleID(session, puzzle_url, headers):
    try:
        response = session.get(puzzle_url, headers=headers, verify=False)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        puzzle_id = data['puzzle_id']
        return puzzle_id
    except requests.exceptions.RequestException as e:
        logger.error(f"There was a problem with the fetch operation: {e}")
        return None

def IsValidCode(code):
    # 验证验证码是否为6位字母和数字的组合
    pattern = r'^[A-Za-z0-9]{6}$'
    if not re.match(pattern, code):
        return False
    # 使用 ast 模块解析
    try:
        ast.parse(code, mode='eval')
        return True
    except (SyntaxError, ValueError):
        return False

def RemixCaptacha(base64_image):
    # 将Base64字符串解码为二进制数据
    image_data = base64.b64decode(base64_image)
    # 使用BytesIO将二进制数据转换为一个可读的文件对象
    image = Image.open(BytesIO(image_data))
    # 创建OCR对象
    ocr = ddddocr.DdddOcr(show_ad=False)
    result = ocr.classification(image)
    # 检查是否为有效的6位验证码
    if IsValidCode(result):
        return result
    else:
        logger.error(f'识别结果无效: {result}')
        return None

def login(USERNAME, PASSWORD):
    puzzid = GetPuzzleID(session, PuzzleID, headers)
    if not puzzid:
        logger.error("Failed to get puzzle ID.")
        return None
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
    # 验证码识别部分
    try:
        refresh_image = session.get(f'https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle-image?puzzle_id={puzzid}', headers=headers, verify=False).json()
        code = RemixCaptacha(refresh_image['imgBase64'])
        if code:
            logger.success(f'[√] 成功获取验证码结果 {code}')
            data['ans'] = str(code)
            login_data = json.dumps(data)
            logger.info(f'[2] 登录数据： {login_data}')
            response = session.post(LoginURL, data=login_data, headers=headers, verify=False)
            response.raise_for_status()  # 检查请求是否成功
            r = response.json()
            token = r['data']['token']
            logger.success(f'[√] 成功获取AuthToken {token}')
            return token
        else:
            logger.error("Failed to recognize captcha code.")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed during login: {e}")
        return None

def KeepAlive(USERNAME, TOKEN):
    data = {
        "username": USERNAME,
        "extensionid": "fpdkjdnhkakefebpekbdhillbhonfjjp",
        "numberoftabs": 0,
        "_v": "1.0.7"
    }
    json_data = json.dumps(data)
    headers['authorization'] = "Bearer " + str(TOKEN)
    try:
        response = session.post(KeepAliveURL, data=json_data, headers=headers, verify=False)
        response.raise_for_status()  # 检查请求是否成功
        r = response.json()
        logger.info(f'[3] 保持链接中... {r}')
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed during keep alive: {e}")

def GetPoint(TOKEN):
    headers['authorization'] = "Bearer " + str(TOKEN)
    try:
        response = session.get(GetPointURL, headers=headers, verify=False)
        response.raise_for_status()  # 检查请求是否成功
        r = response.json()
        logger.success(f'[√] 成功获取Point {r}')
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed during get point: {e}")

def main(USERNAME, PASSWORD):
    TOKEN = ''
    if not TOKEN:
        while True:
            TOKEN = login(USERNAME, PASSWORD)
            if TOKEN:
                break
    # 初始化计数器
    count = 0
    max_count = 200  # 每运行 200 次重新获取 TOKEN
    while True:
        try:
            # 执行保持活动和获取点数的操作
            KeepAlive(USERNAME, TOKEN)
            GetPoint(TOKEN)
            # 更新计数器
            count += 1
            # 每达到 max_count 次后重新获取 TOKEN
            if count >= max_count:
                logger.debug(f'[√] 重新登录获取Token...')
                while True:
                    TOKEN = login(USERNAME, PASSWORD)
                    if TOKEN:
                        break
                count = 0  # 重置计数器
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    with open('password.txt', 'r') as f:
        username, password = f.readline().strip().split(':')
    main(username, password)
