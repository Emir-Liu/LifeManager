<template>
  <view class="detail-container">
    <!-- 目标头部 -->
    <view class="goal-header">
      <view class="status-badge" :class="goal.status">
        {{ getStatusText(goal.status) }}
      </view>
      <text class="goal-title">{{ goal.title }}</text>
      <text class="goal-desc">{{ goal.description }}</text>
    </view>

    <!-- 进度卡片 -->
    <view class="progress-card">
      <view class="progress-header">
        <text class="progress-title">目标进度</text>
        <text class="progress-value">{{ goal.progress }}%</text>
      </view>
      <view class="progress-bar">
        <view class="progress-fill" :style="{ width: goal.progress + '%' }"></view>
      </view>
    </view>

    <!-- 信息卡片 -->
    <view class="info-card">
      <view class="info-row">
        <text class="info-label">优先级</text>
        <text class="info-value priority" :class="goal.priority">
          {{ getPriorityText(goal.priority) }}
        </text>
      </view>
      <view class="info-row">
        <text class="info-label">类型</text>
        <text class="info-value">{{ getTypeText(goal.type) }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">开始时间</text>
        <text class="info-value">{{ goal.createdAt }}</text>
      </view>
      <view class="info-row">
        <text class="info-label">截止时间</text>
        <text class="info-value">{{ goal.deadline }}</text>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="action-bar">
      <button v-if="goal.status !== 'completed'" class="action-btn primary" @tap="handleComplete">
        完成目标
      </button>
      <button class="action-btn secondary" @tap="handleEdit">编辑目标</button>
      <button class="action-btn danger" @tap="handleDelete">删除目标</button>
    </view>
  </view>
</template>

<script>
import goalApi from '@/api/goal.js'

export default {
  data() {
    return {
      goalId: '',
      goal: {
        title: '',
        description: '',
        status: '',
        progress: 0,
        priority: '',
        type: '',
        createdAt: '',
        deadline: ''
      }
    }
  },

  onLoad(options) {
    this.goalId = options.id
    this.loadGoalDetail()
  },

  methods: {
    async loadGoalDetail() {
      try {
        const res = await goalApi.getGoalDetail(this.goalId)
        this.goal = res
      } catch (error) {
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      }
    },

    async handleComplete() {
      try {
        await goalApi.toggleGoalComplete(this.goalId, true)
        uni.showToast({
          title: '恭喜完成目标！',
          icon: 'success'
        })
        this.loadGoalDetail()
      } catch (error) {
        uni.showToast({
          title: '操作失败',
          icon: 'none'
        })
      }
    },

    handleEdit() {
      uni.showToast({
        title: '编辑功能开发中',
        icon: 'none'
      })
    },

    handleDelete() {
      uni.showModal({
        title: '确认删除',
        content: '确定要删除这个目标吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await goalApi.deleteGoal(this.goalId)
              uni.showToast({
                title: '删除成功',
                icon: 'success'
              })
              setTimeout(() => {
                uni.navigateBack()
              }, 1000)
            } catch (error) {
              uni.showToast({
                title: '删除失败',
                icon: 'none'
              })
            }
          }
        }
      })
    },

    getStatusText(status) {
      const map = {
        'in_progress': '进行中',
        'completed': '已完成',
        'paused': '暂停'
      }
      return map[status] || status
    },

    getPriorityText(priority) {
      const map = {
        'low': '低',
        'medium': '中',
        'high': '高'
      }
      return map[priority] || priority
    },

    getTypeText(type) {
      const map = {
        'personal': '个人',
        'study': '学习',
        'work': '工作',
        'health': '健康'
      }
      return map[type] || type
    }
  }
}
</script>

<style scoped>
.detail-container {
  min-height: 100vh;
  background-color: #F5F5F5;
  padding: 20rpx;
}

.goal-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16rpx;
  padding: 40rpx;
  margin-bottom: 20rpx;
}

.status-badge {
  display: inline-block;
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
  font-size: 24rpx;
  background-color: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  margin-bottom: 20rpx;
}

.status-badge.completed {
  background-color: #07C160;
}

.goal-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #ffffff;
  display: block;
  margin-bottom: 16rpx;
}

.goal-desc {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
}

.progress-card {
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 20rpx;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.progress-title {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

.progress-value {
  font-size: 32rpx;
  color: #007AFF;
  font-weight: bold;
}

.progress-bar {
  width: 100%;
  height: 16rpx;
  background-color: #F0F0F0;
  border-radius: 8rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 8rpx;
  transition: width 0.3s;
}

.info-card {
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 20rpx;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #F0F0F0;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 28rpx;
  color: #666;
}

.info-value {
  font-size: 28rpx;
  color: #333;
}

.info-value.priority.low {
  color: #07C160;
}

.info-value.priority.medium {
  color: #FF9800;
}

.info-value.priority.high {
  color: #FF3B30;
}

.action-bar {
  padding: 20rpx 0;
}

.action-btn {
  width: 100%;
  height: 88rpx;
  border-radius: 44rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
  margin-bottom: 20rpx;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
}

.action-btn.secondary {
  background-color: #ffffff;
  color: #007AFF;
  border: 2rpx solid #007AFF;
}

.action-btn.danger {
  background-color: #FF3B30;
  color: #ffffff;
}
</style>
