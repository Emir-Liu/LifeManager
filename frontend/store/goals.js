/**
 * 目标状态管理
 */
import { get, post, del } from '@/utils/request'

const state = {
  list: [],
  current: null,
  loading: false
}

const mutations = {
  SET_LIST(state, list) {
    state.list = list
  },
  ADD_GOAL(state, goal) {
    state.list.unshift(goal)
  },
  UPDATE_GOAL(state, goal) {
    const index = state.list.findIndex(g => g.id === goal.id)
    if (index !== -1) {
      state.list.splice(index, 1, goal)
    }
  },
  DELETE_GOAL(state, goalId) {
    state.list = state.list.filter(g => g.id !== goalId)
  },
  SET_CURRENT(state, goal) {
    state.current = goal
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  }
}

const actions = {
  // 获取目标列表
  async fetchGoals({ commit }) {
    commit('SET_LOADING', true)
    try {
      const list = await get('/goals')
      commit('SET_LIST', list)
      return list
    } catch (error) {
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  // 创建目标
  async createGoal({ commit, dispatch }, goalData) {
    try {
      const goal = await post('/goals', goalData)
      commit('ADD_GOAL', goal)
      return goal
    } catch (error) {
      throw error
    }
  },

  // 获取目标详情
  async fetchGoalDetail({ commit }, goalId) {
    try {
      const goal = await get(`/goals/${goalId}`)
      commit('SET_CURRENT', goal)
      return goal
    } catch (error) {
      throw error
    }
  },

  // 删除目标
  async deleteGoal({ commit }, goalId) {
    try {
      await del(`/goals/${goalId}`)
      commit('DELETE_GOAL', goalId)
    } catch (error) {
      throw error
    }
  }
}

const getters = {
  goalCount: state => state.list.length,
  activeGoals: state => state.list.filter(g => g.status !== 'archived')
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
