#!/bin/bash
# 测试运行脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  LifeManager 测试运行脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}未找到虚拟环境，创建中...${NC}"
    python -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo -e "${YELLOW}安装依赖...${NC}"
pip install -q -r requirements.txt
pip install -q -r requirements-dev.txt

# 运行测试
echo -e "${GREEN}运行测试...${NC}"
pytest $@

echo -e "${GREEN}测试完成！${NC}"

# 显示覆盖率
if [ "$1" == "--cov" ]; then
    echo -e "${YELLOW}打开覆盖率报告...${NC}"
    open htmlcov/index.html || xdg-open htmlcov/index.html
fi
