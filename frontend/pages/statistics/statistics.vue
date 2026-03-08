<template>
  <view class="statistics-page">
    <!-- 顶部导航栏 -->
    <view class="header">
      <text class="title">统计分析</text>
    </view>

    <!-- 时间段选择 -->
    <view class="period-tabs">
      <view
        v-for="period in periods"
        :key="period.value"
        class="period-tab"
        :class="{ active: currentPeriod === period.value }"
        @tap="switchPeriod(period.value)"
      >
        <text>{{ period.label }}</text>
      </view>
    </view>

    <!-- 数据概览 -->
    <view class="overview-section">
      <view class="overview-card">
        <text class="overview-label">完成任务</text>
        <text class="overview-value">{{ stats.completedTasks }}</text>
        <text class="overview-unit">个</text>
      </view>
      <view class="overview-card">
        <text class="overview-label">完成率</text>
        <text class="overview-value">{{ stats.completionRate }}</text>
        <text class="overview-unit">%</text>
      </view>
      <view class="overview-card">
        <text class="overview-label">专注时长</text>
        <text class="overview-value">{{ stats.focusTime }}</text>
        <text class="overview-unit">小时</text>
      </view>
    </view>

    <!-- 热力图 -->
    <view class="heatmap-section">
      <view class="section-header">
        <text class="section-title">活跃热力图</text>
      </view>
      <view class="heatmap-container">
        <view class="heatmap">
          <view
            v-for="(day, index) in heatmapData"
            :key="index"
            class="heatmap-day"
            :class="'level-' + day.level"
            :title="day.date + ': ' + day.count + '个任务'"
          >
          </view>
        </view>
        <view class="heatmap-legend">
          <text class="legend-text">少</text>
          <view class="legend-item level-0"></view>
          <view class="legend-item level-1"></view>
          <view class="legend-item level-2"></view>
          <view class="legend-item level-3"></view>
          <view class="legend-item level-4"></view>
          <text class="legend-text">多</text>
        </view>
      </view>
    </view>

    <!-- 目标进度 -->
    <view class="goals-section">
      <view class="section-header">
        <text class="section-title">目标进度</text>
      </view>
      <view
        v-for="goal in goalProgress"
        :key="goal.id"
        class="goal-item"
      >
        <view class="goal-info">
          <text class="goal-title">{{ goal.title }}</text>
          <text class="goal-progress">{{ goal.completed }}/{{ goal.total }}</text>
        </view>
        <view class="progress-bar">
          <view
            class="progress-fill"
            :style="{ width: goal.percentage + '%' }"
          ></view>
        </view>
      </view>
    </view>

    <!-- 任务分布 -->
    <view class="distribution-section">
      <view class="section-header">
        <text class="section-title">任务分布</text>
      </view>
      <view class="distribution-list">
        <view
          v-for="item in distribution"
          :key="item.category"
          class="distribution-item"
        >
          <view class="distribution-label">
            <text class="category-icon">{{ item.icon }}</text>
            <text class="category-name">{{ item.category }}</text>
          </view>
          <view class="distribution-bar">
            <view
              class="distribution-fill"
              :style="{ width: item.percentage + '%', backgroundColor: item.color }"
            ></view>
          </view>
          <text class="distribution-value">{{ item.count }}个</text>
        </view>
      </view>
    </view>

    <!-- 时间分配 -->
    <view class="time-section">
      <view class="section-header">
        <text class="section-title">时间分配</text>
      </view>
      <view class="time-chart">
        <view
          v-for="item in timeDistribution"
          :key="item.category"
          class="time-item"
        >
          <view class="time-label">
            <text>{{ item.category }}</text>
          </view>
          <view class="time-bar">
            <view
              class="time-fill"
              :style="{ width: item.percentage + '%', backgroundColor: item.color }"
            ></view>
          </view>
          <text class="time-value">{{ item.hours }}h</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import CustomTabbar from '@/components/CustomTabbar/CustomTabbar.vue'

export default {
  components: {
    CustomTabbar
  },
  data() {
    return {
      currentPeriod: 'week',
      periods: [
        { value: 'day', label: '日' },
        { value: 'week', label: '周' },
        { value: 'month', label: '月' },
        { value: 'year', label: '年' }
      ],
      stats: {
        completedTasks: 24,
        completionRate: 85,
        focusTime: 12.5
      },
      heatmapData: [],
      goalProgress: [
        { id: 1, title: '学习Vue3', completed: 8, total: 10, percentage: 80 },
        { id: 2, title: '健身计划', completed: 15, total: 20, percentage: 75 },
        { id: 3, title: '阅读书籍', completed: 3, total: 5, percentage: 60 }
      ],
      distribution: [
        { category: '工作', icon: '💼', count: 12, percentage: 50, color: '#667eea' },
        { category: '学习', icon: '📚', count: 6, percentage: 25, color: '#764ba2' },
        { category: '健康', icon: '💪', count: 4, percentage: 17, color: '#52c41a' },
        { category: '其他', icon: '🎯', count: 2, percentage: 8, color: '#faad14' }
      ],
      timeDistribution: [
        { category: '工作', hours: 8, percentage: 64, color: '#667eea' },
        { category: '学习', hours: 3, percentage: 24, color: '#764ba2' },
        { category: '运动', hours: 1.5, percentage: 12, color: '#52c41a' }
      ]
    }
  },
  onLoad() {
    this.generateHeatmapData()
  },
  methods: {
    switchPeriod(period) {
      this.currentPeriod = period
      // 实际应用中，这里应该根据时间段重新加载数据
      this.loadStats(period)
    },

    loadStats(period) {
      // 模拟数据加载
      const statsMap = {
        day: { completedTasks: 5, completionRate: 90, focusTime: 6 },
        week: { completedTasks: 24, completionRate: 85, focusTime: 12.5 },
        month: { completedTasks: 96, completionRate: 82, focusTime: 50 },
        year: { completedTasks: 1152, completionRate: 80, focusTime: 600 }
      }
      this.stats = statsMap[period]
    },

    generateHeatmapData() {
      // 生成最近30天的热力图数据
      const data = []
      const today = new Date()
      for (let i = 29; i >= 0; i--) {
        const date = new Date(today)
        date.setDate(date.getDate() - i)
        const count = Math.floor(Math.random() * 15)
        let level = 0
        if (count > 0) level = 1
        if (count > 3) level = 2
        if (count > 7) level = 3
        if (count > 11) level = 4

        data.push({
          date: this.formatDate(date),
          count: count,
          level: level
        })
      }
      this.heatmapData = data
    },

    formatDate(date) {
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${month}-${day}`
    }
  }
}
</script>

<style scoped>
.statistics-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 100rpx;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40rpx 40rpx 60rpx;
}

.title {
  font-size: 40rpx;
  font-weight: 600;
  color: white;
}

.period-tabs {
  display: flex;
  background: white;
  padding: 20rpx 40rpx;
  border-radius: 24rpx 24rpx 0 0;
  margin-top: -40rpx;
  margin-left: 40rpx;
  margin-right: 40rpx;
  gap: 20rpx;
}

.period-tab {
  flex: 1;
  text-align: center;
  padding: 20rpx 0;
  font-size: 28rpx;
  color: #666;
  border-radius: 12rpx;
  transition: all 0.3s;
}

.period-tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
}

.overview-section {
  display: flex;
  gap: 20rpx;
  padding: 40rpx;
  background: white;
  margin: 0 40rpx 20rpx;
  border-radius: 24rpx;
}

.overview-card {
  flex: 1;
  text-align: center;
  padding: 30rpx 20rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16rpx;
  color: white;
}

.overview-label {
  font-size: 24rpx;
  display: block;
  margin-bottom: 10rpx;
  opacity: 0.9;
}

.overview-value {
  font-size: 48rpx;
  font-weight: 700;
  display: block;
}

.overview-unit {
  font-size: 24rpx;
  opacity: 0.8;
}

.heatmap-section,
.goals-section,
.distribution-section,
.time-section {
  background: white;
  margin: 0 40rpx 20rpx;
  border-radius: 24rpx;
  padding: 30rpx;
}

.section-header {
  margin-bottom: 30rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.heatmap-container {
  padding: 20rpx 0;
}

.heatmap {
  display: flex;
  flex-wrap: wrap;
  gap: 6rpx;
  margin-bottom: 20rpx;
}

.heatmap-day {
  width: 30rpx;
  height: 30rpx;
  border-radius: 4rpx;
  background: #eee;
}

.heatmap-day.level-0 {
  background: #eee;
}

.heatmap-day.level-1 {
  background: #c6e48b;
}

.heatmap-day.level-2 {
  background: #7bc96f;
}

.heatmap-day.level-3 {
  background: #239a3b;
}

.heatmap-day.level-4 {
  background: #196127;
}

.heatmap-legend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  font-size: 20rpx;
  color: #999;
}

.legend-item {
  width: 20rpx;
  height: 20rpx;
  border-radius: 2rpx;
}

.goal-item {
  margin-bottom: 30rpx;
}

.goal-item:last-child {
  margin-bottom: 0;
}

.goal-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.goal-title {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

.goal-progress {
  font-size: 24rpx;
  color: #667eea;
  font-weight: 600;
}

.progress-bar {
  height: 12rpx;
  background: #f0f0f0;
  border-radius: 6rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 6rpx;
  transition: width 0.3s;
}

.distribution-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.distribution-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.distribution-label {
  width: 120rpx;
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.category-icon {
  font-size: 32rpx;
}

.category-name {
  font-size: 26rpx;
  color: #333;
}

.distribution-bar {
  flex: 1;
  height: 12rpx;
  background: #f0f0f0;
  border-radius: 6rpx;
  overflow: hidden;
}

.distribution-fill {
  height: 100%;
  border-radius: 6rpx;
  transition: width 0.3s;
}

.distribution-value {
  width: 80rpx;
  text-align: right;
  font-size: 24rpx;
  color: #666;
}

.time-chart {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.time-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.time-label {
  width: 120rpx;
  font-size: 26rpx;
  color: #333;
}

.time-bar {
  flex: 1;
  height: 12rpx;
  background: #f0f0f0;
  border-radius: 6rpx;
  overflow: hidden;
}

.time-fill {
  height: 100%;
  border-radius: 6rpx;
  transition: width 0.3s;
}

.time-value {
  width: 80rpx;
  text-align: right;
  font-size: 24rpx;
  color: #666;
}
</style>
