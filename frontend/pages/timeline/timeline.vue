<template>
  <view class="timeline-page">
    <!-- 日期选择器 -->
    <view class="date-picker">
      <button class="date-btn" @click="changeDate(-1)">
        <text>←</text>
      </button>
      <view class="current-date" @click="showDatePicker = true">
        <text>{{ formatDate(currentDate) }}</text>
      </view>
      <button class="date-btn" @click="changeDate(1)">
        <text>→</text>
      </button>
    </view>

    <!-- 时间线内容 -->
    <scroll-view class="timeline-content" scroll-y>
      <!-- 加载状态 -->
      <view v-if="loading" class="loading-state">
        <text>加载中...</text>
      </view>

      <!-- 无数据提示 -->
      <view v-else-if="timeSlots.length === 0" class="empty-state">
        <text class="empty-icon">📅</text>
        <text class="empty-text">暂无日程安排</text>
      </view>

      <!-- 时间段列表 -->
      <view
        v-for="(slot, index) in timeSlots"
        :key="index"
        class="time-slot"
        :class="{ 'available': slot.available, 'unavailable': !slot.available }"
      >
        <view class="time-range">
          <text class="start-time">{{ formatTime(slot.start_time) }}</text>
          <text class="separator">-</text>
          <text class="end-time">{{ formatTime(slot.end_time) }}</text>
          <text class="duration">{{ slot.duration_minutes }}分钟</text>
        </view>

        <view v-if="!slot.available" class="unavailable-reason">
          <text>{{ slot.reason }}</text>
        </view>

        <!-- 任务列表 -->
        <view v-if="slot.available && slot.tasks && slot.tasks.length > 0" class="task-list">
          <view
            v-for="task in slot.tasks"
            :key="task.id"
            class="task-item"
            :class="{ 'completed': task.completed }"
            @click="goToTaskDetail(task.id)"
          >
            <view class="task-info">
              <text class="task-title">{{ task.title }}</text>
              <text class="task-duration">{{ task.duration_minutes }}分钟</text>
            </view>
            <view class="task-status">
              <text v-if="task.completed" class="completed-icon">✓</text>
              <text v-else class="pending-icon">○</text>
            </view>
          </view>
        </view>

        <!-- 添加任务按钮 -->
        <view v-if="slot.available" class="add-task-btn" @click="showAddTask(slot)">
          <text class="icon">+</text>
          <text>添加任务</text>
        </view>
      </view>
    </scroll-view>

    <!-- 快捷操作按钮 -->
    <view class="quick-actions">
      <button class="action-btn" @click="smartAssign">
        <text class="icon">✨</text>
        <text>智能分配</text>
      </button>
      <button class="action-btn" @click="manualAdd">
        <text class="icon">+</text>
        <text>手动添加</text>
      </button>
    </view>

    <!-- 日期选择弹窗 -->
    <uni-popup ref="datePickerPopup" type="bottom" @maskClick="showDatePicker = false">
      <view class="date-picker-popup">
        <view class="popup-header">
          <text class="cancel-btn" @click="showDatePicker = false">取消</text>
          <text class="popup-title">选择日期</text>
          <text class="confirm-btn" @click="confirmDate">确定</text>
        </view>
        <picker-view class="picker-view" :value="pickerValue" @change="onPickerChange">
          <picker-view-column>
            <view v-for="year in years" :key="year">
              <text>{{ year }}年</text>
            </view>
          </picker-view-column>
          <picker-view-column>
            <view v-for="month in months" :key="month">
              <text>{{ month }}月</text>
            </view>
          </picker-view-column>
          <picker-view-column>
            <view v-for="day in days" :key="day">
              <text>{{ day }}日</text>
            </view>
          </picker-view-column>
        </picker-view>
      </view>
    </uni-popup>

    <!-- 添加任务弹窗 -->
    <uni-popup ref="addTaskPopup" type="bottom" @maskClick="showAddTaskPopup = false">
      <view class="add-task-popup">
        <view class="popup-header">
          <text class="cancel-btn" @click="showAddTaskPopup = false">取消</text>
          <text class="popup-title">添加任务</text>
          <text class="confirm-btn" @click="confirmAddTask">确定</text>
        </view>
        <view class="form-content">
          <view class="form-item">
            <text class="label">任务名称</text>
            <input v-model="newTask.title" class="input" placeholder="请输入任务名称" />
          </view>
          <view class="form-item">
            <text class="label">任务时长(分钟)</text>
            <input v-model.number="newTask.duration" type="number" class="input" placeholder="60" />
          </view>
        </view>
      </view>
    </uni-popup>
  </view>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useTasksStore } from '@/store/tasks.js'
import timelineApi from '@/api/timeline.js'

export default {
  setup() {
    const tasksStore = useTasksStore()

    const currentDate = ref(new Date())
    const timelineData = ref({ tasks: [], events: [] })
    const showDatePicker = ref(false)
    const showAddTaskPopup = ref(false)
    const pickerValue = ref([0, 0, 0])
    const loading = ref(false)

    const newTask = ref({
      title: '',
      duration: 60
    })

    const selectedTimeSlot = ref(null)

    // 时间线数据(合并任务和事件)
    const timeSlots = computed(() => {
      const slots = []

      // 添加任务
      timelineData.value.tasks.forEach(task => {
        slots.push({
          id: `task-${task.id}`,
          type: 'task',
          task_type: task.task_type || 'work',
          title: task.title,
          description: task.description,
          start_time: task.start_time || `${task.due_date}T09:00:00`,
          end_time: task.end_time || `${task.due_date}T10:00:00`,
          duration_minutes: task.duration_minutes || 60,
          status: task.status,
          hasConflict: task.has_conflict || false,
          data: task
        })
      })

      // 添加事件
      timelineData.value.events.forEach(event => {
        slots.push({
          id: `event-${event.id}`,
          type: 'event',
          title: event.title,
          description: event.description,
          start_time: `${event.start_date}T${event.start_time}:00`,
          end_time: `${event.start_date}T${event.end_time}:00`,
          duration_minutes: event.duration_minutes || 60,
          hasConflict: event.has_conflict || false,
          data: event
        })
      })

      // 按开始时间排序
      slots.sort((a, b) =>
        new Date(a.start_time) - new Date(b.start_time)
      )

      return slots
    })

    // 日期数据
    const currentYear = new Date().getFullYear()
    const years = computed(() => {
      const arr = []
      for (let i = currentYear - 10; i <= currentYear + 10; i++) {
        arr.push(i)
      }
      return arr
    })

    const months = computed(() => {
      const arr = []
      for (let i = 1; i <= 12; i++) {
        arr.push(i)
      }
      return arr
    })

    const days = computed(() => {
      const year = years.value[pickerValue.value[0]]
      const month = months.value[pickerValue.value[1]]
      const date = new Date(year, month, 0)
      return Array.from({ length: date.getDate() }, (_, i) => i + 1)
    })

    // 页面加载
    onLoad((options) => {
      if (options.date) {
        currentDate.value = new Date(options.date)
      }
      loadTimeline()
    })

    // 加载时间线
    const loadTimeline = async () => {
      loading.value = true
      try {
        const dateStr = currentDate.value.toISOString().split('T')[0]
        const res = await timelineApi.getTimeline(dateStr)

        if (res.data) {
          timelineData.value = {
            tasks: res.data.tasks || [],
            events: res.data.events || []
          }
        }
      } catch (error) {
        console.error('加载时间线失败:', error)
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      } finally {
        loading.value = false
      }
    }

    // 切换日期
    const changeDate = (days) => {
      const newDate = new Date(currentDate.value)
      newDate.setDate(newDate.getDate() + days)
      currentDate.value = newDate
      loadTimeline()
    }

    // 格式化日期
    const formatDate = (date) => {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
      const weekDay = weekDays[date.getDay()]
      return `${year}-${month}-${day} ${weekDay}`
    }

    // 格式化时间
    const formatTime = (timeStr) => {
      const date = new Date(timeStr)
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      return `${hours}:${minutes}`
    }

    // 日期选择器变化
    const onPickerChange = (e) => {
      pickerValue.value = e.detail.value
    }

    // 确认日期选择
    const confirmDate = () => {
      const year = years.value[pickerValue.value[0]]
      const month = months.value[pickerValue.value[1]]
      const day = days.value[pickerValue.value[2]]
      currentDate.value = new Date(year, month - 1, day)
      showDatePicker.value = false
      loadTimeline()
    }

    // 显示添加任务
    const showAddTask = (slot) => {
      selectedTimeSlot.value = slot
      newTask.value = {
        title: '',
        duration: slot.duration_minutes || 60
      }
      showAddTaskPopup.value = true
    }

    // 确认添加任务
    const confirmAddTask = async () => {
      if (!newTask.value.title) {
        uni.showToast({
          title: '请输入任务名称',
          icon: 'none'
        })
        return
      }

      try {
        const dateStr = currentDate.value.toISOString().split('T')[0]

        await tasksStore.createTask({
          title: newTask.value.title,
          due_date: dateStr,
          estimated_hours: newTask.value.duration / 60,
          start_time: '09:00',
          end_time: `${String(9 + Math.floor(newTask.value.duration / 60)).padStart(2, '0')}:${String(newTask.value.duration % 60).padStart(2, '0')}`
        })

        uni.showToast({
          title: '添加成功',
          icon: 'success'
        })
        showAddTaskPopup.value = false
        loadTimeline()
      } catch (error) {
        console.error('添加任务失败:', error)
        uni.showToast({
          title: '添加失败',
          icon: 'none'
        })
      }
    }

    // 智能分配
    const smartAssign = async () => {
      try {
        uni.showModal({
          title: '智能分配',
          content: '是否让AI为您智能分配任务时间？',
          success: async (res) => {
            if (res.confirm) {
              const dateStr = currentDate.value.toISOString().split('T')[0]
              await timelineApi.smartAssignTasks({
                date_range: {
                  start_date: dateStr,
                  end_date: dateStr
                },
                preferences: {
                  preferred_time: '09:00-18:00'
                }
              })
              uni.showToast({
                title: '分配成功',
                icon: 'success'
              })
              loadTimeline()
            }
          }
        })
      } catch (error) {
        console.error('智能分配失败:', error)
        uni.showToast({
          title: '分配失败',
          icon: 'none'
        })
      }
    }

    // 手动添加
    const manualAdd = () => {
      uni.navigateTo({
        url: '/pages/tasks/create'
      })
    }

    // 跳转到任务详情
    const goToTaskDetail = (taskId) => {
      uni.navigateTo({
        url: `/pages/tasks/detail?id=${taskId}`
      })
    }

    return {
      currentDate,
      timeSlots,
      showDatePicker,
      showAddTaskPopup,
      pickerValue,
      newTask,
      selectedTimeSlot,
      years,
      months,
      days,
      changeDate,
      formatDate,
      formatTime,
      onPickerChange,
      confirmDate,
      showAddTask,
      confirmAddTask,
      smartAssign,
      manualAdd,
      goToTaskDetail,
      loading
    }
  }
}
</script>

<style lang="scss" scoped>
.timeline-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
}

.date-picker {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: white;
  border-bottom: 1px solid #eee;
}

.date-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border: none;
  border-radius: 8px;
  font-size: 18px;
  color: #333;
}

.current-date {
  flex: 1;
  text-align: center;
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.timeline-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 0;

  text {
    font-size: 14px;
    color: #999;
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;

  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }

  .empty-text {
    font-size: 14px;
    color: #999;
  }
}

.time-slot {
  background-color: white;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;

  &.available {
    border-left: 4px solid #10b981;
  }

  &.unavailable {
    border-left: 4px solid #ef4444;
    opacity: 0.6;
  }
}

.time-range {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;

  .start-time, .end-time {
    font-size: 14px;
    font-weight: 500;
    color: #333;
  }

  .separator {
    color: #999;
  }

  .duration {
    margin-left: auto;
    font-size: 12px;
    color: #999;
  }
}

.unavailable-reason {
  font-size: 12px;
  color: #ef4444;
  margin-bottom: 8px;
}

.task-list {
  margin-top: 8px;
}

.task-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px;
  background-color: #f5f5f5;
  border-radius: 6px;
  margin-bottom: 8px;

  &.completed {
    opacity: 0.6;
  }
}

.task-info {
  flex: 1;
}

.task-title {
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
}

.task-duration {
  font-size: 12px;
  color: #999;
}

.task-status {
  .completed-icon {
    color: #10b981;
    font-size: 16px;
  }

  .pending-icon {
    color: #999;
    font-size: 16px;
  }
}

.add-task-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px;
  background-color: #6366f1;
  color: white;
  border-radius: 6px;
  font-size: 14px;
  margin-top: 8px;
}

.quick-actions {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  background-color: white;
  border-top: 1px solid #eee;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 12px;
  background-color: #6366f1;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;

  .icon {
    font-size: 16px;
  }
}

.date-picker-popup {
  background-color: white;
  border-radius: 16px 16px 0 0;
  overflow: hidden;
}

.add-task-popup {
  background-color: white;
  border-radius: 16px 16px 0 0;
  overflow: hidden;
}

.popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.cancel-btn, .confirm-btn {
  padding: 8px 16px;
  font-size: 14px;
}

.cancel-btn {
  color: #999;
}

.confirm-btn {
  color: #6366f1;
}

.popup-title {
  font-size: 16px;
  font-weight: 500;
}

.picker-view {
  height: 200px;
}

.form-content {
  padding: 16px;
}

.form-item {
  margin-bottom: 16px;

  .label {
    display: block;
    font-size: 14px;
    color: #333;
    margin-bottom: 8px;
  }

  .input {
    width: 100%;
    height: 40px;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
  }
}
</style>
