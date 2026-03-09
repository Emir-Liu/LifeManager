<template>
  <view class="l-button" :class="[typeClass, sizeClass, { 'l-button--disabled': disabled, 'l-button--loading': loading }]" @tap="handleTap">
    <text v-if="loading" class="l-button__loading">加载中...</text>
    <slot v-else></slot>
  </view>
</template>

<script>
export default {
  name: 'LButton',
  props: {
    type: {
      type: String,
      default: 'primary'
    },
    size: {
      type: String,
      default: 'default'
    },
    disabled: {
      type: Boolean,
      default: false
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    typeClass() {
      return `l-button--${this.type}`
    },
    sizeClass() {
      return `l-button--${this.size}`
    }
  },
  methods: {
    handleTap() {
      if (this.disabled || this.loading) return
      this.$emit('click')
    }
  }
}
</script>

<style scoped>
.l-button {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8rpx;
  font-size: 28rpx;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.l-button--primary {
  background-color: #007AFF;
  color: #fff;
}

.l-button--secondary {
  background-color: #F0F0F0;
  color: #333;
}

.l-button--success {
  background-color: #07C160;
  color: #fff;
}

.l-button--danger {
  background-color: #FF3B30;
  color: #fff;
}

.l-button--default {
  background-color: #fff;
  color: #333;
  border: 1px solid #E5E5E5;
}

.l-button--small {
  height: 60rpx;
  padding: 0 24rpx;
  font-size: 24rpx;
}

.l-button--default {
  height: 80rpx;
  padding: 0 32rpx;
  font-size: 28rpx;
}

.l-button--large {
  height: 100rpx;
  padding: 0 40rpx;
  font-size: 32rpx;
}

.l-button--disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.l-button--loading {
  opacity: 0.7;
}

.l-button__loading {
  font-size: 24rpx;
}
</style>
