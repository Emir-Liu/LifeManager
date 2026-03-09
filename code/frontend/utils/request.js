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
            // 成功响应
            resolve(data.data)
          } else {
            // 业务错误（非200的错误码）
            // 检查是否有详细的错误原因
            let errorMessage = data.message || '请求失败'
            let errorData = data.data || {}
            
            // 如果有详细的reason字段，优先使用
            if (errorData.reason) {
              errorMessage = errorData.reason
            }
            
            // 构造错误对象，包含详细信息
            const error = new Error(errorMessage)
            error.data = errorData
            error.code = data.code
            
            reject(error)
          }
        } else if (res.statusCode === 400 || res.statusCode === 422) {
          // 处理校验错误
          let errorMsg = res.data?.detail || res.data?.message || '请求参数错误'
          
          // 尝试解析Pydantic验证错误
          if (res.data?.detail && Array.isArray(res.data.detail)) {
            // Pydantic验证错误数组
            const errors = res.data.detail.map(err => 
              err.msg || '参数错误'
            )
            errorMsg = errors.join('; ')
          }
          
          reject(new Error(errorMsg))
        } else {
          // 其他HTTP错误
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
