import { get, post, put, del } from '@/utils/request.js'

/**
 * 用户相关 API
 */

export default {
  // 登录
  login(data) {
    return post('/auth/login', data)
  },

  // 注册
  register(data) {
    return post('/auth/register', data)
  },

  // 刷新 token
  refreshToken(refreshToken) {
    return post('/auth/refresh', { refresh_token: refreshToken })
  },

  // 获取当前用户信息
  getUserInfo() {
    return get('/users/me')
  },

  // 更新用户信息
  updateUserInfo(data) {
    return put('/users/me', data)
  },

  // 修改密码
  changePassword(data) {
    return post('/users/me/change-password', data)
  },

  // 上传头像
  uploadAvatar(filePath) {
    return new Promise((resolve, reject) => {
      uni.uploadFile({
        url: 'http://localhost:8000/api/users/me/avatar',
        filePath,
        name: 'file',
        header: {
          'Authorization': `Bearer ${uni.getStorageSync('token')}`
        },
        success: (res) => {
          const data = JSON.parse(res.data)
          if (data.code === 0) {
            resolve(data.data)
          } else {
            reject(new Error(data.message))
          }
        },
        fail: (err) => {
          reject(err)
        }
      })
    })
  }
}
