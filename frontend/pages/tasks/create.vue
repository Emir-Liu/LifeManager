<template>
  <view class="task-create-page">
    <!-- 顶部导航 -->
    <view class="header">
      <view class="nav-bar">
        <view class="back-btn" @click="goBack">
          <text class="icon">←</text>
        </view>
        <text class="title">创建任务</text>
        <text class="save-btn" @click="saveTask">保存</text>
      </view>
    </view>

    <!-- 表单 -->
    <scroll-view class="form-container" scroll-y>
      <!-- 基本信息 -->
      <view class="section">
        <view class="section-title">基本信息</view>

        <view class="form-item">
          <text class="label">任务标题 *</text>
          <input
            v-model="form.title"
            class="input"
            placeholder="请输入任务标题"
            :maxlength="50"
          />
        </view>

        <view class="form-item">
          <text class="label">任务描述</text>
          <textarea
            v-model="form.description"
            class="textarea"
            placeholder="请输入任务描述"
            :maxlength="200"
            :auto-height="true"
          />
        </view>

        <view class="form-item" @click="showGoalPicker = true">
          <text class="label">关联目标</text>
          <view class="picker-value">
            <text v-if="selectedGoal">{{ selectedGoal.title }}</text>
            <text v-else class="placeholder">请选择目标</text>
            <text class="icon">›</text>
          </view>
        </view>
      </view>

      <!-- 时间安排 -->
      <view class="section">
        <view class="section-title">时间安排</view>

        <view class="form-item" @click="showDatePicker = true">
          <text class="label">截止日期 *</text>
          <view class="picker-value">
            <text>{{ form.due_date || '请选择日期' }}</text>
            <text class="icon">›</text>
          </view>
        </view>

        <view class="form-item" @click="showStartTimePicker = true">
          <text class="label">开始时间</text>
          <view class="picker-value">
            <text>{{ form.start_time || '请选择' }}</text>
            <text class="icon">›</text>
          </view>
        </view>

        <view class="form-item" @click="showEndTimePicker = true">
          <text class="label">结束时间</text>
          <view class="picker-value">
            <text>{{ form.end_time || '请选择' }}</text>
            <text class="icon">›</text>
          </view>
        </view>

        <view class="form-item">
          <text class="label">预估工时 (小时)</text>
          <slider
            class="slider"
            :value="form.estimated_hours * 10"
            min="1"
            max="80"
            @change="onEstimatedHoursChange"
          />
          <text class="slider-value">{{ form.estimated_hours }}小时</text>
        </view>
      </view>

      <!-- 任务属性 -->
      <view class="section">
        <view class="section-title">任务属性</view>

        <view class="form-item">
          <text class="label">任务类型</text>
          <picker
            :range="taskTypes"
            :value="taskTypeIndex"
            @change="onTaskTypeChange"
          >
            <view class="picker-value">
              <text>{{ taskTypes[taskTypeIndex] }}</text>
              <text class="icon">›</text>
            </view>
          </picker>
        </view>

        <view class="form-item">
          <text class="label">优先级</text>
          <picker
            :range="priorities"
            :value="priorityIndex"
            @change="onPriorityChange"
          >
            <view class="picker-value">
              <text>{{ priorities[priorityIndex] }}</text>
              <text class="icon">›</text>
            </view>
          </picker>
        </view>

        <view class="form-item switch-item">
          <text class="label">启用提醒</text>
          <switch :checked="form.reminder_enabled" @change="onReminderChange" />
        </view>

        <view v-if="form.reminder_enabled" class="form-item">
          <text class="label">提前提醒 (分钟)</text>
          <picker
            :range="reminderOptions"
            :value="reminderIndex"
            @change="onReminderOptionChange"
          >
            <view class="picker-value">
              <text>{{ reminderOptions[reminderIndex] }}分钟</text>
              <text class="icon">›</text>
            </view>
          </picker>
        </view>
      </view>
    </scroll-view>

    <!-- 目标选择弹窗 -->
    <uni-popup ref="goalPicker" type="bottom" @maskClick="showGoalPicker = false">
      <view class="picker-popup">
        <view class="popup-header">
          <text class="cancel-btn" @click="showGoalPicker = false">取消</text>
          <text class="popup-title">选择目标</text>
          <text class="confirm-btn" @click="confirmGoal">确定</text>
        </view>
        <scroll-view class="picker-content" scroll-y>
          <view
            v-for="goal in goals"
            :key="goal.id"
            class="picker-item"
            :class="{ 'selected': tempGoal?.id === goal.id }"
            @click="selectGoal(goal)"
          >
            <text>{{ goal.title }}</text>
          </view>
        </scroll-view>
      </view>
    </uni-popup>

    <!-- 日期选择弹窗 -->
    <uni-popup ref="datePicker" type="bottom" @maskClick="showDatePicker = false">
      <view class="date-picker-popup">
        <view class="popup-header">
          <text class="cancel-btn" @click="showDatePicker = false">取消</text>
          <text class="popup-title">选择日期</text>
          <text class="confirm-btn" @click="confirmDate">确定</text>
        </view>
        <picker-view class="picker-view" :value="datePickerValue" @change="onDatePickerChange">
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
            <view v-for="day in days(datePickerValue)" :key="day">
              <text>{{ day }}日</text>
            </view>
          </picker-view-column>
        </picker-view>
      </view>
    </uni-popup>
  </view>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useTasksStore } from '@/store/tasks.js'
import { useGoalsStore } from '@/store/goals.js'

export default {
  setup() {
    const tasksStore = useTasksStore()
    const goalsStore = useGoalsStore()

    const loading = ref(false)

    const form = reactive({
      title: '',
      description: '',
      goal_id: null,
      due_date: '',
      start_time: '',
      end_time: '',
      estimated_hours: 1,
      task_type: 'work',
      priority: 'medium',
      reminder_enabled: true,
      reminder_minutes_before: 30
    })

    const taskTypes = ['工作', '学习', '运动', '娱乐', '其他']
    const priorities = ['低', '中', '高']
    const reminderOptions = [0, 5, 10, 15, 30, 60, 120]

    const taskTypeIndex = ref(1)
    const priorityIndex = ref(1)
    const reminderIndex = ref(4)

    const goals = ref([])
    const selectedGoal = ref(null)
    const tempGoal = ref(null)

    // 弹窗状态
    const showGoalPicker = ref(false)
    const showDatePicker = ref(false)
    const showStartTimePicker = ref(false)
    const showEndTimePicker = ref(false)

    const datePickerValue = ref([0, 0, 0])
    const startTimePickerValue = ref([9, 0])
    const endTimePickerValue = ref([10, 0])

    // 年月数据
    const currentYear = new Date().getFullYear()
    const years = computed(() =>
      Array.from({ length: 20 }, (_, i) => currentYear - 10 + i)
    )
    const months = computed(() => Array.from({ length: 12 }, (_, i) => i + 1))
    const days = (pickerValue) => {
      const year = years.value[pickerValue[0]]
      const month = months.value[pickerValue[1]]
      const date = new Date(year, month, 0)
      return Array.from({ length: date.getDate() }, (_, i) => i + 1)
    }

    // 页面加载
    onLoad(async (options) => {
      if (options.date) {
        form.due_date = options.date
      }
      await loadGoals()
    })

    // 加载目标列表
    const loadGoals = async () => {
      try {
        const res = await goalsStore.getGoals()
        goals.value = res.data?.items || []
      } catch (error) {
        console.error('加载目标失败:', error)
      }
    }

    // 选择目标
    const selectGoal = (goal) => {
      tempGoal.value = goal
    }

    const confirmGoal = () => {
      selectedGoal.value = tempGoal.value
      form.goal_id = tempGoal.value?.id
      showGoalPicker.value = false
    }

    // 日期选择
    const onDatePickerChange = (e) => {
      datePickerValue.value = e.detail.value
    }

    const confirmDate = () => {
      const year = years.value[datePickerValue.value[0]]
      const month = months.value[datePickerValue.value[1]]
      const day = days(datePickerValue.value)[datePickerValue.value[2]]
      form.due_date = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
      showDatePicker.value = false
    }

    // 时间选择
    const onStartTimePickerChange = (e) => {
      startTimePickerValue.value = e.detail.value
    }

    const onEndTimePickerChange = (e) => {
      endTimePickerValue.value = e.detail.value
    }

    const confirmStartTime = () => {
      const hour = startTimePickerValue.value[0]
      const minute = startTimePickerValue.value[1]
      form.start_time = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
      showStartTimePicker.value = false
    }

    const confirmEndTime = () => {
      const hour = endTimePickerValue.value[0]
      const minute = endTimePickerValue.value[1]
      form.end_time = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
      showEndTimePicker.value = false
    }

    // 表单事件
    const onTaskTypeChange = (e) => {
      taskTypeIndex.value = e.detail.value
      const typeMap = ['work', 'learning', 'exercise', 'entertainment', 'other']
      form.task_type = typeMap[e.detail.value]
    }

    const onPriorityChange = (e) => {
      priorityIndex.value = e.detail.value
      const priorityMap = ['low', 'medium', 'high']
      form.priority = priorityMap[e.detail.value]
    }

    const onReminderChange = (e) => {
      form.reminder_enabled = e.detail.value
    }

    const onReminderOptionChange = (e) => {
      reminderIndex.value = e.detail.value
      form.reminder_minutes_before = reminderOptions[e.detail.value]
    }

    const onEstimatedHoursChange = (e) => {
      form.estimated_hours = e.detail.value / 10
    }

    // 保存任务
    const saveTask = async () => {
      if (!form.title) {
        uni.showToast({
          title: '请输入任务标题',
          icon: 'none'
        })
        return
      }

      if (!form.due_date) {
        uni.showToast({
          title: '请选择截止日期',
          icon: 'none'
        })
        return
      }

      loading.value = true

      try {
        await tasksStore.createTask(form)
        uni.showToast({
          title: '创建成功',
          icon: 'success'
        })

        setTimeout(() => {
          uni.navigateBack()
        }, 1500)
      } catch (error) {
        console.error('创建任务失败:', error)
        uni.showToast({
          title: '创建失败',
          icon: 'none'
        })
      } finally {
        loading.value = false
      }
    }

    // 返回
    const goBack = () => {
      uni.navigateBack()
    }

    return {
      loading,
      form,
      taskTypes,
      priorities,
      reminderOptions,
      taskTypeIndex,
      priorityIndex,
      reminderIndex,
      goals,
      selectedGoal,
      tempGoal,
      showGoalPicker,
      showDatePicker,
      showStartTimePicker,
      showEndTimePicker,
      datePickerValue,
      startTimePickerValue,
      endTimePickerValue,
      years,
      months,
      days,
      selectGoal,
      confirmGoal,
      onDatePickerChange,
      confirmDate,
      onStartTimePickerChange,
      onEndTimePickerChange,
      confirmStartTime,
      confirmEndTime,
      onTaskTypeChange,
      onPriorityChange,
      onReminderChange,
      onReminderOptionChange,
      onEstimatedHoursChange,
      saveTask,
      goBack
    }
  }
}
</script>

<style lang="scss" scoped>
.task-create-page {
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

.back-btn, .save-btn {
  padding: 8px;
  font-size: 14px;
}

.save-btn {
  margin-left: auto;
}

.title {
  flex: 1;
  text-align: center;
  font-size: 16px;
  font-weight: 500;
}

.form-container {
  padding: 12px;
  padding-bottom: 80px;
}

.section {
  background-color: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 16px;
}

.form-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f3f4f6;

  &:last-child {
    border-bottom: none;
  }

  &.switch-item {
    justify-content: flex-start;
    gap: 12px;
  }
}

.label {
  font-size: 14px;
  color: #374151;
  min-width: 80px;
}

.input,
.textarea {
  flex: 1;
  padding: 8px 12px;
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 14px;
}

.textarea {
  min-height: 80px;
  max-height: 200px;
}

.picker-value {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
  font-size: 14px;
  color: #6366f1;

  .placeholder {
    color: #9ca3af;
  }

  .icon {
    color: #9ca3af;
    font-size: 18px;
  }
}

.slider {
  flex: 1;
  margin: 0 12px;
}

.slider-value {
  font-size: 14px;
  color: #6366f1;
  min-width: 60px;
  text-align: right;
}

.picker-popup,
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

.cancel-btn,
.confirm-btn {
  padding: 8px 16px;
  font-size: 14px;
}

.cancel-btn {
  color: #9ca3af;
}

.confirm-btn {
  color: #6366f1;
}

.popup-title {
  font-size: 16px;
  font-weight: 500;
}

.picker-content {
  max-height: 400px;
}

.picker-item {
  padding: 16px;
  border-bottom: 1px solid #f3f4f6;

  &.selected {
    background-color: #eff6ff;
    color: #6366f1;
  }
}

.picker-view {
  height: 200px;
}
</style>
