import ast
import json
import re
import requests
import random
import time
import datetime
import urllib3
from PIL import Image
import base64
from io import BytesIO
import ddddocr
from loguru import logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

# 获取 PuzzleID
def GetPuzzleID():
    try:
        r = session.get(PuzzleID, headers=headers, verify=False)
        logger.debug(f'[√] PuzzleID 请求响应状态码: {r.status_code}')
        r_json = r.json()
        puzzid = r_json['puzzle_id']
        return puzzid
    except Exception as e:
        logger.error(f'[x] 获取PuzzleID出错: {e}')

# 检查验证码是否为有效表达式
def IsValidExpression(expression):
    pattern = r'^[A-Za-z0-9]{6}$'
    return bool(re.match(pattern, expression))

# 验证码识别
def RemixCaptacha(base64_image):
    try:
        image_data = base64.b64decode(base64_image)
        image = Image.open(BytesIO(image_data))

        # 将图像转换为 RGB 模式
        image = image.convert('RGB')
        new_image = Image.new('RGB', image.size, 'white')
        width, height = image.size

        for x in range(width):
            for y in range(height):
                pixel = image.getpixel((x, y))
                if pixel == (48, 48, 48):  # 黑色像素
                    new_image.putpixel((x, y), pixel)
                else:
                    new_image.putpixel((x, y), (255, 255, 255))  # 白色背景

        ocr = ddddocr.DdddOcr(show_ad=False)
        result = ocr.classification(new_image)
        logger.debug(f'[1] 验证码识别结果：{result}, 是否为可计算验证码: {IsValidExpression(result)}')

        if IsValidExpression(result):
            return result
    except Exception as e:
        logger.error(f'[x] 验证码识别失败: {e}')
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
    
    # 验证码识别部分
    refresh_image = session.get(f'https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle-image?puzzle_id={puzzid}', headers=headers, verify=False)
    logger.debug(f'[√] 验证码图片响应状态码: {refresh_image.status_code}')
    
    if refresh_image.status_code == 200:
        refresh_image_json = refresh_image.json()
        code = RemixCaptacha(refresh_image_json['imgBase64'])
        if code:
            logger.success(f'[√] 成功获取验证码结果 {code}')
            data['ans'] = str(code)
            login_data = json.dumps(data)
            logger.info(f'[2] 登录数据： {login_data}')
            try:
                r = session.post(LoginURL, login_data, headers=headers, verify=False)
                logger.debug(f'[√] 登录请求响应状态码: {r.status_code}')
                logger.debug(f'[√] 登录请求响应内容: {r.text}')
                if r.status_code == 200:
                    login_response_json = r.json()
                    token = login_response_json['data']['token']
                    logger.success(f'[√] 成功获取AuthToken {token}')
                    return token
                else:
                    logger.error(f'[x] 登录请求失败，状态码: {r.status_code}, 响应内容: {r.text}')
            except json.JSONDecodeError as json_err:
                logger.error(f'[x] 无法解析响应为JSON: {json_err}')
            except Exception as e:
                logger.error(f'[x] 请求发生错误: {e}')
        else:
            logger.error(f'[x] 无法识别验证码')
    else:
        logger.error(f'[x] 验证码图片获取失败，状态码: {refresh_image.status_code}')

# 保持活动状态
def KeepAlive(USERNAME, TOKEN):
    data = {"username": USERNAME, "extensionid": "fpdkjdnhkakefebpekbdhillbhonfjjp", "numberoftabs": 0, "_v": "1.0.7"}
    json_data = json.dumps(data)
    headers['authorization'] = "Bearer " + str(TOKEN)
    r = session.post(KeepAliveURL, data=json_data, headers=headers, verify=False)
    logger.debug(f'[√] 保持活动请求响应状态码: {r.status_code}')
    if r.status_code == 200:
        try:
            r_json = r.json()
            logger.info(f'[3] 保持链接中... {r_json}')
        except json.JSONDecodeError as json_err:
            logger.error(f'[x] 无法解析响应为JSON: {json_err}')
    else:
        logger.error(f'[x] 保持活动请求失败，状态码: {r.status_code}, 响应内容: {r.text}')

# 获取 Point
def GetPoint(TOKEN):
    headers['authorization'] = "Bearer " + str(TOKEN)
    r = session.get(GetPointURL, headers=headers, verify=False)
    logger.debug(f'[√] 获取Point请求响应状态码: {r.status_code}')
    if r.status_code == 200:
        try:
            r_json = r.json()
            logger.success(f'[√] 成功获取Point {r_json}')
        except json.JSONDecodeError as json_err:
            logger.error(f'[x] 无法解析响应为JSON: {json_err}')
    else:
        logger.error(f'[x] 获取Point请求失败，状态码: {r.status_code}, 响应内容: {r.text}')

# 主程序入口
def main(USERANEM, PASSWORD):
    TOKEN = ''
    if TOKEN == '':
        while True:
            TOKEN = login(USERANEM, PASSWORD)
            if TOKEN:
                break
    count = 0
    max_count = 200  # 每运行 200 次重新获取 TOKEN
    while True:
        try:
            KeepAlive(USERANEM, TOKEN)
            GetPoint(TOKEN)
            count += 1
            if count >= max_count:
                logger.debug(f'[√] 重新登录获取Token...')
                while True:
                    TOKEN = login(USERANEM, PASSWORD)
                    if TOKEN:
                        break
                count = 0
        except Exception as e:
            logger.error(e)

if __name__ == '__main__':
    with open('password.txt','r') as f:
        username, password = f.readline().strip().split(':')
    main(username, password)
