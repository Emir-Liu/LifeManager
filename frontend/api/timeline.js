import { get, post, put, del } from '@/utils/request.js'

/**
 * 时间线 API
 */
export default {
  // 获取时间线
  getTimeline(date) {
    return get(`/timeline/${date}`)
  },

  // 智能分配任务
  smartAssignTasks(data) {
    return post('/tasks/smart-assign', data)
  },

  // 检测时间冲突
  detectConflicts(data) {
    return post('/tasks/detect-conflicts', data)
  },

  // 获取时间统计
  getTimeStats(params) {
    return get('/time-stats', params)
  }
}
