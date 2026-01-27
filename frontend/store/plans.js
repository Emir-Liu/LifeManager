/**
 * 规划状态管理
 */

const state = {
  current: null,
  detail: null,
  loading: false
}

const mutations = {
  SET_CURRENT(state, plan) {
    state.current = plan
  },
  SET_DETAIL(state, detail) {
    state.detail = detail
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  }
}

const actions = {
  // 生成规划
  async generatePlan({ commit }, { goalId, availableHoursPerDay = 2 }) {
    commit('SET_LOADING', true)
    try {
      const { post } = require('@/utils/request')
      const plan = await post('/plans/generate', {
        goal_id: goalId,
        available_hours_per_day: availableHoursPerDay
      })
      commit('SET_CURRENT', plan)
      return plan
    } catch (error) {
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 获取规划详情
  async fetchPlanDetail({ commit }, planId) {
    commit('SET_LOADING', true)
    try {
      const { get } = require('@/utils/request')
      const plan = await get(`/plans/${planId}`)
      commit('SET_DETAIL', plan)
      return plan
    } catch (error) {
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 确认规划
  async confirmPlan({ commit }, { planId, content = null }) {
    try {
      const { post } = require('@/utils/request')
      const result = await post(`/plans/${planId}/confirm`, content ? { content } : {})
      return result
    } catch (error) {
      throw error
    }
  },

  // 修改规划
  async updatePlan({ commit }, { planId, content }) {
    try {
      const { put } = require('@/utils/request')
      const plan = await put(`/plans/${planId}`, { content })
      commit('SET_CURRENT', plan)
      return plan
    } catch (error) {
      throw error
    }
  }
}

const getters = {
  planStages: state => state.current?.content?.stages || [],
  totalTasks: state => state.current?.total_tasks || 0,
  totalHours: state => state.current?.estimated_total_hours || 0
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
