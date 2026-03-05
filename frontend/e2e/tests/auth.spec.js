import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

test.describe('登录功能测试', () => {
  let loginPage;
  
  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto();
  });
  
  test('成功登录 - 正确的用户名和密码', async ({ page }) => {
    await loginPage.login('testuser', 'password123');
    
    // 验证跳转到目标管理页
    await expect(page).toHaveURL(/\/pages\/goals\/goals/);
    await expect(page.getByText('总目标')).toBeVisible();
  });
  
  test('登录失败 - 错误的密码', async ({ page }) => {
    await loginPage.login('testuser', 'wrongpassword');
    
    // 验证显示错误提示
    await expect(loginPage.errorMessage).toBeVisible();
  });
  
  test('表单验证 - 空的用户名', async ({ page }) => {
    await loginPage.passwordInput.fill('password123');
    await loginPage.submitButton.click();
    
    // 验证显示验证错误
    await expect(loginPage.usernameError).toBeVisible();
  });
  
  test('表单验证 - 空的密码', async ({ page }) => {
    await loginPage.usernameInput.fill('testuser');
    await loginPage.submitButton.click();
    
    // 验证显示验证错误
    await expect(loginPage.passwordError).toBeVisible();
  });
  
  test('跳转到注册页面', async ({ page }) => {
    await loginPage.clickRegister();
    
    // 验证跳转到注册页
    await expect(page).toHaveURL(/\/pages\/register\/register/);
  });
  
  test('记住密码功能', async ({ page }) => {
    await loginPage.rememberMeCheckbox.check();
    await loginPage.login('testuser', 'password123');
    
    // 重新访问登录页，验证是否填充
    await page.goto('/pages/login/login');
    await expect(loginPage.usernameInput).toHaveValue('testuser');
  });
});
