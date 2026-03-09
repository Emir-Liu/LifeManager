import { get, post, put, del } from '@/utils/request.js'

/**
 * 目标管理 API
 */

export default {
  // 获取目标列表
  getGoalList(params = {}) {
    return get('/goals', params)
  },

  // 获取目标详情
  getGoalDetail(id) {
    return get(`/goals/${id}`)
  },

  // 创建目标
  createGoal(data) {
    return post('/goals', data)
  },

  // 更新目标
  updateGoal(id, data) {
    return put(`/goals/${id}`, data)
  },

  // 删除目标
  deleteGoal(id) {
    return del(`/goals/${id}`)
  },

  // 完成/取消完成目标
  toggleGoalComplete(id, completed) {
    return put(`/goals/${id}/complete`, { completed })
  },

  // 获取目标统计
  getGoalStatistics() {
    return get('/goals/statistics')
  }
}
