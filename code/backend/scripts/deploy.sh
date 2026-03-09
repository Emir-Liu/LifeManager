#!/bin/bash

# LifeManager 部署脚本

set -e

echo "========================================="
echo "LifeManager MVP 部署脚本"
echo "========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函数定义
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    print_error "Docker未安装，请先安装Docker"
    exit 1
fi

print_success "Docker已安装"

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

print_success "Docker Compose已安装"

# 停止旧容器
echo ""
echo "停止旧容器..."
docker-compose down || docker compose down
print_success "旧容器已停止"

# 拉取最新镜像
echo ""
echo "拉取最新镜像..."
docker-compose pull || docker compose pull
print_success "镜像拉取完成"

# 构建新镜像
echo ""
echo "构建新镜像..."
docker-compose build --no-cache || docker compose build --no-cache
print_success "镜像构建完成"

# 启动服务
echo ""
echo "启动服务..."
docker-compose up -d || docker compose up -d
print_success "服务已启动"

# 等待数据库就绪
echo ""
echo "等待数据库就绪..."
sleep 10

# 检查服务状态
echo ""
echo "检查服务状态..."
docker-compose ps || docker compose ps

# 显示日志
echo ""
echo "========================================="
echo "部署完成！"
echo "========================================="
echo ""
echo "后端API: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo ""
echo "查看日志: docker-compose logs -f"
echo "停止服务: docker-compose down"
echo ""
print_success "LifeManager MVP 部署成功！"
