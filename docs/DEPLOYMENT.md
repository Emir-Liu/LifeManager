# LifeManager 部署指南

本文档详细说明了如何将 LifeManager 应用部署到生产环境。

## 部署架构

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Nginx     │─────▶│  FastAPI    │─────▶| PostgreSQL  │
│   (80/443)  │      │   (8000)    │      │   (5432)    │
└─────────────┘      └─────────────┘      └─────────────┘
                           │
                           ├──────▶ Redis (6379)
                           │
                           └──────▶ Celery Workers
```

## 部署方式

### 方式一: Docker Compose (推荐)

适合中小型项目，一键部署所有服务。

#### 1. 准备服务器

购买云服务器（腾讯云、阿里云等），推荐配置：
- CPU: 2核
- 内存: 4GB
- 磁盘: 40GB SSD
- 操作系统: Ubuntu 22.04 LTS

#### 2. 安装 Docker

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version

# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER
```

#### 3. 准备配置文件

创建 `deployment/docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: lifemanager_postgres
    environment:
      POSTGRES_DB: lifemanager
      POSTGRES_USER: lifemanager
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped
    networks:
      - lifemanager_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U lifemanager -d lifemanager"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: lifemanager_redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - lifemanager_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile
    container_name: lifemanager_backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    environment:
      - DATABASE_URL=postgresql://lifemanager:${DB_PASSWORD}@postgres:5432/lifemanager
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - FCM_SERVER_KEY=${FCM_SERVER_KEY}
      - SMS_API_KEY=${SMS_API_KEY}
    volumes:
      - ../backend:/app
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - lifemanager_network

  worker:
    build:
      context: ../backend
      dockerfile: Dockerfile
    container_name: lifemanager_worker
    command: celery -A app.worker worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://lifemanager:${DB_PASSWORD}@postgres:5432/lifemanager
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ../backend:/app
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    networks:
      - lifemanager_network

  beat:
    build:
      context: ../backend
      dockerfile: Dockerfile
    container_name: lifemanager_beat
    command: celery -A app.worker beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://lifemanager:${DB_PASSWORD}@postgres:5432/lifemanager
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ../backend:/app
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    networks:
      - lifemanager_network

  nginx:
    image: nginx:alpine
    container_name: lifemanager_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ../frontend/dist:/usr/share/nginx/html:ro
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - lifemanager_network

networks:
  lifemanager_network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

#### 4. 配置环境变量

创建 `deployment/.env`:

```env
# 数据库密码
DB_PASSWORD=your-strong-password-here

# 应用密钥
SECRET_KEY=your-secret-key-change-this-in-production

# OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key

# FCM Server Key
FCM_SERVER_KEY=AAAAyour-fcm-server-key

# 短信API Key
SMS_API_KEY=your-sms-api-key
```

#### 5. 配置 Nginx

创建 `deployment/nginx/nginx.conf`:

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss;

    # 包含站点配置
    include /etc/nginx/conf.d/*.conf;
}
```

创建 `deployment/nginx/conf.d/app.conf`:

```nginx
upstream backend {
    server backend:8000;
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS 配置
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL 证书配置
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 静态文件
    root /usr/share/nginx/html;
    index index.html;

    # 前端路由
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理
    location /api/ {
        proxy_pass http://backend/v1/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket
    location /ws {
        proxy_pass http://backend/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API 文档
    location /docs {
        proxy_pass http://backend/docs;
    }

    # 禁止访问隐藏文件
    location ~ /\. {
        deny all;
    }

    # 静态资源缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 6. 获取 SSL 证书

使用 Let's Encrypt 免费证书:

```bash
# 安装 Certbot
sudo apt install certbot -y

# 停止 Nginx
docker-compose -f docker-compose.prod.yml stop nginx

# 获取证书
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# 复制证书到项目目录
sudo mkdir -p deployment/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem deployment/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem deployment/ssl/

# 启动 Nginx
docker-compose -f docker-compose.prod.yml start nginx
```

#### 7. 部署应用

```bash
cd deployment

# 构建并启动所有服务
docker-compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 初始化数据库
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

#### 8. 验证部署

访问以下地址验证部署是否成功：
- 前端: https://yourdomain.com
- API: https://yourdomain.com/api/
- 文档: https://yourdomain.com/docs

---

### 方式二: 传统部署

适合需要更多自定义配置的场景。

#### 1. 安装依赖

```bash
# 安装 PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# 安装 Redis
sudo apt install redis-server -y

# 安装 Python
sudo apt install python3.10 python3-pip python3-venv -y

# 安装 Nginx
sudo apt install nginx -y

# 安装 Supervisor
sudo apt install supervisor -y
```

#### 2. 配置 PostgreSQL

```bash
# 创建数据库
sudo -u postgres psql
CREATE DATABASE lifemanager;
CREATE USER lifemanager WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE lifemanager TO lifemanager;
\q
```

#### 3. 配置 Redis

```bash
# 启动 Redis
sudo systemctl start redis
sudo systemctl enable redis
```

#### 4. 部署后端

```bash
# 克隆代码
cd /opt
git clone https://github.com/yourusername/LifeManager.git
cd LifeManager/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 数据库迁移
alembic upgrade head

# 测试运行
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 5. 配置 Supervisor

创建 `/etc/supervisor/conf.d/lifemanager.conf`:

```ini
[program:lifemanager_backend]
command=/opt/LifeManager/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
directory=/opt/LifeManager/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/lifemanager/backend.log
environment=PATH="/opt/LifeManager/backend/venv/bin"

[program:lifemanager_worker]
command=/opt/LifeManager/backend/venv/bin/celery -A app.worker worker --loglevel=info
directory=/opt/LifeManager/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/lifemanager/worker.log
environment=PATH="/opt/LifeManager/backend/venv/bin"

[program:lifemanager_beat]
command=/opt/LifeManager/backend/venv/bin/celery -A app.worker beat --loglevel=info
directory=/opt/LifeManager/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/lifemanager/beat.log
environment=PATH="/opt/LifeManager/backend/venv/bin"
```

启动服务:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start lifemanager_*
```

#### 6. 部署前端

```bash
# 构建前端
cd /opt/LifeManager/frontend
npm install
npm run build:h5

# 复制构建文件到 Nginx
sudo cp -r dist/* /var/www/lifemanager/
```

配置 Nginx (与 Docker 方式相同)

#### 7. 启动 Nginx

```bash
sudo nginx -t
sudo systemctl restart nginx
```

---

## 监控和维护

### 日志管理

```bash
# Docker 部署查看日志
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f worker

# 传统部署查看日志
tail -f /var/log/lifemanager/backend.log
tail -f /var/log/lifemanager/worker.log
```

### 数据备份

创建备份脚本 `deployment/scripts/backup.sh`:

```bash
#!/bin/bash

# 配置
BACKUP_DIR="/opt/backups/lifemanager"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U lifemanager lifemanager > $BACKUP_DIR/db_$DATE.sql

# 压缩备份
gzip $BACKUP_DIR/db_$DATE.sql

# 删除旧备份
find $BACKUP_DIR -type f -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: db_$DATE.sql.gz"
```

设置定时任务:

```bash
chmod +x deployment/scripts/backup.sh

# 添加到 crontab
crontab -e

# 每天凌晨2点备份
0 2 * * * /opt/LifeManager/deployment/scripts/backup.sh
```

### 监控服务状态

```bash
# 检查服务状态
docker-compose -f docker-compose.prod.yml ps

# 重启服务
docker-compose -f docker-compose.prod.yml restart backend

# 查看资源使用
docker stats
```

---

## 性能优化

### 1. 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_goals_user_status ON goals(user_id, status);
CREATE INDEX idx_tasks_goal_date ON tasks(goal_id, scheduled_date);
CREATE INDEX idx_tasks_status_date ON tasks(status, scheduled_date);

-- 配置 PostgreSQL
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
-- 重启数据库生效
```

### 2. Redis 优化

```bash
# 编辑 redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
```

### 3. Nginx 优化

```nginx
# worker 进程数
worker_processes auto;

# 连接数
events {
    worker_connections 2048;
    use epoll;
}

# 缓存
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g 
                 inactive=60m use_temp_path=off;
```

---

## 安全加固

### 1. 防火墙配置

```bash
# 安装 UFW
sudo apt install ufw -y

# 允许 SSH
sudo ufw allow 22/tcp

# 允许 HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable
```

### 2. SSH 安全

```bash
# 禁用 root 登录
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# 禁用密码登录（使用密钥）
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# 重启 SSH
sudo systemctl restart sshd
```

### 3. 定期更新

```bash
# 自动更新安全补丁
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

---

## 故障排查

### 问题1: 容器无法启动

```bash
# 查看容器日志
docker-compose -f docker-compose.prod.yml logs backend

# 检查配置
docker-compose -f docker-compose.prod.yml config

# 重建容器
docker-compose -f docker-compose.prod.yml up -d --force-recreate
```

### 问题2: 数据库连接失败

```bash
# 检查数据库容器
docker-compose -f docker-compose.prod.yml ps postgres

# 进入数据库容器
docker-compose -f docker-compose.prod.yml exec postgres psql -U lifemanager -d lifemanager

# 检查网络连接
docker-compose -f docker-compose.prod.yml exec backend ping postgres
```

### 问题3: SSL 证书过期

```bash
# 续期证书
sudo certbot renew

# 重启 Nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

---

## 成本估算

| 资源 | 配置 | 月费用 (人民币) |
|------|------|---------------|
| 云服务器 | 2核4GB | ~50-100元 |
| 域名 | .com | ~60元/年 |
| SSL证书 | Let's Encrypt | 免费 |
| OpenAI API | GPT-4 | 按用量计费 |
| 短信服务 | 1000条/月 | ~20元 |
| 总计 | - | ~100-200元/月 |

---

## 扩展部署

### 水平扩展

当用户量增长时，可以扩展后端服务:

```yaml
# docker-compose.prod.yml
backend:
  deploy:
    replicas: 3

worker:
  deploy:
    replicas: 3
```

### 使用负载均衡

```nginx
upstream backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

---

## 参考资料

- [Docker 官方文档](https://docs.docker.com/)
- [Nginx 官方文档](https://nginx.org/en/docs/)
- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [Let's Encrypt 文档](https://letsencrypt.org/docs/)
