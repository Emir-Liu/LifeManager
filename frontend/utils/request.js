/**
 * 网络请求封装
 */

const BASE_URL = 'http://localhost:8000/api'

/**
 * 请求拦截器
 */
function request(options) {
  // 获取本地存储的 token
  const token = uni.getStorageSync('lifemanager_token')

  // 拼接完整 URL
  let url = options.url
  if (!url.startsWith('http')) {
    url = BASE_URL + url
  }

  return new Promise((resolve, reject) => {
    uni.request({
      url: url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.header
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          const data = res.data
          if (data.code === 0) {
            resolve(data.data)
          } else if (data.code === 401) {
            // token 过期，跳转登录页
            uni.removeStorageSync('token')
            uni.removeStorageSync('userInfo')
            uni.navigateTo({
              url: '/pages/login/login'
            })
            reject(new Error(data.message || '登录已过期'))
          } else {
            reject(new Error(data.message || '请求失败'))
          }
        } else if (res.statusCode === 400 || res.statusCode === 422) {
          // 处理校验错误
          const errorMsg = res.data?.detail || res.data?.message || '请求参数错误'
          uni.showToast({
            title: errorMsg,
            icon: 'none'
          })
          reject(new Error(errorMsg))
        } else {
          const errorMsg = res.data?.detail || res.data?.message || `请求失败: ${res.statusCode}`
          reject(new Error(errorMsg))
        }
      },
      fail: (err) => {
        uni.showToast({
          title: '网络请求失败',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

/**
 * GET 请求
 */
export function get(url, params = {}) {
  return request({
    url,
    method: 'GET',
    data: params
  })
}

/**
 * POST 请求
 */
export function post(url, data = {}) {
  return request({
    url,
    method: 'POST',
    data
  })
}

/**
 * PUT 请求
 */
export function put(url, data = {}) {
  return request({
    url,
    method: 'PUT',
    data
  })
}

/**
 * DELETE 请求
 */
export function del(url, data = {}) {
  return request({
    url,
    method: 'DELETE',
    data
  })
}

export default request
