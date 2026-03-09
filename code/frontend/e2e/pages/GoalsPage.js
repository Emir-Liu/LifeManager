export class GoalsPage {
  constructor(page) {
    this.page = page;
    this.statsCard = page.locator('.stats-card');
    this.totalStat = page.getByText('总目标');
    this.inProgressStat = page.getByText('进行中');
    this.completedStat = page.getByText('已完成');
    
    // 筛选标签
    this.tabAll = page.getByText('全部');
    this.tabInProgress = page.getByText('进行中');
    this.tabCompleted = page.getByText('已完成');
    
    // 目标卡片
    this.goalCards = page.locator('.goal-card');
    this.emptyState = page.locator('.empty-state');
    
    // AI规划按钮
    this.aiPlanningBtn = page.getByText('AI 智能规划');
    this.conversationBtn = page.getByText('对话规划');
    
    // 创建按钮
    this.createBtn = page.locator('.create-btn');
  }
  
  async goto() {
    await this.page.goto('/pages/goals/goals');
  }
  
  async filterByTab(tabName) {
    await this.page.getByText(tabName).click();
  }
  
  async clickGoalCard(index = 0) {
    await this.goalCards.nth(index).click();
  }
  
  async clickCreateButton() {
    await this.createBtn.click();
  }
  
  async clickAIPlanning() {
    await this.aiPlanningBtn.click();
  }
  
  async getGoalCount() {
    return await this.goalCards.count();
  }
  
  async hasEmptyState() {
    return await this.emptyState.isVisible();
  }
  
  async getStats() {
    const total = await this.page.locator('.stat-value').first().textContent();
    const inProgress = await this.page.locator('.stat-value').nth(1).textContent();
    const completed = await this.page.locator('.stat-value').nth(2).textContent();
    return { total, inProgress, completed };
  }
}
