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
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

KeepAliveURL = "https://www.aeropres.in/chromeapi/dawn/v1/userreward/keepalive"
GetPointURL = "https://www.aeropres.in/api/atom/v1/userreferral/getpoint"
LoginURL = "https://www.aeropres.in//chromeapi/dawn/v1/user/login/v2"
PuzzleID = "https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle"
FastCaptchaURL = "https://thedataextractors.com/fast-captcha/api/solve/recaptcha"
FastCaptchaAPIKey = "<fast-captcha-api-key>"

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

# 获取验证码ID
def GetPuzzleID():
    r = session.get(PuzzleID, headers=headers, verify=False).json()
    puzzid = r['puzzle_id']
    return puzzid

# 检查验证码算式
def IsValidExpression(expression):
    pattern = r'^[A-Za-z0-9+\-*/]{6}$'
    try:
        eval(expression.replace(' ', ''))
        return True
    except:
        return False

# 使用 Fast Captcha 识别验证码
def SolveCaptcha(web_url, website_key):
    payload = f'webUrl={web_url}&websiteKey={website_key}'
    captcha_headers = {
        'apiSecretKey': FastCaptchaAPIKey,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(FastCaptchaURL, headers=captcha_headers, data=payload)
    solution = response.json().get('solution', '')
    return solution

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
    # 获取验证码图像
    refresh_image = session.get(f'https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle-image?puzzle_id={puzzid}', headers=headers, verify=False).json()
    captcha_image_url = f'https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle-image?puzzle_id={puzzid}'
    
    # 解决验证码
    captcha_solution = SolveCaptcha(captcha_image_url, puzzid)
    if captcha_solution:
        logger.success(f'[√] 成功获取验证码结果 {captcha_solution}')
        data['ans'] = str(captcha_solution)
        login_data = json.dumps(data)
        logger.info(f'[2] 登录数据： {login_data}')
        try:
            r = session.post(LoginURL, data=login_data, headers=headers, verify=False).json()
            logger.debug(r)
            token = r['data']['token']
            logger.success(f'[√] 成功获取AuthToken {token}')
            return token
        except Exception as e:
            logger.error(f'[x] 登录失败：{e}')

def KeepAlive(USERNAME, TOKEN):
    data = {"username": USERNAME, "extensionid": "fpdkjdnhkakefebpekbdhillbhonfjjp", "numberoftabs": 0, "_v": "1.0.7"}
    json_data = json.dumps(data)
    headers['authorization'] = "Bearer " + str(TOKEN)
    r = session.post(KeepAliveURL, data=json_data, headers=headers, verify=False).json()
    logger.info(f'[3] 保持链接中... {r}')

def GetPoint(TOKEN):
    headers['authorization'] = "Bearer " + str(TOKEN)
    r = session.get(GetPointURL, headers=headers, verify=False).json()
    logger.success(f'[√] 成功获取Point {r}')

def main(USERNAME, PASSWORD):
    TOKEN = ''
    if TOKEN == '':
        while True:
            TOKEN = login(USERNAME, PASSWORD)
            if TOKEN:
                break
    count = 0
    max_count = 200
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

if __name__ == '__main__':
    with open('password.txt', 'r') as f:
        username, password = f.readline().strip().split(':')
    main(username, password)
