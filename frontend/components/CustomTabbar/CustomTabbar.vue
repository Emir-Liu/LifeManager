<template>
  <view class="custom-tabbar">
    <view
      v-for="(item, index) in tabList"
      :key="index"
      class="tab-item"
      :class="{ active: currentTab === item.pagePath, 'ai-center': item.isCenter }"
      @tap="switchTab(item)"
    >
      <text class="tab-icon">{{ item.icon }}</text>
      <text class="tab-text">{{ item.text }}</text>
    </view>
  </view>
</template>

<script>
export default {
  name: 'CustomTabbar',
  data() {
    return {
      currentTab: '',
      tabList: [
        {
          pagePath: '/pages/goals/goals',
          text: '目标',
          icon: '🎯',
          isCenter: false
        },
        {
          pagePath: '/pages/tasks/tasks',
          text: '任务',
          icon: '📋',
          isCenter: false
        },
        {
          pagePath: '/pages/conversation/conversation',
          text: 'AI助手',
          icon: '🤖',
          isCenter: true
        },
        {
          pagePath: '/pages/timeline/calendar-view',
          text: '日程',
          icon: '📅',
          isCenter: false
        },
        {
          pagePath: '/pages/statistics/statistics',
          text: '统计',
          icon: '📊',
          isCenter: false
        }
      ]
    }
  },
  onLoad() {
    this.getCurrentPage()
  },
  onShow() {
    this.getCurrentPage()
  },
  methods: {
    getCurrentPage() {
      const pages = getCurrentPages()
      if (pages.length > 0) {
        const currentPage = pages[pages.length - 1]
        const route = '/' + currentPage.route
        this.currentTab = route
      }
    },

    switchTab(item) {
      if (item.pagePath === this.currentTab) return

      // 使用 redirectTo 替代 switchTab，因为没有配置原生 tabBar
      uni.redirectTo({
        url: item.pagePath,
        fail: () => {
          uni.reLaunch({
            url: item.pagePath
          })
        }
      })
    }
  }
}
</script>

<style scoped>
.custom-tabbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100rpx;
  background: white;
  display: flex;
  align-items: center;
  box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.1);
  z-index: 999;
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  transition: all 0.3s;
}

.tab-icon {
  font-size: 48rpx;
  margin-bottom: 4rpx;
  opacity: 0.6;
}

.tab-text {
  font-size: 20rpx;
  color: #999;
  opacity: 0.8;
}

.tab-item.active .tab-icon {
  opacity: 1;
}

.tab-item.active .tab-text {
  color: #667eea;
  font-weight: 600;
}

.tab-item.ai-center {
  position: relative;
}

.tab-item.ai-center .tab-icon {
  font-size: 56rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  opacity: 1;
}

.tab-item.ai-center .tab-text {
  color: #667eea;
  font-weight: 600;
}

.tab-item.ai-center::before {
  content: '';
  position: absolute;
  top: 10rpx;
  left: 50%;
  transform: translateX(-50%);
  width: 80rpx;
  height: 80rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  opacity: 0.1;
  z-index: -1;
}
</style>
