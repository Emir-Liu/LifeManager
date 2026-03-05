import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { GoalsPage } from '../pages/GoalsPage';
import { GoalDetailPage } from '../pages/GoalDetailPage';

test.describe('目标管理功能测试', () => {
  let goalsPage;
  let loginPage;
  
  test.beforeEach(async ({ page, context }) => {
    loginPage = new LoginPage(page);
    goalsPage = new GoalsPage(page);
    
    // 登录
    await loginPage.goto();
    await loginPage.login('testuser', 'password123');
    await page.waitForURL(/\/pages\/goals\/goals/);
  });
  
  test('查看目标列表', async ({ page }) => {
    const goalCount = await goalsPage.getGoalCount();
    
    // 验证统计信息
    const stats = await goalsPage.getStats();
    expect(stats.total).toBeTruthy();
    
    // 验证目标卡片显示
    if (goalCount > 0) {
      await expect(goalsPage.goalCards.first()).toBeVisible();
    } else {
      await expect(goalsPage.emptyState).toBeVisible();
    }
  });
  
  test('筛选目标 - 进行中', async ({ page }) => {
    await goalsPage.filterByTab('进行中');
    await page.waitForTimeout(500);
    
    // 验证URL更新
    await expect(page).toHaveURL(/.*currentTab=in_progress/);
  });
  
  test('筛选目标 - 已完成', async ({ page }) => {
    await goalsPage.filterByTab('已完成');
    await page.waitForTimeout(500);
    
    // 验证URL更新
    await expect(page).toHaveURL(/.*currentTab=completed/);
  });
  
  test('查看目标详情', async ({ page }) => {
    const goalCount = await goalsPage.getGoalCount();
    if (goalCount === 0) {
      test.skip();
    }
    
    await goalsPage.clickGoalCard(0);
    await page.waitForTimeout(500);
    
    // 验证跳转到详情页
    await expect(page).toHaveURL(/\/pages\/goals\/detail/);
    await expect(page.locator('.goal-title')).toBeVisible();
  });
  
  test('完成目标', async ({ page }) => {
    const goalCount = await goalsPage.getGoalCount();
    if (goalCount === 0) {
      test.skip();
    }
    
    await goalsPage.clickGoalCard(0);
    await page.waitForTimeout(500);
    
    const detailPage = new GoalDetailPage(page);
    const goalInfo = await detailPage.getGoalInfo();
    
    // 点击完成按钮
    await detailPage.clickComplete();
    await page.waitForTimeout(1000);
    
    // 验证状态更新
    const updatedInfo = await detailPage.getGoalInfo();
    // 这里根据实际业务逻辑验证
  });
  
  test('删除目标', async ({ page }) => {
    const initialCount = await goalsPage.getGoalCount();
    if (initialCount === 0) {
      test.skip();
    }
    
    await goalsPage.clickGoalCard(0);
    await page.waitForTimeout(500);
    
    const detailPage = new GoalDetailPage(page);
    await detailPage.clickDelete();
    await page.waitForTimeout(1000);
    
    // 返回列表页验证
    await page.goBack();
    await page.waitForTimeout(500);
    
    const finalCount = await goalsPage.getGoalCount();
    expect(finalCount).toBe(initialCount - 1);
  });
  
  test('生成AI规划', async ({ page }) => {
    const goalCount = await goalsPage.getGoalCount();
    if (goalCount === 0) {
      test.skip();
    }
    
    await goalsPage.clickGoalCard(0);
    await page.waitForTimeout(500);
    
    const detailPage = new GoalDetailPage(page);
    await detailPage.clickGeneratePlan();
    await page.waitForTimeout(2000);
    
    // 验证显示loading
    await expect(page.getByText('AI 思考中...')).toBeVisible();
    // 验证跳转到规划详情页
    await page.waitForURL(/\/pages\/plans\/detail/, { timeout: 10000 });
  });
  
  test('AI智能规划 - 对话式规划', async ({ page }) => {
    await goalsPage.clickAIPlanning();
    await page.waitForTimeout(500);
    
    // 验证跳转到对话页面
    await expect(page).toHaveURL(/\/pages\/conversation\/conversation/);
    await expect(page.getByText('对话规划')).toBeVisible();
  });
});
