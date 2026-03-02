<template>
  <view class="register-container">
    <view class="header">
      <text class="title">创建账号</text>
      <text class="subtitle">加入托管人生</text>
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
        <text class="label">邮箱</text>
        <input
          class="input"
          v-model="formData.email"
          type="email"
          placeholder="请输入邮箱"
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

      <view class="input-group">
        <text class="label">确认密码</text>
        <input
          class="input"
          v-model="formData.confirmPassword"
          type="password"
          placeholder="请再次输入密码"
          maxlength="20"
        />
      </view>

      <button class="register-btn" :disabled="loading" @tap="handleRegister">
        {{ loading ? '注册中...' : '注册' }}
      </button>
    </view>

    <view class="footer">
      <text class="footer-text">已有账号？</text>
      <text class="link" @tap="handleLogin">立即登录</text>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      formData: {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      },
      loading: false
    }
  },
  methods: {
    async handleRegister() {
      // 表单验证
      if (!this.formData.username) {
        uni.showToast({
          title: '请输入账号',
          icon: 'none',
          duration: 2000
        })
        return
      }
      if (this.formData.username.length < 3) {
        uni.showToast({
          title: '账号至少3个字符',
          icon: 'none',
          duration: 2000
        })
        return
      }
      if (this.formData.username.length > 50) {
        uni.showToast({
          title: '账号最多50个字符',
          icon: 'none',
          duration: 2000
        })
        return
      }
      
      // 邮箱为可选字段
      if (this.formData.email && !this.validateEmail(this.formData.email)) {
        uni.showToast({
          title: '邮箱格式不正确',
          icon: 'none',
          duration: 2000
        })
        return
      }
      
      if (!this.formData.password) {
        uni.showToast({
          title: '请输入密码',
          icon: 'none',
          duration: 2000
        })
        return
      }
      if (this.formData.password.length < 6) {
        uni.showToast({
          title: '密码至少6位',
          icon: 'none',
          duration: 2000
        })
        return
      }
      if (this.formData.password.length > 50) {
        uni.showToast({
          title: '密码最多50位',
          icon: 'none',
          duration: 2000
        })
        return
      }
      if (this.formData.password !== this.formData.confirmPassword) {
        uni.showToast({
          title: '两次密码不一致',
          icon: 'none',
          duration: 2000
        })
        return
      }

      this.loading = true
      try {
        const res = await this.$store.dispatch('user/register', {
          username: this.formData.username,
          email: this.formData.email || undefined, // 邮箱为空时传undefined
          password: this.formData.password
        })
        uni.showToast({
          title: '注册成功',
          icon: 'success',
          duration: 1500
        })
        setTimeout(() => {
          uni.switchTab({
            url: '/pages/index/index'
          })
        }, 1500)
      } catch (error) {
        console.error('注册失败:', error)
        let errorMessage = '注册失败，请稍后重试'
        
        // 解析后端返回的详细错误信息
        if (error.data && error.data.reason) {
          errorMessage = error.data.reason
        } else if (error.message) {
          errorMessage = error.message
        } else if (typeof error === 'string') {
          errorMessage = error
        }
        
        // 根据不同的错误类型显示更友好的提示
        if (errorMessage.includes('用户名')) {
          uni.showToast({
            title: errorMessage,
            icon: 'none',
            duration: 3000
          })
        } else if (errorMessage.includes('邮箱')) {
          uni.showToast({
            title: errorMessage,
            icon: 'none',
            duration: 3000
          })
        } else {
          uni.showToast({
            title: errorMessage,
            icon: 'none',
            duration: 2000
          })
        }
      } finally {
        this.loading = false
      }
    },
    
    // 邮箱格式验证
    validateEmail(email) {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return re.test(email)
    },

    handleLogin() {
      uni.navigateBack()
    }
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  padding: 80rpx 60rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
}

.header {
  margin-bottom: 60rpx;
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
  margin-bottom: 32rpx;
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

.register-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  border-radius: 44rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
  margin-top: 20rpx;
}

.register-btn:disabled {
  opacity: 0.6;
}

.footer {
  margin-top: 40rpx;
  text-align: center;
}

.footer-text {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-right: 16rpx;
}

.link {
  font-size: 24rpx;
  color: #ffffff;
  font-weight: bold;
}
</style>
