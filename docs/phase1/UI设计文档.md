# LifeManager MVP UI 设计文档

## 文档信息

- **版本**: v1.0
- **创建日期**: 2026-01-28
- **作者**: UI/UX 设计师
- **状态**: 已发布
- **适用阶段**: Phase 1 - MVP

---

## 1. 设计概述

### 设计原则

- **简洁优先**: MVP 阶段只保留核心功能，避免复杂交互
- **渐进披露**: 重要信息突出显示，次要信息折叠
- **一致性**: 保持颜色、字体、间距的统一
- **反馈及时**: 操作有明确的视觉反馈

### 设计风格

- **主色调**: 紫色系（渐变）- 体现科技感和 AI 智能特性
- **辅助色**: 灰色系 - 用于次要信息和分隔
- **强调色**: 绿色 - 表示成功、完成状态
- **警告色**: 橙色 - 提示用户注意
- **错误色**: 红色 - 错误提示

---

## 2. 全局设计规范

### 颜色规范

```css
/* 主色调 - 紫色渐变 */
--primary-gradient-start: #6366f1;
--primary-gradient-end: #8b5cf6;
--primary-color: #7c3aed;

/* 辅助色 */
--text-primary: #1f2937;
--text-secondary: #6b7280;
--text-tertiary: #9ca3af;
--background-primary: #ffffff;
--background-secondary: #f9fafb;
--background-tertiary: #f3f4f6;
--border-color: #e5e7eb;

/* 状态色 */
--success-color: #10b981;
--warning-color: #f59e0b;
--error-color: #ef4444;
--info-color: #3b82f6;
```

### 字体规范

```css
/* 字体大小 */
--font-size-xs: 12px;
--font-size-sm: 14px;
--font-size-base: 16px;
--font-size-lg: 18px;
--font-size-xl: 20px;
--font-size-2xl: 24px;
--font-size-3xl: 32px;

/* 字重 */
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;
```

### 间距规范

```css
/* 间距单位 (4px 基准) */
--spacing-xs: 4px;
--spacing-sm: 8px;
--spacing-md: 16px;
--spacing-lg: 24px;
--spacing-xl: 32px;
--spacing-2xl: 48px;

/* 圆角 */
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;
--radius-xl: 16px;
--radius-full: 9999px;
```

---

## 3. 页面设计

### 首页 (Index)

**布局**:
```
┌─────────────────────────────┐
│        托管人生             │  Logo + 标题
│    AI 智能人生管理助手      │  副标题
│                             │
│   [渐变紫色背景]            │
│                             │
│      [主按钮] 开始使用       │  大按钮
│      [次按钮] 已有账号登录   │  小按钮
│                             │
└─────────────────────────────┘
```

**设计要点**:
- 背景使用紫色渐变 (`linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)`)
- 标题大号白色字体，居中显示
- 主按钮：白色背景，紫色文字，圆角 12px，高度 48px
- 次按钮：透明背景，白色边框，圆角 8px，高度 40px

---

### 登录页 (Login)

**布局**:
```
┌─────────────────────────────┐
│                             │
│         [Logo]              │  应用 Logo
│        托管人生             │  应用名称
│                             │
├─────────────────────────────┤
│                             │
│   用户名                    │  输入框标签
│   ┌─────────────────────┐   │
│   │ 请输入用户名         │   │  用户名输入
│   └─────────────────────┘   │
│                             │
│   密码                      │  输入框标签
│   ┌─────────────────────┐   │
│   │ 请输入密码           │   │  密码输入(掩码)
│   └─────────────────────┘   │
│                             │
│   [ ] 记住我                │  复选框
│                             │
│   ┌─────────────────────┐   │
│   │      登 录          │   │  登录按钮
│   └─────────────────────┘   │
│                             │
│   还没有账号？去注册 →      │  注册入口
│                             │
└─────────────────────────────┘
```

**设计要点**:
- 顶部居中显示 Logo 和 应用名称
- 输入框：高度 48px，圆角 8px，边框 1px solid #e5e7eb
- 输入框聚焦时边框变为紫色 (#7c3aed)
- 登录按钮：紫色渐变背景，白色文字，圆角 12px，高度 48px
- 底部注册链接：紫色文字，点击跳转

**交互说明**:
- 用户名和密码为空时，登录按钮禁用
- 登录失败显示 Toast 提示
- 登录成功后保存 Token，跳转首页

---

### 注册页 (Register)

**布局**:
```
┌─────────────────────────────┐
│  ← 返回          用户注册   │  顶部导航栏
├─────────────────────────────┤
│                             │
│   用户名 *                  │  输入框标签
│   ┌─────────────────────┐   │
│   │ 请输入用户名         │   │
│   └─────────────────────┘   │
│   3-20个字符，支持字母数字   │  提示文字
│                             │
│   密码 *                    │  输入框标签
│   ┌─────────────────────┐   │
│   │ 请设置密码           │   │
│   └─────────────────────┘   │
│   至少6位字符               │  提示文字
│                             │
│   确认密码 *                │  输入框标签
│   ┌─────────────────────┐   │
│   │ 请再次输入密码       │   │
│   └─────────────────────┘   │
│                             │
│   邮箱 (选填)               │  输入框标签
│   ┌─────────────────────┐   │
│   │ 请输入邮箱(可选)     │   │
│   └─────────────────────┘   │
│                             │
│   ┌─────────────────────┐   │
│   │      注 册          │   │  注册按钮
│   └─────────────────────┘   │
│                             │
│   已有账号？去登录 →        │  登录入口
│                             │
└─────────────────────────────┘
```

**设计要点**:
- 顶部导航栏：左侧返回按钮，中间标题
- 必填项标记红色星号 *
- 实时验证：用户名、密码输入时实时校验
- 密码输入框右侧显示切换显隐图标

**表单验证规则**:
- 用户名：3-20 字符，字母/数字/下划线
- 密码：至少 6 位
- 确认密码：必须与密码一致
- 邮箱：有效邮箱格式（如填写）

**交互说明**:
- 验证失败时输入框边框变红，下方显示错误提示
- 注册成功自动登录并跳转首页
- 用户名已存在时提示错误

---

### 目标列表页 (Goals List)

**布局**:
```
┌─────────────────────────────┐
│  我的目标              [+添加]│  标题 + 添加按钮
├─────────────────────────────┤
│                             │
│  ┌───────────────────────┐  │
│  │ 学习 Python 编程      │  │  目标卡片
│  │ 规划中 • 3月完成     │  │
│  │ [查看规划]            │  │
│  └───────────────────────┘  │
│                             │
│  [空状态提示]              │  无目标时显示
│                             │
└─────────────────────────────┘
```

**设计要点**:
- 顶部固定栏：标题 + 添加按钮（+图标）
- 目标卡片：标题、状态标签、截止时间、按钮
- 卡片间距 16px，左右边距 16px

---

### 创建目标页 (Create Goal)

**布局**:
```
┌─────────────────────────────┐
│  ← 取消          创建目标   │  顶部导航栏
├─────────────────────────────┤
│                             │
│   目标名称 *                │  输入框标签
│   ┌─────────────────────┐   │
│   │ 例如：学习Python编程 │   │
│   └─────────────────────┘   │
│                             │
│   目标描述                  │  输入框标签
│   ┌─────────────────────┐   │
│   │ 描述你的目标...      │   │  多行输入
│   │                     │   │  高度 100px
│   └─────────────────────┘   │
│   0/500                     │  字数统计
│                             │
│   期望完成时间 *            │  日期选择
│   ┌─────────────────────┐   │
│   │ 📅 请选择日期        │   │
│   └─────────────────────┘   │
│                             │
│   ┌─────────────────────┐   │
│   │   AI 生成规划       │   │  主按钮
│   └─────────────────────┘   │
│                             │
└─────────────────────────────┘
```

**设计要点**:
- 描述输入框为多行文本，高度 100px，最大 500 字
- 日期选择器点击后弹出日历选择
- 按钮默认禁用，必填项填写后启用
- 按钮加载状态显示 loading 动画

**交互说明**:
- 点击 AI 生成规划后显示加载状态
- 调用后端 API 创建目标并生成规划
- 成功后跳转到规划详情页

---

### 规划详情页 (Plan Detail)

**布局**:
```
┌─────────────────────────────┐
│  ← 返回        学习Python   │  顶部导航栏(目标名称)
├─────────────────────────────┤
│                             │
│  ┌───────────────────────┐  │
│  │ 🤖 AI 生成的规划       │  │  标签
│  │ 预计 3 个阶段 • 15 个任务│ │  统计信息
│  │ 总耗时：30 小时        │  │
│  └───────────────────────┘  │
│                             │
│  ── 阶段 1：基础准备 ─────  │  阶段标题
│                             │
│  ┌───────────────────────┐  │
│  │ 1. 安装Python环境      │  │  任务卡片
│  │    预计 1 小时         │  │
│  └───────────────────────┘  │
│                             │
│  ┌───────────────────────┐  │
│  │ 2. 配置开发环境        │  │  任务卡片
│  │    预计 0.5 小时       │  │
│  └───────────────────────┘  │
│                             │
│  ── 阶段 2：基础知识 ─────  │  阶段标题
│                             │
│  ┌───────────────────────┐  │
│  │ 3. 学习变量和数据类型  │  │
│  │    预计 2 小时         │  │
│  └───────────────────────┘  │
│         ...                 │  更多任务
│                             │
│                             │
│  ┌───────────────────────┐  │
│  │    确认规划并创建任务  │   │  底部按钮
│  └───────────────────────┘  │
│                             │
└─────────────────────────────┘
```

**设计要点**:
- 顶部显示目标名称
- AI 标签使用紫色背景，白色文字
- 阶段标题：左对齐，左侧紫色竖线装饰
- 任务卡片：左侧序号，圆角 8px，阴影
- 底部固定确认按钮

**交互说明**:
- 任务卡片可点击展开查看详情
- 点击确认按钮后创建所有任务
- 确认后跳转到任务列表

---

### 规划确认/修改页 (Plan Confirm)

**布局**:
```
┌─────────────────────────────┐
│  ← 返回        确认规划    │  顶部导航栏
├─────────────────────────────┤
│                             │
│  你可以修改或删除任务：      │  提示文字
│                             │
│  ── 阶段 1：基础准备 ─────  │
│                             │
│  ┌───────────────────────┐  │
│  │ ☐ 安装Python环境       │  │  复选框
│  │    [预计 1 小时] [×删除]│  │
│  └───────────────────────┘  │
│                             │
│  ┌───────────────────────┐  │
│  │ ☐ 配置开发环境         │  │
│  │    [预计 0.5小时][×删除]│ │
│  └───────────────────────┘  │
│                             │
│  [+ 添加任务]               │  添加按钮
│                             │
│  ── 阶段 2：基础知识 ─────  │
│                             │
│         ...                 │
│                             │
│  ┌───────────────────────┐  │
│  │    + 添加阶段          │  │  添加阶段按钮
│  └───────────────────────┘  │
│                             │
├─────────────────────────────┤
│  ┌─────────┐ ┌───────────┐  │
│  │ 重新生成 │ │ 确认规划  │  │  底部双按钮
│  └─────────┘ └───────────┘  │
└─────────────────────────────┘
```

**设计要点**:
- 每个任务可单独勾选/取消
- 删除按钮：右上角红色 × 图标
- 添加任务/阶段按钮：虚线边框，居中显示
- 底部双按钮：左侧次要（重新生成），右侧主要（确认）

**交互说明**:
- 取消勾选的任务不会创建
- 删除任务需要二次确认
- 重新生成会调用 AI 重新规划
- 确认后创建勾选的任务

---

### 任务列表页 (Tasks List)

**布局**:
```
┌─────────────────────────────┐
│  今日任务             [全部]│  标题 + 筛选
├─────────────────────────────┤
│                             │
│  📅 2025-01-27             │  日期标题
│                             │
│  ┌───────────────────────┐  │
│  │ ☐ 安装 Python 环境    │  │  任务卡片
│  │ 预计 30 分钟          │  │
│  │ [开始]               │  │
│  └───────────────────────┘  │
│                             │
│  ┌───────────────────────┐  │
│  │ ☑ 学习变量和数据类型  │  │  已完成任务
│  │ 已完成               │  │
│  └───────────────────────┘  │
│                             │
└─────────────────────────────┘
```

**设计要点**:
- 顶部固定栏：标题 + 筛选按钮（今日/全部）
- 按日期分组显示任务
- 任务卡片：复选框、任务标题、预计时间
- 已完成任务显示绿色 √

---

### 任务详情页 (Task Detail)

**布局**:
```
┌─────────────────────────────┐
│  ← 返回        任务详情    │  顶部导航栏
├─────────────────────────────┤
│                             │
│  ┌───────────────────────┐  │
│  │                       │  │
│  │   安装Python环境      │  │  任务标题
│  │                       │  │
│  │   ☐ 未完成            │  │  状态标签
│  │                       │  │
│  └───────────────────────┘  │
│                             │
│  所属目标                   │  信息标签
│  ─────────────────────────  │
│  学习Python编程             │  目标名称(可点击跳转)
│                             │
│  截止日期                   │
│  ─────────────────────────  │
│  2025年1月27日              │  日期显示
│                             │
│  预计耗时                   │
│  ─────────────────────────  │
│  1 小时                     │  时长显示
│                             │
│  任务描述                   │
│  ─────────────────────────  │
│  下载Python安装包，按向导   │  描述内容
│  完成安装，配置环境变量。   │
│                             │
│                             │
│  ┌───────────────────────┐  │
│  │      完成任务         │   │  底部按钮
│  └───────────────────────┘  │
│                             │
└─────────────────────────────┘
```

**设计要点**:
- 顶部卡片：标题 + 状态，紫色渐变背景
- 信息分组：标签 + 内容，用分割线分隔
- 底部按钮根据状态变化：
  - 未完成 → "完成任务"
  - 已完成 → "取消完成"（灰色按钮）

**交互说明**:
- 点击完成任务后显示成功提示
- 已完成的任务可以取消完成状态
- 点击所属目标跳转到目标详情

---

## 4. UI 实现说明

### MVP 阶段实现方式

**采用 Uni-app 原生组件 + 自定义 CSS 样式**

**理由**：
- ✅ 降低开发成本，快速验证核心功能
- ✅ 避免维护自定义组件库的额外开销
- ✅ 利用 Uni-app 原生组件的跨平台能力

### 组件使用示例

**按钮组件**：
```vue
<!-- 主按钮 -->
<view class="l-button l-button-primary">创建目标</view>

<!-- 次按钮 -->
<view class="l-button l-button-secondary">取消</view>

<!-- 文字按钮 -->
<view class="l-button l-button-text">查看详情</view>
```

**输入框组件**：
```vue
<view class="l-input-wrapper">
  <input class="l-input" placeholder="请输入目标名称" />
</view>
```

**卡片组件**：
```vue
<view class="l-card">
  <text class="l-card-title">学习 Python 编程</text>
  <text class="l-card-desc">在3个月内掌握Python基础</text>
</view>
```

### 后续优化方向

**Phase 2 考虑引入**：
- uni-ui 组件库（提高开发效率）
- 提取常用样式为全局 CSS 变量
- 封装高频使用的业务组件

---

## 5. 交互设计

### 动画效果

- **页面转场**: 使用 Uni-app 内置转场效果
- **加载状态**: 骨架屏加载、loading 动画
- **成功提示**: Toast 提示，底部弹出，2 秒自动消失
- **错误提示**: Toast 提示，底部弹出，3 秒自动消失

### 手势操作

- 下拉刷新：列表顶部下拉
- 上拉加载：列表底部上拉
- 滑动删除：目标/任务列表左滑
- 点击反馈：按钮点击有缩放效果

---

## 6. 响应式设计

### 屏幕适配

- 支持 iPhone SE (375px) 到 iPhone Pro Max (428px)
- 支持安卓主流分辨率
- 使用 rpx 单位（750rpx 设计稿）

### 安全区域

- 适配刘海屏
- 底部导航栏适配
- 使用 Uni-app `safe-area-inset-bottom`

---

## 7. 可访问性

### 字体大小

- 最小字体 12px
- 可读字体 14-16px
- 标题字体 18-32px

### 颜色对比度

- 正常文字与背景对比度 ≥ 4.5:1
- 大号文字与背景对比度 ≥ 3:1

### 点击区域

- 按钮最小点击区域 44x44px
- 列表项最小点击区域 48x48px

---

## 8. Vuex Store 状态管理设计

### Store 结构

```javascript
// store/index.js
import { createStore } from 'vuex'
import auth from './modules/auth'
import goals from './modules/goals'
import plans from './modules/plans'
import tasks from './modules/tasks'

export default createStore({
  modules: {
    auth,
    goals,
    plans,
    tasks
  }
})
```

### Auth 模块 (store/modules/auth.js)

**State**:
```javascript
state: {
  token: uni.getStorageSync('lifemanager_token') || '',
  userInfo: uni.getStorageSync('lifemanager_user') || null,
  isLoggedIn: false
}
```

**Getters**:
```javascript
getters: {
  isAuthenticated: state => !!state.token,
  user: state => state.userInfo
}
```

**Actions**:
```javascript
actions: {
  // 登录
  async login({ commit }, credentials) {
    const res = await request.post('/auth/login', credentials)
    commit('SET_TOKEN', res.token)
    commit('SET_USER', res.user)
    return res
  },
  
  // 注册
  async register({ dispatch }, data) {
    await request.post('/auth/register', data)
    // 注册成功后自动登录
    return dispatch('login', {
      username: data.username,
      password: data.password
    })
  },
  
  // 退出登录
  logout({ commit }) {
    commit('CLEAR_AUTH')
  }
}
```

---

### Goals 模块 (store/modules/goals.js)

**State**:
```javascript
state: {
  list: [],      // 目标列表
  current: null, // 当前目标
  loading: false
}
```

**Actions**:
```javascript
actions: {
  // 获取目标列表
  async fetchGoals({ commit }) {
    commit('SET_LOADING', true)
    const res = await request.get('/goals')
    commit('SET_LIST', res.data)
    commit('SET_LOADING', false)
  },
  
  // 创建目标
  async createGoal({ dispatch }, goalData) {
    await request.post('/goals', goalData)
    // 刷新列表
    return dispatch('fetchGoals')
  }
}
```

---

### Plans 模块 (store/modules/plans.js)

**State**:
```javascript
state: {
  current: null, // 当前规划
  detail: null,  // 规划详情
  loading: false
}
```

**Actions**:
```javascript
actions: {
  // 生成规划
  async generatePlan({ commit }, { goalId, availableHours }) {
    commit('SET_LOADING', true)
    const res = await request.post(`/goals/${goalId}/generate-plan`, {
      available_hours: availableHours
    })
    commit('SET_CURRENT', res.data)
    commit('SET_LOADING', false)
    return res.data
  },
  
  // 确认规划
  async confirmPlan({ dispatch }, planId) {
    await request.post(`/plans/${planId}/confirm`)
    // 刷新任务列表
    return dispatch('tasks/fetchTasks', null, { root: true })
  }
}
```

---

### Tasks 模块 (store/modules/tasks.js)

**State**:
```javascript
state: {
  list: [],      // 任务列表
  today: [],     // 今日任务
  current: null, // 当前任务
  loading: false
}
```

**Actions**:
```javascript
actions: {
  // 获取今日任务
  async fetchTodayTasks({ commit }) {
    commit('SET_LOADING', true)
    const today = new Date().toISOString().split('T')[0]
    const res = await request.get('/tasks', { params: { date: today } })
    commit('SET_TODAY', res.data)
    commit('SET_LOADING', false)
  },
  
  // 获取任务列表
  async fetchTasks({ commit }, params = {}) {
    const res = await request.get('/tasks', { params })
    commit('SET_LIST', res.data)
  },
  
  // 完成任务
  async completeTask({ dispatch }, taskId) {
    await request.post(`/tasks/${taskId}/complete`)
    return dispatch('fetchTodayTasks')
  },
  
  // 获取任务详情
  async fetchTaskDetail({ commit }, taskId) {
    const res = await request.get(`/tasks/${taskId}`)
    commit('SET_CURRENT', res.data)
    return res.data
  }
}
```

---

## 9. API 调用封装

### Request 工具 (utils/request.js)

```javascript
const BASE_URL = 'http://localhost:8000/api'

export const request = {
  async get(url, options = {}) {
    return this.request('GET', url, options)
  },
  
  async post(url, data, options = {}) {
    return this.request('POST', url, { ...options, data })
  },
  
  async request(method, url, options) {
    const token = uni.getStorageSync('lifemanager_token')
    
    return new Promise((resolve, reject) => {
      uni.request({
        url: BASE_URL + url,
        method,
        header: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : ''
        },
        ...options,
        success: (res) => {
          if (res.statusCode === 200) {
            if (res.data.code === 0) {
              resolve(res.data)
            } else {
              uni.showToast({ title: res.data.message, icon: 'none' })
              reject(new Error(res.data.message))
            }
          } else if (res.statusCode === 401) {
            // Token 过期，跳转登录
            uni.removeStorageSync('lifemanager_token')
            uni.navigateTo({ url: '/pages/login/login' })
            reject(new Error('登录已过期'))
          } else {
            reject(new Error('网络请求失败'))
          }
        },
        fail: reject
      })
    })
  }
}
```

---

## 10. 路由配置

### Pages.json

```json
{
  "pages": [
    { "path": "pages/index/index", "style": { "navigationBarTitleText": "托管人生" } },
    { "path": "pages/login/login", "style": { "navigationBarTitleText": "登录" } },
    { "path": "pages/register/register", "style": { "navigationBarTitleText": "注册" } },
    { "path": "pages/goals/goals", "style": { "navigationBarTitleText": "我的目标" } },
    { "path": "pages/goals/create", "style": { "navigationBarTitleText": "创建目标" } },
    { "path": "pages/plans/detail", "style": { "navigationBarTitleText": "规划详情" } },
    { "path": "pages/plans/confirm", "style": { "navigationBarTitleText": "确认规划" } },
    { "path": "pages/tasks/list", "style": { "navigationBarTitleText": "今日任务" } },
    { "path": "pages/tasks/detail", "style": { "navigationBarTitleText": "任务详情" } }
  ],
  "globalStyle": {
    "navigationBarTextStyle": "black",
    "navigationBarBackgroundColor": "#ffffff"
  }
}
```

---

## 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-01-28 | v1.0 | 从产品与设计文档拆分，专注于UI/UX设计 |

---

## 附录

### 参考文档
- [产品需求文档](./产品需求文档.md)
- [技术架构设计](./技术架构设计.md)
- [后端开发指南](./后端开发指南.md)

### 相关技能
- UI/UX设计师技能：`.codebuddy/skills/ui-ux设计师/`
- Vue3前端开发工程师技能：`.codebuddy/skills/vue3前端开发工程师/`
