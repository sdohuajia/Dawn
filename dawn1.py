import ddddocr
import pytesseract
from PIL import Image
import base64
import requests
import logging

# 初始化日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ocr = ddddocr.DdddOcr()

# 自动识别验证码的函数
def RemixCaptcha(base64_image):
    image_data = base64.b64decode(base64_image)
    result = ocr.classification(image_data)

    # 如果 ddddocr 识别失败，尝试用 Tesseract 识别
    if not result:
        logger.warning("[!] ddddocr 识别失败，尝试使用 Tesseract OCR")
        with open('captcha.png', 'wb') as f:
            f.write(image_data)
        image = Image.open('captcha.png')
        result = pytesseract.image_to_string(image)

    # 自动识别失败时，显示图片并手动输入
    if not result:
        logger.warning("[!] 自动识别失败，显示验证码图片供用户手动输入")
        with open('captcha_manual.png', 'wb') as f:
            f.write(image_data)
        
        # 打开验证码图片供用户查看
        image = Image.open('captcha_manual.png')
        image.show()  # 这行代码将打开图片
        result = input("自动识别失败，请查看图片并手动输入验证码: ")

    return result

# 模拟获取 PuzzleID 的函数
def GetPuzzleID():
    # 这里应该是实际获取 puzzle_id 的逻辑
    return "sample_puzzle_id"

# 登录函数
def login(username, password):
    puzzid = GetPuzzleID()
    if not puzzid:
        logger.error("无法获取 puzzle_id")
        return None

    for attempt in range(3):  # 最多重试3次
        try:
            captcha_response = session.get(f'https://example.com/get_captcha?puzzle_id={puzzid}')
            captcha_image = captcha_response.json().get('imgBase64')
            
            if captcha_image:
                code = RemixCaptcha(captcha_image)

                if code:
                    # 提交登录表单 (这里填写正确的 URL 和请求格式)
                    data = {
                        "username": username,
                        "password": password,
                        "captcha_code": code
                    }
                    response = session.post('https://example.com/login', json=data)
                    
                    if response.status_code == 200:
                        logger.info("登录成功！")
                        return response.json().get('token')
                    else:
                        logger.error(f"登录失败，状态码: {response.status_code}")
                else:
                    logger.error("验证码识别失败")
            else:
                logger.error("未获取到验证码图片")

        except Exception as e:
            logger.error(f"登录尝试失败: {e}")

    return None

# 测试登录流程
username = input("请输入用户名: ")
password = input("请输入密码: ")
login(username, password)
