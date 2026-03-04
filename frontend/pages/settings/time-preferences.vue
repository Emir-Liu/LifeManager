<template>
  <view class="time-preferences-page">
    <!-- 顶部导航 -->
    <view class="header">
      <view class="nav-bar">
        <view class="back-btn" @click="goBack">
          <text class="icon">←</text>
        </view>
        <text class="title">时间偏好设置</text>
        <view class="placeholder"></view>
      </view>
    </view>

    <!-- 睡眠习惯 -->
    <view class="section">
      <view class="section-title">
        <text class="section-icon">😴</text>
        <text>睡眠习惯</text>
      </view>
      <view class="form-item">
        <text class="label">起床时间</text>
        <picker
          mode="time"
          :value="preferences.wake_up_time"
          @change="onWakeUpTimeChange"
        >
          <view class="picker-value">
            <text>{{ preferences.wake_up_time }}</text>
            <text class="icon">›</text>
          </view>
        </picker>
      </view>
      <view class="form-item">
        <text class="label">睡觉时间</text>
        <picker
          mode="time"
          :value="preferences.sleep_time"
          @change="onSleepTimeChange"
        >
          <view class="picker-value">
            <text>{{ preferences.sleep_time }}</text>
            <text class="icon">›</text>
          </view>
        </picker>
      </view>
    </view>

    <!-- 工作时间 -->
    <view class="section">
      <view class="section-title">
        <text class="section-icon">💼</text>
        <text>工作时间</text>
      </view>
      <view class="form-item">
        <text class="label">工作日</text>
        <view class="work-days">
          <view
            v-for="(day, index) in weekDays"
            :key="index"
            class="day-item"
            :class="{ 'selected': isSelectedDay(index) }"
            @click="toggleDay(index)"
          >
            <text>{{ day }}</text>
          </view>
        </view>
      </view>
      <view class="form-item">
        <text class="label">工作开始</text>
        <picker
          mode="time"
          :value="preferences.work_start"
          @change="onWorkStartChange"
        >
          <view class="picker-value">
            <text>{{ preferences.work_start }}</text>
            <text class="icon">›</text>
          </view>
        </picker>
      </view>
      <view class="form-item">
        <text class="label">工作结束</text>
        <picker
          mode="time"
          :value="preferences.work_end"
          @change="onWorkEndChange"
        >
          <view class="picker-value">
            <text>{{ preferences.work_end }}</text>
            <text class="icon">›</text>
          </view>
        </picker>
      </view>
    </view>

    <!-- 午休时间 -->
    <view class="section">
      <view class="section-title">
        <text class="section-icon">🍽️</text>
        <text>午休时间</text>
      </view>
      <view class="form-item">
        <text class="label">午休开始</text>
        <picker
          mode="time"
          :value="preferences.lunch_start"
          @change="onLunchStartChange"
        >
          <view class="picker-value">
            <text>{{ preferences.lunch_start }}</text>
            <text class="icon">›</text>
          </view>
        </picker>
      </view>
      <view class="form-item">
        <text class="label">午休结束</text>
        <picker
          mode="time"
          :value="preferences.lunch_end"
          @change="onLunchEndChange"
        >
          <view class="picker-value">
            <text>{{ preferences.lunch_end }}</text>
            <text class="icon">›</text>
          </view>
        </picker>
      </view>
    </view>

    <!-- 任务偏好 -->
    <view class="section">
      <view class="section-title">
        <text class="section-icon">📋</text>
        <text>任务偏好</text>
      </view>
      <view class="form-item">
        <text class="label">首选任务时间段</text>
        <view class="time-range-input">
          <picker mode="time" :value="preferredTaskStart" @change="onPreferredTaskStartChange">
            <view class="time-input">
              <text>{{ preferredTaskStart }}</text>
            </view>
          </picker>
          <text class="separator">至</text>
          <picker mode="time" :value="preferredTaskEnd" @change="onPreferredTaskEndChange">
            <view class="time-input">
              <text>{{ preferredTaskEnd }}</text>
            </view>
          </picker>
        </view>
      </view>
      <view class="form-item">
        <text class="label">任务间缓冲时间 (分钟)</text>
        <slider
          class="slider"
          :value="preferences.buffer_time_minutes"
          min="0"
          max="30"
          step="5"
          @change="onBufferTimeChange"
        />
        <text class="slider-value">{{ preferences.buffer_time_minutes }}分钟</text>
      </view>
    </view>

    <!-- 保存按钮 -->
    <view class="save-section">
      <button class="save-btn" :disabled="loading" @click="savePreferences">
        <text v-if="!loading">保存设置</text>
        <text v-else>保存中...</text>
      </button>
      <button class="reset-btn" @click="resetPreferences">
        <text>恢复默认</text>
      </button>
    </view>

    <!-- 提示信息 -->
    <view class="tips-section">
      <text class="tips-title">💡 提示</text>
      <text class="tips-content">合理设置时间偏好可以帮助AI更准确地为您安排任务时间。</text>
    </view>
  </view>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useTimePreferencesStore } from '@/store/timePreferences.js'

export default {
  setup() {
    const timePreferencesStore = useTimePreferencesStore()

    const loading = ref(false)
    const preferences = reactive({
      sleep_type: 'normal',
      wake_up_time: '07:00',
      sleep_time: '23:00',
      lunch_start: '12:00',
      lunch_end: '13:30',
      work_start: '09:00',
      work_end: '18:00',
      work_days: '0,1,2,3,4',
      preferred_task_start: '09:00',
      preferred_task_end: '18:00',
      buffer_time_minutes: 10
    })

    const weekDays = ['日', '一', '二', '三', '四', '五', '六']

    const preferredTaskStart = ref('09:00')
    const preferredTaskEnd = ref('18:00')

    // 页面加载
    onLoad(async () => {
      await loadPreferences()
    })

    // 加载偏好设置
    const loadPreferences = async () => {
      try {
        await timePreferencesStore.fetchPreferences()
        Object.assign(preferences, timePreferencesStore.preferences)
        preferredTaskStart.value = preferences.preferred_task_start
        preferredTaskEnd.value = preferences.preferred_task_end
      } catch (error) {
        console.error('加载偏好设置失败:', error)
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      }
    }

    // 判断工作日是否选中
    const isSelectedDay = (index) => {
      const days = preferences.work_days.split(',').map(Number)
      return days.includes(index)
    }

    // 切换工作日
    const toggleDay = (index) => {
      const days = preferences.work_days.split(',').map(Number)
      const idx = days.indexOf(index)

      if (idx > -1) {
        days.splice(idx, 1)
      } else {
        days.push(index)
      }

      days.sort((a, b) => a - b)
      preferences.work_days = days.join(',')
    }

    // 时间选择器事件
    const onWakeUpTimeChange = (e) => {
      preferences.wake_up_time = e.detail.value
    }

    const onSleepTimeChange = (e) => {
      preferences.sleep_time = e.detail.value
    }

    const onWorkStartChange = (e) => {
      preferences.work_start = e.detail.value
    }

    const onWorkEndChange = (e) => {
      preferences.work_end = e.detail.value
    }

    const onLunchStartChange = (e) => {
      preferences.lunch_start = e.detail.value
    }

    const onLunchEndChange = (e) => {
      preferences.lunch_end = e.detail.value
    }

    const onPreferredTaskStartChange = (e) => {
      preferredTaskStart.value = e.detail.value
      preferences.preferred_task_start = e.detail.value
    }

    const onPreferredTaskEndChange = (e) => {
      preferredTaskEnd.value = e.detail.value
      preferences.preferred_task_end = e.detail.value
    }

    const onBufferTimeChange = (e) => {
      preferences.buffer_time_minutes = e.detail.value
    }

    // 保存设置
    const savePreferences = async () => {
      // 验证
      if (preferences.work_days === '') {
        uni.showToast({
          title: '请至少选择一个工作日',
          icon: 'none'
        })
        return
      }

      loading.value = true

      try {
        await timePreferencesStore.updatePreferences(preferences)
        uni.showToast({
          title: '保存成功',
          icon: 'success'
        })
      } catch (error) {
        console.error('保存失败:', error)
        uni.showToast({
          title: '保存失败',
          icon: 'none'
        })
      } finally {
        loading.value = false
      }
    }

    // 恢复默认
    const resetPreferences = () => {
      uni.showModal({
        title: '确认重置',
        content: '确定要恢复默认设置吗？',
        success: (res) => {
          if (res.confirm) {
            timePreferencesStore.resetPreferences()
            Object.assign(preferences, timePreferencesStore.preferences)
            preferredTaskStart.value = preferences.preferred_task_start
            preferredTaskEnd.value = preferences.preferred_task_end

            uni.showToast({
              title: '已恢复默认',
              icon: 'success'
            })
          }
        }
      })
    }

    // 返回
    const goBack = () => {
      uni.navigateBack()
    }

    return {
      loading,
      preferences,
      weekDays,
      preferredTaskStart,
      preferredTaskEnd,
      isSelectedDay,
      toggleDay,
      onWakeUpTimeChange,
      onSleepTimeChange,
      onWorkStartChange,
      onWorkEndChange,
      onLunchStartChange,
      onLunchEndChange,
      onPreferredTaskStartChange,
      onPreferredTaskEndChange,
      onBufferTimeChange,
      savePreferences,
      resetPreferences,
      goBack
    }
  }
}
</script>

<style lang="scss" scoped>
.time-preferences-page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 20px;
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
  gap: 8px;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 500;
  color: #1f2937;
}

.section-icon {
  font-size: 18px;
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
}

.label {
  font-size: 14px;
  color: #374151;
}

.picker-value {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #6366f1;
}

.work-days {
  display: flex;
  gap: 8px;
}

.day-item {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: #f3f4f6;
  color: #9ca3af;
  font-size: 12px;
  cursor: pointer;

  &.selected {
    background-color: #6366f1;
    color: white;
  }
}

.time-range-input {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-input {
  padding: 6px 12px;
  background-color: #f9fafb;
  border-radius: 6px;
  font-size: 14px;
  color: #374151;
}

.separator {
  color: #9ca3af;
  font-size: 14px;
}

.slider {
  flex: 1;
  margin-right: 12px;
}

.slider-value {
  font-size: 14px;
  color: #6366f1;
  min-width: 60px;
  text-align: right;
}

.save-section {
  display: flex;
  gap: 12px;
  padding: 0 12px;
  margin: 16px 0;
}

.save-btn,
.reset-btn {
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

.save-btn {
  background-color: #6366f1;
  color: white;
}

.reset-btn {
  background-color: #f9fafb;
  color: #374151;
  border: 1px solid #e5e7eb;
}

.tips-section {
  margin: 12px;
  padding: 12px;
  background-color: #fef3c7;
  border-radius: 8px;
  border-left: 3px solid #f59e0b;
}

.tips-title {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #92400e;
  margin-bottom: 4px;
}

.tips-content {
  font-size: 12px;
  color: #b45309;
  line-height: 1.5;
}
</style>
