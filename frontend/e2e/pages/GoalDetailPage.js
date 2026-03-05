export class GoalDetailPage {
  constructor(page) {
    this.page = page;
    this.goalTitle = page.locator('.goal-title');
    this.goalDescription = page.locator('.goal-desc');
    this.progressValue = page.locator('.progress-value');
    this.progressBar = page.locator('.progress-fill');
    
    // 信息卡片
    this.priorityLabel = page.getByText('优先级');
    this.priorityValue = page.locator('.info-value.priority');
    this.typeLabel = page.getByText('类型');
    this.deadlineLabel = page.getByText('截止时间');
    
    // AI规划卡片
    this.planCard = page.locator('.plan-card');
    this.generatePlanBtn = page.getByText('生成规划');
    
    // 操作按钮
    this.completeBtn = page.getByText('完成目标');
    this.editBtn = page.getByText('编辑目标');
    this.deleteBtn = page.getByText('删除目标');
  }
  
  async goto(goalId) {
    await this.page.goto(`/pages/goals/detail?id=${goalId}`);
  }
  
  async getGoalInfo() {
    const title = await this.goalTitle.textContent();
    const description = await this.goalDescription.textContent();
    const progress = await this.progressValue.textContent();
    return { title, description, progress };
  }
  
  async clickComplete() {
    await this.completeBtn.click();
    // 确认弹窗
    await this.page.waitForTimeout(500);
  }
  
  async clickDelete() {
    await this.deleteBtn.click();
    // 确认删除弹窗
    await this.page.on('dialog', async dialog => {
      await dialog.accept();
    });
  }
  
  async clickGeneratePlan() {
    await this.generatePlanBtn.click();
  }
  
  async getProgress() {
    return await this.progressValue.textContent();
  }
}
