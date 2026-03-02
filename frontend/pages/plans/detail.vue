<template>
  <view class="container">
    <!-- 顶部导航 -->
    <view class="header">
      <text class="header-title">{{ goal?.title || '规划详情' }}</text>
    </view>

    <!-- 加载状态 -->
    <view class="loading" v-if="loading">
      <text>AI 正在生成规划...</text>
    </view>

    <!-- 规划内容 -->
    <scroll-view scroll-y class="content" v-else-if="plan">
      <!-- AI 生成的规划标签 -->
      <view class="ai-badge">
        <text class="badge-icon">🤖</text>
        <text class="badge-text">AI 生成的规划</text>
      </view>

      <!-- 统计信息 -->
      <view class="stats-card">
        <view class="stat-item">
          <text class="stat-value">{{ plan.total_stages }}</text>
          <text class="stat-label">个阶段</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value">{{ plan.total_tasks }}</text>
          <text class="stat-label">个任务</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value">{{ plan.estimated_total_hours }}</text>
          <text class="stat-label">小时总耗时</text>
        </view>
      </view>

      <!-- 阶段列表 -->
      <view 
        class="stage-section" 
        v-for="(stage, idx) in stages" 
        :key="idx"
      >
        <!-- 阶段标题 -->
        <view class="stage-header">
          <view class="stage-line"></view>
          <text class="stage-title">阶段 {{ stage.order }}：{{ stage.name }}</text>
        </view>

        <!-- 任务列表 -->
        <view 
          class="task-item" 
          v-for="(task, tidx) in stage.tasks" 
          :key="tidx"
          @click="showTaskDetail(task)"
        >
          <text class="task-num">{{ task.order }}</text>
          <view class="task-content">
            <text class="task-name">{{ task.title }}</text>
            <text class="task-desc" v-if="task.description">{{ task.description }}</text>
            <text class="task-time">预计 {{ task.estimated_hours }} 小时</text>
          </view>
        </view>
      </view>

      <!-- 底部留白 -->
      <view style="height: 140rpx;"></view>
    </scroll-view>

    <!-- 底部确认按钮 -->
    <view class="footer" v-if="plan && !loading">
      <button class="confirm-btn" @click="handleConfirmPlan">
        确认规划并创建任务
      </button>
    </view>
  </view>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  data() {
    return {
      goal: null,
      plan: null,
      loading: false
    }
  },
  computed: {
    ...mapGetters('plans', ['planStages']),
    stages() {
      return this.plan?.content?.stages || []
    }
  },
  onLoad(options) {
    if (options.planId) {
      this.loadPlan(options.planId)
    } else if (options.goalId) {
      this.generatePlan(options.goalId)
    }
  },
  methods: {
    ...mapActions('plans', ['fetchPlanDetail', 'generatePlan', 'confirmPlan']),
    ...mapActions('goals', ['fetchGoalDetail']),

    async loadPlan(planId) {
      this.loading = true
      try {
        this.plan = await this.fetchPlanDetail(planId)
        if (this.plan.goal_id) {
          this.goal = await this.fetchGoalDetail(this.plan.goal_id)
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

    async generatePlan(goalId) {
      this.loading = true
      try {
        // 获取目标信息
        this.goal = await this.fetchGoalDetail(goalId)

        // 生成规划
        this.plan = await this.$store.dispatch('plans/generatePlan', {
          goalId: goalId,
          availableHoursPerDay: 2
        })

        uni.showToast({
          title: '规划生成成功',
          icon: 'success'
        })
      } catch (error) {
        uni.showToast({
          title: error.message || '生成失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    },

    async handleConfirmPlan() {
      if (!this.plan) return

      try {
        const result = await this.$store.dispatch('plans/confirmPlan', {
          planId: this.plan.id
        })

        uni.showToast({
          title: `已创建 ${result.tasks_created} 个任务`,
          icon: 'success'
        })

        // 跳转到任务列表
        uni.switchTab({
          url: '/pages/tasks/tasks'
        })
      } catch (error) {
        uni.showToast({
          title: error.message || '确认失败',
          icon: 'none'
        })
      }
    },

    showTaskDetail(task) {
      // 可以显示任务详情弹窗
      console.log('Task:', task)
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
  font-size: 32rpx;
  font-weight: 600;
  color: #1f2937;
  text-align: center;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6b7280;
  font-size: 28rpx;
}

.content {
  flex: 1;
  padding: 20rpx;
}

.ai-badge {
  display: flex;
  align-items: center;
  padding: 16rpx 24rpx;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 12rpx;
  margin-bottom: 20rpx;
}

.badge-icon {
  font-size: 32rpx;
  margin-right: 12rpx;
}

.badge-text {
  font-size: 26rpx;
  color: #ffffff;
  font-weight: 500;
}

.stats-card {
  display: flex;
  background: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-value {
  font-size: 48rpx;
  font-weight: 700;
  color: #6366f1;
  display: block;
  margin-bottom: 8rpx;
}

.stat-label {
  font-size: 24rpx;
  color: #6b7280;
}

.stat-divider {
  width: 1rpx;
  background: #e5e7eb;
  margin: 0 20rpx;
}

.stage-section {
  margin-bottom: 40rpx;
}

.stage-header {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
  padding-left: 20rpx;
}

.stage-line {
  width: 4rpx;
  height: 32rpx;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  margin-right: 16rpx;
  border-radius: 2rpx;
}

.stage-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #1f2937;
}

.task-item {
  display: flex;
  align-items: flex-start;
  background: #ffffff;
  border-radius: 12rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.task-item:active {
  opacity: 0.8;
}

.task-num {
  width: 48rpx;
  height: 48rpx;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: #ffffff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  font-weight: 600;
  margin-right: 20rpx;
  flex-shrink: 0;
}

.task-content {
  flex: 1;
}

.task-name {
  font-size: 28rpx;
  color: #1f2937;
  display: block;
  margin-bottom: 8rpx;
  font-weight: 500;
}

.task-desc {
  font-size: 24rpx;
  color: #6b7280;
  display: block;
  margin-bottom: 8rpx;
  line-height: 1.5;
}

.task-time {
  font-size: 24rpx;
  color: #9ca3af;
  display: block;
}

.footer {
  padding: 20rpx 30rpx 40rpx;
  background: #ffffff;
  box-shadow: 0 -2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.confirm-btn {
  width: 100%;
  height: 96rpx;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: #ffffff;
  border: none;
  border-radius: 24rpx;
  font-size: 32rpx;
  font-weight: 600;
}
</style>
