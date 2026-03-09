// e2e/pages/RegisterPage.js
export class RegisterPage {
  constructor(page) {
    this.page = page;
    this.usernameInput = page.locator('input[placeholder="请输入账号"]').first();
    this.emailInput = page.locator('input[type="email"]');
    this.passwordInput = page.locator('input[type="password"]').first();
    this.confirmPasswordInput = page.locator('input[placeholder="请再次输入密码"]');
    this.registerButton = page.locator('button.register-btn');
    this.loginLink = page.locator('text=立即登录');
  }

  async goto() {
    await this.page.goto('/pages/register/register');
  }

  async register({ username, email, password, confirmPassword }) {
    await this.usernameInput.fill(username);
    if (email) {
      await this.emailInput.fill(email);
    }
    await this.passwordInput.fill(password);
    await this.confirmPasswordInput.fill(confirmPassword);
    await this.registerButton.click();
  }

  async waitForSuccess() {
    await this.page.waitForTimeout(2000);
  }
}
