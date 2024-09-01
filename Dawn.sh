#!/bin/bash

# 脚本保存路径
SCRIPT_PATH="$HOME/Dawn.sh"

# 检查是否以root用户运行脚本
if [ "$(id -u)" != "0" ]; then
    echo "此脚本需要以root用户权限运行。"
    echo "请尝试使用 'sudo -i' 命令切换到root用户，然后再次运行此脚本。"
    exit 1
fi

# 检查并安装 Node.js 和 npm
function install_nodejs_and_npm() {
    if command -v node > /dev/null 2>&1; then
        echo "Node.js 已安装"
    else
        echo "Node.js 未安装，正在安装..."
        curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi

    if command -v npm > /dev/null 2>&1; then
        echo "npm 已安装"
    else
        echo "npm 未安装，正在安装..."
        sudo apt-get install -y npm
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

# 检查和安装其他软件包
function check_and_install() {
    for package in "$@"; do
        if ! dpkg -l | grep -q "^ii  $package "; then
            echo "$package 未安装，正在安装..."
            sudo apt-get install -y "$package"
        else
            echo "$package 已安装"
        fi
    done
}

# 安装并启动 Dawn 的函数
function install_and_start_dawn() {
    echo "更新包列表..."
    sudo apt update
    
    # 安装 Node.js 和 npm，PM2
    install_nodejs_and_npm
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
    pm2 start python3 -- dawn.py

    # 等待用户按任意键以返回主菜单
    read -p "按任意键返回主菜单..."
}

# 查看日志的函数
function view_logs() {
    pm2 log dawn.py
    # 等待用户按任意键以返回主菜单
    read -p "按任意键返回主菜单..."
}

# 停止并删除 Dawn 的函数
function stop_and_remove_dawn() {
    if pm2 list | grep -q "dawn"; then
        echo "停止 Dawn..."
        pm2 stop dawn.py
        echo "删除 Dawn..."
        pm2 delete dawn.py
    else
        echo "Dawn 未在运行"
    fi

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
        echo "3) 停止并删除 Dawn"
        echo "4) 退出"

        read -p "请输入选项 [1-4]: " choice

        case $choice in
            1)
                install_and_start_dawn
                ;;
            2)
                view_logs
                ;;
            3)
                stop_and_remove_dawn
                ;;
            4)
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
