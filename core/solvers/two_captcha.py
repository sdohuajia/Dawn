import asyncio
import base64
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Tuple
import httpx

import cv2
import numpy as np
from paddleocr import PaddleOCR
rec_model_path = './en_PP-OCRv4_rec_infer'
if os.name == 'posix':  # Linux 和 macOS 使用 posix
    rec_model_path = './en_PP-OCRv3_rec_infer' # 识别模型文件夹路径

ocr = PaddleOCR(rec_model_dir=rec_model_path, lang='en',  use_angle_cls=False, show_log=False)
class TwoCaptchaImageSolver:
    BASE_URL = "https://api.2captcha.com"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=10)
    async def solvecaps(self,imgBase: str)-> Tuple[str, bool]:
        image_data = base64.b64decode(imgBase)
        image_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        # cv2.waitKey(0)
        _, binary_image_img = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY_INV)
        kernel_img = np.ones((2, 2), np.uint8)
        opening_img = cv2.morphologyEx(binary_image_img, cv2.MORPH_ERODE, kernel_img)
        success, image_data = cv2.imencode('.png', opening_img)
        image_data = image_data.tobytes()
        results = await asyncio.to_thread(ocr.ocr, image_data,  False, True,False)
        line_text, confidence = results[0][0]
        capcode = line_text.replace(" ", "")
        return  (capcode, True)
    async def solve(self, image: str) -> Tuple[str, bool]:
        try:
            captcha_data = {
                "clientKey": self.api_key,
                "softId": 4706,
                "task": {
                    "type": "ImageToTextTask",
                    "body": image,
                    "phrase": False,
                    "case": True,
                    "numeric": 4,
                    "math": False,
                    "minLength": 6,
                    "maxLength": 6,
                    "comment": "Pay close attention to the letter case.",
                },
            }

            resp = await self.client.post(
                f"{self.BASE_URL}/createTask", json=captcha_data
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("errorId") == 0:
                return await self.get_captcha_result(data.get("taskId"))
            return data.get("errorDescription"), False

        except httpx.HTTPStatusError as err:
            return f"HTTP error occurred: {err}", False
        except Exception as err:
            return f"An unexpected error occurred: {err}", False

    async def get_captcha_result(
        self, task_id: int | str
    ) -> tuple[Any, bool, int | str] | tuple[str, bool, int | str] | tuple[str, bool]:
        for _ in range(10):
            try:
                resp = await self.client.post(
                    f"{self.BASE_URL}/getTaskResult",
                    json={"clientKey": self.api_key, "taskId": task_id},
                )
                resp.raise_for_status()
                result = resp.json()

                if result.get("errorId") != 0:
                    return result.get("errorDescription"), False, task_id

                if result.get("status") == "ready":
                    return result["solution"].get("text", ""), True, task_id

                await asyncio.sleep(3)

            except httpx.HTTPStatusError as err:
                return f"HTTP error occurred: {err}", False, task_id
            except Exception as err:
                return f"An unexpected error occurred: {err}", False, task_id

        return "Max time for solving exhausted", False

    async def report_bad(self, task_id: str | int) -> Tuple[Any, bool]:
        try:
            resp = await self.client.post(
                f"{self.BASE_URL}/reportIncorrect",
                json={"clientKey": self.api_key, "taskId": task_id},
            )
            resp.raise_for_status()
            return resp.json(), True
        except httpx.HTTPStatusError as err:
            return f"HTTP error occurred: {err}", False
        except Exception as err:
            return f"An unexpected error occurred: {err}", False
