import { defineStore } from 'pinia'
import timePreferencesApi from '@/api/timePreferences.js'
import { ref } from 'vue'

export const useTimePreferencesStore = defineStore('timePreferences', () => {
  // State
  const preferences = ref({
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

  const loading = ref(false)

  // Actions
  // 获取时间偏好
  const fetchPreferences = async () => {
    loading.value = true
    try {
      const res = await timePreferencesApi.getTimePreferences()
      preferences.value = res.data || preferences.value
      return res
    } catch (error) {
      console.error('获取时间偏好失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新时间偏好
  const updatePreferences = async (data) => {
    loading.value = true
    try {
      const res = await timePreferencesApi.updateTimePreferences(data)
      preferences.value = { ...preferences.value, ...data }
      return res
    } catch (error) {
      console.error('更新时间偏好失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 重置为默认值
  const resetPreferences = () => {
    preferences.value = {
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
    }
  }

  // Getters
  // 工作日数组
  const workDaysArray = () => {
    return preferences.value.work_days.split(',').map(Number)
  }

  // 工作时间段(分钟)
  const workDurationMinutes = () => {
    const [startHour, startMin] = preferences.value.work_start.split(':').map(Number)
    const [endHour, endMin] = preferences.value.work_end.split(':').map(Number)
    return (endHour - startHour) * 60 + (endMin - startMin)
  }

  // 午休时间段(分钟)
  const lunchDurationMinutes = () => {
    const [startHour, startMin] = preferences.value.lunch_start.split(':').map(Number)
    const [endHour, endMin] = preferences.value.lunch_end.split(':').map(Number)
    return (endHour - startHour) * 60 + (endMin - startMin)
  }

  // 睡眠时间段(分钟)
  const sleepDurationMinutes = () => {
    const [startHour, startMin] = preferences.value.sleep_time.split(':').map(Number)
    const [endHour, endMin] = preferences.value.wake_up_time.split(':').map(Number)

    let duration = (24 - startHour + endHour) * 60 + (endMin - startMin)
    if (duration >= 24 * 60) {
      duration -= 24 * 60
    }
    return duration
  }

  return {
    // State
    preferences,
    loading,

    // Actions
    fetchPreferences,
    updatePreferences,
    resetPreferences,

    // Getters
    workDaysArray,
    workDurationMinutes,
    lunchDurationMinutes,
    sleepDurationMinutes
  }
})
