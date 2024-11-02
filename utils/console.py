import os
import sys

import urllib3
from art import tprint
from loguru import logger


def setup():
    urllib3.disable_warnings()
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format="<light-cyan>{time:HH:mm:ss}</light-cyan> | <level> {level: <8}</level> | - <white>{"
        "message}</white>",
    )
    logger.add("./logs/logs.log", rotation="1 day", retention="7 days")


def show_dev_info():
    os.system("cls")
    tprint("JamBit")
    print("\033[36m" + "我的推特主页: " + "\033[34m" + "https://x.com/Hy78516012" + "\033[34m")
    print(
        "\033[36m"
        + "我的GitHub: "
        + "\033[34m"
        + "https://github.com/Gzgod"
        + "\033[34m"
    )
    print()
