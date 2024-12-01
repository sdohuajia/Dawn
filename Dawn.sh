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

# 安装和配置函数
function install_and_configure() {
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
        sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
        sudo apt install libopencv-dev python3-opencv
        # 添加 pip 升级命令
        python3.11 -m pip install --upgrade pip  # 升级 pip
        echo "Python 3.11 和 pip 安装完成。"
    }

    # 检查 Python 版本
    check_python_installed

    # 更新包列表并安装 git 和 tmux
    echo "正在更新软件包列表和安装 git 和 tmux..."
    sudo apt update
    sudo apt install -y git tmux python3.11-venv libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev

    # 检查 Dawn 目录是否存在，如果存在则删除	
    if [ -d "$DAWN_DIR" ]; then	
        echo "检测到 Dawn 目录已存在，正在删除..."	
        rm -rf "$DAWN_DIR"	
        echo "Dawn 目录已删除。"	
    fi

     # 检查并终止已存在的 Dawn tmux 会话
    if tmux has-session -t dawn 2>/dev/null; then
        echo "检测到正在运行的 dawn 会话，正在终止..."
        tmux kill-session -t dawn
        echo "已终止现有的 dawn 会话。"
    fi
    
    # 克隆 GitHub 仓库
    echo "正在从 GitHub 克隆仓库..."
    git clone https://github.com/sdohuajia/Dawn-bot.git "$DAWN_DIR"

    # 检查克隆操作是否成功
    if [ ! -d "$DAWN_DIR" ]; then
        echo "克隆失败，请检查网络连接或仓库地址。"
        exit 1
    fi

    # 进入仓库目录
    cd "$DAWN_DIR" || { echo "无法进入 Dawn 目录"; exit 1; }

    # 创建虚拟环境
    python3.11 -m venv venv  # 创建虚拟环境
    source venv/bin/activate  # 激活虚拟环境

    # 配置邮件和Token
    echo "请分别输入您的邮箱、密码和2captcha API密钥"
    read -p "请输入邮箱: " email
    read -p "请输入密码: " password
    read -p "请输入2captcha API密钥: " captcha_key

    # 验证输入不为空
    while [[ -z "$email" || -z "$password" || -z "$captcha_key" ]]; do
        echo "错误：邮箱、密码和2captcha API密钥都不能为空！"
        read -p "请输入邮箱: " email
        read -p "请输入密码: " password
        read -p "请输入2captcha API密钥: " captcha_key
    done

    # 更新settings.yaml文件中的two_captcha_api_key
    settings_file="$DAWN_DIR/config/settings.yaml"
    if [ -f "$settings_file" ]; then
        # 使用sed替换two_captcha_api_key的值
        sed -i "s/two_captcha_api_key: .*/two_captcha_api_key: \"$captcha_key\"/" "$settings_file"
    else
        echo "错误：未找到settings.yaml文件"
        exit 1
    fi

    # 组合成需要的格式并写入farm.txt
    email_token="${email}:${password}"
    farm_file="$DAWN_DIR/config/data/farm.txt"
    echo "$email_token" > "$farm_file"
    echo "账户信息已写入 $farm_file"

    # 配置代理信息
    read -p "请输入您的代理信息，格式为 (http://user:pass@ip:port): " proxy_info
    proxies_file="$DAWN_DIR/config/data/proxies.txt"

    # 将代理信息写入文件
    echo "$proxy_info" > "$proxies_file"
    echo "代理信息已添加到 $proxies_file."

    echo "安装、克隆、虚拟环境设置和配置已完成！"
    echo "正在运行脚本 python3 run.py..."
    
    echo "正在使用 tmux 启动 main.py..."
    tmux new-session -d -s dawn  # 创建新的 tmux 会话，名称为 dawn
    tmux send-keys -t dawn "cd Dawn" C-m  # 切换到 Dawn 目录
    tmux send-keys -t dawn "source \"venv/bin/activate\"" C-m  # 激活虚拟环境
    tmux send-keys -t dawn "python3.11 -m pip install -r requirements.txt" C-m  # 安装依赖
    tmux send-keys -t dawn "python3.11 run.py" C-m  # 启动 main.py
    echo "使用 'tmux attach -t dawn' 命令来查看日志。"
    echo "要退出 tmux 会话，请按 Ctrl+B 然后按 D。"

    # 提示用户按任意键返回主菜单
    read -n 1 -s -r -p "按任意键返回主菜单..."
}

# 安装和配置 Grassnode 函数
function setup_grassnode() {
    # 检查 grass 目录是否存在，如果存在则删除
    if [ -d "grass" ]; then
        echo "检测到 grass 目录已存在，正在删除..."
        rm -rf grass
        echo "grass 目录已删除。"
    fi

    # 检查并终止已存在的 grass tmux 会话
    if tmux has-session -t grass 2>/dev/null; then
        echo "检测到正在运行的 grass 会话，正在终止..."
        tmux kill-session -t grass
        echo "已终止现有的 Nodepay 会话。"
    fi
    
    # 安装 npm 环境
    sudo apt update
    sudo apt install -y nodejs npm
    sudo apt-get install tmux
    sudo apt install node-cacache node-gyp node-mkdirp node-nopt node-tar node-which

    # 检查 Node.js 版本
    node_version=$(node -v 2>/dev/null)
    if [[ $? -ne 0 || "$node_version" != v16* ]]; then
        echo "当前 Node.js 版本为 $node_version，正在安装 Node.js 16..."
        # 安装 Node.js 16
        curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
        sudo apt install -y nodejs
    else
        echo "Node.js 版本符合要求：$node_version"
    fi

    echo "正在从 GitHub 克隆 grass 仓库..."
    git clone https://github.com/sdohuajia/grass-2.0.git grass
    if [ ! -d "grass" ]; then
        echo "克隆失败，请检查网络连接或仓库地址。"
        exit 1
    fi

    cd "grass" || { echo "无法进入 grass 目录"; exit 1; }

    # 配置代理信息
    read -p "请输入您的代理信息，格式为 http://user:pass@ip:port: " proxy_info
    proxy_file="/root/grass/proxy.txt"  # 更新文件路径为 /root/grass/proxy.txt

    # 将代理信息写入文件
    echo "$proxy_info" > "$proxy_file"
    echo "代理信息已添加到 $proxy_file."

    # 获取用户ID并写入 uid.txt
    read -p "请输入您的 userId: " user_id
    uid_file="/root/grass/uid.txt"  # uid 文件路径

    # 将 userId 写入文件
    echo "$user_id" > "$uid_file"
    echo "userId 已添加到 $uid_file."

    # 安装 npm 依赖
    echo "正在安装 npm 依赖..."
    npm install

    # 使用 tmux 自动运行 npm start
    tmux new-session -d -s grass  # 创建新的 tmux 会话，名称为 grass
    tmux send-keys -t teneo "cd grass" C-m  # 切换到 grass 目录
    tmux send-keys -t grass "npm start" C-m # 启动 npm start
    echo "npm 已在 tmux 会话中启动。"
    echo "使用 'tmux attach -t grass' 命令来查看日志。"
    echo "要退出 tmux 会话，请按 Ctrl+B 然后按 D。"

    # 提示用户按任意键返回主菜单
    read -n 1 -s -r -p "按任意键返回主菜单..."
}

# 安装和配置 Teneo 函数
function setup_Teneonode() {
    # 检查 teneo 目录是否存在，如果存在则删除
    if [ -d "teneo" ]; then
        echo "检测到 teneo 目录已存在，正在删除..."
        rm -rf teneo
        echo "teneo 目录已删除。"
    fi

    # 检查并终止已存在的 teneo tmux 会话
    if tmux has-session -t teneo 2>/dev/null; then
        echo "检测到正在运行的 teneo 会话，正在终止..."
        tmux kill-session -t teneo
        echo "已终止现有的 teneo 会话。"
    fi
    
    echo "正在从 GitHub 克隆 teneo 仓库..."
    git clone https://github.com/sdohuajia/Teneo.git teneo
    if [ ! -d "teneo" ]; then
        echo "克隆失败，请检查网络连接或仓库地址。"
        exit 1
    fi

    cd "teneo" || { echo "无法进入 teneo 目录"; exit 1; }

    # 安装 Node.js 和 npm（如果尚未安装）
    if ! command -v npm &> /dev/null; then
    echo "正在安装 Node.js 和 npm..."
    curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
    sudo apt-get install -y nodejs
    fi

    # 安装 npm 依赖项
    echo "正在安装 npm 依赖项..."
    npm install || { echo "npm 依赖项安装失败"; exit 1; }

    # 创建 account.js 文件
    echo "正在配置账户信息..."
    read -p "请输入邮箱: " email
    read -s -p "请输入密码: " password
    echo  # 换行

    # 创建 account.js 文件
    cat > account.js << EOF
module.exports = [
  {
    email: "${email}",
    password: "${password}"
  },
  // Add more accounts as needed
];
EOF

    # 配置代理信息
    read -p "请输入您的代理信息，格式为 http://user:pass@ip:port: " proxy_info
    proxies_file="/root/teneo/proxy.txt"

    # 将代理信息写入文件
    echo "$proxy_info" > "$proxies_file"
    echo "代理信息已添加到 $proxies_file."

    echo "正在使用 tmux 启动应用..."
    tmux new-session -d -s teneo  # 创建新的 tmux 会话，名称为 teneo
    tmux send-keys -t teneo "cd teneo" C-m  # 切换到 teneo 目录
    tmux send-keys -t teneo "node index.js" C-m  # 使用 node index 启动应用
    echo "使用 'tmux attach -t teneo' 命令来查看日志。"
    echo "要退出 tmux 会话，请按 Ctrl+B 然后按 D。"

    # 提示用户按任意键返回主菜单
    read -n 1 -s -r -p "按任意键返回主菜单..."
}

# 安装和配置 Humanity 函数
function setup_Humanity() {
    # 检查 Humanity 目录是否存在，如果存在则删除
    if [ -d "Humanity" ]; then
        echo "检测到 Humanity 目录已存在，正在删除..."
        rm -rf Humanity
        echo "Humanity 目录已删除。"
    fi
    
    # 安装 Python 3.11
    sudo apt update
    sudo apt install -y software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt-get install -y python3-apt
    sudo apt-get install -y python3-dev libffi-dev
    # 添加 python3.11-venv 的安装
    sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
    echo "Python 3.11 和 pip 安装完成。"

    echo "正在从 GitHub 克隆 teneo 仓库..."
    git clone https://github.com/sdohuajia/Humanity.git
    if [ ! -d "Humanity" ]; then
        echo "克隆失败，请检查网络连接或仓库地址。"
        exit 1
    fi

    cd "Humanity" || { echo "无法进入 Humanity 目录"; exit 1; }

    # 创建虚拟环境
    python3.11 -m venv venv  # 创建虚拟环境
    source venv/bin/activate  # 激活虚拟环境
    
    echo "正在安装所需的 Python 包..."
    if [ ! -f requirements.txt ]; then
        echo "未找到 requirements.txt 文件，无法安装依赖。"
        exit 1
    fi
    
    python3.11 -m pip install -r requirements.txt

    # 手动安装 httpx
    python3.11 -m pip install httpx 
    
    # 配置私钥信息
    read -p "请输入您的私钥: " private_key
    private_keys_file="/root/Humanity/private_keys.txt"

    # 将私钥信息写入文件
    echo "$private_key" >> "$private_keys_file"
    echo "私钥信息已添加到 $private_keys_file."

    # 运行脚本
    echo "正在使用 tmux 启动 bot.py..."
    tmux new-session -d -s Humanity  # 创建新的 tmux 会话，名称为 Humanity
    tmux send-keys -t Humanity "cd Humanity" C-m  # 切换到 teneo 目录
    tmux send-keys -t Humanity "source \"venv/bin/activate\"" C-m  # 激活虚拟环境
    tmux send-keys -t Humanity "python3 bot.py" C-m  # 启动 bot.py
    echo "使用 'tmux attach -t Humanity' 命令来查看日志。"
    echo "要退出 tmux 会话，请按 Ctrl+B 然后按 D。"

    # 提示用户按任意键返回主菜单
    read -n 1 -s -r -p "按任意键返回主菜单..."
}

# 安装和配置 Nodepay 函数
function setup_Nodepay() {
    # 检查 Nodepay 目录是否存在，如果存在则删除
    if [ -d "Nodepay" ]; then
        echo "检测到 Nodepay 目录已存在，正在删除..."
        rm -rf Nodepay
        echo "Nodepay 目录已删除。"
    fi
    
    # 检查并终止已存在的 Nodepay tmux 会话
    if tmux has-session -t Nodepay 2>/dev/null; then
        echo "检测到正在运行的 Nodepay 会话，正在终止..."
        tmux kill-session -t Nodepay
        echo "已终止现有的 Nodepay 会话。"
    fi
    
    # 检查 Python 是否安装
    function check_python_installed() {
        if command -v python3.11 &>/dev/null; then
            echo "Python 3.11 已安装。"
        else
            echo "未安装 Python 3.11，正在安装..."
            install_python
        fi
    }

    # 安装 Python 3.11 和系统依赖
    function install_python() {
        echo "正在安装 Python 3.11 和系统依赖..."
        sudo apt update
        sudo apt install -y software-properties-common
        sudo add-apt-repository ppa:deadsnakes/ppa -y
        
        # 安装 Python 和系统依赖
        sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip libopencv-dev python3-opencv build-essential libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev libjpeg-dev libpng-dev libtiff-dev libcurl4-openssl-dev libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libcairo2-dev pkg-config gcc g++ make git tmux

        # 升级 pip
        python3.11 -m pip install --upgrade pip
        echo "Python 3.11 和系统依赖安装完成。"
    }

    # 检查 Python 版本
    check_python_installed

    echo "正在从 GitHub 克隆 Nodepay 仓库..."
    git clone https://github.com/sdohuajia/Nodepay.git Nodepay
    if [ ! -d "Nodepay" ]; then
        echo "克隆失败，请检查网络连接或仓库地址。"
        exit 1
    fi

    cd "Nodepay" || { echo "无法进入 Nodepay 目录"; exit 1; }

    # 配置代理信息
    read -p "请输入您的代理信息，格式为 （http://user:pass@ip:port或者socks5）: " proxy_info
    proxies_file="/root/Nodepay/proxy.txt"

    # 将代理信息写入文件
    echo "$proxy_info" > "$proxies_file"
    echo "代理信息已添加到 $proxies_file"

    # 获取用户ID并写入 token.txt
    read -p "请输入您的 np_tokens: " user_id
    uid_file="/root/Nodepay/token.txt"

    # 将 userId 写入文件
    echo "$user_id" > "$uid_file"
    echo "userId 已添加到 $uid_file"

    # 使用 tmux 启动应用
    echo "正在使用 tmux 启动 main.py..."
    tmux new-session -d -s Nodepay  # 创建新的 tmux 会话，名称为 Nodepay
    tmux send-keys -t Nodepay "cd Nodepay" C-m  # 切换到 Nodepay 目录
    tmux send-keys -t Nodepay "python3 -m pip install -r requirements.txt" C-m  # 安装依赖
    tmux send-keys -t Nodepay "python3 main.py" C-m  # 启动 main.py

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
        echo "1. 安装部署 Dawn"
        echo "2. 安装部署 Grass"
        echo "3. 安装部署 Teneo"
        echo "4. Humanity每日签到"
        echo "5. 安装部署 Nodepay"
        echo "6. 退出"

        read -p "请输入您的选择 (1,2,3,4,5,6): " choice
        case $choice in
            1)
                install_and_configure  # 调用安装和配置函数
                ;;
            2)
                setup_grassnode  # 调用安装和配置函数
                ;;
            3)
                setup_Teneonode  # 调用安装和配置函数
                ;;    
            4)
                setup_Humanity  # 调用安装和配置函数
                ;;    
            5)
                setup_Nodepay  # 调用安装和配置函数
                ;;    
            6)
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

# 进入主菜单
main_menu
