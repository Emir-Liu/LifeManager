# Google Calendar API Demo 安装指南

## 前置要求

- Python 3.7 或更高版本
- Google 账号（用于 OAuth 2.0 认证）

## 安装步骤

### 1. 安装 Python 依赖

```bash
# 进入项目目录
cd e:/project/LifeManager/others/code_demo

# 安装依赖
pip install -r requirements.txt
```

或手动安装：

```bash
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

### 2. 获取 Google OAuth 2.0 凭证

#### 2.1 创建 Google Cloud 项目

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 点击"创建项目"
3. 输入项目名称（如：`calendar-api-demo`）
4. 点击"创建"

#### 2.2 启用 Calendar API

1. 在 Google Cloud Console 中，进入"API 和服务" > "库"
2. 搜索"Calendar API"
3. 点击"Google Calendar API"
4. 点击"启用"

#### 2.3 配置 OAuth 同意屏幕

1. 进入"API 和服务" > "OAuth 同意屏幕"
2. 选择"外部"
3. 填写必要信息：
   - 应用名称：`Calendar API Demo`
   - 用户支持电子邮件：你的邮箱
   - 开发者联系信息：你的邮箱
4. 点击"保存并继续"
5. 其他步骤可以点击"保存并继续"跳过

#### 2.4 创建 OAuth 2.0 客户端 ID

1. 进入"API 和服务" > "凭据"
2. 点击"创建凭据" > "OAuth 客户端 ID"
3. 应用类型选择：`桌面应用程序`
4. 名称输入：`Calendar API Demo Client`
5. 点击"创建"

#### 2.5 下载凭据文件

1. 创建凭据后，会弹出下载窗口
2. 下载 JSON 文件
3. 将文件重命名为 `client_secret.json`
4. 放置到 `e:/project/LifeManager/others/code_demo/` 目录下

**注意**：`client_secret.json` 文件包含敏感信息，不要提交到版本控制系统（如 Git）。

### 3. 运行示例

#### 3.1 首次运行（OAuth 认证）

首次运行任何示例时，会自动打开浏览器进行 OAuth 2.0 认证：

```bash
python examples.py
```

认证流程：
1. 浏览器会自动打开 Google 登录页面
2. 登录你的 Google 账号
3. 点击"允许"授权访问日历
4. 认证成功后，会在当前目录生成 `token.json` 文件
5. 后续运行会自动使用保存的凭证

#### 3.2 运行特定示例

编辑 `examples.py` 文件，在文件末尾取消注释要运行的示例：

```python
if __name__ == '__main__':
    # 运行所有示例
    # run_all_examples()

    # 或运行单个示例
    example_1_create_simple_event()
```

然后运行：

```bash
python examples.py
```

## 项目结构

```
code_demo/
├── config.py                      # 配置文件
├── base_client.py                 # 基础客户端
├── calendars_service.py           # 日历资源服务
├── events_service.py              # 事件资源服务
├── calendarlist_service.py        # 日历列表资源服务
├── acl_service.py                 # 访问控制列表服务
├── freebusy_service.py           # 忙闲查询服务
├── settings_service.py            # 设置资源服务
├── channels_service.py            # 通道资源服务
├── google_calendar_client.py      # 统一客户端
├── examples.py                    # 使用示例
├── requirements.txt               # 依赖包列表
├── INSTALL.md                     # 安装指南（本文件）
└── README.md                      # 详细文档
```

## 常见问题

### Q1: 认证失败或 token 过期

**解决方案**：
```bash
# 删除过期的 token 文件
rm token.json

# 重新运行示例，会重新进行认证
python examples.py
```

### Q2: 配额超限（429 错误）

**解决方案**：
- 减少请求频率
- 使用缓存减少重复请求
- 检查配额使用情况：[Google Cloud Console](https://console.cloud.google.com/apis/dashboard)

### Q3: 权限不足（403 错误）

**解决方案**：
- 检查 `config.py` 中的 `SCOPES` 配置
- 确保在 Google Cloud Console 中启用了 Calendar API
- 重新生成 `client_secret.json`

### Q4: 找不到模块

**解决方案**：
```bash
# 确保在正确的目录
cd e:/project/LifeManager/others/code_demo

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

### Q5: 跨时区问题

**解决方案**：
在 `config.py` 中修改默认时区：
```python
TIMEZONE = 'Asia/Shanghai'  # 或其他时区
```

或在创建事件时指定时区：
```python
event = client.events.insert(
    summary='会议',
    start=datetime.now(),
    end=datetime.now() + timedelta(hours=1),
    # 时间会在 base_client.py 中自动处理
)
```

## 下一步

1. 阅读详细文档：[README.md](README.md)
2. 查看完整示例：[examples.py](examples.py)
3. 根据需求修改配置：[config.py](config.py)
4. 集成到你的项目中

## 参考资料

- [Google Calendar API v3 官方文档](https://developers.google.com/workspace/calendar/api/v3/reference)
- [Python 客户端库文档](https://googleapis.github.io/google-api-python-client/docs/epy/googleapiclient.html)
- [OAuth 2.0 认证指南](https://developers.google.com/workspace/guides/authenticate-overview)

## 支持

如有问题，请查阅：
1. 本文档的"常见问题"部分
2. [README.md](README.md) 中的错误处理章节
3. Google Calendar API 官方文档
