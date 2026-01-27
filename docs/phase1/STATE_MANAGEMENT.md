# LifeManager MVP 前端状态管理文档

## 文档信息

- **版本**: v1.0
- **创建日期**: 2026-01-27
- **作者**: 产品经理
- **状态**: 已发布
- **适用阶段**: Phase 1 - MVP

---

## 1. 状态管理概述

### 1.1 状态管理工具

**采用方案**: Vuex

**选型理由**:
- ✅ Vue 3 官方推荐
- ✅ 适合中小型项目
- ✅ 提供完善的状态管理功能
- ✅ 支持模块化

### 1.2 状态分类

```
全局状态（Vuex）
├── user 模块
│   ├── token: JWT Token
│   ├── userInfo: 用户信息
│   └── isLogin: 登录状态
├── goal 模块
│   ├── goals: 目标列表
│   ├── currentGoal: 当前目标
│   └── loading: 加载状态
└── task 模块
    ├── tasks: 任务列表
    ├── todayTasks: 今日任务
    └── loading: 加载状态
```

---

## 2. Vuex 配置

### 2.1 Store 初始化

```javascript
// frontend/store/index.js

import { createStore } from 'vuex'
import user from './modules/user.js'
import goal from './modules/goal.js'
import task from './modules/task.js'

const store = createStore({
  modules: {
    user,
    goal,
    task
  }
})

export default store
```

### 2.2 挂载到应用

```javascript
// frontend/main.js

import { createSSRApp } from 'vue'
import App from './App.vue'
import store from './store'

export function createApp() {
  const app = createSSRApp(App)
  app.use(store)
  return {
    app
  }
}
```

---

## 3. User 模块

### 3.1 State

```javascript
// frontend/store/modules/user.js

import { storage } from '@/utils/storage.js'

const state = {
  token: storage.getToken() || '',
  userInfo: storage.getUser() || null
}
```

### 3.2 Getters

```javascript
const getters = {
  // 是否已登录
  isLogin: state => !!state.token,

  // 用户名
  username: state => state.userInfo?.username || '',

  // 用户 ID
  userId: state => state.userInfo?.user_id || null
}
```

### 3.3 Mutations

```javascript
const mutations = {
  SET_TOKEN(state, token) {
    state.token = token
    storage.setToken(token)
  },

  SET_USER_INFO(state, userInfo) {
    state.userInfo = userInfo
    storage.setUser(userInfo)
  },

  CLEAR_AUTH(state) {
    state.token = ''
    state.userInfo = null
    storage.clearAuth()
  }
}
```

### 3.4 Actions

```javascript
import { post } from '@/utils/request.js'

const actions = {
  // 用户登录
  async login({ commit }, { username, password }) {
    const res = await post('/auth/login', { username, password })

    commit('SET_TOKEN', res.token)
    commit('SET_USER_INFO', {
      user_id: res.user_id,
      username: res.username
    })

    return res
  },

  // 用户注册
  async register({ commit }, { username, password, email }) {
    const res = await post('/auth/register', { username, password, email })

    commit('SET_TOKEN', res.token)
    commit('SET_USER_INFO', {
      user_id: res.user_id,
      username: res.username
    })

    return res
  },

  // 用户登出
  logout({ commit }) {
    commit('CLEAR_AUTH')
    uni.reLaunch({
      url: '/pages/index/index'
    })
  }
}
```

### 3.5 导出

```javascript
export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
```

---

## 4. Goal 模块

### 4.1 State

```javascript
// frontend/store/modules/goal.js

const state = {
  goals: [],           // 目标列表
  currentGoal: null,   // 当前选中的目标
  loading: false,      // 加载状态
  plan: null,          // 当前目标的规划
  planLoading: false   // 规划加载状态
}
```

### 4.2 Getters

```javascript
const getters = {
  // 获取规划中的目标
  planningGoals: state => {
    return state.goals.filter(g => g.status === 'planning')
  },

  // 获取已确认的目标
  confirmedGoals: state => {
    return state.goals.filter(g => g.status === 'confirmed')
  },

  // 获取已完成的目标
  completedGoals: state => {
    return state.goals.filter(g => g.status === 'completed')
  },

  // 是否有当前目标
  hasCurrentGoal: state => !!state.currentGoal
}
```

### 4.3 Mutations

```javascript
const mutations = {
  SET_GOALS(state, goals) {
    state.goals = goals
  },

  ADD_GOAL(state, goal) {
    state.goals.unshift(goal)
  },

  UPDATE_GOAL(state, goal) {
    const index = state.goals.findIndex(g => g.id === goal.id)
    if (index !== -1) {
      state.goals[index] = goal
    }
  },

  DELETE_GOAL(state, goalId) {
    state.goals = state.goals.filter(g => g.id !== goalId)
  },

  SET_CURRENT_GOAL(state, goal) {
    state.currentGoal = goal
  },

  SET_LOADING(state, loading) {
    state.loading = loading
  },

  SET_PLAN(state, plan) {
    state.plan = plan
  },

  SET_PLAN_LOADING(state, loading) {
    state.planLoading = loading
  }
}
```

### 4.4 Actions

```javascript
import { get, post, del } from '@/utils/request.js'

const actions = {
  // 获取目标列表
  async fetchGoals({ commit }) {
    commit('SET_LOADING', true)
    try {
      const goals = await get('/goals')
      commit('SET_GOALS', goals)
      return goals
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 创建目标
  async createGoal({ commit }, goalData) {
    const goal = await post('/goals', goalData)
    commit('ADD_GOAL', goal)
    return goal
  },

  // 删除目标
  async deleteGoal({ commit }, goalId) {
    await del(`/goals/${goalId}`)
    commit('DELETE_GOAL', goalId)
  },

  // 获取目标详情
  async fetchGoalDetail({ commit }, goalId) {
    const goal = await get(`/goals/${goalId}`)
    commit('SET_CURRENT_GOAL', goal)
    return goal
  },

  // 生成规划
  async generatePlan({ commit }, { goalId, availableHoursPerDay }) {
    commit('SET_PLAN_LOADING', true)
    try {
      const plan = await post('/plans/generate', {
        goal_id: goalId,
        available_hours_per_day: availableHoursPerDay
      })
      commit('SET_PLAN', plan)

      // 更新目标状态为 planning
      const goal = await get(`/goals/${goalId}`)
      commit('SET_CURRENT_GOAL', goal)
      commit('UPDATE_GOAL', goal)

      return plan
    } finally {
      commit('SET_PLAN_LOADING', false)
    }
  },

  // 确认规划
  async confirmPlan({ commit }, planId) {
    const result = await post(`/plans/${planId}/confirm`)

    // 重新获取目标详情
    const goalId = result.plan_id
    const goal = await get(`/goals/${goalId}`)
    commit('SET_CURRENT_GOAL', goal)
    commit('UPDATE_GOAL', goal)

    return result
  }
}
```

### 4.5 导出

```javascript
export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
```

---

## 5. Task 模块

### 5.1 State

```javascript
// frontend/store/modules/task.js

const state = {
  tasks: [],           // 任务列表
  todayTasks: [],      // 今日任务
  loading: false,      // 加载状态
  filter: 'today'     // 筛选类型：today, all
}
```

### 5.2 Getters

```javascript
const getters = {
  // 今日未完成任务
  pendingTodayTasks: state => {
    return state.todayTasks.filter(t => !t.completed)
  },

  // 今日已完成任务
  completedTodayTasks: state => {
    return state.todayTasks.filter(t => t.completed)
  },

  // 今日任务统计
  todayTaskStats: state => {
    const total = state.todayTasks.length
    const completed = state.todayTasks.filter(t => t.completed).length
    return { total, completed, pending: total - completed }
  }
}
```

### 5.3 Mutations

```javascript
const mutations = {
  SET_TASKS(state, tasks) {
    state.tasks = tasks
  },

  SET_TODAY_TASKS(state, tasks) {
    state.todayTasks = tasks
  },

  ADD_TASK(state, task) {
    state.tasks.unshift(task)
  },

  UPDATE_TASK(state, task) {
    const index = state.tasks.findIndex(t => t.id === task.id)
    if (index !== -1) {
      state.tasks[index] = task
    }

    // 更新今日任务
    const todayIndex = state.todayTasks.findIndex(t => t.id === task.id)
    if (todayIndex !== -1) {
      state.todayTasks[todayIndex] = task
    }
  },

  SET_LOADING(state, loading) {
    state.loading = loading
  },

  SET_FILTER(state, filter) {
    state.filter = filter
  }
}
```

### 5.4 Actions

```javascript
import { get, post, put } from '@/utils/request.js'

const actions = {
  // 获取任务列表
  async fetchTasks({ commit }, { goalId, date, status }) {
    commit('SET_LOADING', true)
    try {
      const params = {}
      if (goalId) params.goal_id = goalId
      if (date) params.date = date
      if (status) params.status = status

      const tasks = await get('/tasks', params)
      commit('SET_TASKS', tasks)
      return tasks
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 获取今日任务
  async fetchTodayTasks({ commit }) {
    commit('SET_LOADING', true)
    try {
      const { data } = await get('/tasks/today')
      commit('SET_TODAY_TASKS', data)
      return data
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 创建任务
  async createTask({ commit }, taskData) {
    const task = await post('/tasks', taskData)
    commit('ADD_TASK', task)
    return task
  },

  // 完成任务
  async completeTask({ commit }, taskId) {
    const task = await put(`/tasks/${taskId}/complete`)
    commit('UPDATE_TASK', task)
    return task
  },

  // 取消完成任务
  async uncompleteTask({ commit }, taskId) {
    const task = await put(`/tasks/${taskId}/uncomplete`)
    commit('UPDATE_TASK', task)
    return task
  }
}
```

### 5.5 导出

```javascript
export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
```

---

## 6. 在组件中使用

### 6.1 使用 State 和 Getters

```javascript
// frontend/pages/goals/goals.vue

<template>
  <view>
    <view v-for="goal in planningGoals" :key="goal.id">
      {{ goal.title }}
    </view>
  </view>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  computed: {
    ...mapGetters('goal', ['planningGoals'])
  },

  onLoad() {
    this.fetchGoals()
  },

  methods: {
    async fetchGoals() {
      await this.$store.dispatch('goal/fetchGoals')
    }
  }
}
</script>
```

### 6.2 调用 Actions

```javascript
// frontend/pages/goals/create.vue

<script>
export default {
  data() {
    return {
      title: '',
      description: '',
      deadline: ''
    }
  },

  methods: {
    async createGoal() {
      try {
        await this.$store.dispatch('goal/createGoal', {
          title: this.title,
          description: this.description,
          deadline: this.deadline
        })

        uni.showToast({
          title: '创建成功',
          icon: 'success'
        })

        uni.navigateBack()
      } catch (error) {
        uni.showToast({
          title: '创建失败',
          icon: 'none'
        })
      }
    }
  }
}
</script>
```

### 6.3 登录状态检查

```javascript
// frontend/pages/goals/goals.vue

<script>
import { mapGetters } from 'vuex'

export default {
  computed: {
    ...mapGetters('user', ['isLogin'])
  },

  onLoad() {
    // 检查登录状态
    if (!this.isLogin) {
      uni.redirectTo({
        url: '/pages/login/login'
      })
      return
    }

    this.fetchGoals()
  }
}
</script>
```

---

## 7. 持久化策略

### 7.1 持久化插件（可选）

```javascript
// frontend/store/plugins/persist.js

import { storage } from '@/utils/storage.js'

export default (store) => {
  store.subscribe((mutation, state) => {
    // 持久化用户信息
    if (mutation.type.startsWith('user/')) {
      storage.setUser(state.user.userInfo)
      storage.setToken(state.user.token)
    }

    // 持久化目标列表（可选）
    if (mutation.type.startsWith('goal/')) {
      storage.set('goals', state.goal.goals)
    }
  })
}
```

### 7.2 注册插件

```javascript
// frontend/store/index.js

import persistPlugin from './plugins/persist.js'

const store = createStore({
  modules: { ... },
  plugins: [persistPlugin]
})
```

---

## 8. 性能优化

### 8.1 使用计算属性缓存

```javascript
// ✅ 正确：使用计算属性
computed: {
  filteredGoals() {
    return this.goals.filter(goal => goal.status === 'planning')
  }
}

// ❌ 错误：在模板中直接过滤
// <view v-for="goal in goals.filter(g => g.status === 'planning')">
```

### 8.2 避免不必要的响应式

```javascript
// ✅ 正确：非响应式数据
data() {
  return {
    formData: {
      title: '',
      description: ''
    }
  }
}

// ❌ 错误：大量数据使用响应式
// 如果数据量很大，考虑使用 shallowRef 或 markRaw
```

---

## 9. 调试工具

### 9.1 Vue DevTools

安装 Vue DevTools 浏览器插件，可以：
- 查看 Vuex 状态
- 追踪状态变化
- 时间旅行调试

### 9.2 控制台日志

```javascript
// 开发环境打印状态变化
if (process.env.NODE_ENV === 'development') {
  store.subscribe((mutation, state) => {
    console.log('Mutation:', mutation.type)
    console.log('State:', state)
  })
}
```

---

## 10. 常见问题

### Q1: 如何在页面刷新后保持登录状态？

**答**: Token 存储在本地存储中，页面刷新时自动恢复：

```javascript
// store/modules/user.js
const state = {
  token: storage.getToken() || '',  // 从本地存储恢复
  userInfo: storage.getUser() || null
}
```

### Q2: 如何在多个组件共享状态？

**答**: 使用 Vuex 的全局状态，任意组件都可以访问：

```javascript
// 组件 A：设置状态
this.$store.commit('goal/SET_CURRENT_GOAL', goal)

// 组件 B：获取状态
const goal = this.$store.state.goal.currentGoal
```

### Q3: 如何处理异步操作？

**答**: 使用 Action 处理异步操作，返回 Promise：

```javascript
// 在组件中
try {
  await this.$store.dispatch('goal/fetchGoals')
  console.log('加载成功')
} catch (error) {
  console.error('加载失败', error)
}
```

---

## 11. 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-01-27 | v1.0 | 初始版本，完成状态管理设计 |
