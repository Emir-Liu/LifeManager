import { get, post, put, del } from '@/utils/request.js'

const BASE_URL = 'http://localhost:8000/api'

// 获取token
function getToken() {
  return uni.getStorageSync('lifemanager_token')
}

/**
 * 对话管理 API
 */
export default {
  baseURL: BASE_URL,
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

  // 获取AI回复
  chatWithAI(conversationId, data) {
    return post(`/conversations/${conversationId}/chat`, {
      message: data.content
    })
  },

  // 流式 AI 对话
  chatWithAIStream(conversationId, data, onEvent) {
    return new Promise((resolve, reject) => {
      const token = getToken()
      const url = `${this.baseURL}/conversations/${conversationId}/chat/stream`

      // 处理 SSE 数据
      const processSSEData = function(data, onEvent) {
        const lines = data.split('\n')
        let currentEvent = null

        for (const line of lines) {
          if (line.startsWith('event:')) {
            currentEvent = line.substring(6).trim()
          } else if (line.startsWith('data:')) {
            const dataStr = line.substring(5).trim()
            if (dataStr && currentEvent && onEvent) {
              try {
                const dataObj = JSON.parse(dataStr)
                onEvent(currentEvent, dataObj)
              } catch (e) {
                console.error('解析 SSE 数据失败:', e, dataStr)
              }
            }
          }
        }
      }

      // 使用 XMLHttpRequest 实现流式接收
      const xhr = new XMLHttpRequest()

      xhr.open('POST', url, true)
      xhr.setRequestHeader('Content-Type', 'application/json')
      xhr.setRequestHeader('Authorization', `Bearer ${token}`)

      let buffer = ''

      xhr.onreadystatechange = function() {
        if (xhr.readyState === 3) {  // LOADING - 正在接收数据
          // 处理新接收的数据
          const newData = xhr.responseText.substring(buffer.length)
          buffer = xhr.responseText
          processSSEData(newData, onEvent)
        } else if (xhr.readyState === 4) {  // DONE - 完成
          if (xhr.status === 200) {
            // 处理剩余数据
            const newData = xhr.responseText.substring(buffer.length)
            if (newData) {
              processSSEData(newData, onEvent)
            }
            resolve()
          } else {
            reject(new Error(`请求失败: ${xhr.status}`))
          }
        }
      }

      xhr.onerror = function() {
        reject(new Error('网络请求失败'))
      }

      // 发送请求
      xhr.send(JSON.stringify({
        message: data.content
      }))

      // 存储 xhr 以便取消
      this.currentStreamRequest = xhr
    })
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
