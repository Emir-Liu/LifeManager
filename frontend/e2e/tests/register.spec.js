import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { RegisterPage } from '../pages/RegisterPage';

test.describe('注册功能测试', () => {
  let registerPage;
  
  test.beforeEach(async ({ page }) => {
    registerPage = new RegisterPage(page);
    await registerPage.goto();
  });
  
  test('成功注册 - 完整信息', async ({ page }) => {
    const timestamp = Date.now();
    await registerPage.register(
      `testuser${timestamp}`,
      'test@example.com',
      'password123'
    );
    
    // 验证跳转到目标管理页
    await expect(page).toHaveURL(/\/pages\/goals\/goals/);
  });
  
  test('注册失败 - 用户名已存在', async ({ page }) => {
    await registerPage.register('testuser', 'test@example.com', 'password123');
    
    // 验证显示错误提示
    await expect(registerPage.errorMessage).toBeVisible();
  });
  
  test('表单验证 - 密码不一致', async ({ page }) => {
    await registerPage.usernameInput.fill('newuser');
    await registerPage.emailInput.fill('new@example.com');
    await registerPage.passwordInput.fill('password123');
    await registerPage.confirmPasswordInput.fill('password456');
    await registerPage.submitButton.click();
    
    // 验证显示错误提示
    await expect(registerPage.passwordError).toBeVisible();
  });
  
  test('表单验证 - 无效的邮箱格式', async ({ page }) => {
    await registerPage.usernameInput.fill('newuser');
    await registerPage.emailInput.fill('invalid-email');
    await registerPage.passwordInput.fill('password123');
    await registerPage.confirmPasswordInput.fill('password123');
    await registerPage.submitButton.click();
    
    // 验证显示错误提示
    await expect(registerPage.emailError).toBeVisible();
  });
  
  test('密码强度验证 - 弱密码', async ({ page }) => {
    await registerPage.usernameInput.fill('newuser');
    await registerPage.emailInput.fill('new@example.com');
    await registerPage.passwordInput.fill('123');
    await registerPage.confirmPasswordInput.fill('123');
    await registerPage.submitButton.click();
    
    // 验证显示密码强度提示
    await expect(registerPage.passwordStrength).toBeVisible();
  });
  
  test('跳转到登录页面', async ({ page }) => {
    await registerPage.clickLogin();
    
    // 验证跳转到登录页
    await expect(page).toHaveURL(/\/pages\/login\/login/);
  });
});
