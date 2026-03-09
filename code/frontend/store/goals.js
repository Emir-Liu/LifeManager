/**
 * 目标状态管理 - Pinia版本
 */
import { defineStore } from 'pinia'
import { get, post, del } from '@/utils/request'

export const useGoalsStore = defineStore('goals', {
  state: () => ({
    list: [],
    current: null,
    loading: false
  }),

  getters: {
    goalCount: (state) => state.list.length,
    activeGoals: (state) => state.list.filter(g => g.status !== 'archived')
  },

  actions: {
    // 获取目标列表
    async fetchGoals() {
      this.loading = true
      try {
        const list = await get('/goals')
        this.list = list
        return list
      } catch (error) {
        throw error
      } finally {
        this.loading = false
      }
    },

    // 创建目标
    async createGoal(goalData) {
      try {
        const goal = await post('/goals', goalData)
        this.list.unshift(goal)
        return goal
      } catch (error) {
        throw error
      }
    },

    // 获取目标详情
    async fetchGoalDetail(goalId) {
      try {
        const goal = await get(`/goals/${goalId}`)
        this.current = goal
        return goal
      } catch (error) {
        throw error
      }
    },

    // 删除目标
    async deleteGoal(goalId) {
      try {
        await del(`/goals/${goalId}`)
        this.list = this.list.filter(g => g.id !== goalId)
      } catch (error) {
        throw error
      }
    }
  }
})
