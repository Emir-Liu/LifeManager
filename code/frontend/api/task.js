import { get, post, put, del } from '@/utils/request.js'

/**
 * 任务管理 API
 */

export default {
  // 获取任务列表
  getTaskList(params = {}) {
    return get('/tasks', params)
  },

  // 获取任务详情
  getTaskDetail(id) {
    return get(`/tasks/${id}`)
  },

  // 创建任务
  createTask(data) {
    return post('/tasks', data)
  },

  // 更新任务
  updateTask(id, data) {
    return put(`/tasks/${id}`, data)
  },

  // 删除任务
  deleteTask(id) {
    return del(`/tasks/${id}`)
  },

  // 完成/取消完成任务
  toggleTaskComplete(id, completed) {
    return put(`/tasks/${id}/complete`, { completed })
  },

  // 获取今日任务
  getTodayTasks() {
    return get('/tasks/today')
  },

  // 获取任务统计
  getTaskStatistics() {
    return get('/tasks/statistics')
  }
}
