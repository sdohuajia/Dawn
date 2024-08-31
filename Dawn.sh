#!/bin/bash

# 脚本保存路径
SCRIPT_PATH="$HOME/Dawn.sh"

# 检查并安装必备工具的函数
function check_and_install() {
    for cmd in "$@"; do
        if ! command -v "$cmd" &> /dev/null; then
            echo "$cmd 未安装，正在安装..."
            if [ "$cmd" == "python3-pip" ]; then
                sudo apt install -y python3-pip
            else
                sudo apt install -y "$cmd"
            fi
        else
            echo "$cmd 已安装"
        fi
    done
}

# 安装特定版本 Go 的函数
function install_go() {
    REQUIRED_GO_VERSION="1.22.3"
    CURRENT_GO_VERSION=$(go version 2>/dev/null | awk '{print $3}' | cut -d. -f1,2)

    if [ "$CURRENT_GO_VERSION" != "$REQUIRED_GO_VERSION" ]; then
        echo "当前 Go 版本 ($CURRENT_GO_VERSION) 不符合要求 ($REQUIRED_GO_VERSION)。正在安装正确版本..."
        wget -q https://golang.org/dl/go$REQUIRED_GO_VERSION.linux-amd64.tar.gz || { echo "下载 Go 失败"; exit 1; }
        sudo rm -rf /usr/local/go
        sudo tar -C /usr/local -xzf go$REQUIRED_GO_VERSION.linux-amd64.tar.gz
        echo "export PATH=\$PATH:/usr/local/go/bin" >> ~/.bashrc
        source ~/.bashrc
        echo "Go $REQUIRED_GO_VERSION 安装完成。"
    else
        echo "Go 已经是正确版本 ($REQUIRED_GO_VERSION)。"
    fi
}

# 安装 PM2 的函数
function install_pm2() {
    if ! command -v pm2 &> /dev/null; then
        echo "PM2 未安装，正在安装..."
        npm install pm2@latest -g
    else
        echo "PM2 已安装"
    fi
}

# 启动 Dawn 的函数
function install_and_start_dawn() {
    echo "更新包列表..."
    sudo apt update

    check_and_install go git curl python3-pip

    # 安装 Go 和 PM2
    install_go
    install_pm2

    # 安装 Python 包
    pip3 install pillow ddddocr requests loguru

    # 获取用户名和密码
    read -r -p "请输入邮箱: " DAWNUSERNAME
    export DAWNUSERNAME=$DAWNUSERNAME
    read -r -p "请输入密码: " DAWNPASSWORD
    export DAWNPASSWORD=$DAWNPASSWORD

    echo "$DAWNUSERNAME:$DAWNPASSWORD" > password.txt

    wget -O dawn.py https://raw.githubusercontent.com/b1n4he/DawnAuto/main/dawn.py || { echo "下载 dawn.py 失败"; exit 1; }

    # 更新和安装其他必要的软件
    sudo apt update && sudo apt upgrade -y
    check_and_install curl iptables build-essential git wget jq make gcc nano tmux htop nvme-cli pkg-config libssl-dev libleveldb-dev tar clang bsdmainutils ncdu unzip lz4 snapd

    # 启动 Dawn
    pm2 start dawn.py

    # 等待用户按任意键以返回主菜单
    read -p "按任意键返回主菜单..."
}

# 查看日志的函数
function view_logs() {
    pm2 log dawn
    # 等待用户按任意键以返回主菜单
    read -p "按任意键返回主菜单..."
}

# 主菜单函数
function main_menu() {
    while true; do
        clear
        echo "脚本由大赌社区哈哈哈哈编写，推特 @ferdie_jhovie，免费开源，请勿相信收费"
        echo "================================================================"
        echo "节点社区 Telegram 群组: https://t.me/niuwuriji"
        echo "节点社区 Telegram 频道: https://t.me/niuwuriji"
        echo "节点社区 Discord 社群: https://discord.gg/GbMV5EcNWF"
        echo "退出脚本，请按键盘 ctrl + C 退出即可"
        echo "请选择要执行的操作:"
        echo "1) 安装并启动 Dawn"
        echo "2) 查看日志"
        echo "3) 退出"

        read -p "请输入选项 [1-3]: " choice

        case $choice in
            1)
                install_and_start_dawn
                ;;
            2)
                view_logs
                ;;
            3)
                echo "退出脚本..."
                exit 0
                ;;
            *)
                echo "无效选项，请重新选择。"
                read -n 1 -s -r -p "按任意键继续..."
                ;;
        esac
    done
}

# 运行主菜单
main_menu
