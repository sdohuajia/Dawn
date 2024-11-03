#!/bin/bash

# 脚本保存路径
SCRIPT_PATH="$HOME/Dawn.sh"
DAWN_DIR="$HOME/Dawn"

# 检查是否以 root 用户运行脚本
if [ "$(id -u)" != "0" ]; then
    echo "此脚本需要以 root 用户权限运行。"
    echo "请尝试使用 'sudo -i' 命令切换到 root 用户，然后再次运行此脚本。"
    exit 1
fi

# 检查 Python 3.11 是否已安装
function check_python_installed() {
    if command -v python3.11 &>/dev/null; then
        echo "Python 3.11 已安装。"
    else
        echo "未安装 Python 3.11，正在安装..."
        install_python
    fi
}

# 安装 Python 3.11
function install_python() {
    sudo apt update
    sudo apt install -y software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
    echo "Python 3.11 和 pip 安装完成。"
}

# 安装和配置函数
function install_and_configure() {
    # 检查 Dawn 目录是否存在，如果存在则删除
    if [ -d "$DAWN_DIR" ]; then
        echo "检测到 Dawn 目录已存在，正在删除..."
        rm -rf "$DAWN_DIR"
        echo "Dawn 目录已删除。"
    fi

    # 更新包列表并安装 git
    echo "正在更新软件包列表和安装 git..."
    sudo apt update
    sudo apt install -y git

    # 克隆 GitHub 仓库
    echo "正在从 GitHub 克隆仓库..."
    git clone https://github.com/sdohuajia/Dawn.git

    # 检查克隆操作是否成功
    if [ ! -d "$DAWN_DIR" ]; then
        echo "克隆失败，请检查网络连接或仓库地址。"
        exit 1
    fi

    # 进入仓库目录
    cd "$DAWN_DIR" || { echo "无法进入 Dawn 目录"; exit 1; }

    # 创建并激活虚拟环境
    echo "正在创建和激活虚拟环境..."
    python3.11 -m venv venv
    source "$DAWN_DIR/venv/bin/activate"

    # 安装依赖
    echo "正在安装所需的 Python 包..."
    if [ ! -f requirements.txt ]; then
        echo "未找到 requirements.txt 文件，无法安装依赖。"
        exit 1
    fi
    pip install -r requirements.txt
    pip install httpx

    # 配置 anti-captcha API 密钥
    read -p "请输入您的 anti-captcha API 密钥: " anti_captcha_api_key
    config_file="$DAWN_DIR/config/settings.yaml"
    if [ ! -f "$config_file" ]; then
        echo "配置文件 $config_file 不存在."
        exit 1
    fi
    sed -i "s/anti_captcha_api_key: \".*\"/anti_captcha_api_key: \"$anti_captcha_api_key\"/" "$config_file"

    # 配置邮件和密码
    read -p "请输入您的邮箱和密码，格式为 email:password: " email_password
    farm_file="$DAWN_DIR/config/data/farm.txt"
    [ ! -f "$farm_file" ] && touch "$farm_file"
    { echo "$email_password"; cat "$farm_file"; } > "$farm_file.tmp" && mv "$farm_file.tmp" "$farm_file"

    # 配置代理信息
    read -p "请输入您的代理信息，格式为 http://user:pass@ip:port: " proxy_info
    proxies_file="$DAWN_DIR/config/data/proxies.txt"
    [ ! -f "$proxies_file" ] && touch "$proxies_file"
    { echo "$proxy_info"; cat "$proxies_file"; } > "$proxies_file.tmp" && mv "$proxies_file.tmp" "$proxies_file"

    echo "安装、克隆、虚拟环境设置和配置已完成！"
    echo "正在运行脚本 python3.11 run.py..."
    python3.11 run.py
}

# 安装和配置 Grassnode 函数
function setup_grassnode() {
    echo "正在从 GitHub 克隆 grass 仓库..."
    git clone https://github.com/sdohuajia/grass.git
    if [ ! -d "/root/grass" ]; then
        echo "克隆失败，请检查网络连接或仓库地址。"
        exit 1
    fi

    cd "/root/grass" || { echo "无法进入 grass 目录"; exit 1; }
    echo "正在安装所需的 Python 包..."
    if [ ! -f requirements.txt ]; then
        echo "未找到 requirements.txt 文件，无法安装依赖。"
        exit 1
    fi
    python3.11 -m pip install -r requirements.txt

    # 配置代理信息
    read -p "请输入您的代理信息，格式为 http://user:pass@ip:port: " proxy_info
    proxies_file="$DAWN_DIR/config/data/proxies.txt"

    # 检查 proxies.txt 文件是否存在
    [ ! -f "$proxies_file" ] && touch "$proxies_file"

    # 删除空行并将用户输入写入 proxies.txt 的第一行
    {
    echo "$proxy_info"
    grep -v '^$' "$proxies_file"  # 删除原文件中的空行
    } > "$proxies_file.tmp" && mv "$proxies_file.tmp" "$proxies_file"

    echo "代理信息已添加到 $proxy_file."
    
    # 运行 setup.py
    [ -f setup.py ] && { echo "正在运行 setup.py..."; python3.11 setup.py; }

    echo "正在使用 screen 启动 main.py..."
    screen -S Grass -dm python3.11 main.py
    echo "使用 'screen -r Grass' 命令来查看日志。"
    echo "要退出 screen 会话，请按 Ctrl+A 然后按 D。"

    # 提示用户按任意键返回主菜单
    read -n 1 -s -r -p "按任意键返回主菜单..."
}

# 主菜单函数
function main_menu() {
    while true; do
        clear
        echo "脚本由大赌社区哈哈哈哈编写，推特 @ferdie_jhovie，免费开源，请勿相信收费"
        echo "如有问题，可联系推特，仅此只有一个号"
        echo "================================================================"
        echo "退出脚本，请按键盘 ctrl + C 退出即可"
        echo "请选择要执行的操作:"
        echo "1. 安装部署Dawn"
        echo "2. 安装部署Grass"
        echo "3. 退出"

        read -p "请输入您的选择 (1，2，3): " choice
        case $choice in
            1)
                install_and_configure  # 调用安装和配置函数
                ;;
            2)
                setup_grassnode  # 调用安装和配置函数
                ;;
            3)
                echo "退出脚本..."
                exit 0
                ;;
            *)
                echo "无效的选择，请重试."
                read -n 1 -s -r -p "按任意键继续..."
                ;;
        esac
    done
}

# 检查 Python 版本
check_python_installed

# 进入主菜单
main_menu
