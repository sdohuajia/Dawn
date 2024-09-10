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
from loguru import logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

# 获取验证码图片的 puzzle_id
def GetPuzzleID():
    r = session.get(PuzzleID, headers=headers, verify=False).json()
    puzzid = r['puzzle_id']
    return puzzid

# 使用 YesCaptcha 进行验证码识别
def GetCaptchaFromYesCaptcha(base64_image):
    api_url = 'https://api.yescaptcha.com/solve'
    api_key = '你的 YesCaptcha API Key'  # 替换为你的 API Key
    payload = {
        'clientKey': api_key,
        'task': {
            'type': 'ImageToTextTask',
            'body': base64_image
        }
    }

    try:
        response = requests.post(api_url, json=payload)
        result = response.json()

        if result.get('errorId') == 0:
            captcha_text = result.get('solution', {}).get('text')
            logger.success(f'[√] 成功通过 YesCaptcha 获取验证码：{captcha_text}')
            return captcha_text
        else:
            logger.error(f'[x] YesCaptcha 识别失败: {result.get("errorDescription")}')
            return None
    except Exception as e:
        logger.error(f'[x] 请求 YesCaptcha 出错: {e}')
        return None

# 登录流程
def login(USERNAME, PASSWORD, last_captcha_time):
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

    # 判断是否需要重新获取验证码（每4小时获取一次）
    now = time.time()
    if now - last_captcha_time > 4 * 3600:  # 4 小时 = 4 * 3600 秒
        refresh_image = session.get(f'https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle-image?puzzle_id={puzzid}', headers=headers, verify=False).json()
        code = GetCaptchaFromYesCaptcha(refresh_image['imgBase64'])
        if code:
            data['ans'] = str(code)
            last_captcha_time = now  # 更新最后一次获取验证码的时间

    login_data = json.dumps(data)
    logger.info(f'[2] 登录数据： {login_data}')
    
    try:
        r = session.post(LoginURL, login_data, headers=headers, verify=False).json()
        logger.debug(r)
        token = r['data']['token']
        logger.success(f'[√] 成功获取AuthToken {token}')
        return token, last_captcha_time
    except Exception as e:
        logger.error(f'[x] 验证码错误，尝试重新获取...')
        return None, last_captcha_time

# 保持活动状态
def KeepAlive(USERNAME, TOKEN):
    data = {"username": USERNAME, "extensionid": "fpdkjdnhkakefebpekbdhillbhonfjjp", "numberoftabs": 0, "_v": "1.0.7"}
    json_data = json.dumps(data)
    headers['authorization'] = "Bearer " + str(TOKEN)
    r = session.post(KeepAliveURL, data=json_data, headers=headers, verify=False).json()
    logger.info(f'[3] 保持链接中... {r}')

# 获取点数
def GetPoint(TOKEN):
    headers['authorization'] = "Bearer " + str(TOKEN)
    r = session.get(GetPointURL, headers=headers, verify=False).json()
    logger.success(f'[√] 成功获取Point {r}')

# 主循环
def main(USERNAME, PASSWORD):
    TOKEN = ''
    last_captcha_time = 0  # 上次获取验证码的时间初始化为 0
    if TOKEN == '':
        while True:
            TOKEN, last_captcha_time = login(USERNAME, PASSWORD, last_captcha_time)
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
                    TOKEN, last_captcha_time = login(USERNAME, PASSWORD, last_captcha_time)
                    if TOKEN:
                        break
                count = 0  # 重置计数器
        except Exception as e:
            logger.error(e)

if __name__ == '__main__':
    with open('password.txt', 'r') as f:
        username, password = f.readline().strip().split(':')
    main(username, password)
