================================
PLAYWRIGHT TESTING BEST PRACTICES
================================

**VERIFICATION_HASH:** `89e8aab6db8a617c`

## SELECTOR STRATEGIES

### Priority Order (Most to Least Preferred)

1. **Semantic Selectors** (BEST)
   page.getByRole('button', { name: 'Submit' })
   page.getByLabel('Username')
   page.getByPlaceholder('Enter email')
   page.getByText('Welcome')

2. **data-testid Attributes** (STABLE)
   page.getByTestId('submit-button')

3. **CSS/XPath** (LAST RESORT - Fragile)
   page.locator('.my-class')
   page.locator('//div[@class="content"]')

### Selector Best Practices

✅ DO:
- Use semantic selectors (getByRole, getByLabel, getByPlaceholder)
- Use data-testid for custom elements without semantic roles
- Create stable, meaningful test IDs
- Use multiple fallback selectors: page.locator('.product-list, .products, [data-testid="product-list"]')

❌ AVOID:
- Dynamic selectors: div:nth-child(3)
- CSS classes that may change: .btn-primary.submit-button
- Language-dependent text selectors
- Fragile XPath expressions

## ASSERTIONS & WAITING

### Web-First Assertions (Auto-Wait)

✅ CORRECT:
await expect(page.getByText('welcome')).toBeVisible();
await expect(successMessage).toContainText('Order confirmed!');
await expect(page.getByTestId('status')).toHaveText('Success');

❌ WRONG:
expect(await page.getByText('welcome').isVisible()).toBe(true);

### Wait Strategies

✅ CORRECT:
await page.waitForSelector('[data-testid="success-message"]');
await page.waitForResponse('**/api/save');
await page.waitForURL('/dashboard');
await page.waitForLoadState('networkidle');

❌ AVOID:
await page.waitForTimeout(5000);  // Arbitrary waits = flaky tests

## FIXTURES & PAGE OBJECTS

### Custom Fixtures Pattern

// fixtures.ts
import { test as base } from '@playwright/test';
import { TodoPage } from './pages/todo-page';
import { SettingsPage } from './pages/settings-page';

type MyFixtures = {
  todoPage: TodoPage;
  settingsPage: SettingsPage;
};

export const test = base.extend<MyFixtures>({
  todoPage: async ({ page }, use) => {
    const todoPage = new TodoPage(page);
    await todoPage.goto();
    await todoPage.addToDo('item1');
    await use(todoPage);
    await todoPage.removeAll();  // Cleanup
  },

  settingsPage: async ({ page }, use) => {
    await use(new SettingsPage(page));
  },
});

export { expect } from '@playwright/test';

### Page Object Model

// pages/todo-page.ts
export class TodoPage {
  private page: Page;
  private addButton: Locator;
  private todoInput: Locator;

  constructor(page: Page) {
    this.page = page;
    this.addButton = page.getByRole('button', { name: 'Add' });
    this.todoInput = page.getByPlaceholder('What needs to be done?');
  }

  async goto() {
    await this.page.goto('/todo');
  }

  async addToDo(text: string) {
    await this.todoInput.fill(text);
    await this.addButton.click();
    await expect(this.page.getByText(text)).toBeVisible();
  }
}

### Authentication Fixtures

export const test = base.extend<MyFixtures>({
  adminPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      storageState: 'playwright/.auth/admin.json'
    });
    const adminPage = new AdminPage(await context.newPage());
    await use(adminPage);
    await context.close();
  },
});

## TEST ORGANIZATION

### Project Structure

tests/
├── pages/                    # Page Object Models
│   ├── base.ts              # Base page class
│   ├── authentication.page.ts
│   ├── dashboard.page.ts
│   └── index.ts             # Exports
├── fixtures/                 # Custom fixtures
│   ├── ui.fixtures.ts
│   ├── api.fixtures.ts
│   └── core.fixtures.ts
├── scenarios/                # Test files
│   ├── auth.spec.ts
│   └── checkout.spec.ts
└── playwright.config.ts

### Parallel Execution

// Run tests in parallel (default)
import { defineConfig } from '@playwright/test';

export default defineConfig({
  fullyParallel: true,
  workers: process.env.CI ? 2 : undefined,
});

// Force parallel in specific suite
test.describe.configure({ mode: 'parallel' });

// Force serial for dependent tests
test.describe.configure({ mode: 'serial' });

### Test Tagging

// Use tags for organization
test('critical path test @critical', async ({ page }) => {});
test('requires mocking @mocking', async ({ page }) => {});

// Run specific tests
// npx playwright test --grep @critical
// npx playwright test --grep-invert @mocking

## TEST ISOLATION

### Each Test Gets Fresh Context

// Automatic isolation - no setup needed
test('test 1', async ({ page }) => {
  // Fresh page, fresh context
});

test('test 2', async ({ page }) => {
  // Completely isolated from test 1
});

### Independent Tests

✅ CORRECT:
test1: creates user1 + asserts created
test2: (setup: creates user1) + logs in + asserts login
test3: (setup: creates user1 + login) + checkout + asserts checkout

❌ WRONG:
test1: creates user1
test2: logs in with user1 (depends on test1)
test3: checkout (depends on test1 and test2)

## SOFT ASSERTIONS

// Continue test even if assertion fails
await expect.soft(page.getByTestId('status')).toHaveText('Success');
await page.getByRole('link', { name: 'next page' }).click();
// Test continues even if status check failed

## API MOCKING

await page.route('/api/users', route => route.fulfill({
  status: 200,
  body: JSON.stringify(mockData),
  headers: { 'Content-Type': 'application/json' }
}));

await page.goto('https://example.com');

## DEBUGGING

### Visual Debugging

// Record videos
const context = await browser.newContext({
  recordVideo: { dir: 'videos/' }
});

// Screenshots on failure (auto in playwright.config.ts)
screenshot: 'only-on-failure'

// Trace viewer
await context.tracing.start({ screenshots: true, snapshots: true });
await context.tracing.stop({ path: 'trace.zip' });
// View: npx playwright show-trace trace.zip

### Test Naming

✅ DESCRIPTIVE:
test('submitting valid form shows success message', ...)
test('user can add item to cart and checkout', ...)

❌ VAGUE:
test('test1', ...)
test('form test', ...)

## COMMON ANTI-PATTERNS

❌ Arbitrary timeouts
await page.waitForTimeout(2000);

❌ Non-stable selectors
page.locator('div:nth-child(3)')
page.locator('.btn-primary')

❌ Testing implementation details
expect(await page.locator('.internal-class').count()).toBe(5);

❌ Non-idempotent tests
test('increment counter', ...) // Fails on second run

❌ External dependencies without mocking
// Don't call real payment APIs in tests

## PERFORMANCE

### Reuse Authentication State

// global-setup.ts
await page.goto('/login');
await page.fill('[name="username"]', 'admin');
await page.fill('[name="password"]', 'password');
await page.click('button[type="submit"]');
await page.context().storageState({ path: 'auth.json' });

// playwright.config.ts
use: { storageState: 'auth.json' }

### Parallel Workers

workers: process.env.CI ? 2 : undefined  // Adjust based on resources

## PLAYWRIGHT AGENTS (TASK TOOL)

Three specialized agents available in ~/.claude/agents-archive/ for comprehensive Playwright workflows:

### 1. playwright-test-planner (Green)
**When to use:** Creating comprehensive test plans for web applications

**What it does:**
- Navigates and explores your web application interactively
- Maps user flows and identifies critical paths
- Creates detailed test scenarios covering:
  - Happy path scenarios
  - Edge cases and boundary conditions
  - Error handling and validation
- Generates structured markdown test plans

**Example usage:**
"I need test scenarios for our checkout process at https://mystore.com/checkout"
→ Agent explores the page and creates comprehensive test plan document

### 2. playwright-test-generator (Blue)
**When to use:** Creating automated browser tests from test plans or requirements

**What it does:**
- Takes test plan/scenario and generates actual Playwright test code
- Executes steps in real-time using browser automation
- Generates robust test files with:
  - Best practice selectors
  - Proper step comments
  - Organized test structure
- Creates one test file per scenario

**Example usage:**
"Create a test that logs into my app at localhost:3000, then verifies dashboard loads"
→ Agent generates working Playwright test code

### 3. playwright-test-healer (Red)
**When to use:** Debugging and fixing failing Playwright tests

**What it does:**
- Runs tests to identify failures
- Debugs each failing test systematically
- Investigates root causes:
  - Changed selectors
  - Timing issues
  - Assertion failures
  - Application changes
- Fixes test code and verifies fixes work
- Iterates until tests pass

**Example usage:**
"The login test is failing, can you fix it?"
→ Agent debugs, identifies issue, fixes code, and verifies test passes

### Complete Workflow

1. **Plan** → Use playwright-test-planner to explore app and create test scenarios
2. **Generate** → Use playwright-test-generator to convert scenarios into test code
3. **Heal** → Use playwright-test-healer when tests break to debug and fix

**How to use agents:**
Use the Task tool with subagent_type parameter to launch these agents.

## QUICK REFERENCE

Semantic Selectors:  getByRole, getByLabel, getByPlaceholder, getByText
Stable Selectors:    getByTestId
Auto-Wait:           expect().toBeVisible() automatically waits
Avoid:               waitForTimeout, fragile CSS, nth-child
Fixtures:            Extend test, provide reusable setup/teardown
Page Objects:        Encapsulate page interactions
Parallel:            fullyParallel: true in config
Isolation:           Each test gets fresh context automatically
Mocking:             page.route() for API responses
Debugging:           Videos, screenshots, trace viewer
Agents:              planner (create scenarios) → generator (write tests) → healer (fix tests)

================================