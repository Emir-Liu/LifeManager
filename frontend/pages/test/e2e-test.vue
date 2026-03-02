<template>
  <view class="e2e-test-container">
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

    <!-- 测试页面嵌入区域 -->
    <view class="test-page-container">
      <view v-if="currentTestPage === 'register'" class="embedded-page">
        <register-page ref="registerRef" />
      </view>
      <view v-else-if="currentTestPage === 'login'" class="embedded-page">
        <login-page ref="loginRef" />
      </view>
      <view v-else class="placeholder">
        <text>等待测试指令...</text>
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
// 导入真实业务页面
import RegisterPage from '@/pages/register/register.vue'
import LoginPage from '@/pages/login/login.vue'

export default {
  components: {
    RegisterPage,
    LoginPage
  },

  data() {
    return {
      // WebSocket连接
      ws: null,
      isConnected: false,
      wsUrl: 'ws://localhost:8765', // 智能体WebSocket服务器地址

      // 测试状态
      testStatus: '就绪',
      currentTestPage: null,
      currentScenario: null,

      // 请求拦截记录
      requestLogs: [],
      interceptedRequests: [],

      // 测试结果
      testResults: [],

      // 待执行的指令队列
      commandQueue: [],

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
    // ==================== WebSocket连接管理 ====================

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
          // 尝试重连
          setTimeout(() => this.connectWebSocket(), 3000)
        })

        this.ws.onError((err) => {
          console.error('WebSocket错误:', err)
          this.isConnected = false
          this.testStatus = '连接错误'
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

    // ==================== 请求拦截器 ====================

    initRequestInterceptor() {
      // 保存原始请求方法
      this.originalRequest = uni.request

      // 重写uni.request
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

        // 记录请求
        self.addRequestLog({
          method: requestInfo.method,
          url: requestInfo.url,
          status: '请求中...',
          success: true
        })

        return new Promise((resolve, reject) => {
          // 调用原始请求
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

              // 保存拦截的请求
              self.interceptedRequests.push(responseInfo)

              // 更新日志
              self.updateRequestLog(requestInfo.url, {
                status: `${res.statusCode} (${duration}ms)`,
                success: responseInfo.success
              })

              // 发送给智能体
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

    // ==================== 指令处理 ====================

    handleCommand(command) {
      console.log('收到指令:', command)

      switch (command.type) {
        case 'load_page':
          this.handleLoadPage(command)
          break
        case 'fill_form':
          this.handleFillForm(command)
          break
        case 'click_element':
          this.handleClickElement(command)
          break
        case 'verify_element':
          this.handleVerifyElement(command)
          break
        case 'get_request_history':
          this.handleGetRequestHistory(command)
          break
        case 'clear_storage':
          this.handleClearStorage(command)
          break
        case 'execute_scenario':
          this.handleExecuteScenario(command)
          break
        default:
          this.sendMessage({
            type: 'error',
            commandId: command.id,
            error: `未知指令类型: ${command.type}`
          })
      }
    },

    // ==================== 指令实现 ====================

    handleLoadPage(command) {
      const { page, params = {} } = command
      this.currentTestPage = page
      this.testStatus = `加载页面: ${page}`

      // 清除之前的请求记录
      this.interceptedRequests = []
      this.requestLogs = []

      this.sendMessage({
        type: 'page_loaded',
        commandId: command.id,
        page: page,
        timestamp: Date.now()
      })
    },

    handleFillForm(command) {
      const { selector, value, field } = command

      // 获取当前页面的ref
      const pageRef = this.$refs[`${this.currentTestPage}Ref`]
      if (!pageRef) {
        this.sendMessage({
          type: 'error',
          commandId: command.id,
          error: '页面未加载'
        })
        return
      }

      // 设置表单数据
      if (field && pageRef.formData) {
        pageRef.formData[field] = value
      }

      this.sendMessage({
        type: 'form_filled',
        commandId: command.id,
        field: field,
        value: value
      })
    },

    handleClickElement(command) {
      const { selector, action } = command
      const pageRef = this.$refs[`${this.currentTestPage}Ref`]

      if (!pageRef) {
        this.sendMessage({
          type: 'error',
          commandId: command.id,
          error: '页面未加载'
        })
        return
      }

      // 调用页面方法
      if (action === 'register' && pageRef.handleRegister) {
        pageRef.handleRegister()
      } else if (action === 'login' && pageRef.handleLogin) {
        pageRef.handleLogin()
      }

      this.sendMessage({
        type: 'element_clicked',
        commandId: command.id,
        action: action
      })
    },

    handleVerifyElement(command) {
      const { selector, expected, property = 'text' } = command
      const pageRef = this.$refs[`${this.currentTestPage}Ref`]

      let actual = null
      let passed = false

      if (pageRef && pageRef.formData) {
        actual = pageRef.formData[selector]
        passed = actual === expected
      }

      const result = {
        type: 'verification_result',
        commandId: command.id,
        selector: selector,
        expected: expected,
        actual: actual,
        passed: passed
      }

      this.testResults.push({
        name: `验证 ${selector}`,
        passed: passed,
        message: passed ? '符合预期' : `期望: ${expected}, 实际: ${actual}`
      })

      this.sendMessage(result)
    },

    handleGetRequestHistory(command) {
      this.sendMessage({
        type: 'request_history',
        commandId: command.id,
        requests: this.interceptedRequests
      })
    },

    handleClearStorage(command) {
      uni.clearStorageSync()
      this.sendMessage({
        type: 'storage_cleared',
        commandId: command.id
      })
    },

    async handleExecuteScenario(command) {
      const { scenario } = command
      this.currentScenario = scenario
      this.testStatus = `执行场景: ${scenario.name}`

      const results = []

      for (const step of scenario.steps) {
        this.testStatus = `执行: ${step.name}`

        try {
          await this.executeStep(step)
          results.push({
            step: step.name,
            passed: true
          })
        } catch (error) {
          results.push({
            step: step.name,
            passed: false,
            error: error.message
          })
          break
        }

        // 步骤间等待
        if (step.wait) {
          await this.delay(step.wait)
        }
      }

      this.sendMessage({
        type: 'scenario_completed',
        commandId: command.id,
        scenario: scenario.name,
        results: results
      })
    },

    async executeStep(step) {
      return new Promise((resolve, reject) => {
        switch (step.action) {
          case 'load_page':
            this.currentTestPage = step.page
            resolve()
            break
          case 'fill_form':
            const pageRef = this.$refs[`${this.currentTestPage}Ref`]
            if (pageRef && pageRef.formData) {
              Object.assign(pageRef.formData, step.data)
            }
            resolve()
            break
          case 'click':
            const ref = this.$refs[`${this.currentTestPage}Ref`]
            if (ref && step.method && ref[step.method]) {
              ref[step.method]()
            }
            resolve()
            break
          case 'wait':
            setTimeout(resolve, step.duration || 1000)
            break
          default:
            reject(new Error(`未知步骤: ${step.action}`))
        }
      })
    },

    delay(ms) {
      return new Promise(resolve => setTimeout(resolve, ms))
    }
  }
}
</script>

<style scoped>
.e2e-test-container {
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

.test-page-container {
  flex: 1;
  background-color: #ffffff;
  margin: 20rpx;
  border-radius: 16rpx;
  overflow: hidden;
}

.embedded-page {
  height: 100%;
}

.placeholder {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder text {
  font-size: 32rpx;
  color: #999;
}

.log-panel {
  background-color: #ffffff;
  margin: 0 20rpx 20rpx;
  border-radius: 16rpx;
  padding: 20rpx;
  max-height: 300rpx;
}

.log-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 16rpx;
}

.log-content {
  max-height: 200rpx;
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
