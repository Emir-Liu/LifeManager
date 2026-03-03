<template>
  <view class="time-line">
    <!-- 时间轴容器 -->
    <scroll-view
      class="time-line-scroll"
      scroll-y
      :scroll-top="scrollTop"
      :scroll-into-view="scrollToId"
    >
      <!-- 时间刻度 -->
      <view class="time-scale">
        <view
          v-for="hour in hours"
          :key="hour"
          class="hour-mark"
          :class="{ 'current': isCurrentHour(hour) }"
        >
          <text class="hour-label">{{ formatHour(hour) }}</text>
          <view class="hour-line"></view>
        </view>
      </view>

      <!-- 任务容器 -->
      <view class="tasks-container">
        <!-- 当前时间线 -->
        <view
          v-if="currentTime"
          class="current-time-line"
          :style="{ top: getCurrentTimeTop() }"
        >
          <view class="time-indicator"></view>
        </view>

        <!-- 任务卡片 -->
        <view
          v-for="item in timeSlots"
          :key="item.id"
          class="task-card"
          :class="{
            'task': item.type === 'task',
            'event': item.type === 'event',
            'conflict': item.hasConflict,
            'dragging': draggingItem?.id === item.id
          }"
          :style="getTaskStyle(item)"
          @touchstart="handleTouchStart($event, item)"
          @touchmove="handleTouchMove($event)"
          @touchend="handleTouchEnd($event, item)"
          @click="handleClick(item)"
          @longpress="handleLongPress(item)"
        >
          <view class="task-header">
            <text class="task-type-icon">{{ getTaskIcon(item.type) }}</text>
            <text class="task-title">{{ item.title }}</text>
          </view>

          <view v-if="item.description" class="task-desc">
            <text>{{ item.description }}</text>
          </view>

          <view class="task-info">
            <text class="task-time">{{ formatTimeRange(item) }}</text>
            <text v-if="item.duration_minutes" class="task-duration">
              {{ item.duration_minutes }}分钟
            </text>
          </view>

          <!-- 冲突提示 -->
          <view v-if="item.hasConflict" class="conflict-badge">
            <text>⚠️ 冲突</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 空状态 -->
    <view v-if="timeSlots.length === 0" class="empty-state">
      <text class="empty-icon">📅</text>
      <text class="empty-text">今日暂无安排</text>
    </view>
  </view>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'

export default {
  name: 'TimeLine',

  props: {
    // 日期
    date: {
      type: Date,
      default: () => new Date()
    },
    // 时间段数据
    timeSlots: {
      type: Array,
      default: () => []
    },
    // 是否可编辑
    editable: {
      type: Boolean,
      default: true
    },
    // 是否显示时间刻度
    showScale: {
      type: Boolean,
      default: true
    }
  },

  emits: [
    'task-click',
    'task-drag',
    'task-edit',
    'task-delete'
  ],

  setup(props, { emit }) {
    const scrollTop = ref(0)
    const scrollToId = ref('')
    const currentTime = ref(new Date())

    // 拖拽状态
    const draggingItem = ref(null)
    const dragStartY = ref(0)
    const dragStartTime = ref(null)
    const isDragging = ref(false)

    // 小时列表 (0-23)
    const hours = computed(() => {
      return Array.from({ length: 24 }, (_, i) => i)
    })

    // 格式化小时
    const formatHour = (hour) => {
      return `${String(hour).padStart(2, '0')}:00`
    }

    // 判断是否是当前小时
    const isCurrentHour = (hour) => {
      const now = new Date()
      return now.getHours() === hour && props.date.toDateString() === now.toDateString()
    }

    // 获取当前时间线的位置
    const getCurrentTimeTop = () => {
      const now = currentTime.value
      const hours = now.getHours()
      const minutes = now.getMinutes()
      const top = (hours + minutes / 60) * 60 // 每小时60px高度
      return `${top}px`
    }

    // 格式化时间范围
    const formatTimeRange = (item) => {
      const start = new Date(item.start_time)
      const end = new Date(item.end_time)
      const startTime = `${String(start.getHours()).padStart(2, '0')}:${String(start.getMinutes()).padStart(2, '0')}`
      const endTime = `${String(end.getHours()).padStart(2, '0')}:${String(end.getMinutes()).padStart(2, '0')}`
      return `${startTime} - ${endTime}`
    }

    // 获取任务图标
    const getTaskIcon = (type) => {
      const icons = {
        task: '📋',
        event: '📅',
        learning: '📚',
        work: '💼',
        exercise: '🏃',
        rest: '😴'
      }
      return icons[type] || '📌'
    }

    // 获取任务样式
    const getTaskStyle = (item) => {
      const start = new Date(item.start_time)
      const end = new Date(item.end_time)

      const startHours = start.getHours() + start.getMinutes() / 60
      const endHours = end.getHours() + end.getMinutes() / 60

      const top = startHours * 60
      const height = (endHours - startHours) * 60

      return {
        top: `${top}px`,
        height: `${Math.max(height, 30)}px`, // 最小高度30px
        backgroundColor: getTaskColor(item.type, item.priority)
      }
    }

    // 获取任务颜色
    const getTaskColor = (type, priority) => {
      const colors = {
        task: '#3B82F6',
        event: '#10B981',
        learning: '#8B5CF6',
        work: '#F59E0B',
        exercise: '#EF4444',
        rest: '#6B7280'
      }

      // 根据优先级调整透明度
      let color = colors[type] || '#6366F1'
      if (priority === 'high') {
        color = color
      } else if (priority === 'medium') {
        color = color + 'CC'
      } else {
        color = color + '99'
      }

      return color
    }

    // 触摸开始
    const handleTouchStart = (e, item) => {
      if (!props.editable) return

      isDragging.value = false
      draggingItem.value = item
      dragStartY.value = e.touches[0].clientY
      dragStartTime.value = item.start_time
    }

    // 触摸移动
    const handleTouchMove = (e) => {
      if (!props.editable || !draggingItem.value) return

      const deltaY = e.touches[0].clientY - dragStartY.value

      // 阈值判断,避免误触
      if (Math.abs(deltaY) > 10) {
        isDragging.value = true
      }

      if (isDragging.value) {
        // 计算新的时间
        const deltaMinutes = deltaY / 60 * 60 // 每像素对应1分钟
        const startTime = new Date(dragStartTime.value)
        startTime.setMinutes(startTime.getMinutes() + deltaMinutes)

        // 触发拖拽事件
        emit('task-drag', {
          item: draggingItem.value,
          newStartTime: startTime.toISOString()
        })
      }
    }

    // 触摸结束
    const handleTouchEnd = (e, item) => {
      if (isDragging.value && draggingItem.value) {
        // 触发拖拽完成事件
        emit('task-drag', {
          item: draggingItem.value,
          confirmed: true
        })
      }

      draggingItem.value = null
      dragStartY.value = 0
      dragStartTime.value = null
      isDragging.value = false
    }

    // 点击任务
    const handleClick = (item) => {
      if (isDragging.value) return
      emit('task-click', item)
    }

    // 长按任务
    const handleLongPress = (item) => {
      if (!props.editable) return

      uni.showActionSheet({
        itemList: ['编辑', '删除'],
        success: (res) => {
          if (res.tapIndex === 0) {
            emit('task-edit', item)
          } else if (res.tapIndex === 1) {
            emit('task-delete', item)
          }
        }
      })
    }

    // 更新当前时间
    let timeInterval = null
    onMounted(() => {
      timeInterval = setInterval(() => {
        currentTime.value = new Date()
      }, 60000) // 每分钟更新一次

      // 滚动到当前时间附近
      const now = new Date()
      const hours = now.getHours() - 2
      if (hours > 0) {
        scrollTop.value = hours * 60
      }
    })

    onUnmounted(() => {
      if (timeInterval) {
        clearInterval(timeInterval)
      }
    })

    return {
      scrollTop,
      scrollToId,
      currentTime,
      hours,
      formatHour,
      isCurrentHour,
      getCurrentTimeTop,
      formatTimeRange,
      getTaskIcon,
      getTaskStyle,
      handleTouchStart,
      handleTouchMove,
      handleTouchEnd,
      handleClick,
      handleLongPress,
      draggingItem
    }
  }
}
</script>

<style lang="scss" scoped>
.time-line {
  position: relative;
  height: 100%;
  overflow: hidden;
}

.time-line-scroll {
  height: 100%;
  position: relative;
}

.time-scale {
  position: absolute;
  left: 0;
  top: 0;
  width: 60px;
  height: 1440px; // 24小时 * 60px/小时
  background-color: #f9fafb;
  border-right: 1px solid #e5e7eb;
}

.hour-mark {
  height: 60px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;

  &.current {
    background-color: #fef3c7;
  }
}

.hour-label {
  font-size: 12px;
  color: #9ca3af;
}

.hour-line {
  position: absolute;
  right: 0;
  width: 8px;
  height: 1px;
  background-color: #e5e7eb;
}

.tasks-container {
  margin-left: 60px;
  position: relative;
  height: 1440px;
  min-height: 100%;
}

.current-time-line {
  position: absolute;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #f59e0b;
  z-index: 10;
  pointer-events: none;

  .time-indicator {
    position: absolute;
    left: -6px;
    top: -5px;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: #f59e0b;
    box-shadow: 0 0 4px rgba(245, 158, 11, 0.5);
  }
}

.task-card {
  position: absolute;
  left: 8px;
  right: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  background-color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.1s;

  &:active {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }

  &.dragging {
    opacity: 0.8;
    transform: scale(1.02);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    z-index: 100;
  }

  &.conflict {
    border: 2px solid #ef4444;
  }
}

.task-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.task-type-icon {
  font-size: 14px;
}

.task-title {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-desc {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.task-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-time {
  font-size: 11px;
  color: #9ca3af;
}

.task-duration {
  font-size: 11px;
  color: #9ca3af;
  background-color: rgba(0, 0, 0, 0.05);
  padding: 2px 6px;
  border-radius: 3px;
}

.conflict-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background-color: #ef4444;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 8px;
  white-space: nowrap;
}

.empty-state {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
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
</style>
