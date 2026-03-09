<template>
  <view class="simple-test-container">
    <!-- 测试控制面板 -->
    <view class="control-panel">
      <text class="panel-title">E2E 测试控制台</text>
      <view class="status-bar">
        <text class="status-text">状态: {{ testStatus }}</text>
        <text class="connection-status" :class="{ connected: isConnected }">
          {{ isConnected ? '已连接' : '未连接' }}
        </text>
      </view>
    </view>

    <!-- 请求日志面板 -->
    <view class="log-panel">
      <text class="log-title">请求日志</text>
      <scroll-view class="log-content" scroll-y>
        <view v-for="(log, index) in requestLogs" :key="index" class="log-item">
          <text class="log-method">{{ log.method }}</text>
          <text class="log-url">{{ log.url }}</text>
          <text :class="['log-status', log.success ? 'success' : 'error']">
            {{ log.status }}
          </text>
        </view>
      </scroll-view>
    </view>

    <!-- 测试结果面板 -->
    <view class="result-panel" v-if="testResults.length > 0">
      <text class="result-title">测试结果</text>
      <view v-for="(result, index) in testResults" :key="index" class="result-item">
        <text :class="['result-status', result.passed ? 'passed' : 'failed']">
          {{ result.passed ? '✓' : '✗' }}
        </text>
        <text class="result-name">{{ result.name }}</text>
        <text class="result-message">{{ result.message }}</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      // WebSocket连接
      ws: null,
      isConnected: false,
      wsUrl: 'ws://localhost:8765',

      // 测试状态
      testStatus: '就绪',

      // 请求拦截记录
      requestLogs: [],
      interceptedRequests: [],

      // 测试结果
      testResults: [],

      // 原始uni.request引用
      originalRequest: null
    }
  },

  onLoad() {
    this.initRequestInterceptor()
    this.connectWebSocket()
  },

  onUnload() {
    this.disconnectWebSocket()
    this.restoreRequest()
  },

  methods: {
    connectWebSocket() {
      try {
        this.ws = uni.connectSocket({
          url: this.wsUrl,
          success: () => {
            console.log('WebSocket连接成功')
          }
        })

        this.ws.onOpen(() => {
          this.isConnected = true
          this.testStatus = '已连接'
          this.sendMessage({
            type: 'client_ready',
            platform: 'uni-app',
            timestamp: Date.now()
          })
        })

        this.ws.onMessage((res) => {
          this.handleCommand(JSON.parse(res.data))
        })

        this.ws.onClose(() => {
          this.isConnected = false
          this.testStatus = '连接断开'
        })

        this.ws.onError((err) => {
          console.error('WebSocket错误:', err)
          this.isConnected = false
        })
      } catch (e) {
        console.error('WebSocket连接失败:', e)
      }
    },

    disconnectWebSocket() {
      if (this.ws) {
        this.ws.close()
        this.ws = null
      }
    },

    sendMessage(data) {
      if (this.ws && this.isConnected) {
        this.ws.send({
          data: JSON.stringify(data)
        })
      }
    },

    initRequestInterceptor() {
      this.originalRequest = uni.request
      const self = this

      uni.request = function(options) {
        const startTime = Date.now()
        const requestInfo = {
          id: Date.now() + Math.random(),
          method: options.method || 'GET',
          url: options.url,
          data: options.data,
          header: options.header,
          timestamp: startTime
        }

        self.addRequestLog({
          method: requestInfo.method,
          url: requestInfo.url,
          status: '请求中...',
          success: true
        })

        return new Promise((resolve, reject) => {
          self.originalRequest.call(uni, {
            ...options,
            success: (res) => {
              const duration = Date.now() - startTime
              const responseInfo = {
                ...requestInfo,
                statusCode: res.statusCode,
                responseData: res.data,
                duration: duration,
                success: res.statusCode >= 200 && res.statusCode < 300
              }

              self.interceptedRequests.push(responseInfo)
              self.updateRequestLog(requestInfo.url, {
                status: `${res.statusCode} (${duration}ms)`,
                success: responseInfo.success
              })

              self.sendMessage({
                type: 'request_intercepted',
                data: responseInfo
              })

              resolve(res)
            },
            fail: (err) => {
              self.updateRequestLog(requestInfo.url, {
                status: '失败',
                success: false
              })
              reject(err)
            }
          })
        })
      }
    },

    restoreRequest() {
      if (this.originalRequest) {
        uni.request = this.originalRequest
      }
    },

    addRequestLog(log) {
      this.requestLogs.unshift(log)
      if (this.requestLogs.length > 50) {
        this.requestLogs.pop()
      }
    },

    updateRequestLog(url, update) {
      const log = this.requestLogs.find(l => l.url === url)
      if (log) {
        Object.assign(log, update)
      }
    },

    handleCommand(command) {
      console.log('收到指令:', command)

      switch (command.type) {
        case 'get_request_history':
          this.handleGetRequestHistory(command)
          break
        case 'test_request':
          this.handleTestRequest(command)
          break
        default:
          console.log('未知指令:', command.type)
      }
    },

    handleGetRequestHistory(command) {
      this.sendMessage({
        type: 'request_history',
        commandId: command.id,
        requests: this.interceptedRequests
      })
    },

    async handleTestRequest(command) {
      const { method, url, data } = command.params
      this.testStatus = `执行测试: ${method} ${url}`

      try {
        const response = await uni.request({
          url: url,
          method: method,
          data: data,
          header: {
            'Content-Type': 'application/json'
          }
        })

        const passed = response.statusCode >= 200 && response.statusCode < 300
        this.testResults.push({
          name: `${method} ${url}`,
          passed: passed,
          message: passed ? '成功' : `失败: ${response.statusCode}`
        })

        this.sendMessage({
          type: 'test_result',
          commandId: command.id,
          passed: passed,
          status: response.statusCode,
          data: response.data
        })
      } catch (error) {
        this.testResults.push({
          name: `${method} ${url}`,
          passed: false,
          message: `异常: ${error.message}`
        })

        this.sendMessage({
          type: 'test_result',
          commandId: command.id,
          passed: false,
          error: error.message
        })
      }

      this.testStatus = '就绪'
    }
  }
}
</script>

<style scoped>
.simple-test-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  display: flex;
  flex-direction: column;
}

.control-panel {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 30rpx;
}

.panel-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #ffffff;
  display: block;
  margin-bottom: 20rpx;
}

.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-text {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
}

.connection-status {
  font-size: 24rpx;
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
  background-color: #ff6b6b;
  color: #ffffff;
}

.connection-status.connected {
  background-color: #51cf66;
}

.log-panel {
  background-color: #ffffff;
  margin: 20rpx;
  border-radius: 16rpx;
  padding: 20rpx;
  max-height: 400rpx;
}

.log-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 16rpx;
}

.log-content {
  max-height: 300rpx;
}

.log-item {
  display: flex;
  align-items: center;
  padding: 12rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.log-method {
  font-size: 22rpx;
  color: #667eea;
  background-color: #f0f0ff;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  margin-right: 16rpx;
  min-width: 80rpx;
  text-align: center;
}

.log-url {
  flex: 1;
  font-size: 24rpx;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.log-status {
  font-size: 22rpx;
  margin-left: 16rpx;
}

.log-status.success {
  color: #51cf66;
}

.log-status.error {
  color: #ff6b6b;
}

.result-panel {
  background-color: #ffffff;
  margin: 0 20rpx 20rpx;
  border-radius: 16rpx;
  padding: 20rpx;
}

.result-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 16rpx;
}

.result-item {
  display: flex;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.result-status {
  font-size: 32rpx;
  margin-right: 16rpx;
  width: 40rpx;
}

.result-status.passed {
  color: #51cf66;
}

.result-status.failed {
  color: #ff6b6b;
}

.result-name {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.result-message {
  font-size: 24rpx;
  color: #999;
}
</style>
