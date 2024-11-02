#!/bin/bash

# 脚本保存路径
SCRIPT_PATH="$HOME/Dawn.sh"

# 检查是否以 root 用户运行脚本
if [ "$(id -u)" != "0" ]; then
    echo "此脚本需要以 root 用户权限运行。"
    echo "请尝试使用 'sudo -i' 命令切换到 root 用户，然后再次运行此脚本。"
    exit 1
fi

# 检查 Python 版本
function check_python_version() {
    if command -v python3 &>/dev/null; then
        python_version=$(python3 --version | awk '{print \$2}')
        echo "当前 Python 版本: $python_version"
        
        # 检查版本是否大于或等于 3.11
        if [[ $(echo "$python_version < 3.11" | bc) -eq 1 ]]; then
            echo "Python 版本低于 3.11，正在安装最新版本..."
            install_python
        else
            echo "Python 版本符合要求。"
        fi
    else
        echo "未安装 Python，正在安装最新版本..."
        install_python
    fi
}

# 安装 Python 3.11
function install_python() {
    sudo apt update
    sudo apt install -y software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install -y python3.11 python3.11-venv python3.11-dev
    echo "Python 3.11 安装完成。"
}

# 安装和配置函数
function install_and_configure() {
    # 更新包列表
    echo "正在更新软件包列表..."
    sudo apt update

    # 安装 git（如果尚未安装）
    echo "正在安装 git..."
    sudo apt install -y git

    # 克隆 GitHub 仓库
    echo "正在从 GitHub 克隆仓库..."
    git clone https://github.com/sdohuajia/Dawn.git

    # 进入仓库目录
    cd Dawn

    # 创建虚拟环境
    echo "正在创建虚拟环境..."
    python3 -m venv venv

    # 激活虚拟环境
    echo "正在激活虚拟环境..."
    source venv/bin/activate

    # 安装依赖
    echo "正在安装所需的 Python 包..."
    pip install -r requirements.txt

    # 提示用户输入 anti-captcha API key
    read -p "请输入您的 anti-captcha API 密钥: " anti_captcha_api_key

    # 设置配置文件路径
    config_file="/root/Dawn/config/settings.yaml"

    # 检查配置文件是否存在
    if [ ! -f "$config_file" ]; then
        echo "配置文件 $config_file 不存在."
        exit 1
    fi

    # 替换 settings.yaml 中的 anti-captcha API key
    echo "正在更新 settings.yaml 中的 anti-captcha API 密钥..."
    sed -i "s/anti_captcha_api_key: \".*\"/anti_captcha_api_key: \"$anti_captcha_api_key\"/" "$config_file"

    # 提示用户输入邮件和密码
    read -p "请输入您的邮箱和密码，格式为 email:password: " email_password

    # 设置 farm.txt 文件路径
    farm_file="/root/Dawn/config/data/farm.txt"

    # 检查 farm.txt 文件是否存在
    if [ ! -f "$farm_file" ]; then
        echo "正在创建 farm.txt 文件，路径为 $farm_file."
        touch "$farm_file"
    fi

    # 将用户输入写入 farm.txt
    echo "$email_password" >> "$farm_file"

    # 提示用户输入代理信息
    read -p "请输入您的代理信息，格式为 http://user:pass@ip:port: " proxy_info

    # 设置 proxies.txt 文件路径
    proxies_file="/root/Dawn/config/data/proxies.txt"

    # 检查 proxies.txt 文件是否存在
    if [ ! -f "$proxies_file" ]; then
        echo "正在创建 proxies.txt 文件，路径为 $proxies_file."
        touch "$proxies_file"
    fi

    # 将用户输入写入 proxies.txt
    echo "$proxy_info" >> "$proxies_file"

    echo "代理信息已添加到 $proxies_file."
    echo "安装、克隆、虚拟环境
