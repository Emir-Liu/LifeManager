<template>
  <view class="conversation-page">
    <!-- 顶部导航栏 -->
    <view class="header">
      <view class="nav-bar">
        <view class="back-btn" @click="goBack">
          <text class="icon">←</text>
        </view>
        <text class="title">{{ conversationTitle }}</text>
        <view class="menu-btn" @click="showMenu = true">
          <text class="icon">⋯</text>
        </view>
      </view>
    </view>

    <!-- 消息列表 -->
    <scroll-view
      class="message-list"
      :scroll-top="scrollTop"
      scroll-y
      :scroll-into-view="scrollToView"
    >
      <!-- 用户消息 -->
      <view
        v-for="message in messages"
        :key="message.id"
        :id="`msg-${message.id}`"
        class="message-item"
        :class="[message.role, { streaming: message.streaming, pending: message.pending }]"
      >
        <view class="message-content">
          <!-- 文本消息 - 用户 -->
          <view v-if="message.message_type === 'text' && message.role === 'user'" class="text-message">
            <text>{{ message.content }}</text>
          </view>

          <!-- 文本消息 - AI (使用 Markdown 渲染) -->
          <view v-else-if="message.message_type === 'text' && message.role === 'assistant'">
            <MarkdownRenderer
              v-if="message.useMarkdown"
              :content="message.content"
            />
            <view v-else class="text-message">
              <text>{{ message.content }}</text>
            </view>
          </view>

          <!-- 操作卡片 -->
          <view v-else-if="message.message_type === 'action_request'" class="action-card">
            <view class="action-title">
              <text class="icon">✨</text>
              <text>操作建议</text>
            </view>
            <view class="action-content">
              {{ message.content }}
            </view>
            <view class="action-buttons">
              <button
                v-for="action in getActions(message)"
                :key="action.id"
                class="action-btn"
                :class="action.action_type"
                @click="confirmAction(action)"
              >
                {{ getActionLabel(action.action_type) }}
              </button>
            </view>
          </view>

          <!-- 时间信息 -->
          <view class="message-time">
            {{ formatTime(message.created_at) }}
          </view>
        </view>
      </view>

      <!-- AI 正在输入提示 -->
      <view v-if="isTyping" class="message-item assistant typing">
        <view class="message-content">
          <view class="typing-indicator">
            <view class="dot"></view>
            <view class="dot"></view>
            <view class="dot"></view>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 输入框 -->
    <view class="input-area">
      <textarea
        v-model="inputMessage"
        class="message-input"
        placeholder="输入你的问题..."
        :auto-height="true"
        :maxlength="500"
        :confirm-hold="true"
        @confirm="handleConfirm"
        :show-confirm-bar="false"
      />
      <button class="send-btn" :disabled="!inputMessage || isSending" @click="sendMessage">
        <text v-if="!isSending">发送</text>
        <text v-else>发送中...</text>
      </button>
    </view>

    <!-- 菜单弹窗 -->
    <view v-if="showMenu" class="menu-overlay" @click="showMenu = false">
      <view class="menu-popup" @click.stop>
        <view class="menu-item" @click="clearHistory">
          <text>清空对话历史</text>
        </view>
        <view class="menu-item" @click="showMenu = false">
          <text>取消</text>
        </view>
      </view>
    </view>

    <!-- 自定义底部导航 -->
    <CustomTabbar />
  </view>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import { useConversationStore } from '@/store/conversation.js'
import conversationApi from '@/api/conversation.js'
import CustomTabbar from '@/components/CustomTabbar/CustomTabbar.vue'
import MarkdownRenderer from '@/components/MarkdownRenderer/MarkdownRenderer.vue'

export default {
  components: {
    CustomTabbar,
    MarkdownRenderer
  },
  setup() {
    const conversationStore = useConversationStore()

    const conversationId = ref(null)
    const messages = computed(() => conversationStore.messages)
    const inputMessage = ref('')
    const isTyping = computed(() => conversationStore.isTyping)
    const isSending = computed(() => conversationStore.isSending)
    const scrollTop = ref(0)
    const scrollToView = ref('')
    const showMenu = ref(false)

    const conversationTitle = computed(() => {
      const conv = conversationStore.currentConversation
      return conv?.title || '智能助手'
    })

    // 页面加载
    onLoad(async (options) => {
      if (options.conversation_id) {
        conversationId.value = options.conversation_id
        await conversationStore.fetchConversationDetail(options.conversation_id)
        await conversationStore.fetchMessages(options.conversation_id)
      } else {
        // 如果没有 conversation_id，尝试获取用户的最新对话
        const data = await conversationStore.fetchConversations({ limit: 1 })
        const conversations = data?.items || []
        if (conversations.length > 0) {
          // 使用最新的对话
          conversationId.value = conversations[0].id
          await conversationStore.fetchConversationDetail(conversationId.value)
          await conversationStore.fetchMessages(conversationId.value)
        } else {
          // 没有对话，创建新对话
          const type = options.conversation_type || 'general_chat'
          await createConversation(type)
        }
      }
    })

    // 创建对话
    const createConversation = async (type = 'general_chat') => {
      try {
        const res = await conversationStore.createConversation({
          conversation_type: type,
          title: getConversationTitle(type)
        })
        // res 已经是解析后的对话对象（request.js返回data.data）
        if (res && res.id) {
          conversationId.value = res.id
        } else {
          console.error('创建对话返回数据:', res)
          throw new Error('创建对话返回数据格式错误')
        }
      } catch (error) {
        console.error('创建对话失败:', error)
        uni.showToast({
          title: '创建对话失败',
          icon: 'none'
        })
        throw error
      }
    }

    // 获取对话标题
    const getConversationTitle = (type) => {
      const titles = {
        goal_planning: '目标规划',
        schedule_planning: '日程规划',
        task_adjustment: '任务调整',
        general_chat: '智能助手'
      }
      return titles[type] || '智能助手'
    }

    // 发送消息
    const sendMessage = async () => {
      if (!inputMessage.value || isSending.value) return

      // 如果没有对话ID，先创建对话
      if (!conversationId.value) {
        try {
          await createConversation('general_chat')
        } catch (error) {
          console.error('创建对话失败:', error)
          return
        }
      }

      const message = inputMessage.value.trim()
      if (!message) return

      inputMessage.value = ''

      // 立即显示用户消息
      conversationStore.appendMessage({
        id: Date.now(),
        conversation_id: conversationId.value,
        role: 'user',
        message_type: 'text',
        content: message,
        created_at: new Date().toISOString(),
        pending: true  // 标记为待同步
      })

      try {
        // 使用流式接口
        await conversationStore.chatWithAIStream(conversationId.value, message)
        await nextTick()
        scrollToBottom()
      } catch (error) {
        console.error('发送消息失败:', error)
        uni.showToast({
          title: '发送失败',
          icon: 'none'
        })
      }
    }

    // 处理键盘确认事件
    const handleConfirm = (e) => {
      // 在 uni-app 中，textarea 的 confirm 事件在按下键盘确认键时触发
      // PC 端通常对应 Enter 键
      sendMessage()
    }

    // 确认操作
    const confirmAction = async (action) => {
      try {
        await conversationStore.executeAction(action.id)
        uni.showToast({
          title: '操作已执行',
          icon: 'success'
        })

        // 刷新消息列表
        await conversationStore.fetchMessages(conversationId.value)
      } catch (error) {
        console.error('执行操作失败:', error)
        uni.showToast({
          title: '执行失败',
          icon: 'none'
        })
      }
    }

    // 获取消息中的操作
    const getActions = (message) => {
      return message.actions || []
    }

    // 获取操作标签
    const getActionLabel = (actionType) => {
      const labels = {
        'create_goal': '创建目标',
        'create_task': '创建任务',
        'update_task': '更新任务',
        'delete_task': '删除任务'
      }
      return labels[actionType] || '确认'
    }

    // 滚动到底部
    const scrollToBottom = () => {
      setTimeout(() => {
        if (messages.value.length > 0) {
          const lastMsg = messages.value[messages.value.length - 1]
          scrollToView.value = `msg-${lastMsg.id}`
        }
      }, 100)
    }

    // 格式化时间
    const formatTime = (timeStr) => {
      const date = new Date(timeStr)
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      return `${hours}:${minutes}`
    }

    // 清空历史
    const clearHistory = () => {
      uni.showModal({
        title: '确认清空',
        content: '确定要清空对话历史吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await conversationStore.updateConversation(conversationId.value, {
                status: 'cancelled'
              })
              showMenu.value = false
              uni.showToast({
                title: '已清空',
                icon: 'success'
              })
            } catch (error) {
              console.error('清空失败:', error)
              uni.showToast({
                title: '清空失败',
                icon: 'none'
              })
            }
          }
        }
      })
    }

    // 返回
    const goBack = () => {
      uni.navigateBack()
    }

    return {
      conversationId,
      messages,
      inputMessage,
      isTyping,
      isSending,
      scrollTop,
      scrollToView,
      showMenu,
      conversationTitle,
      sendMessage,
      handleConfirm,
      confirmAction,
      getActions,
      getActionLabel,
      formatTime,
      clearHistory,
      goBack
    }
  }
}
</script>

<style lang="scss" scoped>
.conversation-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
  padding-bottom: 100rpx;
}

.header {
  background-color: #6366f1;
  color: white;
}

.nav-bar {
  display: flex;
  align-items: center;
  height: 44px;
  padding: 0 16px;
}

.back-btn, .menu-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon {
  font-size: 20px;
}

.title {
  flex: 1;
  text-align: center;
  font-size: 16px;
  font-weight: 500;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.message-item {
  margin-bottom: 16px;
  display: flex;

  &.user {
    justify-content: flex-end;

    .message-content {
      background-color: #6366f1;
      color: white;
    }
  }

  &.assistant {
    justify-content: flex-start;

    .message-content {
      background-color: white;
      color: #333;
    }
  }
}

.message-content {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 12px;
  position: relative;
}

.text-message {
  line-height: 1.6;
}

.action-card {
  .action-title {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
    font-weight: 500;
  }

  .action-content {
    margin-bottom: 12px;
    line-height: 1.6;
  }

  .action-buttons {
    display: flex;
    gap: 8px;
  }
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;

  &.create_goal {
    background-color: #10b981;
    color: white;
  }

  &.create_task {
    background-color: #3b82f6;
    color: white;
  }
}

.message-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 4px;

  .assistant & {
    color: #999;
  }
}

.typing {
  .message-content {
    padding: 8px 12px;
  }
}

.typing-indicator {
  display: flex;
  gap: 4px;

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #999;
    animation: typing 1.4s infinite;

    &:nth-child(2) {
      animation-delay: 0.2s;
    }

    &:nth-child(3) {
      animation-delay: 0.4s;
    }
  }
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-4px);
  }
}

@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}

// 流式输出时的光标效果
.message-item.assistant {
  &.streaming {
    .message-content {
      .text-message::after {
        content: '';
        display: inline-block;
        width: 2px;
        height: 16px;
        background-color: #6366f1;
        animation: blink 1s infinite;
        vertical-align: middle;
        margin-left: 2px;
      }
    }
  }
}

// 用户消息发送中状态
.message-item.user {
  &.pending {
    opacity: 0.7;

    .message-content::after {
      content: '发送中...';
      display: block;
      font-size: 12px;
      color: rgba(255, 255, 255, 0.8);
      margin-top: 4px;
    }
  }
}

.input-area {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background-color: white;
  border-top: 1px solid #eee;
}

.message-input {
  flex: 1;
  min-height: 36px;
  max-height: 120px;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.send-btn {
  padding: 8px 20px;
  background-color: #6366f1;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;

  &:disabled {
    background-color: #ccc;
  }
}

.menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  z-index: 999;
}

.menu-popup {
  background-color: white;
  border-radius: 16px 16px 0 0;
  overflow: hidden;
  width: 100%;
}

.menu-item {
  padding: 16px;
  text-align: center;
  border-bottom: 1px solid #eee;

  &:last-child {
    border-bottom: none;
    color: #999;
  }
}
</style>
