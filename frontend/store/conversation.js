import { defineStore } from 'pinia'
import conversationApi from '@/api/conversation.js'
import { ref, computed } from 'vue'

export const useConversationStore = defineStore('conversation', () => {
  // State
  const conversations = ref([])
  const currentConversation = ref(null)
  const messages = ref([])
  const isTyping = ref(false)
  const isSending = ref(false)
  const loading = ref(false)

  // Getters
  const activeConversations = computed(() =>
    conversations.value.filter(c => c.status === 'active')
  )

  const messageCount = computed(() => messages.value.length)

  // Actions
  // 获取对话列表
  const fetchConversations = async (params = {}) => {
    loading.value = true
    try {
      const res = await conversationApi.getConversations(params)
      conversations.value = res.data?.items || []
      return res
    } catch (error) {
      console.error('获取对话列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 创建对话
  const createConversation = async (data) => {
    try {
      const res = await conversationApi.createConversation(data)
      currentConversation.value = res.data
      messages.value = []
      return res
    } catch (error) {
      console.error('创建对话失败:', error)
      throw error
    }
  }

  // 获取对话详情
  const fetchConversationDetail = async (id) => {
    try {
      const res = await conversationApi.getConversationDetail(id)
      currentConversation.value = res.data
      return res
    } catch (error) {
      console.error('获取对话详情失败:', error)
      throw error
    }
  }

  // 获取消息列表
  const fetchMessages = async (conversationId, params = {}) => {
    loading.value = true
    try {
      const res = await conversationApi.getMessages(conversationId, params)
      messages.value = res.data?.items || []
      return res
    } catch (error) {
      console.error('获取消息列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 发送消息(普通)
  const sendMessage = async (conversationId, content) => {
    if (!conversationId || isSending.value) {
      throw new Error('对话ID无效或正在发送中')
    }

    isSending.value = true
    isTyping.value = true

    // 添加用户消息到列表
    const userMessage = {
      id: Date.now(),
      conversation_id: conversationId,
      role: 'user',
      message_type: 'text',
      content,
      created_at: new Date().toISOString()
    }
    messages.value.push(userMessage)

    try {
      const res = await conversationApi.sendMessage(conversationId, {
        role: 'user',
        message_type: 'text',
        content
      })

      // 添加AI回复到列表
      if (res.data) {
        messages.value.push(res.data)
      }

      return res
    } catch (error) {
      console.error('发送消息失败:', error)
      // 移除失败的用户消息
      messages.value = messages.value.filter(m => m.id !== userMessage.id)
      throw error
    } finally {
      isSending.value = false
      isTyping.value = false
    }
  }

  // 发送消息(流式)
  const chatWithAI = async (conversationId, content, onChunk) => {
    if (!conversationId || isSending.value) {
      throw new Error('对话ID无效或正在发送中')
    }

    isSending.value = true
    isTyping.value = true

    // 添加用户消息到列表
    const userMessage = {
      id: Date.now(),
      conversation_id: conversationId,
      role: 'user',
      message_type: 'text',
      content,
      created_at: new Date().toISOString()
    }
    messages.value.push(userMessage)

    // 创建AI消息占位符
    const aiMessage = {
      id: Date.now() + 1,
      conversation_id: conversationId,
      role: 'assistant',
      message_type: 'text',
      content: '',
      created_at: new Date().toISOString()
    }
    messages.value.push(aiMessage)

    try {
      const res = await conversationApi.chatWithAI(conversationId, {
        message: content
      })

      // 如果返回完整的AI消息,更新占位符
      if (res.data?.ai_message) {
        Object.assign(aiMessage, res.data.ai_message)
      }

      return res
    } catch (error) {
      console.error('AI对话失败:', error)
      // 移除失败的消息
      messages.value = messages.value.filter(m =>
        m.id !== userMessage.id && m.id !== aiMessage.id
      )
      throw error
    } finally {
      isSending.value = false
      isTyping.value = false
    }
  }

  // 消息反馈
  const feedbackMessage = async (messageId, feedback) => {
    try {
      return await conversationApi.feedbackMessage(messageId, { feedback })
    } catch (error) {
      console.error('反馈消息失败:', error)
      throw error
    }
  }

  // 获取操作列表
  const fetchActions = async (conversationId, params = {}) => {
    try {
      return await conversationApi.getActions(conversationId, params)
    } catch (error) {
      console.error('获取操作列表失败:', error)
      throw error
    }
  }

  // 执行操作
  const executeAction = async (actionId) => {
    try {
      return await conversationApi.executeAction(actionId)
    } catch (error) {
      console.error('执行操作失败:', error)
      throw error
    }
  }

  // 更新操作状态
  const updateAction = async (actionId, status) => {
    try {
      return await conversationApi.updateAction(actionId, { status })
    } catch (error) {
      console.error('更新操作失败:', error)
      throw error
    }
  }

  // 更新对话
  const updateConversation = async (id, data) => {
    try {
      const res = await conversationApi.updateConversation(id, data)
      if (currentConversation.value?.id === id) {
        currentConversation.value = res.data
      }
      return res
    } catch (error) {
      console.error('更新对话失败:', error)
      throw error
    }
  }

  // 删除对话
  const deleteConversation = async (id) => {
    try {
      await conversationApi.deleteConversation(id)
      conversations.value = conversations.value.filter(c => c.id !== id)
      if (currentConversation.value?.id === id) {
        currentConversation.value = null
        messages.value = []
      }
    } catch (error) {
      console.error('删除对话失败:', error)
      throw error
    }
  }

  // 清空当前对话
  const clearCurrentConversation = () => {
    currentConversation.value = null
    messages.value = []
    isTyping.value = false
    isSending.value = false
  }

  // 添加消息到列表(用于流式更新)
  const appendMessage = (message) => {
    messages.value.push(message)
  }

  // 更新消息内容(用于流式更新)
  const updateMessage = (messageId, content) => {
    const message = messages.value.find(m => m.id === messageId)
    if (message) {
      message.content = content
    }
  }

  return {
    // State
    conversations,
    currentConversation,
    messages,
    isTyping,
    isSending,
    loading,

    // Getters
    activeConversations,
    messageCount,

    // Actions
    fetchConversations,
    createConversation,
    fetchConversationDetail,
    fetchMessages,
    sendMessage,
    chatWithAI,
    feedbackMessage,
    fetchActions,
    executeAction,
    updateAction,
    updateConversation,
    deleteConversation,
    clearCurrentConversation,
    appendMessage,
    updateMessage
  }
})
