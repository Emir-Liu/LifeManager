<script>
	export default {
		onLaunch: function() {
			console.log('App Launch')
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		}
	}
</script>

<style>
	/*每个页面公共css */
	@import './static/styles/variables.css';
	@import './static/styles/global.css';

	/* 全局响应式设计 */
	page {
		font-size: var(--font-size);
	}

	/* 移动端适配 */
	@media screen and (max-width: 768px) {
		.container {
			padding: var(--spacing) var(--spacing-sm);
		}

		.card {
			padding: var(--spacing-md);
			border-radius: var(--radius-md);
		}

		.btn {
			padding: var(--spacing-sm) var(--spacing);
		}

		.btn-lg {
			padding: var(--spacing) var(--spacing-md);
			font-size: var(--font-size-md);
		}

		.text-xl {
			font-size: var(--font-size-lg);
		}

		.text-2xl {
			font-size: var(--font-size-xl);
		}
	}

	/* 平板适配 */
	@media screen and (min-width: 769px) and (max-width: 1024px) {
		.container {
			max-width: var(--container-md);
		}
	}

	/* 桌面适配 */
	@media screen and (min-width: 1025px) {
		.container {
			max-width: var(--container-lg);
		}
	}
</style>
