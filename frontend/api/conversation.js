import { get, post, put, del } from '@/utils/request.js'

/**
 * 对话管理 API
 */
export default {
  // 创建对话
  createConversation(data) {
    return post('/conversations', data)
  },

  // 获取对话列表
  getConversations(params = {}) {
    return get('/conversations', params)
  },

  // 获取对话详情
  getConversationDetail(id) {
    return get(`/conversations/${id}`)
  },

  // 更新对话
  updateConversation(id, data) {
    return put(`/conversations/${id}`, data)
  },

  // 删除对话
  deleteConversation(id) {
    return del(`/conversations/${id}`)
  },

  // 发送消息
  sendMessage(conversationId, data) {
    return post(`/conversations/${conversationId}/messages`, data)
  },

  // 获取消息列表
  getMessages(conversationId, params = {}) {
    return get(`/conversations/${conversationId}/messages`, params)
  },

  // 获取AI回复(流式)
  chatWithAI(conversationId, data) {
    return post(`/conversations/${conversationId}/chat`, data)
  },

  // 消息反馈
  feedbackMessage(messageId, data) {
    return post(`/conversation-messages/${messageId}/feedback`, data)
  },

  // 获取操作列表
  getActions(conversationId, params = {}) {
    return get(`/conversations/${conversationId}/actions`, params)
  },

  // 执行操作
  executeAction(actionId) {
    return post(`/conversation-actions/${actionId}/execute`)
  },

  // 更新操作状态
  updateAction(actionId, data) {
    return put(`/conversation-actions/${actionId}`, data)
  }
}
