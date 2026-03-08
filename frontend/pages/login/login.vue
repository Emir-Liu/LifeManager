<template>
  <view class="login-container">
    <!-- 状态栏 -->
    <view class="status-bar">
      <text class="time">{{ currentTime }}</text>
      <view class="status-icons">
        <text class="icon">📶</text>
        <text class="icon">📡</text>
        <text class="icon">🔋</text>
      </view>
    </view>

    <!-- 头部 -->
    <view class="header">
      <text class="logo">🎯</text>
      <text class="app-name">LifeManager</text>
      <text class="app-slogan">智能生活管理助手</text>
    </view>

    <!-- 表单容器 -->
    <view class="form-container">
      <view class="input-group">
        <text class="label">手机号 / 邮箱</text>
        <input
          class="input"
          v-model="formData.username"
          placeholder="请输入手机号或邮箱"
          maxlength="50"
        />
      </view>

      <view class="input-group">
        <text class="label">密码</text>
        <input
          class="input"
          v-model="formData.password"
          type="password"
          placeholder="请输入密码"
          maxlength="20"
        />
      </view>

      <view class="form-options">
        <label class="remember-me" @tap="toggleRemember">
          <view class="checkbox" :class="{ checked: rememberMe }">
            <text v-if="rememberMe">✓</text>
          </view>
          <text>记住我</text>
        </label>
        <text class="link" @tap="handleForgot">忘记密码？</text>
      </view>

      <button class="submit-btn" :disabled="loading" @tap="handleLogin">
        {{ loading ? '登录中...' : '登录' }}
      </button>

      <view class="divider">
        <view class="line"></view>
        <text>其他登录方式</text>
        <view class="line"></view>
      </view>

      <view class="social-login">
        <view class="social-btn" @tap="wechatLogin">
          <text class="social-icon">💬</text>
        </view>
        <view class="social-btn" @tap="qqLogin">
          <text class="social-icon">🐧</text>
        </view>
        <view class="social-btn" @tap="githubLogin">
          <text class="social-icon">🐱</text>
        </view>
      </view>

      <view class="register-link">
        <text>还没有账号？</text>
        <view class="link" @tap="handleRegister">立即注册</view>
      </view>

      <view class="guest-login">
        <button class="guest-btn" @tap="handleGuestLogin">游客登录</button>
      </view>
    </view>

    <!-- 功能展示 -->
    <view class="features">
      <view class="feature-item">
        <text class="feature-icon">📋</text>
        <text class="feature-text">任务管理</text>
      </view>
      <view class="feature-item">
        <text class="feature-icon">📊</text>
        <text class="feature-text">统计分析</text>
      </view>
      <view class="feature-item">
        <text class="feature-icon">🤖</text>
        <text class="feature-text">AI助手</text>
      </view>
    </view>
  </view>
</template>

<script>
import { useUserStore } from '@/store'

export default {
  data() {
    return {
      formData: {
        username: '',
        password: ''
      },
      loading: false,
      rememberMe: false,
      currentTime: '9:41'
    }
  },
  onLoad() {
    this.updateTime()
    setInterval(() => this.updateTime(), 60000)
  },
  methods: {
    updateTime() {
      const now = new Date()
      const hours = String(now.getHours()).padStart(2, '0')
      const minutes = String(now.getMinutes()).padStart(2, '0')
      this.currentTime = `${hours}:${minutes}`
    },

    toggleRemember() {
      this.rememberMe = !this.rememberMe
    },

    async handleLogin() {
      // 表单验证
      if (!this.formData.username) {
        uni.showToast({
          title: '请输入手机号或邮箱',
          icon: 'none'
        })
        return
      }
      if (!this.formData.password) {
        uni.showToast({
          title: '请输入密码',
          icon: 'none'
        })
        return
      }

      this.loading = true
      try {
        const userStore = useUserStore()
        const res = await userStore.login(this.formData)
        uni.showToast({
          title: '登录成功',
          icon: 'success'
        })
        setTimeout(() => {
          uni.reLaunch({
            url: '/pages/conversation/conversation'
          })
        }, 1000)
      } catch (error) {
        uni.showToast({
          title: error.message || '登录失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    },

    handleRegister() {
      console.log('点击注册按钮')
      uni.navigateTo({
        url: '/pages/register/register',
        success: () => {
          console.log('跳转成功')
        },
        fail: (err) => {
          console.error('跳转失败:', err)
          uni.showToast({
            title: '跳转失败: ' + (err.errMsg || '未知错误'),
            icon: 'none',
            duration: 3000
          })
        }
      })
    },

    handleForgot() {
      uni.showToast({
        title: '功能开发中',
        icon: 'none'
      })
    },

    handleGuestLogin() {
      uni.showModal({
        title: '游客登录',
        content: '注意：游客模式下数据仅保存在本地，更换设备后无法恢复。\n\n是否继续？',
        success: (res) => {
          if (res.confirm) {
            uni.reLaunch({
              url: '/pages/conversation/conversation'
            })
          }
        }
      })
    },

    wechatLogin() {
      uni.showToast({
        title: '微信登录功能开发中...',
        icon: 'none'
      })
    },

    qqLogin() {
      uni.showToast({
        title: 'QQ登录功能开发中...',
        icon: 'none'
      })
    },

    githubLogin() {
      uni.showToast({
        title: 'GitHub登录功能开发中...',
        icon: 'none'
      })
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  padding: 20rpx;
}

.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 40rpx;
  color: white;
  font-size: 24rpx;
}

.status-icons {
  display: flex;
  gap: 16rpx;
}

.header {
  text-align: center;
  padding: 40rpx 0;
}

.logo {
  font-size: 96rpx;
  display: block;
  margin-bottom: 20rpx;
}

.app-name {
  font-size: 48rpx;
  font-weight: 700;
  color: white;
  display: block;
  margin-bottom: 10rpx;
}

.app-slogan {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
  display: block;
}

.form-container {
  background-color: white;
  border-radius: 24rpx;
  padding: 60rpx 40rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
  margin-bottom: 40rpx;
}

.input-group {
  margin-bottom: 40rpx;
}

.label {
  font-size: 28rpx;
  color: #666;
  font-weight: 500;
  display: block;
  margin-bottom: 16rpx;
}

.input {
  width: 100%;
  height: 88rpx;
  padding: 0 32rpx;
  background-color: #f5f5f5;
  border-radius: 24rpx;
  font-size: 30rpx;
  border: 4rpx solid #e0e0e0;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 50rpx;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 16rpx;
  font-size: 26rpx;
  color: #666;
}

.checkbox {
  width: 32rpx;
  height: 32rpx;
  border: 2rpx solid #ccc;
  border-radius: 6rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20rpx;
  color: white;
}

.checkbox.checked {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
}

.link {
  font-size: 26rpx;
  color: #667eea;
  font-weight: 600;
}

.submit-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 24rpx;
  font-size: 32rpx;
  font-weight: 600;
  border: none;
  margin-bottom: 40rpx;
}

.submit-btn:disabled {
  opacity: 0.6;
}

.divider {
  display: flex;
  align-items: center;
  margin: 40rpx 0;
  color: #999;
  font-size: 26rpx;
  gap: 30rpx;
}

.line {
  flex: 1;
  height: 2rpx;
  background: #e0e0e0;
}

.social-login {
  display: flex;
  gap: 30rpx;
  margin-bottom: 40rpx;
}

.social-btn {
  flex: 1;
  height: 88rpx;
  border: 4rpx solid #e0e0e0;
  border-radius: 24rpx;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.social-icon {
  font-size: 48rpx;
}

.register-link {
  text-align: center;
  font-size: 28rpx;
  color: #666;
  margin-bottom: 40rpx;
}

.guest-login {
  text-align: center;
}

.guest-btn {
  padding: 24rpx 60rpx;
  background: transparent;
  color: #999;
  border: 4rpx solid #e0e0e0;
  border-radius: 24rpx;
  font-size: 28rpx;
}

.features {
  display: flex;
  justify-content: space-around;
  background: white;
  border-radius: 24rpx;
  padding: 40rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
}

.feature-item {
  text-align: center;
}

.feature-icon {
  font-size: 56rpx;
  display: block;
  margin-bottom: 16rpx;
}

.feature-text {
  font-size: 24rpx;
  color: #666;
}
</style>
