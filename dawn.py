import requests
import json
import datetime
import base64
from PIL import Image
from io import BytesIO
import re
import ddddocr
from loguru import logger

# URL 设置
KeepAliveURL = "https://www.aeropres.in/chromeapi/dawn/v1/userreward/keepalive"
GetPointURL = "https://www.aeropres.in/api/atom/v1/userreferral/getpoint"
LoginURL = "https://www.aeropres.in//chromeapi/dawn/v1/user/login/v2"
PuzzleID = "https://www.aeropres.in/chromeapi/dawn/v1/puzzle/get-puzzle"
FastCaptchaURL = "https://thedataextractors.com/fast-captcha/api/solve/recaptcha"

# 从文件中读取 Fast Captcha API 密钥
def get_fast_captcha_api_key():
    with open('fast_captcha_api_key.txt', 'r') as file:
        return file.read().strip()

def GetPuzzleID():
    try:
        r = requests.get(PuzzleID, verify=False).json()
        puzzid = r['puzzle_id']
        return puzzid
    except requests.exceptions.RequestException as e:
        logger.error(f"获取 Puzzle ID 失败: {e}")
        return None

def IsValidExpression(expression):
    # 检查表达式是否为6位的字母和数字组合
    pattern = r'^[A-Za-z0-9]{6}$'
    return bool(re.match(pattern, expression))

def solve_captcha(api_key, website_url, website_key):
    headers = {
        'apiSecretKey': api_key,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = f'webUrl={website_url}&websiteKey={website_key}'
    try:
        response = requests.post(FastCaptchaURL, headers=headers, data=payload, verify=False)
        response.raise_for_status()
        return response.json().get('solution')
    except requests.exceptions.RequestException as e:
        logger.error(f"解决验证码失败: {e}")
        return None

def RemixCaptacha(base64_image):
    # 将Base64字符串解码为二进制数据
    image_data = base64.b64decode(base64_image)
    image = Image.open(BytesIO(image_data))

    # 图像处理
    image = image.convert('RGB')
    new_image = Image.new('RGB', image.size, 'white')
    width, height = image.size
    for x in range(width):
        for y in range(height):
            pixel = image.getpixel((x, y))
            if pixel == (48, 48, 48):  # 黑色像素
                new_image.putpixel((x, y), pixel)  # 保留原始黑色
            else:
                new_image.putpixel((x, y), (255, 255, 255))  # 替换为白色

    # 使用 OCR 识别验证码
    ocr = ddddocr.DdddOcr(show_ad=False)
    ocr.set_ranges(0)
    result = ocr.classification(new_image)
    logger.debug(f'[1] 验证码识别结果：{result}，是否为可计算验证码 {IsValidExpression(result)}')
    if IsValidExpression(result):
        return result

def login(USERNAME, PASSWORD):
    puzzid = GetPuzzleID()
    if not puzzid:
        logger.error("获取 Puzzle ID 失败，登录终止")
        return False

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
    try:
        refresh_image = requests.get(f'https://www.aeropres.in/chromeapi/dawn/v1/puzzle/refresh-image/{puzzid}', verify=False).json()
        base64_image = refresh_image['image']
        captcha_solution = RemixCaptacha(base64_image)
        logger.debug(f'[2] 识别结果: {captcha_solution}')
        data['ans'] = captcha_solution
        
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(LoginURL, json=data, headers=headers, verify=False)
        logger.debug(f'[3] 登录请求返回: {response.text}')
        if response.status_code == 200:
            result = response.json()
            if result['result'] == 'success':
                logger.info('登录成功')
                return True
            else:
                logger.error(f'登录失败: {result.get("msg")}')
                return False
        else:
            logger.error(f'请求失败: {response.status_code}')
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"登录请求失败: {e}")
        return False

def keep_alive():
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(KeepAliveURL, headers=headers, verify=False)
        if response.status_code == 200:
            logger.info('保持在线请求成功')
        else:
            logger.error(f'保持在线请求失败: {response.status_code}')
    except requests.exceptions.RequestException as e:
        logger.error(f"保持在线请求失败: {e}")

def get_point():
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(GetPointURL, headers=headers, verify=False)
        if response.status_code == 200:
            result = response.json()
            logger.info(f'获取积分成功: {result}')
        else:
            logger.error(f'获取积分失败: {response.status_code}')
    except requests.exceptions.RequestException as e:
        logger.error(f"获取积分失败: {e}")

if __name__ == "__main__":
    USERNAME = "your_username"  # 替换为实际用户名
    PASSWORD = "your_password"  # 替换为实际密码

    if login(USERNAME, PASSWORD):
        keep_alive()
        get_point()
