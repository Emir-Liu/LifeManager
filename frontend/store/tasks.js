/**
 * 任务状态管理
 */

const state = {
  list: [],
  today: [],
  current: null,
  loading: false
}

const mutations = {
  SET_LIST(state, list) {
    state.list = list
  },
  SET_TODAY(state, list) {
    state.today = list
  },
  ADD_TASK(state, task) {
    state.list.unshift(task)
  },
  UPDATE_TASK(state, task) {
    const index = state.list.findIndex(t => t.id === task.id)
    if (index !== -1) {
      state.list.splice(index, 1, task)
    }
  },
  SET_CURRENT(state, task) {
    state.current = task
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  }
}

const actions = {
  // 获取今日任务
  async fetchTodayTasks({ commit }) {
    commit('SET_LOADING', true)
    try {
      const { get } = require('@/utils/request')
      const result = await get('/tasks/today')
      commit('SET_TODAY', result.data || result)
      return result
    } catch (error) {
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 获取任务列表
  async fetchTasks({ commit }, params = {}) {
    commit('SET_LOADING', true)
    try {
      const { get } = require('@/utils/request')
      const list = await get('/tasks', params)
      commit('SET_LIST', list.data || list)
      return list
    } catch (error) {
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 获取任务详情
  async fetchTaskDetail({ commit }, taskId) {
    try {
      const { get } = require('@/utils/request')
      const task = await get(`/tasks/${taskId}`)
      commit('SET_CURRENT', task)
      return task
    } catch (error) {
      throw error
    }
  },

  // 完成任务
  async completeTask({ commit, dispatch }, taskId) {
    try {
      const { put } = require('@/utils/request')
      const task = await put(`/tasks/${taskId}/complete`)
      commit('UPDATE_TASK', task)
      return task
    } catch (error) {
      throw error
    }
  },

  // 取消完成任务
  async uncompleteTask({ commit }, taskId) {
    try {
      const { put } = require('@/utils/request')
      const task = await put(`/tasks/${taskId}/uncomplete`)
      commit('UPDATE_TASK', task)
      return task
    } catch (error) {
      throw error
    }
  }
}

const getters = {
  completedTasks: state => state.today.filter(t => t.completed),
  pendingTasks: state => state.today.filter(t => !t.completed),
  completedCount: state => state.today.filter(t => t.completed).length,
  pendingCount: state => state.today.filter(t => !t.completed).length
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
