import { get, post, put, del } from '@/utils/request.js'

/**
 * 时间偏好管理 API
 */
export default {
  // 获取时间偏好
  getTimePreferences() {
    return get('/time-preferences')
  },

  // 更新时间偏好
  updateTimePreferences(data) {
    return put('/time-preferences', data)
  }
}
