/**
 * 用户状态管理 - Pinia版本
 */
import { defineStore } from 'pinia'
import { post } from '@/utils/request'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: uni.getStorageSync('lifemanager_token') || '',
    userInfo: uni.getStorageSync('lifemanager_user') || null
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    user: (state) => state.userInfo
  },

  actions: {
    // 登录
    async login(credentials) {
      try {
        const data = await post('/auth/login', credentials)
        this.token = data.token
        this.userInfo = {
          id: data.user_id,
          username: data.username
        }
        uni.setStorageSync('lifemanager_token', data.token)
        uni.setStorageSync('lifemanager_user', {
          id: data.user_id,
          username: data.username
        })
        return data
      } catch (error) {
        throw error
      }
    },

    // 注册
    async register(userData) {
      try {
        await post('/auth/register', userData)
        // 注册成功后自动登录
        return this.login({
          username: userData.username,
          password: userData.password
        })
      } catch (error) {
        throw error
      }
    },

    // 退出登录
    logout() {
      this.token = ''
      this.userInfo = null
      uni.removeStorageSync('lifemanager_token')
      uni.removeStorageSync('lifemanager_user')
    }
  }
})
