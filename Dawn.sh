#!/bin/bash

# 脚本保存路径
SCRIPT_PATH="$HOME/Dawn.sh"

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

    if ! command -v go &> /dev/null; then
        echo "Go 未安装，开始安装..."
        install_go
    else
        echo "Go 已经安装，检查版本..."
        install_go
    fi

    if ! command -v git &> /dev/null; then
        echo "Git 未安装，开始安装..."
        sudo apt install -y git
    else
        echo "Git 已经安装，跳过安装。"
    fi

    install_node
}

# 节点安装功能
function install_node() {
    install_pm2

    pip3 install pillow ddddocr requests loguru

    # 获取用户名和密码
    read -r -p "请输入邮箱: " DAWNUSERNAME
    export DAWNUSERNAME=$DAWNUSERNAME
    read -r -p "请输入密码: " DAWNPASSWORD
    export DAWNPASSWORD=$DAWNPASSWORD

    echo "$DAWNUSERNAME:$DAWNPASSWORD" > password.txt

    wget -O dawn.py https://raw.githubusercontent.com/b1n4he/DawnAuto/main/dawn.py || { echo "下载 dawn.py 失败"; exit 1; }

    # 更新和安装必要的软件
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y curl iptables build-essential git wget jq make gcc nano tmux htop nvme-cli pkg-config libssl-dev libleveldb-dev tar clang bsdmainutils ncdu unzip libleveldb-dev lz4 snapd

    pm2 start dawn.py
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
        echo "2) 退出"

        read -p "请输入选项 [1-2]: " choice

        case $choice in
            1)
                install_and_start_dawn
                ;;
            2)
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
