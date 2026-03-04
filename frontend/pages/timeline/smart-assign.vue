<template>
  <view class="smart-assign-page">
    <!-- 顶部导航 -->
    <view class="header">
      <view class="nav-bar">
        <view class="back-btn" @click="goBack">
          <text class="icon">←</text>
        </view>
        <text class="title">智能分配任务</text>
        <view class="placeholder"></view>
      </view>
    </view>

    <!-- 日期范围选择 -->
    <view class="section">
      <view class="section-title">
        <text>分配日期范围</text>
      </view>
      <view class="date-range">
        <view class="date-item" @click="showStartDatePicker = true">
          <text class="label">开始日期</text>
          <text class="date-text">{{ formatDate(startDate) }}</text>
        </view>
        <text class="separator">至</text>
        <view class="date-item" @click="showEndDatePicker = true">
          <text class="label">结束日期</text>
          <text class="date-text">{{ formatDate(endDate) }}</text>
        </view>
      </view>
    </view>

    <!-- 时间偏好 -->
    <view class="section">
      <view class="section-title">
        <text>时间偏好</text>
      </view>
      <view class="preference-list">
        <view class="preference-item" @click="showTimeRangePicker = true">
          <text class="label">首选时间</text>
          <text class="value">{{ preferredTime }}</text>
          <text class="icon">›</text>
        </view>
        <view class="preference-item" @click="toggleWorkDays">
          <text class="label">排除周末</text>
          <switch :checked="excludeWeekend" @change="toggleWorkDays" />
        </view>
        <view class="preference-item">
          <text class="label">缓冲时间</text>
          <text class="value">{{ bufferTime }}分钟</text>
          <slider
            class="slider"
            :value="bufferTime"
            min="0"
            max="30"
            step="5"
            @change="onBufferTimeChange"
          />
        </view>
      </view>
    </view>

    <!-- 待分配任务列表 -->
    <view class="section">
      <view class="section-title">
        <text>待分配任务 ({{ selectedTasks.length }})</text>
        <text class="select-all" @click="selectAll">全选</text>
      </view>
      <view class="task-list">
        <view
          v-for="task in availableTasks"
          :key="task.id"
          class="task-item"
          :class="{ 'selected': isSelected(task.id) }"
          @click="toggleTask(task)"
        >
          <view class="task-checkbox">
            <text v-if="isSelected(task.id)" class="checked-icon">✓</text>
          </view>
          <view class="task-info">
            <text class="task-title">{{ task.title }}</text>
            <text class="task-meta">
              {{ task.estimated_hours || 1 }}小时
              {{ task.priority ? `· ${getPriorityLabel(task.priority)}` : '' }}
            </text>
          </view>
        </view>
      </view>
    </view>

    <!-- 分配结果预览 -->
    <view v-if="assignments.length > 0" class="section">
      <view class="section-title">
        <text>分配结果预览</text>
      </view>
      <view class="assignment-list">
        <view
          v-for="(assignment, index) in assignments"
          :key="index"
          class="assignment-item"
        >
          <text class="assignment-date">{{ formatDate(assignment.assigned_date) }}</text>
          <text class="assignment-time">
            {{ assignment.start_time }} - {{ assignment.end_time }}
          </text>
          <text class="assignment-task">{{ assignment.task_title }}</text>
          <view v-if="assignment.conflicts.length > 0" class="conflict-badge">
            <text>⚠️ {{ assignment.conflicts.length }}个冲突</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 底部操作按钮 -->
    <view class="bottom-actions">
      <button
        class="preview-btn"
        :disabled="selectedTasks.length === 0"
        @click="previewAssignment"
      >
        <text>预览分配</text>
      </button>
      <button
        class="confirm-btn"
        :disabled="selectedTasks.length === 0 || !hasPreview"
        @click="confirmAssignment"
      >
        <text>确认分配</text>
      </button>
    </view>

    <!-- 日期选择弹窗 -->
    <uni-popup ref="startDatePicker" type="bottom" @maskClick="showStartDatePicker = false">
      <view class="date-picker-popup">
        <view class="popup-header">
          <text class="cancel-btn" @click="showStartDatePicker = false">取消</text>
          <text class="popup-title">选择开始日期</text>
          <text class="confirm-btn" @click="confirmStartDate">确定</text>
        </view>
        <picker-view class="picker-view" :value="startPickerValue" @change="onStartDateChange">
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
            <view v-for="day in days(startPickerValue)" :key="day">
              <text>{{ day }}日</text>
            </view>
          </picker-view-column>
        </picker-view>
      </view>
    </uni-popup>

    <uni-popup ref="endDatePicker" type="bottom" @maskClick="showEndDatePicker = false">
      <view class="date-picker-popup">
        <view class="popup-header">
          <text class="cancel-btn" @click="showEndDatePicker = false">取消</text>
          <text class="popup-title">选择结束日期</text>
          <text class="confirm-btn" @click="confirmEndDate">确定</text>
        </view>
        <picker-view class="picker-view" :value="endPickerValue" @change="onEndDateChange">
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
            <view v-for="day in days(endPickerValue)" :key="day">
              <text>{{ day }}日</text>
            </view>
          </picker-view-column>
        </picker-view>
      </view>
    </uni-popup>
  </view>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useTasksStore } from '@/store/tasks.js'
import timelineApi from '@/api/timeline.js'
import { useTimePreferencesStore } from '@/store/timePreferences.js'

export default {
  setup() {
    const tasksStore = useTasksStore()
    const timePreferencesStore = useTimePreferencesStore()

    // 日期范围
    const startDate = ref(new Date())
    const endDate = ref(new Date(Date.now() + 7 * 24 * 60 * 60 * 1000))

    // 时间偏好
    const preferredTime = ref('09:00-18:00')
    const excludeWeekend = ref(true)
    const bufferTime = ref(10)

    // 任务
    const availableTasks = ref([])
    const selectedTasks = ref([])

    // 分配结果
    const assignments = ref([])
    const hasPreview = ref(false)

    // 弹窗状态
    const showStartDatePicker = ref(false)
    const showEndDatePicker = ref(false)
    const showTimeRangePicker = ref(false)

    // 日期选择器值
    const startPickerValue = ref([0, 0, 0])
    const endPickerValue = ref([0, 0, 0])

    // 年月数据
    const years = computed(() => {
      const currentYear = new Date().getFullYear()
      return Array.from({ length: 20 }, (_, i) => currentYear - 10 + i)
    })

    const months = computed(() => Array.from({ length: 12 }, (_, i) => i + 1))

    const days = (pickerValue) => {
      const year = years.value[pickerValue[0]]
      const month = months.value[pickerValue[1]]
      const date = new Date(year, month, 0)
      return Array.from({ length: date.getDate() }, (_, i) => i + 1)
    }

    // 页面加载
    onLoad(async () => {
      await loadAvailableTasks()
      await loadTimePreferences()
    })

    // 加载待分配任务
    const loadAvailableTasks = async () => {
      try {
        const res = await tasksStore.getTaskList({ status: 'pending' })
        availableTasks.value = res.data?.items || []
      } catch (error) {
        console.error('加载任务失败:', error)
      }
    }

    // 加载时间偏好
    const loadTimePreferences = async () => {
      try {
        await timePreferencesStore.fetchPreferences()
        const prefs = timePreferencesStore.preferences
        preferredTime.value = `${prefs.preferred_task_start}-${prefs.preferred_task_end}`
        bufferTime.value = prefs.buffer_time_minutes || 10
      } catch (error) {
        console.error('加载时间偏好失败:', error)
      }
    }

    // 格式化日期
    const formatDate = (date) => {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
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

    // 判断是否选中
    const isSelected = (taskId) => {
      return selectedTasks.value.some(t => t.id === taskId)
    }

    // 切换任务选中状态
    const toggleTask = (task) => {
      const index = selectedTasks.value.findIndex(t => t.id === task.id)
      if (index > -1) {
        selectedTasks.value.splice(index, 1)
      } else {
        selectedTasks.value.push(task)
      }
    }

    // 全选
    const selectAll = () => {
      if (selectedTasks.value.length === availableTasks.value.length) {
        selectedTasks.value = []
      } else {
        selectedTasks.value = [...availableTasks.value]
      }
    }

    // 预览分配
    const previewAssignment = async () => {
      if (selectedTasks.value.length === 0) {
        uni.showToast({
          title: '请选择任务',
          icon: 'none'
        })
        return
      }

      uni.showLoading({ title: '预览中...' })

      try {
        const res = await timelineApi.smartAssignTasks({
          goal_id: selectedTasks.value[0].goal_id,
          task_ids: selectedTasks.value.map(t => t.id),
          date_range: {
            start_date: formatDate(startDate.value),
            end_date: formatDate(endDate.value)
          },
          preferences: {
            preferred_time: preferredTime.value,
            exclude_weekend: excludeWeekend.value,
            buffer_time_minutes: bufferTime.value
          }
        })

        assignments.value = res.data?.assignments || []
        hasPreview.value = true
      } catch (error) {
        console.error('预览失败:', error)
        uni.showToast({
          title: '预览失败',
          icon: 'none'
        })
      } finally {
        uni.hideLoading()
      }
    }

    // 确认分配
    const confirmAssignment = async () => {
      uni.showModal({
        title: '确认分配',
        content: `确定要为${selectedTasks.value.length}个任务分配时间吗?`,
        success: async (res) => {
          if (res.confirm) {
            uni.showLoading({ title: '分配中...' })

            try {
              // 执行实际的分配操作
              for (const assignment of assignments.value) {
                await tasksStore.updateTask(assignment.task_id, {
                  start_time: assignment.start_time,
                  end_time: assignment.end_time,
                  start_date: assignment.assigned_date,
                  end_date: assignment.assigned_date
                })
              }

              uni.showToast({
                title: '分配成功',
                icon: 'success'
              })

              setTimeout(() => {
                uni.navigateBack()
              }, 1500)
            } catch (error) {
              console.error('分配失败:', error)
              uni.showToast({
                title: '分配失败',
                icon: 'none'
              })
            } finally {
              uni.hideLoading()
            }
          }
        }
      })
    }

    // 日期选择器事件
    const onStartDateChange = (e) => {
      startPickerValue.value = e.detail.value
    }

    const onEndDateChange = (e) => {
      endPickerValue.value = e.detail.value
    }

    const confirmStartDate = () => {
      const year = years.value[startPickerValue.value[0]]
      const month = months.value[startPickerValue.value[1]]
      const day = days(startPickerValue.value)[startPickerValue.value[2]]
      startDate.value = new Date(year, month - 1, day)
      showStartDatePicker.value = false
    }

    const confirmEndDate = () => {
      const year = years.value[endPickerValue.value[0]]
      const month = months.value[endPickerValue.value[1]]
      const day = days(endPickerValue.value)[endPickerValue.value[2]]
      endDate.value = new Date(year, month - 1, day)
      showEndDatePicker.value = false
    }

    const toggleWorkDays = () => {
      excludeWeekend.value = !excludeWeekend.value
    }

    const onBufferTimeChange = (e) => {
      bufferTime.value = e.detail.value
    }

    // 返回
    const goBack = () => {
      uni.navigateBack()
    }

    return {
      startDate,
      endDate,
      preferredTime,
      excludeWeekend,
      bufferTime,
      availableTasks,
      selectedTasks,
      assignments,
      hasPreview,
      showStartDatePicker,
      showEndDatePicker,
      showTimeRangePicker,
      startPickerValue,
      endPickerValue,
      years,
      months,
      days,
      formatDate,
      getPriorityLabel,
      isSelected,
      toggleTask,
      selectAll,
      previewAssignment,
      confirmAssignment,
      onStartDateChange,
      onEndDateChange,
      confirmStartDate,
      confirmEndDate,
      toggleWorkDays,
      onBufferTimeChange,
      goBack
    }
  }
}
</script>

<style lang="scss" scoped>
.smart-assign-page {
  min-height: 100vh;
  background-color: #f5f5f5;
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
}

.back-btn {
  cursor: pointer;
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

.section {
  background-color: white;
  margin: 12px;
  padding: 16px;
  border-radius: 12px;
}

.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 500;
  color: #1f2937;
}

.select-all {
  font-size: 14px;
  color: #6366f1;
  cursor: pointer;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 12px;
}

.date-item {
  flex: 1;
  padding: 12px;
  background-color: #f9fafb;
  border-radius: 8px;
  text-align: center;

  .label {
    display: block;
    font-size: 12px;
    color: #9ca3af;
    margin-bottom: 4px;
  }

  .date-text {
    font-size: 14px;
    font-weight: 500;
    color: #1f2937;
  }
}

.separator {
  color: #9ca3af;
  font-size: 14px;
}

.preference-list {
  .preference-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid #f3f4f6;

    &:last-child {
      border-bottom: none;
    }

    .label {
      font-size: 14px;
      color: #374151;
    }

    .value {
      font-size: 14px;
      color: #6366f1;
    }

    .icon {
      color: #9ca3af;
      font-size: 18px;
    }

    .slider {
      width: 120px;
      height: 24px;
    }
  }
}

.task-list {
  .task-item {
    display: flex;
    align-items: center;
    padding: 12px;
    background-color: #f9fafb;
    border-radius: 8px;
    margin-bottom: 8px;

    &.selected {
      background-color: #eff6ff;
      border: 1px solid #6366f1;
    }
  }
}

.task-checkbox {
  width: 24px;
  height: 24px;
  border: 2px solid #d1d5db;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;

  .task-item.selected & {
    background-color: #6366f1;
    border-color: #6366f1;
  }
}

.checked-icon {
  color: white;
  font-size: 14px;
}

.task-info {
  flex: 1;
}

.task-title {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 4px;
}

.task-meta {
  font-size: 12px;
  color: #9ca3af;
}

.assignment-list {
  .assignment-item {
    position: relative;
    padding: 12px;
    background-color: #f9fafb;
    border-radius: 8px;
    margin-bottom: 8px;
  }
}

.assignment-date {
  display: block;
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 4px;
}

.assignment-time {
  font-size: 14px;
  font-weight: 500;
  color: #6366f1;
}

.assignment-task {
  font-size: 14px;
  color: #374151;
}

.conflict-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background-color: #fef3c7;
  color: #f59e0b;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
}

.bottom-actions {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  background-color: white;
  border-top: 1px solid #e5e7eb;
  position: sticky;
  bottom: 0;
}

.preview-btn,
.confirm-btn {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;

  &:disabled {
    opacity: 0.5;
  }
}

.preview-btn {
  background-color: #f9fafb;
  color: #374151;
  border: 1px solid #e5e7eb;
}

.confirm-btn {
  background-color: #6366f1;
  color: white;
}

.date-picker-popup {
  background-color: white;
  border-radius: 16px 16px 0 0;
  overflow: hidden;
}

.popup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.cancel-btn {
  font-size: 14px;
  color: #9ca3af;
}

.confirm-btn {
  font-size: 14px;
  color: #6366f1;
}

.popup-title {
  font-size: 16px;
  font-weight: 500;
}

.picker-view {
  height: 200px;
}
</style>
