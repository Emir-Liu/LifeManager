<template>
  <view class="admin-conversations-page">
    <!-- 顶部导航栏 -->
    <view class="header">
      <view class="nav-bar">
        <view class="back-btn" @click="goBack">
          <text class="icon">←</text>
        </view>
        <text class="title">对话管理</text>
        <view class="placeholder"></view>
      </view>
    </view>

    <!-- 统计卡片 -->
    <view class="stats-container">
      <view class="stat-card">
        <text class="stat-label">总对话数</text>
        <text class="stat-value">{{ stats.total_conversations }}</text>
      </view>
      <view class="stat-card">
        <text class="stat-label">总消息数</text>
        <text class="stat-value">{{ stats.total_messages }}</text>
      </view>
      <view class="stat-card">
        <text class="stat-label">活跃对话</text>
        <text class="stat-value">{{ stats.active_conversations }}</text>
      </view>
      <view class="stat-card">
        <text class="stat-label">用户数</text>
        <text class="stat-value">{{ stats.total_users }}</text>
      </view>
    </view>

    <!-- 筛选栏 -->
    <view class="filter-bar">
      <input
        v-model="searchKeyword"
        class="search-input"
        placeholder="搜索对话标题..."
        @confirm="handleSearch"
      />
      <button class="search-btn" @click="handleSearch">搜索</button>
    </view>

    <!-- 对话列表 -->
    <scroll-view class="conversation-list" scroll-y @scrolltolower="loadMore">
      <view
        v-for="conv in conversations"
        :key="conv.id"
        class="conversation-item"
        @click="viewConversation(conv)"
      >
        <view class="conv-header">
          <text class="conv-title">{{ conv.title || '未命名对话' }}</text>
          <text class="conv-id">#{{ conv.id }}</text>
        </view>
        <view class="conv-info">
          <text class="conv-type">{{ getConversationTypeLabel(conv.conversation_type) }}</text>
          <text class="conv-status" :class="conv.status">
            {{ getStatusLabel(conv.status) }}
          </text>
        </view>
        <view class="conv-meta">
          <text class="conv-messages">{{ conv.message_count }} 条消息</text>
          <text class="conv-time">{{ formatDate(conv.created_at) }}</text>
        </view>
        <view class="conv-actions">
          <button class="action-btn danger" @click.stop="deleteConversation(conv.id)">
            删除
          </button>
        </view>
      </view>

      <!-- 加载状态 -->
      <view v-if="loading" class="loading-text">加载中...</view>
      <view v-if="!hasMore && conversations.length > 0" class="loading-text">没有更多了</view>
      <view v-if="!loading && conversations.length === 0" class="empty-text">
        暂无对话数据
      </view>
    </scroll-view>

    <!-- 消息详情弹窗 -->
    <view v-if="selectedConversation" class="modal-overlay" @click="closeModal">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">对话消息</text>
          <text class="close-btn" @click="closeModal">×</text>
        </view>
        <scroll-view class="modal-body" scroll-y>
          <view
            v-for="msg in messages"
            :key="msg.id"
            class="message-item"
            :class="msg.role"
          >
            <view class="message-role">
              {{ msg.role === 'user' ? '用户' : 'AI' }}
            </view>
            <view class="message-content">
              {{ msg.content }}
            </view>
            <view class="message-time">
              {{ formatTime(msg.created_at) }}
            </view>
          </view>
        </scroll-view>
      </view>
    </view>

    <!-- 自定义底部导航 -->
    <CustomTabbar />
  </view>
</template>

<script>
import { ref, onMounted } from 'vue'
import adminApi from '@/api/admin.js'
import CustomTabbar from '@/components/CustomTabbar/CustomTabbar.vue'

export default {
  components: {
    CustomTabbar
  },
  setup() {
    const conversations = ref([])
    const messages = ref([])
    const selectedConversation = ref(null)
    const stats = ref({
      total_conversations: 0,
      total_messages: 0,
      total_users: 0,
      active_conversations: 0
    })
    const loading = ref(false)
    const hasMore = ref(true)
    const searchKeyword = ref('')
    const skip = ref(0)
    const limit = ref(20)

    // 加载统计数据
    const loadStats = async () => {
      try {
        const data = await adminApi.getConversationStats()
        stats.value = data
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    }

    // 加载对话列表
    const loadConversations = async (reset = false) => {
      if (loading.value) return

      loading.value = true
      try {
        if (reset) {
          skip.value = 0
          conversations.value = []
        }

        const data = await adminApi.getAllConversations({
          skip: skip.value,
          limit: limit.value,
          search: searchKeyword.value || undefined
        })

        if (reset) {
          conversations.value = data.items
        } else {
          conversations.value.push(...data.items)
        }

        hasMore.value = conversations.value.length < data.total
      } catch (error) {
        console.error('加载对话列表失败:', error)
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      } finally {
        loading.value = false
      }
    }

    // 加载更多
    const loadMore = () => {
      if (!hasMore.value || loading.value) return
      skip.value += limit.value
      loadConversations()
    }

    // 搜索
    const handleSearch = () => {
      loadConversations(true)
    }

    // 查看对话详情
    const viewConversation = async (conv) => {
      selectedConversation.value = conv
      loading.value = true
      try {
        const data = await adminApi.getConversationMessages(conv.id, {
          skip: 0,
          limit: 100
        })
        messages.value = data.items || []
      } catch (error) {
        console.error('加载消息失败:', error)
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      } finally {
        loading.value = false
      }
    }

    // 关闭弹窗
    const closeModal = () => {
      selectedConversation.value = null
      messages.value = []
    }

    // 删除对话
    const deleteConversation = async (conversationId) => {
      uni.showModal({
        title: '确认删除',
        content: '确定要删除这个对话吗？删除后无法恢复。',
        success: async (res) => {
          if (res.confirm) {
            try {
              await adminApi.deleteConversation(conversationId)
              uni.showToast({
                title: '删除成功',
                icon: 'success'
              })
              // 刷新列表
              loadConversations(true)
              loadStats()
            } catch (error) {
              console.error('删除失败:', error)
              uni.showToast({
                title: '删除失败',
                icon: 'none'
              })
            }
          }
        }
      })
    }

    // 获取对话类型标签
    const getConversationTypeLabel = (type) => {
      const labels = {
        'goal_planning': '目标规划',
        'schedule_planning': '日程规划',
        'task_adjustment': '任务调整',
        'general_chat': '智能助手'
      }
      return labels[type] || type
    }

    // 获取状态标签
    const getStatusLabel = (status) => {
      const labels = {
        'active': '活跃',
        'completed': '已完成',
        'cancelled': '已取消'
      }
      return labels[status] || status
    }

    // 格式化日期
    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      return `${month}-${day} ${hours}:${minutes}`
    }

    // 格式化时间
    const formatTime = (timeStr) => {
      const date = new Date(timeStr)
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      return `${hours}:${minutes}`
    }

    // 返回
    const goBack = () => {
      uni.navigateBack()
    }

    onMounted(() => {
      loadStats()
      loadConversations()
    })

    return {
      conversations,
      messages,
      selectedConversation,
      stats,
      loading,
      hasMore,
      searchKeyword,
      loadMore,
      handleSearch,
      viewConversation,
      closeModal,
      deleteConversation,
      getConversationTypeLabel,
      getStatusLabel,
      formatDate,
      formatTime,
      goBack
    }
  }
}
</script>

<style lang="scss" scoped>
.admin-conversations-page {
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

.back-btn, .placeholder {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.title {
  flex: 1;
  text-align: center;
  font-size: 16px;
  font-weight: 500;
}

.stats-container {
  display: flex;
  gap: 10px;
  padding: 16px;
  background-color: white;
  margin-bottom: 10px;
}

.stat-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #6366f1;
}

.filter-bar {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background-color: white;
  margin-bottom: 10px;
}

.search-input {
  flex: 1;
  height: 36px;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.search-btn {
  height: 36px;
  padding: 0 16px;
  background-color: #6366f1;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
}

.conversation-list {
  flex: 1;
  padding: 0 16px;
}

.conversation-item {
  background-color: white;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.conv-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.conv-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  flex: 1;
}

.conv-id {
  font-size: 12px;
  color: #999;
  margin-left: 8px;
}

.conv-info {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.conv-type {
  padding: 2px 8px;
  background-color: #e3f2fd;
  color: #1976d2;
  border-radius: 4px;
  font-size: 12px;
}

.conv-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;

  &.active {
    background-color: #e8f5e9;
    color: #2e7d32;
  }

  &.completed {
    background-color: #fff3e0;
    color: #e65100;
  }

  &.cancelled {
    background-color: #ffebee;
    color: #c62828;
  }
}

.conv-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
}

.conv-actions {
  display: flex;
  justify-content: flex-end;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 12px;

  &.danger {
    background-color: #ffebee;
    color: #c62828;
  }
}

.loading-text,
.empty-text {
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 14px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.modal-content {
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  background-color: white;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.modal-title {
  font-size: 16px;
  font-weight: 500;
}

.close-btn {
  font-size: 24px;
  color: #999;
  cursor: pointer;
}

.modal-body {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.message-item {
  margin-bottom: 16px;
  padding: 12px;
  border-radius: 8px;

  &.user {
    background-color: #6366f1;
    color: white;
  }

  &.assistant {
    background-color: #f5f5f5;
    color: #333;
  }
}

.message-role {
  font-size: 12px;
  margin-bottom: 4px;
  opacity: 0.8;
}

.message-content {
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.message-time {
  font-size: 12px;
  margin-top: 8px;
  opacity: 0.7;
}
</style>
