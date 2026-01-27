/**
 * 用户状态管理
 */

const state = {
  token: uni.getStorageSync('lifemanager_token') || '',
  userInfo: uni.getStorageSync('lifemanager_user') || null
}

const mutations = {
  SET_TOKEN(state, token) {
    state.token = token
    uni.setStorageSync('lifemanager_token', token)
  },
  SET_USER(state, userInfo) {
    state.userInfo = userInfo
    uni.setStorageSync('lifemanager_user', userInfo)
  },
  CLEAR_AUTH(state) {
    state.token = ''
    state.userInfo = null
    uni.removeStorageSync('lifemanager_token')
    uni.removeStorageSync('lifemanager_user')
  }
}

const actions = {
  // 登录
  async login({ commit }, credentials) {
    try {
      const { post } = require('@/utils/request')
      const data = await post('/auth/login', credentials)
      commit('SET_TOKEN', data.token)
      commit('SET_USER', {
        id: data.user_id,
        username: data.username
      })
      return data
    } catch (error) {
      throw error
    }
  },

  // 注册
  async register({ dispatch }, userData) {
    try {
      const { post } = require('@/utils/request')
      await post('/auth/register', userData)
      // 注册成功后自动登录
      return dispatch('login', {
        username: userData.username,
        password: userData.password
      })
    } catch (error) {
      throw error
    }
  },

  // 退出登录
  logout({ commit }) {
    commit('CLEAR_AUTH')
  }
}

const getters = {
  isLoggedIn: state => !!state.token,
  user: state => state.userInfo
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
