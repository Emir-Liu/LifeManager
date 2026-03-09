<template>
  <view class="calendar">
    <!-- 头部：月份选择 -->
    <view class="calendar-header">
      <button class="nav-btn" @click="prevMonth">
        <text class="icon">‹</text>
      </button>
      <text class="current-month">{{ formatMonth(currentDate) }}</text>
      <button class="nav-btn" @click="nextMonth">
        <text class="icon">›</text>
      </button>
    </view>

    <!-- 星期标题 -->
    <view class="week-header">
      <view
        v-for="weekDay in weekDays"
        :key="weekDay"
        class="week-day"
        :class="{ 'weekend': [0, 6].includes(weekDay.index) }"
      >
        <text>{{ weekDay.label }}</text>
      </view>
    </view>

    <!-- 日期网格 -->
    <view class="calendar-grid">
      <view
        v-for="day in calendarDays"
        :key="day.key"
        class="day-cell"
        :class="{
          'other-month': day.isOtherMonth,
          'today': day.isToday,
          'selected': isSelected(day),
          'has-tasks': day.taskCount > 0
        }"
        @click="selectDate(day)"
      >
        <text class="day-number">{{ day.day }}</text>

        <!-- 任务数量徽章 -->
        <view v-if="day.taskCount > 0" class="task-badge">
          <text class="badge-text">{{ day.taskCount > 99 ? '99+' : day.taskCount }}</text>
        </view>

        <!-- 小圆点标记(多个任务时显示) -->
        <view v-if="day.taskCount > 0 && day.taskCount <= 3" class="task-dots">
          <view
            v-for="i in Math.min(day.taskCount, 3)"
            :key="i"
            class="dot"
          ></view>
        </view>
      </view>
    </view>

    <!-- 今日按钮 -->
    <button class="today-btn" @click="goToToday">
      <text>今天</text>
    </button>
  </view>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'Calendar',

  props: {
    // 当前选中的日期
    modelValue: {
      type: Date,
      default: () => new Date()
    },
    // 按日期分组的任务数据 { '2026-03-01': 5, ... }
    tasksByDate: {
      type: Object,
      default: () => ({})
    },
    // 最小可选日期
    minDate: {
      type: Date,
      default: null
    },
    // 最大可选日期
    maxDate: {
      type: Date,
      default: null
    }
  },

  emits: ['update:modelValue', 'date-select', 'month-change'],

  setup(props, { emit }) {
    const currentDate = ref(new Date(props.modelValue))

    // 星期标题
    const weekDays = [
      { label: '日', index: 0 },
      { label: '一', index: 1 },
      { label: '二', index: 2 },
      { label: '三', index: 3 },
      { label: '四', index: 4 },
      { label: '五', index: 5 },
      { label: '六', index: 6 }
    ]

    // 计算日历天数
    const calendarDays = computed(() => {
      const year = currentDate.value.getFullYear()
      const month = currentDate.value.getMonth()

      // 当月第一天
      const firstDay = new Date(year, month, 1)
      // 当月最后一天
      const lastDay = new Date(year, month + 1, 0)
      // 上月最后一天
      const prevLastDay = new Date(year, month, 0)

      const days = []

      // 填充上月的日期
      const startDayOfWeek = firstDay.getDay()
      for (let i = startDayOfWeek - 1; i >= 0; i--) {
        const day = prevLastDay.getDate() - i
        const date = new Date(year, month - 1, day)
        days.push({
          key: `prev-${day}`,
          day,
          date,
          isOtherMonth: true,
          isToday: isSameDay(date, new Date()),
          taskCount: getTaskCount(date)
        })
      }

      // 填充当月的日期
      for (let i = 1; i <= lastDay.getDate(); i++) {
        const date = new Date(year, month, i)
        days.push({
          key: `current-${i}`,
          day: i,
          date,
          isOtherMonth: false,
          isToday: isSameDay(date, new Date()),
          taskCount: getTaskCount(date)
        })
      }

      // 填充下月的日期
      const remainingDays = 42 - days.length // 6行 x 7列 = 42
      for (let i = 1; i <= remainingDays; i++) {
        const date = new Date(year, month + 1, i)
        days.push({
          key: `next-${i}`,
          day: i,
          date,
          isOtherMonth: true,
          isToday: isSameDay(date, new Date()),
          taskCount: getTaskCount(date)
        })
      }

      return days
    })

    // 判断是否是同一天
    const isSameDay = (date1, date2) => {
      return date1.getFullYear() === date2.getFullYear() &&
             date1.getMonth() === date2.getMonth() &&
             date1.getDate() === date2.getDate()
    }

    // 获取日期的任务数量
    const getTaskCount = (date) => {
      const dateStr = formatDateKey(date)
      return props.tasksByDate[dateStr] || 0
    }

    // 格式化日期为 key
    const formatDateKey = (date) => {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }

    // 格式化月份
    const formatMonth = (date) => {
      const year = date.getFullYear()
      const month = date.getMonth() + 1
      return `${year}年${month}月`
    }

    // 判断日期是否选中
    const isSelected = (day) => {
      return isSameDay(day.date, props.modelValue)
    }

    // 选择日期
    const selectDate = (day) => {
      emit('update:modelValue', day.date)
      emit('date-select', day.date)
    }

    // 上一个月
    const prevMonth = () => {
      const newDate = new Date(currentDate.value)
      newDate.setMonth(newDate.getMonth() - 1)
      currentDate.value = newDate
      emit('month-change', newDate)
    }

    // 下一个月
    const nextMonth = () => {
      const newDate = new Date(currentDate.value)
      newDate.setMonth(newDate.getMonth() + 1)
      currentDate.value = newDate
      emit('month-change', newDate)
    }

    // 回到今天
    const goToToday = () => {
      const today = new Date()
      currentDate.value = today
      selectDate({ date: today })
    }

    // 监听外部传入的日期变化
    watch(() => props.modelValue, (newVal) => {
      if (newVal) {
        currentDate.value = new Date(newVal)
      }
    })

    return {
      currentDate,
      weekDays,
      calendarDays,
      formatMonth,
      isSelected,
      selectDate,
      prevMonth,
      nextMonth,
      goToToday
    }
  }
}
</script>

<style lang="scss" scoped>
.calendar {
  background-color: white;
  border-radius: 12px;
  overflow: hidden;
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #f3f4f6;
}

.nav-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f9fafb;
  border: none;
  border-radius: 6px;
  cursor: pointer;

  &:active {
    background-color: #e5e7eb;
  }

  .icon {
    font-size: 18px;
    color: #6b7280;
  }
}

.current-month {
  font-size: 16px;
  font-weight: 500;
  color: #1f2937;
}

.week-header {
  display: flex;
  padding: 12px 16px;
  background-color: #fafafa;
  border-bottom: 1px solid #f3f4f6;
}

.week-day {
  flex: 1;
  text-align: center;
  font-size: 12px;
  color: #9ca3af;

  &.weekend {
    color: #ef4444;
  }
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
  padding: 8px;
}

.day-cell {
  position: relative;
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;

  &.other-month {
    .day-number {
      color: #d1d5db;
    }
  }

  &.today {
    background-color: #fef3c7;

    .day-number {
      color: #f59e0b;
      font-weight: 600;
    }
  }

  &.selected {
    background-color: #6366f1;

    .day-number {
      color: white;
    }

    .badge-text {
      color: white;
    }
  }

  &.has-tasks:not(.selected) {
    background-color: #f3f4f6;
  }

  &:active:not(.selected):not(.other-month) {
    background-color: #e5e7eb;
  }
}

.day-number {
  font-size: 14px;
  color: #374151;
  margin-bottom: 2px;
}

.task-badge {
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  background-color: #6366f1;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;

  .badge-text {
    font-size: 10px;
    color: white;
    line-height: 1;
  }
}

.task-dots {
  display: flex;
  gap: 2px;
  margin-top: 2px;

  .dot {
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background-color: #6366f1;
  }
}

.today-btn {
  width: 100%;
  padding: 12px;
  background-color: #f9fafb;
  color: #6366f1;
  border: none;
  border-top: 1px solid #f3f4f6;
  font-size: 14px;
  font-weight: 500;

  &:active {
    background-color: #e5e7eb;
  }
}
</style>
