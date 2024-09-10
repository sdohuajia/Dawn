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
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from loguru import logger

KeepAliveURL = "https://www.aeropres.in/chromeapi/dawn/v1/userreward/keepalive"
GetPointURL = "https://www.aeropres.in/api/atom/v1/userreferral/getpoint"
LoginURL = "https://www.aeropres.in//chromeapi/dawn/v1/user/login/v2"
PuzzleID = "https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle"

# YesCaptcha API 配置
YESCAPTCHA_API_KEY = "your_yescaptcha_api_key"  # 替换为你自己的 YesCaptcha API 密钥
YESCAPTCHA_URL = "https://api.yescaptcha.com/solve"  # YesCaptcha 的 API 端点

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

def GetPuzzleID():
    r = session.get(PuzzleID, headers=headers, verify=False).json()
    puzzid = r['puzzle_id']
    return puzzid

# 检查验证码算式
def IsValidExpression(expression):
    pattern = r'^[A-Za-z0-9\+\-\*/]{6}$'
    if re.match(pattern, expression):
        return True
    return False

# YesCaptcha 验证码识别
def YesCaptchaRecognition(base64_image):
    # YesCaptcha API 请求数据
    payload = {
        "api_key": YESCAPTCHA_API_KEY,
        "tasks": [{
            "type": "image_to_text",
            "body": base64_image
        }]
    }

    # 发送验证码图片到 YesCaptcha
    response = requests.post(YESCAPTCHA_URL, json=payload)
    result = response.json()

    if result.get("success") and result["tasks"][0].get("result"):
        captcha_code = result["tasks"][0]["result"]
        logger.success(f'[√] 成功通过 YesCaptcha 获取验证码: {captcha_code}')
        return captcha_code
    else:
        logger.error(f'[x] YesCaptcha 验证码识别失败，错误信息: {result}')
        return None

# 替换 RemixCaptacha 函数为 YesCaptcha 接入
def RemixCaptacha(base64_image):
    # 调用 YesCaptcha 来识别验证码
    result = YesCaptchaRecognition(base64_image)
    logger.debug(f'[1] YesCaptcha 验证码识别结果：{result}，是否为可计算验证码 {IsValidExpression(result)}')

    if IsValidExpression(result):
        return result
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
    refresh_image = session.get(f'https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle-image?puzzle_id={puzzid}', headers=headers, verify=False).json()
    code = RemixCaptacha(refresh_image['imgBase64'])
    
    if code:
        logger.success(f'[√] 成功获取验证码结果 {code}')
        data['ans'] = str(code)
        login_data = json.dumps(data)
        logger.info(f'[2] 登录数据： {login_data}')
        try:
            r = session.post(LoginURL, login_data, headers=headers, verify=False).json()
            logger.debug(r)
            token = r['data']['token']
            logger.success(f'[√] 成功获取AuthToken {token}')
            return token
        except Exception as e:
            logger.error(f'[x] 登录失败，错误信息: {e}')
            return None
    return None

# 保持会话
def KeepAlive(USERNAME, TOKEN):
    data = {
        "username": USERNAME,
        "extensionid": "fpdkjdnhkakefebpekbdhillbhonfjjp",
        "numberoftabs": 0,
        "_v": "1.0.7"
    }
    json_data = json.dumps(data)
    headers['authorization'] = "Bearer " + str(TOKEN)
    r = session.post(KeepAliveURL, data=json_data, headers=headers, verify=False).json()
    logger.info(f'[3] 保持链接中... {r}')

# 获取积分
def GetPoint(TOKEN):
    headers['authorization'] = "Bearer " + str(TOKEN)
    r = session.get(GetPointURL, headers=headers, verify=False).json()
    logger.success(f'[√] 成功获取Point {r}')

# 主函数
def main(USERNAME, PASSWORD):
    TOKEN = ''
    last_login_time = None  # 记录上次登录的时间
    
    while True:
        current_time = time.time()
        
        # 如果从上次登录时间起超过 12 小时（43200 秒），则重新登录
        if last_login_time is None or (current_time - last_login_time) > 43200:
            TOKEN = login(USERNAME, PASSWORD)
            if TOKEN:
                last_login_time = current_time  # 更新上次登录时间
                logger.info(f'[√] 成功登录，12 小时后将重新登录')
        
        try:
            # 执行保持活动和获取点数的操作
            KeepAlive(USERNAME, TOKEN)
            GetPoint(TOKEN)
        except Exception as e:
            logger.error(e)
        
        time.sleep(300)  # 每5分钟执行一次保持会话和获取积分操作

if __name__ == '__main__':
    with open('password.txt', 'r') as f:
        username, password = f.readline().strip().split(':')
    main(username, password)
