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
      const data = await conversationApi.getConversations(params)
      // request.js 直接返回 data.data，所以 data 就是对话列表数据
      conversations.value = data?.items || []
      return data
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
      // request.js 直接返回 data.data，所以 res 就是消息数据
      const data = await conversationApi.getMessages(conversationId, params)
      // 后端返回的消息按 sequence 降序排列，需要反转
      const items = data?.items || []
      messages.value = items.reverse()
      return data
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

  // 发送消息(流式) - 使用AI接口
  const chatWithAI = async (conversationId, content, onChunk) => {
    if (!conversationId || isSending.value) {
      throw new Error('对话ID无效或正在发送中')
    }

    isSending.value = true
    isTyping.value = true

    try {
      // 调用AI聊天接口
      const res = await conversationApi.chatWithAI(conversationId, {
        content: content
      })

      // 添加用户消息到列表
      if (res.user_message) {
        messages.value.push(res.user_message)
      }

      // 添加AI回复到列表
      if (res.ai_message) {
        messages.value.push(res.ai_message)
      }

      return res
    } catch (error) {
      console.error('AI对话失败:', error)
      // 如果失败，移除可能已添加的用户消息
      if (res && res.user_message) {
        messages.value = messages.value.filter(m => m.id !== res.user_message.id)
      }
      throw error
    } finally {
      isSending.value = false
      isTyping.value = false
    }
  }

  // 流式 AI 对话
  const chatWithAIStream = async (conversationId, content) => {
    console.log('开始流式对话:', conversationId, content)

    if (!conversationId || isSending.value) {
      throw new Error('对话ID无效或正在发送中')
    }

    isSending.value = true
    isTyping.value = true

    // 记录临时消息的创建时间（前端本地时间）
    const localCreatedAt = new Date().toISOString()

    // 创建临时 AI 消息用于流式显示
    const tempMessageId = `temp-${Date.now()}`
    const tempAiMessage = ref({
      id: tempMessageId,
      conversation_id: conversationId,
      role: 'assistant',
      message_type: 'text',
      content: '',
      created_at: localCreatedAt,
      streaming: true,
      useMarkdown: true  // 流式过程中也使用 Markdown 解析
    })
    messages.value.push(tempAiMessage.value)
    console.log('临时消息已创建:', tempAiMessage.value)

    try {
      await conversationApi.chatWithAIStream(conversationId, {
        content: content
      }, (event, data) => {
        console.log('收到事件:', event, data)
        // 处理流式响应
        if (event === 'ai_chunk') {
          // 追加内容
          tempAiMessage.value.content += data.content
          console.log('AI 内容更新:', tempAiMessage.value.content)
          // 更新数组中的引用
          const index = messages.value.findIndex(m => m.id === tempMessageId)
          if (index !== -1) {
            messages.value[index] = tempAiMessage.value
          }
        } else if (event === 'ai_complete') {
          // 替换为完整消息，但保留前端本地创建时间
          console.log('AI 回复完成:', data)
          const index = messages.value.findIndex(m => m.id === tempMessageId)
          if (index !== -1) {
            data.useMarkdown = true
            data.streaming = false  // 完成后移除流式标记
            data.created_at = localCreatedAt  // 保留前端本地时间，避免时区问题
            messages.value[index] = data
          }
        } else if (event === 'user_message') {
          // 同步用户消息
          console.log('用户消息同步:', data)
          const index = messages.value.findIndex(m => m.pending)
          if (index !== -1) {
            // 保留前端的本地创建时间
            const originalTime = messages.value[index].created_at
            messages.value[index] = data
            messages.value[index].created_at = originalTime
          }
        } else if (event === 'error') {
          console.error('流式错误:', data)
          throw new Error(data.message)
        }
      })

      console.log('流式对话完成')
      return tempAiMessage.value
    } catch (error) {
      console.error('AI对话失败:', error)
      // 移除临时消息
      messages.value = messages.value.filter(m => m.id !== tempMessageId)
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
    chatWithAIStream,
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
