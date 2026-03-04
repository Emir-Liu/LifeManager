/**
 * 规划状态管理 - Pinia版本
 */
import { defineStore } from 'pinia'
import { get, post, put } from '@/utils/request'

export const usePlansStore = defineStore('plans', {
  state: () => ({
    current: null,
    detail: null,
    loading: false
  }),

  getters: {
    planStages: (state) => state.current?.content?.stages || [],
    totalTasks: (state) => state.current?.total_tasks || 0,
    totalHours: (state) => state.current?.estimated_total_hours || 0
  },

  actions: {
    // 生成规划
    async generatePlan({ goalId, availableHoursPerDay = 2 }) {
      this.loading = true
      try {
        const plan = await post('/plans/generate', {
          goal_id: goalId,
          available_hours_per_day: availableHoursPerDay
        })
        this.current = plan
        return plan
      } catch (error) {
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取规划详情
    async fetchPlanDetail(planId) {
      this.loading = true
      try {
        const plan = await get(`/plans/${planId}`)
        this.detail = plan
        return plan
      } catch (error) {
        throw error
      } finally {
        this.loading = false
      }
    },

    // 确认规划
    async confirmPlan({ planId, content = null }) {
      try {
        const result = await post(`/plans/${planId}/confirm`, content ? { content } : {})
        return result
      } catch (error) {
        throw error
      }
    },

    // 修改规划
    async updatePlan({ planId, content }) {
      try {
        const plan = await put(`/plans/${planId}`, { content })
        this.current = plan
        return plan
      } catch (error) {
        throw error
      }
    }
  }
})
