# LifeManager 部署脚本 (Windows PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "LifeManager MVP 部署脚本 (Windows)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Docker是否安装
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker已安装: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker未安装，请先安装Docker Desktop" -ForegroundColor Red
    exit 1
}

# 检查Docker Compose是否安装
try {
    $composeVersion = docker-compose --version
    Write-Host "✅ Docker Compose已安装: $composeVersion" -ForegroundColor Green
} catch {
    try {
        $composeVersion = docker compose version
        Write-Host "✅ Docker Compose已安装: $composeVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ Docker Compose未安装，请先安装Docker Compose" -ForegroundColor Red
        exit 1
    }
}

# 停止旧容器
Write-Host ""
Write-Host "停止旧容器..." -ForegroundColor Yellow
docker-compose down 2>$null
if ($?) {
    Write-Host "✅ 旧容器已停止" -ForegroundColor Green
} else {
    Write-Host "⚠️  没有旧容器需要停止" -ForegroundColor Yellow
}

# 拉取最新镜像
Write-Host ""
Write-Host "拉取最新镜像..." -ForegroundColor Yellow
docker-compose pull
Write-Host "✅ 镜像拉取完成" -ForegroundColor Green

# 构建新镜像
Write-Host ""
Write-Host "构建新镜像..." -ForegroundColor Yellow
docker-compose build --no-cache
Write-Host "✅ 镜像构建完成" -ForegroundColor Green

# 启动服务
Write-Host ""
Write-Host "启动服务..." -ForegroundColor Yellow
docker-compose up -d
Write-Host "✅ 服务已启动" -ForegroundColor Green

# 等待数据库就绪
Write-Host ""
Write-Host "等待数据库就绪..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 检查服务状态
Write-Host ""
Write-Host "检查服务状态..." -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "部署完成！" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "后端API: http://localhost:8000" -ForegroundColor White
Write-Host "API文档: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "查看日志: docker-compose logs -f" -ForegroundColor Gray
Write-Host "停止服务: docker-compose down" -ForegroundColor Gray
Write-Host ""
Write-Host "✅ LifeManager MVP 部署成功！" -ForegroundColor Green
