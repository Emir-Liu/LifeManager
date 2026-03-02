/**
 * 任务卡片组件单元测试
 */
import { mount } from '@vue/test-utils'
import TaskCard from '@/components/TaskCard.vue'

describe('TaskCard 组件', () => {
  const mockTask = {
    id: 1,
    title: '测试任务',
    description: '这是测试任务描述',
    due_date: '2026-06-30',
    completed: false,
    estimated_hours: 2,
    stage_name: '阶段1',
    goal_title: '测试目标'
  }

  it('正确渲染任务信息', () => {
    const wrapper = mount(TaskCard, {
      propsData: {
        task: mockTask
      }
    })

    expect(wrapper.text()).toContain('测试任务')
    expect(wrapper.text()).toContain('预计 2 小时')
  })

  it('未完成任务显示正确状态', () => {
    const wrapper = mount(TaskCard, {
      propsData: {
        task: mockTask
      }
    })

    expect(wrapper.find('.checkbox.checked').exists()).toBe(false)
  })

  it('已完成任务显示正确状态', () => {
    const completedTask = {
      ...mockTask,
      completed: true
    }

    const wrapper = mount(TaskCard, {
      propsData: {
        task: completedTask
      }
    })

    expect(wrapper.find('.checkbox.checked').exists()).toBe(true)
    expect(wrapper.find('.task-title.completed').exists()).toBe(true)
  })

  it('点击任务卡片触发详情事件', async () => {
    const wrapper = mount(TaskCard, {
      propsData: {
        task: mockTask
      }
    })

    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
    expect(wrapper.emitted('click')[0]).toEqual([mockTask.id])
  })

  it('点击复选框触发完成事件', async () => {
    const wrapper = mount(TaskCard, {
      propsData: {
        task: mockTask
      }
    })

    const checkbox = wrapper.find('.checkbox')
    await checkbox.trigger('click')

    expect(wrapper.emitted('complete')).toBeTruthy()
    expect(wrapper.emitted('complete')[0]).toEqual([mockTask.id])
  })

  it('点击开始按钮触发开始事件', async () => {
    const wrapper = mount(TaskCard, {
      propsData: {
        task: mockTask
      }
    })

    const button = wrapper.find('.action-btn')
    await button.trigger('click')

    expect(wrapper.emitted('start')).toBeTruthy()
    expect(wrapper.emitted('start')[0]).toEqual([mockTask.id])
  })

  it('已完成任务不显示开始按钮', () => {
    const completedTask = {
      ...mockTask,
      completed: true
    }

    const wrapper = mount(TaskCard, {
      propsData: {
        task: completedTask
      }
    })

    expect(wrapper.find('.action-btn').exists()).toBe(false)
  })
})

describe('GoalCard 组件', () => {
  const mockGoal = {
    id: 1,
    title: '测试目标',
    description: '这是测试目标描述',
    status: 'in_progress',
    progress: 50,
    deadline: '2026-12-31'
  }

  it('正确渲染目标信息', () => {
    const wrapper = mount(GoalCard, {
      propsData: {
        goal: mockGoal
      }
    })

    expect(wrapper.text()).toContain('测试目标')
    expect(wrapper.text()).toContain('进度: 50%')
  })

  it('显示正确的状态标签', () => {
    const wrapper = mount(GoalCard, {
      propsData: {
        goal: mockGoal
      }
    })

    expect(wrapper.find('.goal-status.in_progress').exists()).toBe(true)
  })

  it('点击目标卡片触发详情事件', async () => {
    const wrapper = mount(GoalCard, {
      propsData: {
        goal: mockGoal
      }
    })

    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
    expect(wrapper.emitted('click')[0]).toEqual([mockGoal.id])
  })
})

describe('PlanViewer 组件', () => {
  const mockPlan = {
    stages: [
      {
        name: '阶段1',
        order: 1,
        tasks: [
          { title: '任务1', estimated_hours: 2, order: 1 },
          { title: '任务2', estimated_hours: 1, order: 2 }
        ]
      },
      {
        name: '阶段2',
        order: 2,
        tasks: [
          { title: '任务3', estimated_hours: 3, order: 1 }
        ]
      }
    ]
  }

  it('正确渲染规划阶段', () => {
    const wrapper = mount(PlanViewer, {
      propsData: {
        plan: mockPlan
      }
    })

    const stages = wrapper.findAll('.stage')
    expect(stages.length).toBe(2)
  })

  it('正确渲染阶段中的任务', () => {
    const wrapper = mount(PlanViewer, {
      propsData: {
        plan: mockPlan
      }
    })

    expect(wrapper.text()).toContain('任务1')
    expect(wrapper.text()).toContain('任务2')
    expect(wrapper.text()).toContain('任务3')
  })

  it('显示总工时和任务数', () => {
    const wrapper = mount(PlanViewer, {
      propsData: {
        plan: mockPlan
      }
    })

    expect(wrapper.text()).toContain('3个任务')
    expect(wrapper.text()).toContain('6小时')
  })

  it('点击任务触发任务选择事件', async () => {
    const wrapper = mount(PlanViewer, {
      propsData: {
        plan: mockPlan
      }
    })

    const tasks = wrapper.findAll('.task-item')
    await tasks[0].trigger('click')

    expect(wrapper.emitted('task-select')).toBeTruthy()
  })

  it('点击确认按钮触发确认事件', async () => {
    const wrapper = mount(PlanViewer, {
      propsData: {
        plan: mockPlan
      }
    })

    const confirmBtn = wrapper.find('.confirm-btn')
    await confirmBtn.trigger('click')

    expect(wrapper.emitted('confirm')).toBeTruthy()
  })
})

describe('StatusBadge 组件', () => {
  it('正确显示进行中状态', () => {
    const wrapper = mount(StatusBadge, {
      propsData: {
        status: 'in_progress'
      }
    })

    expect(wrapper.find('.badge.in_progress').exists()).toBe(true)
    expect(wrapper.text()).toContain('进行中')
  })

  it('正确显示已完成状态', () => {
    const wrapper = mount(StatusBadge, {
      propsData: {
        status: 'completed'
      }
    })

    expect(wrapper.find('.badge.completed').exists()).toBe(true)
    expect(wrapper.text()).toContain('已完成')
  })

  it('正确显示规划中状态', () => {
    const wrapper = mount(StatusBadge, {
      propsData: {
        status: 'planning'
      }
    })

    expect(wrapper.find('.badge.planning').exists()).toBe(true)
    expect(wrapper.text()).toContain('规划中')
  })
})

describe('ProgressCircle 组件', () => {
  it('正确渲染进度百分比', () => {
    const wrapper = mount(ProgressCircle, {
      propsData: {
        progress: 50
      }
    })

    expect(wrapper.find('.progress-text').text()).toBe('50%')
  })

  it('正确渲染进度圆环', () => {
    const wrapper = mount(ProgressCircle, {
      propsData: {
        progress: 75
      }
    })

    const circle = wrapper.find('svg circle.progress')
    expect(circle.attributes('stroke-dashoffset')).toBeDefined()
  })

  it('0进度显示灰色', () => {
    const wrapper = mount(ProgressCircle, {
      propsData: {
        progress: 0
      }
    })

    expect(wrapper.find('.progress-circle').classes()).toContain('gray')
  })

  it('100进度显示绿色', () => {
    const wrapper = mount(ProgressCircle, {
      propsData: {
        progress: 100
      }
    })

    expect(wrapper.find('.progress-circle').classes()).toContain('success')
  })
})
