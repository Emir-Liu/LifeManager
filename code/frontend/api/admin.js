import { get, post, put, del } from '@/utils/request.js'

const BASE_URL = 'http://localhost:8000/api'

// 获取token
function getToken() {
  return uni.getStorageSync('lifemanager_token')
}

/**
 * 管理员对话管理 API
 */
export default {
  baseURL: BASE_URL,

  // 获取所有对话列表
  getAllConversations(params = {}) {
    return get('/admin/conversations', params)
  },

  // 获取对话详情
  getConversationDetail(conversationId) {
    return get(`/admin/conversations/${conversationId}`)
  },

  // 获取对话消息列表
  getConversationMessages(conversationId, params = {}) {
    return get(`/admin/conversations/${conversationId}/messages`, params)
  },

  // 删除对话
  deleteConversation(conversationId) {
    return del(`/admin/conversations/${conversationId}`)
  },

  // 获取用户的所有对话
  getUserConversations(userId, params = {}) {
    return get(`/admin/conversations/users/${userId}/conversations`, params)
  },

  // 搜索消息内容
  searchMessages(keyword, params = {}) {
    return get('/admin/conversations/messages/search', { keyword, ...params })
  },

  // 获取对话统计信息
  getConversationStats() {
    return get('/admin/conversations/stats/overview')
  }
}
