/**
 * 任务状态管理 - Pinia版本
 */
import { defineStore } from 'pinia'
import { get, put } from '@/utils/request'

export const useTasksStore = defineStore('tasks', {
  state: () => ({
    list: [],
    today: [],
    current: null,
    loading: false
  }),

  getters: {
    completedTasks: (state) => state.today.filter(t => t.completed),
    pendingTasks: (state) => state.today.filter(t => !t.completed),
    completedCount: (state) => state.today.filter(t => t.completed).length,
    pendingCount: (state) => state.today.filter(t => !t.completed).length
  },

  actions: {
    // 获取今日任务
    async fetchTodayTasks() {
      this.loading = true
      try {
        const result = await get('/tasks/today')
        console.log('获取今日任务响应:', result)
        // request.js 已经返回 data.data，所以 result 直接就是任务数组
        const taskList = result || []
        console.log('提取的任务列表:', taskList)
        this.today = taskList
        return result
      } catch (error) {
        console.error('获取今日任务失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取任务列表
    async fetchTasks(params = {}) {
      this.loading = true
      try {
        const list = await get('/tasks', params)
        this.list = list || []
        return list
      } catch (error) {
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取任务详情
    async fetchTaskDetail(taskId) {
      try {
        const task = await get(`/tasks/${taskId}`)
        this.current = task
        return task
      } catch (error) {
        throw error
      }
    },

    // 完成任务
    async completeTask(taskId) {
      try {
        const task = await put(`/tasks/${taskId}/complete`)
        const index = this.list.findIndex(t => t.id === task.id)
        if (index !== -1) {
          this.list.splice(index, 1, task)
        }
        return task
      } catch (error) {
        throw error
      }
    },

    // 取消完成任务
    async uncompleteTask(taskId) {
      try {
        const task = await put(`/tasks/${taskId}/uncomplete`)
        const index = this.list.findIndex(t => t.id === task.id)
        if (index !== -1) {
          this.list.splice(index, 1, task)
        }
        return task
      } catch (error) {
        throw error
      }
    }
  }
})
