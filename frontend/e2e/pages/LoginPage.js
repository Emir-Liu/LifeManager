// e2e/pages/LoginPage.js
export class LoginPage {
  constructor(page) {
    this.page = page;
    this.usernameInput = page.locator('input[placeholder="请输入账号"]');
    this.passwordInput = page.locator('input[type="password"][placeholder="请输入密码"]');
    this.loginButton = page.locator('button.login-btn');
    this.registerLink = page.locator('text=还没有账号？去注册');
    this.errorToast = page.locator('.uni-toast');
  }

  async goto() {
    await this.page.goto('/pages/login/login');
  }

  async login(username, password) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }

  async waitForSuccess() {
    await this.page.waitForTimeout(1500);
  }
}
