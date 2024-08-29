#!/bin/bash

# 脚本保存路径
SCRIPT_PATH="$HOME/Dawn.sh"

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
        echo "3) 国外服务器运行节点（无需代理）"

        read -p "请输入选项 [1-3]: " choice

        case $choice in
            1)
                install_and_start_dawn
                ;;
            2)
                echo "退出脚本..."
                exit 0
                ;;
            3)
                run_foreign_server_node
                ;;
            *)
                echo "无效选项，请重新选择。"
                ;;
        esac
    done
}

# 安装特定版本 Go 的函数
function install_go() {
    REQUIRED_GO_VERSION="1.22.3"
    CURRENT_GO_VERSION=$(go version 2>/dev/null | awk -F ' ' '{print $3}' | sed 's/go//')

    if [ "$CURRENT_GO_VERSION" != "$REQUIRED_GO_VERSION" ]; then
        echo "当前 Go 版本 ($CURRENT_GO_VERSION) 不符合要求 ($REQUIRED_GO_VERSION)。正在安装正确版本..."
        wget -q https://golang.org/dl/go$REQUIRED_GO_VERSION.linux-amd64.tar.gz
        sudo rm -rf /usr/local/go
        sudo tar -C /usr/local -xzf go$REQUIRED_GO_VERSION.linux-amd64.tar.gz
        export PATH=$PATH:/usr/local/go/bin
        echo "Go $REQUIRED_GO_VERSION 安装完成。"
        source ~/.bashrc
    else
        echo "Go 已经是正确版本 ($REQUIRED_GO_VERSION)。"
    fi
}

# 安装 Go 环境并启动 Dawn 的函数
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

    echo "克隆项目..."
    if [ -d "Dawn-main" ]; then
        echo "Dawn-main 目录已存在，跳过克隆。"
    else
        git clone https://github.com/sdohuajia/Dawn-main.git
    fi
    cd Dawn-main || { echo "无法进入 Dawn-main 目录"; exit 1; }

    if [ ! -f "conf.toml" ]; then
        echo "配置文件 conf.toml 不存在，请确保文件存在并重新运行脚本。"
        exit 1
    fi

    echo "下载 Go 依赖..."
    go mod download

    echo "请编辑 conf.toml 文件。完成编辑后，按任意键继续..."
    nano conf.toml

    read -n 1 -s -r -p "按任意键继续..."

    echo "构建项目..."
    go build -o main .

    if [ ! -f "main" ]; then
        echo "构建失败，未找到可执行文件 main。"
        exit 1
    fi

    echo "执行项目..."
    ./main

    # 执行完成后直接返回主菜单，无需等待用户输入
}

# 运行主菜单
main_menu
