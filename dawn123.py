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
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from loguru import logger

KeepAliveURL = "https://www.aeropres.in/chromeapi/dawn/v1/userreward/keepalive"
GetPointURL = "https://www.aeropres.in/api/atom/v1/userreferral/getpoint"
LoginURL = "https://www.aeropres.in/chromeapi/dawn/v1/user/login/v2"
PuzzleID = "https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle"

session = requests.Session()

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

def RemixCaptchaWithYesCaptcha(base64_image):
    YESCAPTCHA_API_URL = "https://api.yescaptcha.com/createTask"
    API_KEY = "YOUR_YESCAPTCHA_API_KEY"
    data = {
        "clientKey": API_KEY,
        "task": {
            "type": "ImageToTextTask",
            "body": base64_image
        }
    }

    try:
        response = session.post(YESCAPTCHA_API_URL, json=data, verify=False).json()
        if response.get("taskId"):
            task_id = response["taskId"]
            logger.info(f'[√] 成功创建任务，任务ID: {task_id}')
            return get_yescaptcha_result(task_id)
        else:
            logger.error(f'[x] 创建验证码识别任务失败: {response}')
            return None
    except Exception as e:
        logger.error(f'[x] YesCaptcha 请求失败: {e}')
        return None

def get_yescaptcha_result(task_id):
    YESCAPTCHA_RESULT_URL = "https://api.yescaptcha.com/getTaskResult"
    data = {
        "clientKey": "YOUR_YESCAPTCHA_API_KEY",
        "taskId": task_id
    }

    for _ in range(10):
        try:
            response = session.post(YESCAPTCHA_RESULT_URL, json=data, verify=False, timeout=10).json()
            if response['status'] == "ready":
                code = response['solution']['text']
                logger.info(f'[√] 成功获取验证码结果: {code}')
                return code
            else:
                logger.info(f'[√] 等待验证码识别结果...')
                time.sleep(3)
        except requests.RequestException as e:
            logger.error(f'[x] 获取验证码识别结果失败: {e}')
    
    logger.error('[x] 获取验证码结果超时')
    return None

def IsValidExpression(expression):
    pattern = r'^[A-Za-z0-9\+\-\*/]{6}$'
    return bool(re.match(pattern, expression))

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

    refresh_image = session.get(f'https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle-image?puzzle_id={puzzid}', headers=headers, verify=False).json()
    base64_image = refresh_image['imgBase64']
    code = RemixCaptchaWithYesCaptcha(base64_image)
    
    if code and IsValidExpression(code):
        logger.success(f'[√] 成功获取验证码结果 {code}')
        data['ans'] = str(code)
        login_data = json.dumps(data)
        logger.info(f'[2] 登录数据： {login_data}')
        try:
            r = session.post(LoginURL, login_data, headers=headers, verify=False, timeout=10).json()
            logger.debug(r)
            token = r['data']['token']
            logger.success(f'[√] 成功获取AuthToken {token}')
            return token
        except requests.RequestException as e:
            logger.error(f'[x] 登录失败，错误信息: {e}')
            return None
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
    retry_attempts = 3

    for attempt in range(retry_attempts):
        try:
            r = session.post(KeepAliveURL, data=json_data, headers=headers, verify=False, timeout=10).json()
            if r.get('success') == True:
                logger.info(f'[3] 保持链接中... {r}')
                break
            else:
                logger.error(f'[x] 保持链接失败: {r}')
        except requests.RequestException as e:
            logger.error(f'[x] 保持链接失败: {e}')
            if attempt < retry_attempts - 1:
                time.sleep(5)  # 重试间隔
            else:
                logger.error('[x] 达到最大重试次数，停止重试')

def GetPoint(TOKEN):
    headers['authorization'] = "Bearer " + str(TOKEN)
    retry_attempts = 3

    for attempt in range(retry_attempts):
        try:
            r = session.get(GetPointURL, headers=headers, verify=False, timeout=10).json()
            if r.get('success') == True:
                logger.success(f'[√] 成功获取Point {r}')
                break
            else:
                logger.error(f'[x] 获取Point失败: {r}')
        except requests.RequestException as e:
            logger.error(f'[x] 获取Point失败: {e}')
            if attempt < retry_attempts - 1:
                time.sleep(5)  # 重试间隔
            else:
                logger.error('[x] 达到最大重试次数，停止重试')

def main(USERNAME, PASSWORD):
    TOKEN = ''
    last_login_time = None
    login_interval = 12 * 3600  # 12小时（以秒为单位）

    if TOKEN == '':
        TOKEN = login(USERNAME, PASSWORD)
        last_login_time = time.time()  # 记录首次登录时间

    while True:
        try:
            if time.time() - last_login_time >= login_interval:
                logger.debug(f'[√] 重新登录获取Token...')
                TOKEN = login(USERNAME, PASSWORD)
                last_login_time = time.time()  # 记录登录时间

            KeepAlive(USERNAME, TOKEN)
            GetPoint(TOKEN)

            time.sleep(300)  # 每5分钟保持一次会话

        except Exception as e:
            logger.error(e)

if __name__ == '__main__':
    with open('password.txt', 'r') as f:
        username, password = f.readline().strip().split(':')
    main(username, password)
