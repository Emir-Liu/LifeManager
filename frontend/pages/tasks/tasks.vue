<template>
  <view class="container">
    <!-- 顶部导航 -->
    <view class="header">
      <text class="header-title">今日任务</text>
      <view class="filter-tabs">
        <view 
          class="tab-item" 
          :class="{ active: filter === 'today' }"
          @click="filter = 'today'"
        >今日</view>
        <view 
          class="tab-item" 
          :class="{ active: filter === 'all' }"
          @click="filter = 'all'"
        >全部</view>
      </view>
    </view>

    <!-- 任务列表 -->
    <scroll-view scroll-y class="task-list" @scrolltolower="loadMore">
      <!-- 按日期分组 -->
      <view class="date-group" v-for="(date, idx) in groupedTasks" :key="idx">
        <text class="date-title">{{ formatDate(date.date) }}</text>

        <!-- 任务卡片 -->
        <view 
          class="task-card" 
          v-for="task in date.tasks" 
          :key="task.id"
          @click="goToTaskDetail(task.id)"
        >
          <view class="task-left">
            <view class="checkbox" :class="{ checked: task.completed }">
              <text v-if="task.completed" class="check-icon">✓</text>
            </view>
            <view class="task-info">
              <text class="task-title" :class="{ completed: task.completed }">{{ task.title }}</text>
              <text class="task-time">预计 {{ task.estimated_hours }} 小时</text>
            </view>
          </view>
          <view class="task-right">
            <button class="action-btn" v-if="!task.completed" @click.stop="completeTask(task.id)">
              开始
            </button>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-if="taskList.length === 0 && !loading">
        <text class="empty-icon">📋</text>
        <text class="empty-text">暂无任务</text>
      </view>

      <!-- 加载状态 -->
      <view class="loading" v-if="loading">
        <text>加载中...</text>
      </view>
    </scroll-view>

    <!-- 浮动添加按钮 -->
    <view class="fab" @click="addTask">
      <text class="fab-icon">+</text>
    </view>
  </view>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  data() {
    return {
      filter: 'today', // today | all
      loading: false
    }
  },
  computed: {
    ...mapGetters('tasks', ['today', 'list']),
    taskList() {
      return this.filter === 'today' ? this.today : this.list
    },
    groupedTasks() {
      const groups = {}
      this.taskList.forEach(task => {
        const date = task.due_date ? task.due_date.split('T')[0] : '未安排'
        if (!groups[date]) {
          groups[date] = { date, tasks: [] }
        }
        groups[date].tasks.push(task)
      })
      return Object.values(groups).sort((a, b) => new Date(a.date) - new Date(b.date))
    }
  },
  onLoad() {
    this.loadTasks()
  },
  onPullDownRefresh() {
    this.loadTasks().finally(() => {
      uni.stopPullDownRefresh()
    })
  },
  methods: {
    ...mapActions('tasks', ['fetchTodayTasks', 'fetchTasks', 'completeTask']),
    
    async loadTasks() {
      this.loading = true
      try {
        if (this.filter === 'today') {
          await this.fetchTodayTasks()
        } else {
          await this.fetchTasks()
        }
      } catch (error) {
        uni.showToast({
          title: error.message || '加载失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    },

    goToTaskDetail(taskId) {
      uni.navigateTo({
        url: `/pages/tasks/detail?id=${taskId}`
      })
    },

    async completeTask(taskId) {
      try {
        await this.completeTask(taskId)
        uni.showToast({
          title: '任务已完成',
          icon: 'success'
        })
      } catch (error) {
        uni.showToast({
          title: error.message || '操作失败',
          icon: 'none'
        })
      }
    },

    addTask() {
      uni.navigateTo({
        url: '/pages/tasks/create'
      })
    },

    formatDate(dateStr) {
      if (dateStr === '未安排') return '未安排'
      const date = new Date(dateStr)
      const today = new Date()
      const tomorrow = new Date(today)
      tomorrow.setDate(tomorrow.getDate() + 1)

      if (dateStr === today.toISOString().split('T')[0]) {
        return '今天'
      } else if (dateStr === tomorrow.toISOString().split('T')[0]) {
        return '明天'
      }
      return dateStr
    },

    loadMore() {
      // 上拉加载更多
    }
  },
  watch: {
    filter() {
      this.loadTasks()
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

.header {
  padding: 30rpx;
  background: #ffffff;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.header-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #1f2937;
  display: block;
  margin-bottom: 20rpx;
}

.filter-tabs {
  display: flex;
  gap: 20rpx;
}

.tab-item {
  padding: 12rpx 32rpx;
  font-size: 28rpx;
  color: #6b7280;
  border-radius: 24rpx;
  background: #f3f4f6;
}

.tab-item.active {
  color: #ffffff;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
}

.task-list {
  flex: 1;
  padding: 20rpx;
}

.date-group {
  margin-bottom: 30rpx;
}

.date-title {
  font-size: 24rpx;
  color: #6b7280;
  display: block;
  margin-bottom: 16rpx;
  padding-left: 8rpx;
}

.task-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx;
  background: #ffffff;
  border-radius: 16rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.task-left {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 20rpx;
}

.checkbox {
  width: 40rpx;
  height: 40rpx;
  border: 2rpx solid #e5e7eb;
  border-radius: 8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.checkbox.checked {
  background: #10b981;
  border-color: #10b981;
}

.check-icon {
  color: #ffffff;
  font-size: 24rpx;
  font-weight: bold;
}

.task-info {
  flex: 1;
}

.task-title {
  font-size: 28rpx;
  color: #1f2937;
  display: block;
  margin-bottom: 8rpx;
}

.task-title.completed {
  color: #9ca3af;
  text-decoration: line-through;
}

.task-time {
  font-size: 24rpx;
  color: #6b7280;
}

.action-btn {
  padding: 12rpx 24rpx;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: #ffffff;
  border: none;
  border-radius: 8rpx;
  font-size: 24rpx;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100rpx 0;
}

.empty-icon {
  font-size: 120rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #9ca3af;
}

.loading {
  text-align: center;
  padding: 40rpx;
  color: #6b7280;
}

.fab {
  position: fixed;
  right: 40rpx;
  bottom: 100rpx;
  width: 120rpx;
  height: 120rpx;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(99, 102, 241, 0.4);
}

.fab-icon {
  font-size: 60rpx;
  color: #ffffff;
  font-weight: 300;
}
</style>
