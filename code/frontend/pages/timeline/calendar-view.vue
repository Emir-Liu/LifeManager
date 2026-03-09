<template>
  <view class="calendar-view-page">
    <!-- 日历组件 -->
    <Calendar
      v-model="selectedDate"
      :tasks-by-date="tasksByDate"
      @date-select="onDateSelect"
      @month-change="onMonthChange"
    />

    <!-- 选中日期的任务列表 -->
    <view class="tasks-section">
      <view class="section-header">
        <text class="section-title">{{ formatDate(selectedDate) }} 任务</text>
        <text class="task-count">{{ dayTasks.length }}个任务</text>
      </view>

      <!-- 任务列表 -->
      <view class="tasks-list">
        <!-- 空状态 -->
        <view v-if="dayTasks.length === 0" class="empty-state">
          <text class="empty-icon">📝</text>
          <text class="empty-text">今日暂无任务</text>
          <button class="add-task-btn" @click="createTask">
            <text>添加任务</text>
          </button>
        </view>

        <!-- 任务卡片 -->
        <view
          v-for="item in dayTasks"
          :key="item.id"
          class="task-card"
          :class="{
            'task': item.type === 'task',
            'event': item.type === 'event',
            'completed': item.completed
          }"
          @click="handleTaskClick(item)"
        >
          <view class="task-left">
            <view class="task-time">{{ formatTime(item) }}</view>
            <view class="task-duration">{{ item.duration_minutes || 60 }}分钟</view>
          </view>

          <view class="task-right">
            <text class="task-title">{{ item.title }}</text>
            <text v-if="item.description" class="task-desc">{{ item.description }}</text>

            <!-- 任务标签 -->
            <view class="task-tags">
              <text v-if="item.priority" class="tag" :class="item.priority">
                {{ getPriorityLabel(item.priority) }}
              </text>
              <text v-if="item.type === 'event'" class="tag event">
                日程
              </text>
            </view>
          </view>

          <!-- 完成状态 -->
          <view class="task-status" @click.stop="toggleComplete(item)">
            <text v-if="item.completed" class="completed-icon">✓</text>
            <text v-else class="pending-icon">○</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 月度统计 -->
    <view class="stats-section">
      <view class="stats-card">
        <text class="stats-title">本月统计</text>
        <view class="stats-grid">
          <view class="stat-item">
            <text class="stat-value">{{ monthStats.totalTasks }}</text>
            <text class="stat-label">任务数</text>
          </view>
          <view class="stat-item">
            <text class="stat-value">{{ monthStats.completedTasks }}</text>
            <text class="stat-label">已完成</text>
          </view>
          <view class="stat-item">
            <text class="stat-value">{{ monthStats.totalHours }}</text>
            <text class="stat-label">总工时</text>
          </view>
          <view class="stat-item">
            <text class="stat-value">{{ monthStats.completionRate }}%</text>
            <text class="stat-label">完成率</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 底部操作按钮 -->
    <view class="bottom-actions">
      <button class="action-btn smart-assign" @click="goToSmartAssign">
        <text class="icon">✨</text>
        <text>智能分配</text>
      </button>
      <button class="action-btn add-task" @click="createTask">
        <text class="icon">+</text>
        <text>添加任务</text>
      </button>
      <button class="action-btn time-line" @click="goToTimeline">
        <text class="icon">📊</text>
        <text>时间线</text>
      </button>
    </view>

    <!-- 自定义底部导航 -->
    <CustomTabbar />
  </view>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import Calendar from '@/components/Calendar.vue'
import { useTasksStore } from '@/store/tasks.js'
import CustomTabbar from '@/components/CustomTabbar/CustomTabbar.vue'

export default {
  components: {
    Calendar,
    CustomTabbar
  },

  setup() {
    const tasksStore = useTasksStore()

    const selectedDate = ref(new Date())
    const tasksByDate = ref({})
    const allTasks = ref([])
    const allEvents = ref([])

    // 选中日期的任务
    const dayTasks = computed(() => {
      const dateStr = formatDateKey(selectedDate.value)
      return allTasks.value.filter(t => formatDateKey(new Date(t.due_date)) === dateStr)
        .map(task => ({
          id: `task-${task.id}`,
          type: 'task',
          title: task.title,
          description: task.description,
          start_time: task.start_time,
          end_time: task.end_time,
          duration_minutes: task.duration_minutes,
          priority: task.priority,
          completed: task.status === 'completed'
        }))
        .concat(
          allEvents.value
            .filter(e => e.start_date === dateStr)
            .map(event => ({
              id: `event-${event.id}`,
              type: 'event',
              title: event.title,
              description: event.description,
              start_time: event.start_time,
              end_time: event.end_time,
              duration_minutes: event.duration_minutes,
              completed: false
            }))
        )
        .sort((a, b) => {
          const timeA = a.start_time || '00:00'
          const timeB = b.start_time || '00:00'
          return timeA.localeCompare(timeB)
        })
    })

    // 月度统计
    const monthStats = computed(() => {
      const year = selectedDate.value.getFullYear()
      const month = selectedDate.value.getMonth()

      const monthTasks = allTasks.value.filter(t => {
        const taskDate = new Date(t.due_date)
        return taskDate.getFullYear() === year && taskDate.getMonth() === month
      })

      const completed = monthTasks.filter(t => t.status === 'completed').length
      const totalHours = monthTasks.reduce((sum, t) => sum + (t.estimated_hours || 1), 0)
      const completionRate = monthTasks.length > 0 ? Math.round((completed / monthTasks.length) * 100) : 0

      return {
        totalTasks: monthTasks.length,
        completedTasks: completed,
        totalHours: totalHours.toFixed(1),
        completionRate
      }
    })

    // 页面加载
    onLoad(async () => {
      await loadTasks()
      await loadEvents()
      updateTasksByDate()
    })

    // 加载任务
    const loadTasks = async () => {
      try {
        const res = await tasksStore.getTaskList()
        allTasks.value = res.data?.items || []
      } catch (error) {
        console.error('加载任务失败:', error)
      }
    }

    // 加载事件
    const loadEvents = async () => {
      // TODO: 集成事件API
      allEvents.value = []
    }

    // 更新按日期分组的任务
    const updateTasksByDate = () => {
      const grouped = {}

      allTasks.value.forEach(task => {
        const dateStr = formatDateKey(new Date(task.due_date))
        if (!grouped[dateStr]) {
          grouped[dateStr] = 0
        }
        grouped[dateStr]++
      })

      allEvents.value.forEach(event => {
        if (!grouped[event.start_date]) {
          grouped[event.start_date] = 0
        }
        grouped[event.start_date]++
      })

      tasksByDate.value = grouped
    }

    // 格式化日期为key
    const formatDateKey = (date) => {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }

    // 格式化日期
    const formatDate = (date) => {
      const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
      return `${date.getMonth() + 1}月${date.getDate()}日 ${weekDays[date.getDay()]}`
    }

    // 格式化时间
    const formatTime = (item) => {
      const start = item.start_time || '09:00'
      const end = item.end_time || '10:00'
      return `${start}-${end}`
    }

    // 获取优先级标签
    const getPriorityLabel = (priority) => {
      const labels = {
        high: '高',
        medium: '中',
        low: '低'
      }
      return labels[priority] || ''
    }

    // 日期选择
    const onDateSelect = (date) => {
      selectedDate.value = date
    }

    // 月份变化
    const onMonthChange = (date) => {
      selectedDate.value = date
    }

    // 点击任务
    const handleTaskClick = (item) => {
      if (item.type === 'task') {
        const taskId = item.id.replace('task-', '')
        uni.navigateTo({
          url: `/pages/tasks/detail?id=${taskId}`
        })
      }
    }

    // 切换完成状态
    const toggleComplete = async (item) => {
      if (item.type === 'task') {
        const taskId = item.id.replace('task-', '')
        try {
          await tasksStore.toggleTaskComplete(taskId, !item.completed)
          await loadTasks()
          updateTasksByDate()
        } catch (error) {
          console.error('更新任务状态失败:', error)
        }
      }
    }

    // 创建任务
    const createTask = () => {
      uni.navigateTo({
        url: `/pages/tasks/create?date=${formatDateKey(selectedDate.value)}`
      })
    }

    // 跳转智能分配
    const goToSmartAssign = () => {
      uni.navigateTo({
        url: '/pages/timeline/smart-assign'
      })
    }

    // 跳转时间线
    const goToTimeline = () => {
      uni.navigateTo({
        url: `/pages/timeline/timeline?date=${formatDateKey(selectedDate.value)}`
      })
    }

    return {
      selectedDate,
      tasksByDate,
      dayTasks,
      monthStats,
      formatDate,
      formatTime,
      getPriorityLabel,
      onDateSelect,
      onMonthChange,
      handleTaskClick,
      toggleComplete,
      createTask,
      goToSmartAssign,
      goToTimeline
    }
  }
}
</script>

<style lang="scss" scoped>
.calendar-view-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 80px;
}

.tasks-section {
  margin: 12px;
  background-color: white;
  border-radius: 12px;
  padding: 16px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  color: #1f2937;
}

.task-count {
  font-size: 12px;
  color: #9ca3af;
}

.tasks-list {
  .task-card {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px;
    background-color: #f9fafb;
    border-radius: 8px;
    margin-bottom: 8px;

    &.completed {
      opacity: 0.6;

      .task-title {
        text-decoration: line-through;
        color: #9ca3af;
      }
    }
  }
}

.task-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  min-width: 60px;
}

.task-time {
  font-size: 12px;
  font-weight: 500;
  color: #6366f1;
}

.task-duration {
  font-size: 10px;
  color: #9ca3af;
}

.task-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-title {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
}

.task-desc {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.4;
}

.task-tags {
  display: flex;
  gap: 4px;
  margin-top: 4px;
}

.tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;

  &.high {
    background-color: #fef3c7;
    color: #92400e;
  }

  &.medium {
    background-color: #dbeafe;
    color: #1e40af;
  }

  &.low {
    background-color: #d1fae5;
    color: #065f46;
  }

  &.event {
    background-color: #ede9fe;
    color: #5b21b6;
  }
}

.task-status {
  padding: 4px;

  .completed-icon {
    color: #10b981;
    font-size: 18px;
  }

  .pending-icon {
    color: #d1d5db;
    font-size: 18px;
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 0;
  gap: 12px;
}

.empty-icon {
  font-size: 48px;
  opacity: 0.5;
}

.empty-text {
  font-size: 14px;
  color: #9ca3af;
}

.add-task-btn {
  padding: 8px 20px;
  background-color: #6366f1;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
}

.stats-section {
  margin: 12px;
}

.stats-card {
  background-color: white;
  border-radius: 12px;
  padding: 16px;
}

.stats-title {
  display: block;
  font-size: 14px;
  color: #9ca3af;
  margin-bottom: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #6366f1;
}

.stat-label {
  font-size: 12px;
  color: #9ca3af;
}

.bottom-actions {
  display: flex;
  gap: 8px;
  padding: 12px;
  background-color: white;
  border-top: 1px solid #e5e7eb;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
}

.action-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px;
  background-color: #f9fafb;
  border: none;
  border-radius: 8px;
  font-size: 12px;
  color: #374151;

  .icon {
    font-size: 20px;
  }

  &.smart-assign {
    background-color: #fef3c7;
    color: #92400e;
  }

  &.add-task {
    background-color: #6366f1;
    color: white;
  }

  &.time-line {
    background-color: #dbeafe;
    color: #1e40af;
  }
}
</style>
