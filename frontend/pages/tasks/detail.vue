<template>
  <view class="container">
    <!-- 任务标题卡片 -->
    <view class="task-header">
      <view class="header-bg"></view>
      <text class="task-title">{{ task.title }}</text>
      <view class="status-badge" :class="statusClass">
        <text>{{ statusText }}</text>
      </view>
    </view>

    <!-- 任务详情 -->
    <scroll-view scroll-y class="detail-content">
      <!-- 所属目标 -->
      <view class="info-section">
        <text class="info-label">所属目标</text>
        <view class="info-divider"></view>
        <text class="info-value" @click="goToGoal">{{ task.goal_title || '未关联' }}</text>
      </view>

      <!-- 截止日期 -->
      <view class="info-section">
        <text class="info-label">截止日期</text>
        <view class="info-divider"></view>
        <text class="info-value">{{ formatDate(task.due_date) }}</text>
      </view>

      <!-- 预计耗时 -->
      <view class="info-section">
        <text class="info-label">预计耗时</text>
        <view class="info-divider"></view>
        <text class="info-value">{{ task.estimated_hours }} 小时</text>
      </view>

      <!-- 任务描述 -->
      <view class="info-section" v-if="task.description">
        <text class="info-label">任务描述</text>
        <view class="info-divider"></view>
        <text class="info-desc">{{ task.description }}</text>
      </view>

      <!-- 创建时间 -->
      <view class="info-section">
        <text class="info-label">创建时间</text>
        <view class="info-divider"></view>
        <text class="info-value">{{ formatDateTime(task.created_at) }}</text>
      </view>
    </scroll-view>

    <!-- 底部按钮 -->
    <view class="footer">
      <button 
        class="footer-btn" 
        :class="task.completed ? 'secondary' : 'primary'"
        @click="toggleComplete"
        :disabled="loading"
      >
        {{ task.completed ? '取消完成' : '完成任务' }}
      </button>
    </view>
  </view>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  data() {
    return {
      task: {},
      loading: false
    }
  },
  computed: {
    statusText() {
      return this.task.completed ? '已完成' : '未完成'
    },
    statusClass() {
      return this.task.completed ? 'completed' : 'pending'
    }
  },
  onLoad(options) {
    if (options.id) {
      this.loadTaskDetail(options.id)
    }
  },
  methods: {
    ...mapActions('tasks', ['fetchTaskDetail', 'completeTask', 'uncompleteTask']),

    async loadTaskDetail(taskId) {
      try {
        this.task = await this.fetchTaskDetail(taskId)
      } catch (error) {
        uni.showToast({
          title: error.message || '加载失败',
          icon: 'none'
        })
      }
    },

    async toggleComplete() {
      if (this.loading) return

      this.loading = true
      try {
        if (this.task.completed) {
          await this.uncompleteTask(this.task.id)
          uni.showToast({
            title: '已取消完成',
            icon: 'success'
          })
        } else {
          await this.completeTask(this.task.id)
          uni.showToast({
            title: '任务已完成',
            icon: 'success'
          })
        }
        // 重新加载
        await this.loadTaskDetail(this.task.id)
      } catch (error) {
        uni.showToast({
          title: error.message || '操作失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    },

    goToGoal() {
      if (this.task.goal_id) {
        uni.navigateTo({
          url: `/pages/goals/detail?id=${this.task.goal_id}`
        })
      }
    },

    formatDate(dateStr) {
      if (!dateStr) return '未设置'
      const date = new Date(dateStr)
      return `${date.getFullYear()}年${date.getMonth() +1}月${date.getDate()}日`
    },

    formatDateTime(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return `${date.getFullYear()}-${String(date.getMonth() +1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
    }
  }
}
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f9fafb;
}

.task-header {
  position: relative;
  padding: 60rpx 40rpx 40rpx;
  background: #ffffff;
}

.header-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 200rpx;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 0 0 40rpx 40rpx;
}

.task-title {
  position: relative;
  font-size: 40rpx;
  font-weight: 600;
  color: #1f2937;
  display: block;
  margin-bottom: 20rpx;
  padding-top: 40rpx;
}

.status-badge {
  position: relative;
  display: inline-block;
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
  font-size: 24rpx;
}

.status-badge.pending {
  background: #fef3c7;
  color: #d97706;
}

.status-badge.completed {
  background: #d1fae5;
  color: #059669;
}

.detail-content {
  flex: 1;
  padding: 20rpx;
}

.info-section {
  background: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 16rpx;
}

.info-label {
  font-size: 24rpx;
  color: #6b7280;
  display: block;
  margin-bottom: 16rpx;
}

.info-divider {
  height: 1rpx;
  background: #e5e7eb;
  margin-bottom: 16rpx;
}

.info-value {
  font-size: 28rpx;
  color: #1f2937;
  display: block;
  word-break: break-all;
}

.info-value:active {
  opacity: 0.6;
}

.info-desc {
  font-size: 28rpx;
  color: #4b5563;
  line-height: 1.6;
  display: block;
}

.footer {
  padding: 20rpx 30rpx 40rpx;
  background: #ffffff;
  box-shadow: 0 -2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.footer-btn {
  width: 100%;
  height: 96rpx;
  border: none;
  border-radius: 24rpx;
  font-size: 32rpx;
  font-weight: 600;
}

.footer-btn.primary {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: #ffffff;
}

.footer-btn.secondary {
  background: #f3f4f6;
  color: #6b7280;
}

.footer-btn[disabled] {
  opacity: 0.6;
}
</style>
