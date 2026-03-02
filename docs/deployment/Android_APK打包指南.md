# Android APK 打包指南

## 📱 生成 Android APK 文件

**项目**: LifeManager 托管人生
**平台**: Android
**打包方式**: HBuilderX 云打包（推荐）

---

## 方法1：使用 HBuilderX 云打包（推荐）⭐

### 步骤1：下载并安装 HBuilderX

1. 访问官网下载：https://www.dcloud.io/hbuilderx.html
2. 选择 **App 开发版**（支持云打包）
3. 安装并启动 HBuilderX

### 步骤2：导入项目

1. 在 HBuilderX 中选择 `文件` → `导入` → `从本地目录导入`
2. 选择项目目录：`e:/project/LifeManager/frontend`
3. 点击导入

### 步骤3：配置 manifest.json

1. 在 HBuilderX 左侧项目树中找到 `manifest.json`
2. 双击打开（会打开可视化配置界面）
3. 配置以下信息：

#### 基础配置
```
应用名称: 托管人生
版本名称: 1.0.0
版本号: 100
应用图标: 选择或上传应用图标
```

#### App 图标配置
- 选择 `App图标配置`
- 上传应用图标（1024x1024 像素）
- 自动生成不同尺寸的图标

#### Android 配置
- **包名**: `com.lifemanager.app`（唯一标识）
- **应用签名**:
  - 选择 `使用云端证书`（测试版）或 `使用自有证书`（正式版）
  - 云端证书：自动生成，但应用签名不一致
  - 自有证书：需要生成 keystore 文件（见下方）

### 步骤4：生成自有签名证书（可选，正式发布需要）

#### 方法A：使用命令行生成

```bash
# 进入 JDK bin 目录
cd "C:\Program Files\Java\jdk-xx\bin"

# 生成 keystore
keytool -genkey -alias lifemanager -keyalg RSA -keysize 2048 -validity 36500 -keystore lifemanager.keystore

# 会提示输入以下信息：
# - 输入密钥库口令: 设置一个密码（如：lifemanager123）
# - 再次输入新口令: 重复密码
# - 您的名字与姓氏是什么?: LifeManager
# - 您的组织单位名称是什么?: Development
# - 您的组织名称是什么?: LifeManager
# - 您所在的城市或区域名称是什么?: Beijing
# - 您所在的省/市/自治区名称是什么?: Beijing
# - 该单位的双字母国家/地区代码是什么?: CN
# - CN=LifeManager, OU=Development, O=LifeManager, L=Beijing, ST=Beijing, C=CN 是否正确?: 是
# - 输入 <lifemanager> 的密钥口令: 再次输入密码
```

#### 方法B：使用在线工具生成
- 访问：https://keystore-store.com/
- 输入信息生成 keystore 文件

### 步骤5：云打包

1. 在 HBuilderX 中点击 `发行` → `原生App-云打包`
2. 配置打包参数：

#### Android 打包配置
```
类型: 正式版
应用包名: com.lifemanager.app
应用图标: 已配置
应用名称: 托管人生
版本名称: 1.0.0
版本号: 100

证书类型:
  - 测试版：选择"使用云端证书"
  - 正式版：选择"使用自有证书"并上传 keystore 文件

证书信息（如使用自有证书）:
  - 别名: lifemanager
  - 私钥密码: lifemanager123
  - Keystore 密码: lifemanager123
```

3. 点击 `打包` 按钮
4. 等待打包完成（通常需要 5-10 分钟）
5. 打包成功后，APK 文件会自动下载到浏览器默认下载目录

### 步骤6：安装 APK 到手机

#### 方法A：USB 传输
1. 使用 USB 数据线连接手机和电脑
2. 启用手机 USB 调试模式
3. 将 APK 文件复制到手机
4. 在手机上点击安装
5. 允许安装未知来源应用

#### 方法B：云存储传输
1. 将 APK 上传到云盘（如：百度网盘、阿里云盘）
2. 在手机上下载并安装

#### 方法C：使用 ADB 安装
```bash
# 确保手机已连接并开启 USB 调试
adb devices

# 安装 APK
adb install lifemanager-v1.0.0.apk

# 如果安装失败，尝试覆盖安装
adb install -r lifemanager-v1.0.0.apk
```

---

## 方法2：使用命令行打包（进阶）

### 前置条件
```bash
# 1. 安装 Node.js
# 下载：https://nodejs.org/

# 2. 安装 uni-app CLI
npm install -g @dcloudio/uvm
npm install -g @dcloudio/vue-cli-plugin-uni

# 3. 安装 Java JDK
# 下载：https://www.oracle.com/java/technologies/downloads/
```

### 打包步骤

```bash
# 1. 进入前端项目目录
cd e:/project/LifeManager/frontend

# 2. 安装依赖
npm install

# 3. 构建为 Android 项目
npm run build:app-android

# 或使用 vue-cli
npx cross-env NODE_ENV=production UNI_PLATFORM=app-plus vue-cli-service uni-build

# 4. 打包生成的资源位于:
# unpackage/resources/__UNI__xxxxxxx/
```

### 使用 Android Studio 打包

```bash
# 1. 下载并安装 Android Studio
# https://developer.android.com/studio

# 2. 导入项目
# File -> New -> Import Project
# 选择: unpackage/resources/__UNI__xxxxxxx/

# 3. 配置签名
# Build -> Generate Signed Bundle / APK
# 选择 APK
# 选择或创建 keystore
# 选择 release
# 点击 Finish

# 4. APK 文件位置
# app/build/outputs/apk/release/app-release.apk
```

---

## 打包常见问题

### 问题1：云打包失败
**原因**：
- manifest.json 配置错误
- 网络问题
- DCloud 账号未登录

**解决方案**：
1. 检查 manifest.json 配置是否正确
2. 检查网络连接
3. 登录 DCloud 账号（发行 -> 登录）

### 问题2：应用图标未生效
**原因**：
- 图标尺寸不正确
- 缓存问题

**解决方案**：
1. 使用 1024x1024 像素的图标
2. 清理 HBuilderX 缓存

### 问题3：签名错误
**错误信息**: `Signature mismatch`

**解决方案**：
- 确保使用相同的 keystore 文件和密码
- 如果测试，可以使用云端证书

### 问题4：安装失败
**错误信息**: `解析包时出现问题`

**解决方案**：
1. 检查 APK 文件是否完整
2. 检查 Android 版本是否兼容（最低 Android 5.0）
3. 清理手机存储空间

---

## APK 文件位置

打包成功后，APK 文件位于：

### HBuilderX 云打包
- **默认位置**: 浏览器默认下载目录
- **文件名**: `lifemanager_100.apk` 或 `__UNI__xxxxxxx.apk`

### 本地打包
- **位置**: `unpackage/release/apk/`
- **文件名**: `app-release.apk`

---

## 验证安装

### 1. 安装后检查
```bash
# 查看 APK 包名
adb shell pm list packages | findstr lifemanager

# 查看应用版本
adb shell dumpsys package com.lifemanager.app | findstr version

# 启动应用
adb shell am start -n com.lifemanager.app/io.dcloud.PandoraEntry
```

### 2. 功能测试清单
- [ ] 应用启动正常
- [ ] 注册登录功能
- [ ] 创建目标功能
- [ ] AI 规划生成
- [ ] 任务列表显示
- [ ] 任务完成功能
- [ ] 网络请求正常

---

## 生产环境配置

### 修改 API 地址

在打包前，需要将 API 地址修改为生产环境地址：

#### 方法1：修改 request.js
```javascript
// frontend/utils/request.js
const baseURL = 'https://your-production-domain.com/api' // 生产环境地址
```

#### 方法2：使用环境变量
```javascript
// frontend/utils/request.js
const baseURL = process.env.NODE_ENV === 'production'
  ? 'https://your-production-domain.com/api'
  : 'http://localhost:8000/api'
```

### HTTPS 配置
- 确保 API 服务器使用 HTTPS
- 在 manifest.json 中配置网络安全策略

---

## 上传到应用商店

### Google Play 上传

1. **注册开发者账号**
   - 访问：https://play.google.com/console
   - 注册费用：$25（一次性）

2. **准备素材**
   - 应用图标（512x512）
   - 应用截图（至少2张，至少320像素宽）
   - 宣传视频（可选）
   - 应用说明

3. **上传 APK**
   - 创建应用
   - 上传签名后的 APK
   - 填写应用信息
   - 提交审核

### 国内应用商店

| 应用商店 | 上传地址 | 审核时间 |
|---------|---------|---------|
| 华为应用市场 | https://developer.huawei.com/consumer/cn/ | 2-3天 |
| 小米应用商店 | https://dev.mi.com/distribute | 1-2天 |
| 腾讯应用宝 | https://open.tencent.com/ | 2-3天 |
| OPPO 软件商店 | https://open.oppomobile.com/ | 2-3天 |
| vivo 应用商店 | https://dev.vivo.com.cn/ | 2-3天 |

---

## 快速命令参考

```bash
# 查看连接的设备
adb devices

# 安装 APK
adb install lifemanager.apk

# 卸载应用
adb uninstall com.lifemanager.app

# 查看日志
adb logcat -s UniApp

# 清除应用数据
adb shell pm clear com.lifemanager.app

# 重启应用
adb shell am force-stop com.lifemanager.app
adb shell am start -n com.lifemanager.app/io.dcloud.PandoraEntry
```

---

## 📋 打包前检查清单

- [ ] manifest.json 配置完整
- [ ] 应用图标已上传
- [ ] 应用包名已设置
- [ ] 版本号和版本名称正确
- [ ] API 地址已修改为生产环境
- [ ] 签名证书已准备（正式发布）
- [ ] 应用描述和截图已准备
- [ ] 已完成功能测试

---

## 📞 技术支持

- **HBuilderX 官方文档**: https://uniapp.dcloud.net.cn/
- **DCloud 社区**: https://ask.dcloud.net.cn/
- **Uni-app 云打包指南**: https://uniapp.dcloud.net.cn/tutorial/publish-app-plus.html

---

**文档版本**: 1.0.0
**最后更新**: 2026-02-03
**适用版本**: LifeManager v1.0.0
