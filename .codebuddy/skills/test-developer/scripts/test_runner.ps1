# PowerShell 测试运行脚本

Write-Host "========================================" -ForegroundColor Green
Write-Host "  LifeManager 测试运行脚本" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# 检查虚拟环境
if (-not (Test-Path "venv")) {
    Write-Host "未找到虚拟环境，创建中..." -ForegroundColor Yellow
    python -m venv venv
}

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
& venv\Scripts\Activate.ps1

# 安装依赖
Write-Host "安装依赖..." -ForegroundColor Yellow
pip install -q -r requirements.txt
pip install -q -r requirements-dev.txt

# 运行测试
Write-Host "运行测试..." -ForegroundColor Green
pytest $args

Write-Host "测试完成！" -ForegroundColor Green

# 显示覆盖率
if ($args -contains "--cov") {
    Write-Host "打开覆盖率报告..." -ForegroundColor Yellow
    Start-Process htmlcov\index.html
}
