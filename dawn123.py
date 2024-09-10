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

# 获取验证码 PuzzleID
def GetPuzzleID():
    r = session.get(PuzzleID, headers=headers, verify=False).json()
    puzzid = r['puzzle_id']
    return puzzid

# 使用 YesCaptcha API 识别验证码
def RemixCaptchaWithYesCaptcha(base64_image):
    # YesCaptcha API 网址
    YESCAPTCHA_API_URL = "https://api.yescaptcha.com/createTask"

    # 替换成你的 YesCaptcha API Key
    API_KEY = "YOUR_YESCAPTCHA_API_KEY"

    # YesCaptcha 请求数据
    data = {
        "clientKey": API_KEY,
        "task": {
            "type": "ImageToTextTask",
            "body": base64_image
        }
    }

    # 发送请求并获取任务ID
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

# 获取验证码识别结果
def get_yescaptcha_result(task_id):
    # YesCaptcha 获取结果 API 网址
    YESCAPTCHA_RESULT_URL = "https://api.yescaptcha.com/getTaskResult"
    
    # 查询 YesCaptcha 结果
    data = {
        "clientKey": "YOUR_YESCAPTCHA_API_KEY",
        "taskId": task_id
    }

    # 轮询任务状态，最多尝试 10 次
    for _ in range(10):
        try:
            response = session.post(YESCAPTCHA_RESULT_URL, json=data, verify=False).json()
            if response['status'] == "ready":
                code = response['solution']['text']
                logger.info(f'[√] 成功获取验证码结果: {code}')
                return code
            else:
                logger.info(f'[√] 等待验证码识别结果...')
                time.sleep(3)  # 等待 3 秒后再次查询
        except Exception as e:
            logger.error(f'[x] 获取验证码识别结果失败: {e}')
    
    logger.error('[x] 获取验证码结果超时')
    return None

# 检查验证码算式
def IsValidExpression(expression):
    pattern = r'^[A-Za-z0-9\+\-\*/]{6}$'
    if re.match(pattern, expression):
        return True
    return False

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
    base64_image = refresh_image['imgBase64']
    code = RemixCaptchaWithYesCaptcha(base64_image)
    
    if code and IsValidExpression(code):
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
            logger.error(e)

if __name__ == '__main__':
    with open('password.txt', 'r') as f:
        username, password = f.readline().strip().split(':')
    main(username, password)
