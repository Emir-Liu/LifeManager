<template>
  <view class="l-input">
    <text v-if="label" class="l-input__label">{{ label }}</text>
    <input
      class="l-input__inner"
      :type="type"
      :value="value"
      :placeholder="placeholder"
      :disabled="disabled"
      :maxlength="maxlength"
      @input="handleInput"
      @blur="handleBlur"
      @focus="handleFocus"
    />
    <text v-if="suffix" class="l-input__suffix">{{ suffix }}</text>
  </view>
</template>

<script>
export default {
  name: 'LInput',
  props: {
    value: {
      type: [String, Number],
      default: ''
    },
    type: {
      type: String,
      default: 'text'
    },
    placeholder: {
      type: String,
      default: ''
    },
    label: {
      type: String,
      default: ''
    },
    suffix: {
      type: String,
      default: ''
    },
    disabled: {
      type: Boolean,
      default: false
    },
    maxlength: {
      type: Number,
      default: -1
    }
  },
  methods: {
    handleInput(e) {
      this.$emit('input', e.detail.value)
    },
    handleBlur(e) {
      this.$emit('blur', e)
    },
    handleFocus(e) {
      this.$emit('focus', e)
    }
  }
}
</script>

<style scoped>
.l-input {
  display: flex;
  flex-direction: column;
  margin-bottom: 32rpx;
}

.l-input__label {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 12rpx;
  font-weight: 500;
}

.l-input__inner {
  height: 80rpx;
  padding: 0 24rpx;
  background-color: #F5F5F5;
  border-radius: 8rpx;
  font-size: 28rpx;
  color: #333;
  border: 1px solid transparent;
  transition: all 0.3s;
}

.l-input__inner:focus {
  background-color: #fff;
  border-color: #007AFF;
}

.l-input__inner:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.l-input__suffix {
  position: absolute;
  right: 24rpx;
  top: 50%;
  transform: translateY(-50%);
  font-size: 24rpx;
  color: #999;
}
</style>
