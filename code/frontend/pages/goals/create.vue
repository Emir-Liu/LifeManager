<template>
  <view class="create-container">
    <view class="header">
      <text class="title">创建新目标</text>
      <text class="subtitle">设定你的目标，AI 帮你规划</text>
    </view>

    <view class="form-container">
      <view class="form-group">
        <text class="label">目标名称 *</text>
        <input
          class="input"
          v-model="formData.title"
          placeholder="例如：学习 Python 编程"
          maxlength="50"
        />
      </view>

      <view class="form-group">
        <text class="label">目标描述</text>
        <textarea
          class="textarea"
          v-model="formData.description"
          placeholder="详细描述你的目标..."
          maxlength="500"
        />
      </view>

      <view class="form-group">
        <text class="label">期望完成时间 *</text>
        <picker
          mode="date"
          :value="formData.deadline"
          @change="handleDateChange"
        >
          <view class="picker-input">
            {{ formData.deadline || '选择日期' }}
          </view>
        </picker>
      </view>

      <view class="form-group">
        <text class="label">优先级</text>
        <view class="priority-list">
          <view
            v-for="item in priorities"
            :key="item.value"
            class="priority-item"
            :class="{ active: formData.priority === item.value }"
            @tap="handlePriorityChange(item.value)"
          >
            {{ item.label }}
          </view>
        </view>
      </view>

      <view class="form-group">
        <text class="label">目标类型</text>
        <view class="type-list">
          <view
            v-for="item in types"
            :key="item.value"
            class="type-item"
            :class="{ active: formData.type === item.value }"
            @tap="handleTypeChange(item.value)"
          >
            <text class="type-icon">{{ item.icon }}</text>
            <text class="type-label">{{ item.label }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="footer">
      <button class="submit-btn" :disabled="loading" @tap="handleSubmit">
        {{ loading ? '创建中...' : '创建目标' }}
      </button>
      <button class="cancel-btn" @tap="handleCancel">取消</button>
    </view>
  </view>
</template>

<script>
import goalApi from '@/api/goal.js'

export default {
  data() {
    return {
      formData: {
        title: '',
        description: '',
        deadline: '',
        priority: 'medium',
        type: 'personal'
      },
      priorities: [
        { label: '低', value: 'low' },
        { label: '中', value: 'medium' },
        { label: '高', value: 'high' }
      ],
      types: [
        { label: '个人', value: 'personal', icon: '👤' },
        { label: '学习', value: 'study', icon: '📚' },
        { label: '工作', value: 'work', icon: '💼' },
        { label: '健康', value: 'health', icon: '❤️' }
      ],
      loading: false
    }
  },

  methods: {
    handleDateChange(e) {
      this.formData.deadline = e.detail.value
    },

    handlePriorityChange(value) {
      this.formData.priority = value
    },

    handleTypeChange(value) {
      this.formData.type = value
    },

    async handleSubmit() {
      // 表单验证
      if (!this.formData.title) {
        uni.showToast({
          title: '请输入目标名称',
          icon: 'none'
        })
        return
      }
      if (!this.formData.deadline) {
        uni.showToast({
          title: '请选择完成时间',
          icon: 'none'
        })
        return
      }

      this.loading = true
      try {
        await goalApi.createGoal(this.formData)
        uni.showToast({
          title: '创建成功',
          icon: 'success'
        })
        setTimeout(() => {
          uni.navigateBack()
        }, 1000)
      } catch (error) {
        uni.showToast({
          title: error.message || '创建失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    },

    handleCancel() {
      uni.navigateBack()
    }
  }
}
</script>

<style scoped>
.create-container {
  min-height: 100vh;
  background-color: #F5F5F5;
  display: flex;
  flex-direction: column;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60rpx 40rpx;
}

.title {
  font-size: 40rpx;
  font-weight: bold;
  color: #ffffff;
  display: block;
  margin-bottom: 12rpx;
}

.subtitle {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.8);
  display: block;
}

.form-container {
  flex: 1;
  background-color: #ffffff;
  border-radius: 24rpx 24rpx 0 0;
  padding: 40rpx;
  margin-top: -20rpx;
}

.form-group {
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

.textarea {
  width: 100%;
  min-height: 160rpx;
  padding: 20rpx 24rpx;
  background-color: #F5F5F5;
  border-radius: 8rpx;
  font-size: 28rpx;
  color: #333;
}

.picker-input {
  width: 100%;
  height: 80rpx;
  padding: 0 24rpx;
  background-color: #F5F5F5;
  border-radius: 8rpx;
  font-size: 28rpx;
  color: #333;
  line-height: 80rpx;
}

.priority-list {
  display: flex;
  gap: 20rpx;
}

.priority-item {
  flex: 1;
  height: 80rpx;
  background-color: #F5F5F5;
  border-radius: 8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  color: #666;
  transition: all 0.3s;
}

.priority-item.active {
  background-color: #007AFF;
  color: #ffffff;
}

.type-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.type-item {
  flex: 0 0 calc(50% - 10rpx);
  background-color: #F5F5F5;
  border-radius: 12rpx;
  padding: 32rpx 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  transition: all 0.3s;
  border: 2rpx solid transparent;
}

.type-item.active {
  border-color: #007AFF;
  background-color: #E3F2FD;
}

.type-icon {
  font-size: 48rpx;
}

.type-label {
  font-size: 26rpx;
  color: #666;
}

.type-item.active .type-label {
  color: #007AFF;
}

.footer {
  padding: 20rpx 40rpx 40rpx;
  background-color: #ffffff;
}

.submit-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  border-radius: 44rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
  margin-bottom: 20rpx;
}

.submit-btn:disabled {
  opacity: 0.6;
}

.cancel-btn {
  width: 100%;
  height: 88rpx;
  background-color: #F5F5F5;
  color: #666;
  border-radius: 44rpx;
  font-size: 28rpx;
  border: none;
}
</style>
