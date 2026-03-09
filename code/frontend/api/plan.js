import { get, post, put } from '@/utils/request.js'

/**
 * 规划管理 API
 */

export default {
  // 获取规划详情
  getPlanDetail(id) {
    return get(`/plans/${id}`)
  },

  // 生成规划
  generatePlan(goalId, availableHoursPerDay = 2) {
    return post('/plans/generate', {
      goal_id: goalId,
      available_hours_per_day: availableHoursPerDay
    })
  },

  // 确认规划
  confirmPlan(planId) {
    return post(`/plans/${planId}/confirm`)
  },

  // 修改规划
  updatePlan(planId, content) {
    return put(`/plans/${planId}`, { content })
  }
}
