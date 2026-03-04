<template>
  <view class="goals-container">
    <!-- 顶部统计卡片 -->
    <view class="stats-card">
      <view class="stat-item">
        <text class="stat-value">{{ stats.total }}</text>
        <text class="stat-label">总目标</text>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item">
        <text class="stat-value">{{ stats.inProgress }}</text>
        <text class="stat-label">进行中</text>
      </view>
      <view class="stat-divider"></view>
      <view class="stat-item">
        <text class="stat-value">{{ stats.completed }}</text>
        <text class="stat-label">已完成</text>
      </view>
    </view>

    <!-- 筛选标签 -->
    <view class="filter-tabs">
      <view
        v-for="tab in tabs"
        :key="tab.value"
        class="tab-item"
        :class="{ active: currentTab === tab.value }"
        @tap="handleTabChange(tab.value)"
      >
        {{ tab.label }}
      </view>
    </view>

    <!-- 目标列表 -->
    <view class="goals-list">
      <view v-for="goal in filteredGoals" :key="goal.id" class="goal-card" @tap="handleGoalDetail(goal.id)">
        <view class="goal-header">
          <text class="goal-title">{{ goal.title }}</text>
          <view class="goal-actions">
            <view class="goal-status" :class="goal.status">
              {{ getStatusText(goal.status) }}
            </view>
            <view class="delete-btn" @tap.stop="handleDelete(goal.id)">
              <text class="delete-icon">×</text>
            </view>
          </view>
        </view>

        <view class="goal-info">
          <text class="goal-desc">{{ goal.description }}</text>
          <view class="goal-meta">
            <text class="meta-item" v-if="goal.deadline">
              📅 {{ formatDate(goal.deadline) }}
            </text>
            <text class="meta-item" v-if="goal.priority">
              {{ getPriorityIcon(goal.priority) }} {{ getPriorityText(goal.priority) }}
            </text>
          </view>
        </view>

        <!-- 进度条 -->
        <view class="progress-section">
          <view class="progress-bar">
            <view class="progress-fill" :style="{ width: goal.progress + '%' }"></view>
          </view>
          <text class="progress-text">{{ goal.progress || 0 }}%</text>
        </view>

        <!-- 对话规划按钮 -->
        <view v-if="goal.status === 'active'" class="conversation-btn" @tap.stop="startGoalPlanning(goal)">
          <text class="btn-icon">✨</text>
          <text>对话规划</text>
        </view>
      </view>
    </view>

    <!-- AI 智能规划按钮 -->
    <view class="ai-planning-btn" @tap="startNewPlanning">
      <text class="btn-icon">🤖</text>
      <text>AI 智能规划</text>
    </view>
        </view>

        <view class="goal-footer">
          <view class="goal-progress">
            <text class="progress-label">进度: {{ goal.progress }}%</text>
            <view class="progress-bar">
              <view class="progress-fill" :style="{ width: goal.progress + '%' }"></view>
            </view>
          </view>
          <text class="goal-date">{{ goal.deadline }}</text>
        </view>
      </view>

      <!-- 空状态 -->
      <view v-if="filteredGoals.length === 0" class="empty-state">
        <text class="empty-text">暂无目标</text>
        <text class="empty-hint">点击下方按钮创建第一个目标</text>
      </view>
    </view>

    <!-- 创建按钮 -->
    <view class="create-btn" @tap="handleCreate">
      <text class="create-icon">+</text>
    </view>
  </view>
</template>

<script>
import goalApi from '@/api/goal.js'

export default {
  data() {
    return {
      stats: {
        total: 0,
        inProgress: 0,
        completed: 0
      },
      tabs: [
        { label: '全部', value: 'all' },
        { label: '进行中', value: 'in_progress' },
        { label: '已完成', value: 'completed' }
      ],
      currentTab: 'all',
      goals: []
    }
  },

  computed: {
    filteredGoals() {
      if (this.currentTab === 'all') return this.goals
      return this.goals.filter(goal => goal.status === this.currentTab)
    }
  },

  onLoad() {
    this.loadGoals()
    this.loadStats()
  },

  onShow() {
    // 从详情页返回时刷新数据
    this.loadGoals()
    this.loadStats()
  },

  methods: {
    async loadGoals() {
      try {
        const res = await goalApi.getGoalList()
        this.goals = res
      } catch (error) {
        console.error('加载目标失败:', error)
      }
    },

    async loadStats() {
      try {
        const res = await goalApi.getGoalStatistics()
        this.stats = res
      } catch (error) {
        console.error('加载统计失败:', error)
      }
    },

    handleTabChange(value) {
      this.currentTab = value
    },

    handleGoalDetail(id) {
      uni.navigateTo({
        url: `/pages/goals/detail?id=${id}`
      })
    },

    handleCreate() {
      uni.navigateTo({
        url: '/pages/goals/create'
      })
    },

    // 开始新的规划(对话)
    startNewPlanning() {
      uni.navigateTo({
        url: '/pages/conversation/conversation?conversation_type=goal_planning'
      })
    },

    // 对话规划
    startGoalPlanning(goal) {
      uni.navigateTo({
        url: `/pages/conversation/conversation?conversation_type=task_adjustment&goal_id=${goal.id}`
      })
    },

    // 格式化日期
    formatDate(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    },

    // 获取优先级图标
    getPriorityIcon(priority) {
      const icons = {
        high: '🔴',
        medium: '🟡',
        low: '🟢'
      }
      return icons[priority] || ''
    },

    // 获取优先级文本
    getPriorityText(priority) {
      const texts = {
        high: '高优先级',
        medium: '中优先级',
        low: '低优先级'
      }
      return texts[priority] || ''
    },

    handleDelete(goalId) {
      uni.showModal({
        title: '确认删除',
        content: '删除后将无法恢复，确定要删除该目标吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await goalApi.deleteGoal(goalId)
              uni.showToast({
                title: '删除成功',
                icon: 'success'
              })
              // 刷新列表
              this.loadGoals()
              this.loadStats()
            } catch (error) {
              uni.showToast({
                title: error.message || '删除失败',
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
    }
  }
}
</script>

<style scoped>
.goals-container {
  min-height: 100vh;
  background-color: #F5F5F5;
  padding-bottom: 120rpx;
}

.stats-card {
  display: flex;
  align-items: center;
  justify-content: space-around;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60rpx 40rpx;
  margin-bottom: 20rpx;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 48rpx;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 12rpx;
}

.stat-label {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
}

.stat-divider {
  width: 1rpx;
  height: 80rpx;
  background-color: rgba(255, 255, 255, 0.3);
}

.filter-tabs {
  display: flex;
  background-color: #ffffff;
  padding: 20rpx;
  margin-bottom: 20rpx;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 20rpx;
  font-size: 28rpx;
  color: #666;
  position: relative;
}

.tab-item.active {
  color: #007AFF;
  font-weight: bold;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60rpx;
  height: 4rpx;
  background-color: #007AFF;
  border-radius: 2rpx;
}

.goals-list {
  padding: 20rpx;
}

.goal-card {
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.goal-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  flex: 1;
}

.goal-actions {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.goal-status {
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
  font-size: 24rpx;
}

.delete-btn {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: #FFF3E0;
}

.delete-icon {
  font-size: 40rpx;
  color: #FF5722;
  font-weight: bold;
}

.goal-status.in_progress {
  background-color: #E3F2FD;
  color: #007AFF;
}

.goal-status.completed {
  background-color: #E8F5E9;
  color: #07C160;
}

.goal-status.paused {
  background-color: #FFF3E0;
  color: #FF9800;
}

.goal-info {
  margin-bottom: 24rpx;
}

.goal-desc {
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
}

.goal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.goal-progress {
  flex: 1;
  margin-right: 20rpx;
}

.progress-label {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 8rpx;
  display: block;
}

.progress-bar {
  width: 100%;
  height: 8rpx;
  background-color: #F0F0F0;
  border-radius: 4rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 4rpx;
  transition: width 0.3s;
}

.goal-date {
  font-size: 24rpx;
  color: #999;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 0;
}

.empty-text {
  font-size: 32rpx;
  color: #999;
  margin-bottom: 16rpx;
}

.empty-hint {
  font-size: 24rpx;
  color: #CCCCCC;
}

.create-btn {
  position: fixed;
  right: 40rpx;
  bottom: 40rpx;
  width: 120rpx;
  height: 120rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(102, 126, 234, 0.4);
}

.create-icon {
  font-size: 72rpx;
  color: #ffffff;
  font-weight: bold;
}
</style>
