<template>
  <view class="login-container">
    <view class="header">
      <text class="title">欢迎回来</text>
      <text class="subtitle">登录托管人生</text>
    </view>

    <view class="form-container">
      <view class="input-group">
        <text class="label">账号</text>
        <input
          class="input"
          v-model="formData.username"
          placeholder="请输入账号"
          maxlength="20"
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

      <view class="actions">
        <text class="link" @tap="handleRegister">还没有账号？去注册</text>
        <text class="link" @tap="handleForgot">忘记密码？</text>
      </view>

      <button class="login-btn" :disabled="loading" @tap="handleLogin">
        {{ loading ? '登录中...' : '登录' }}
      </button>
    </view>

    <view class="footer">
      <text class="footer-text">登录即表示同意《用户协议》和《隐私政策》</text>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      formData: {
        username: '',
        password: ''
      },
      loading: false
    }
  },
  methods: {
    async handleLogin() {
      // 表单验证
      if (!this.formData.username) {
        uni.showToast({
          title: '请输入账号',
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
        const res = await this.$store.dispatch('user/login', this.formData)
        uni.showToast({
          title: '登录成功',
          icon: 'success'
        })
        setTimeout(() => {
          uni.switchTab({
            url: '/pages/index/index'
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
      uni.navigateTo({
        url: '/pages/register/register'
      })
    },

    handleForgot() {
      uni.showToast({
        title: '功能开发中',
        icon: 'none'
      })
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  padding: 80rpx 60rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
}

.header {
  margin-bottom: 80rpx;
}

.title {
  font-size: 56rpx;
  font-weight: bold;
  color: #ffffff;
  display: block;
  margin-bottom: 16rpx;
}

.subtitle {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.8);
  display: block;
}

.form-container {
  background-color: #ffffff;
  border-radius: 24rpx;
  padding: 60rpx 40rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
}

.input-group {
  margin-bottom: 40rpx;
}

.label {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
  display: block;
  margin-bottom: 16rpx;
}

.input {
  width: 100%;
  height: 80rpx;
  padding: 0 24rpx;
  background-color: #F5F5F5;
  border-radius: 8rpx;
  font-size: 28rpx;
  color: #333;
}

.actions {
  display: flex;
  justify-content: space-between;
  margin-bottom: 40rpx;
}

.link {
  font-size: 24rpx;
  color: #007AFF;
}

.login-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  border-radius: 44rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
}

.login-btn:disabled {
  opacity: 0.6;
}

.footer {
  margin-top: auto;
  text-align: center;
}

.footer-text {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
}
</style>
