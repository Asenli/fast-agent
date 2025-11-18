#!/bin/bash

# Docker 清理脚本
# 用于清理 fast-agent 项目的 Docker 容器、镜像和相关资源

set -e

echo "=========================================="
echo "Fast-Agent Docker 清理工具"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 显示菜单
show_menu() {
    echo "请选择清理选项："
    echo ""
    echo "1) 停止并删除容器（保留镜像）"
    echo "2) 停止并删除容器和镜像"
    echo "3) 停止并删除容器、镜像和卷"
    echo "4) 仅删除未使用的镜像（悬空镜像）"
    echo "5) 删除所有未使用的镜像"
    echo "6) 完整清理（所有未使用的资源）"
    echo "7) 仅查看镜像列表"
    echo "8) 退出"
    echo ""
    read -p "请输入选项 [1-8]: " choice
}

# 执行清理
clean_containers() {
    echo -e "${YELLOW}正在停止并删除容器...${NC}"
    docker-compose down
    echo -e "${GREEN}✓ 容器已删除${NC}"
}

clean_containers_and_images() {
    echo -e "${YELLOW}正在停止并删除容器和镜像...${NC}"
    docker-compose down --rmi all
    echo -e "${GREEN}✓ 容器和镜像已删除${NC}"
}

clean_all() {
    echo -e "${YELLOW}正在停止并删除容器、镜像和卷...${NC}"
    docker-compose down --rmi all -v
    echo -e "${GREEN}✓ 容器、镜像和卷已删除${NC}"
}

clean_dangling_images() {
    echo -e "${YELLOW}正在删除悬空镜像...${NC}"
    docker image prune -f
    echo -e "${GREEN}✓ 悬空镜像已删除${NC}"
}

clean_unused_images() {
    echo -e "${YELLOW}正在删除所有未使用的镜像...${NC}"
    docker image prune -a -f
    echo -e "${GREEN}✓ 未使用的镜像已删除${NC}"
}

clean_system() {
    echo -e "${RED}警告：这将删除所有未使用的 Docker 资源！${NC}"
    read -p "确认继续？(y/N): " confirm
    if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
        echo -e "${YELLOW}正在清理所有未使用的资源...${NC}"
        docker system prune -a -f
        echo -e "${GREEN}✓ 系统清理完成${NC}"
    else
        echo "已取消"
    fi
}

list_images() {
    echo -e "${GREEN}Fast-Agent 相关镜像：${NC}"
    echo ""
    docker images | grep -E "fast-agent|REPOSITORY" || echo "未找到相关镜像"
    echo ""
    echo -e "${GREEN}所有镜像：${NC}"
    docker images
}

# 主循环
while true; do
    show_menu
    case $choice in
        1)
            clean_containers
            ;;
        2)
            clean_containers_and_images
            ;;
        3)
            clean_all
            ;;
        4)
            clean_dangling_images
            ;;
        5)
            clean_unused_images
            ;;
        6)
            clean_system
            ;;
        7)
            list_images
            ;;
        8)
            echo "退出"
            exit 0
            ;;
        *)
            echo -e "${RED}无效选项，请重新选择${NC}"
            ;;
    esac
    echo ""
    read -p "按 Enter 键继续..."
    echo ""
done

