import { createStore } from 'vuex'
import user from './user.js'
import goals from './goals.js'
import plans from './plans.js'
import tasks from './tasks.js'

const store = createStore({
  modules: {
    user,
    goals,
    plans,
    tasks
  }
})

export default store
