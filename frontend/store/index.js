import { createPinia } from 'pinia'

const pinia = createPinia()

export default pinia

// 导出所有 stores
export { useUserStore } from './user.js'
export { useGoalsStore } from './goals.js'
export { usePlansStore } from './plans.js'
export { useTasksStore } from './tasks.js'
export { useConversationStore } from './conversation.js'
export { useTimePreferencesStore } from './timePreferences.js'
