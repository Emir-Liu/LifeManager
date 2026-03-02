<template>
	<view class="content">
	<view class="welcome-section">
			<text class="title">托管人生</text>
			<text class="subtitle">AI 智能人生管理助手</text>
		</view>
	<view class="description">
			<text class="desc-text">让 AI 帮你规划人生，实现目标</text>
		</view>
		<view class="btn-group">
			<button class="primary-btn" @click="handleStart">开始使用</button>
			<button class="secondary-btn" @click="handleLogin">登录</button>
		</view>
	</view>
</template>

<script>
	import { mapGetters } from 'vuex'

	export default {
		data() {
			return {
				title: '托管人生'
			}
		},
		computed: {
			...mapGetters('user', ['isLoggedIn'])
		},
		onLoad() {
			// 检查登录状态
			if (this.isLoggedIn) {
				// 登录后跳转到目标页（不是 TabBar 切换）
				uni.redirectTo({
					url: '/pages/goals/goals'
				})
			}
		},
		methods: {
			handleStart() {
				uni.navigateTo({
					url: '/pages/register/register'
				});
			},
			handleLogin() {
				uni.navigateTo({
					url: '/pages/login/login'
				});
			}
		}
	}
</script>

<style>
	.content {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 40rpx;
		min-height: 100vh;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	}

	.welcome-section {
		margin-top: 100rpx;
		margin-bottom: 60rpx;
	}

	.title {
		font-size: 72rpx;
		font-weight: bold;
		color: #ffffff;
		display: block;
		text-align: center;
		margin-bottom: 20rpx;
	}

	.subtitle {
		font-size: 32rpx;
		color: rgba(255, 255, 255, 0.8);
		display: block;
		text-align: center;
	}

	.description {
		margin-bottom: 100rpx;
	}

	.desc-text {
		font-size: 28rpx;
		color: rgba(255, 255, 255, 0.9);
	}

	.btn-group {
		display: flex;
		flex-direction: column;
		width: 100%;
		gap: 30rpx;
	}

	.primary-btn {
		width: 100%;
		height: 100rpx;
		background-color: #ffffff;
		color: #667eea;
		border-radius: 50rpx;
		font-size: 32rpx;
		font-weight: bold;
		border: none;
	}

	.secondary-btn {
		width: 100%;
		height: 100rpx;
		background-color: rgba(255, 255, 255, 0.2);
		color: #ffffff;
		border-radius: 50rpx;
		font-size: 32rpx;
		border: 2rpx solid rgba(255, 255, 255, 0.5);
	}
</style>
