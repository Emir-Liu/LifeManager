import storage from '@/utils/storage.js'

const STORAGE_KEY = 'user_info'

export default {
  namespaced: true,

  state: {
    token: '',
    userInfo: null,
    isLoggedIn: false
  },

  getters: {
    // 获取用户信息
    getUserInfo(state) {
      return state.userInfo
    },
    // 获取 token
    getToken(state) {
      return state.token
    },
    // 是否已登录
    isLoggedIn(state) {
      return state.isLoggedIn
    }
  },

  mutations: {
    // 设置 token
    SET_TOKEN(state, token) {
      state.token = token
      if (token) {
        uni.setStorageSync('token', token)
      } else {
        uni.removeStorageSync('token')
      }
    },
    // 设置用户信息
    SET_USER_INFO(state, userInfo) {
      state.userInfo = userInfo
      state.isLoggedIn = !!userInfo
      if (userInfo) {
        storage.set(STORAGE_KEY, userInfo)
      } else {
        storage.remove(STORAGE_KEY)
      }
    },
    // 清空用户信息
    CLEAR_USER(state) {
      state.token = ''
      state.userInfo = null
      state.isLoggedIn = false
      uni.removeStorageSync('token')
      storage.remove(STORAGE_KEY)
    }
  },

  actions: {
    // 登录
    async login({ commit }, { username, password }) {
      const request = require('@/utils/request.js')
      try {
        const res = await request.post('/auth/login', {
          username,
          password
        })
        commit('SET_TOKEN', res.token)
        commit('SET_USER_INFO', res.user)
        return res
      } catch (error) {
        throw error
      }
    },

    // 注册
    async register({ commit }, { username, password, email }) {
      const request = require('@/utils/request.js')
      try {
        const res = await request.post('/auth/register', {
          username,
          password,
          email
        })
        commit('SET_TOKEN', res.token)
        commit('SET_USER_INFO', res.user)
        return res
      } catch (error) {
        throw error
      }
    },

    // 退出登录
    logout({ commit }) {
      commit('CLEAR_USER')
      uni.showToast({
        title: '已退出登录',
        icon: 'success'
      })
    },

    // 获取用户信息
    async getUserInfo({ commit }) {
      const request = require('@/utils/request.js')
      try {
        const res = await request.get('/users/me')
        commit('SET_USER_INFO', res)
        return res
      } catch (error) {
        throw error
      }
    },

    // 初始化用户信息
    initUser({ commit }) {
      const token = uni.getStorageSync('token')
      const userInfo = storage.get(STORAGE_KEY)

      if (token && userInfo) {
        commit('SET_TOKEN', token)
        commit('SET_USER_INFO', userInfo)
      }
    }
  }
}
