# Playwright Chrome Extension Testing

## Critical: Extension Loading Pattern

**Standard Playwright CANNOT load Chrome extensions.** Use `launchPersistentContext`:

```javascript
import { chromium } from 'playwright';
import path from 'path';

const extensionPath = path.join(__dirname, 'dist');
const context = await chromium.launchPersistentContext('', {
  headless: false,  // REQUIRED: Extensions need headed mode
  args: [
    '--disable-extensions-except=' + extensionPath,
    '--load-extension=' + extensionPath,
  ],
});

const page = await context.newPage();
await page.goto('https://example.com');
// Extension is loaded!
```

## Key Parameters

- First arg `''`: Empty string = fresh temporary profile
- `headless: false`: Extensions ONLY work in headed mode
- `--disable-extensions-except`: Disable all except this path
- `--load-extension`: Load unpacked extension

## Getting Extension ID

Extension ID is randomly generated (e.g., `mkdbacmghakikjkemcahonodffmphffp`):

```javascript
// Method 1: From service worker
const serviceWorkers = context.serviceWorkers();
const extId = serviceWorkers[0].url().match(/chrome-extension:\/\/([a-z]+)\//)?.[1];

// Method 2: From page context
const extId = await page.evaluate(() => chrome.runtime.id);
```

## Accessing Extension Pages

```javascript
const canvasUrl = `chrome-extension://${extId}/src/canvas/index.html`;
await page.goto(canvasUrl);
```

## Testing chrome.storage

```javascript
const result = await page.evaluate(async () => {
  const data = await chrome.storage.local.get(['cards']);
  return data.cards || [];
});
```

## Console Monitoring

```javascript
page.on('console', msg => console.log('[Console]', msg.text()));
page.on('pageerror', error => console.error('[Error]', error.message));
```

## Path Resolution (Test Scripts)

Test scripts in subdirectories must navigate up:

```javascript
// test-scripts/test.mjs
const ext = path.join(__dirname, '..', 'dist');  // Go up one level

// tests/e2e/test.spec.ts
const ext = path.join(__dirname, '../..', 'dist'); // Go up two levels
```

## Playwright Test Fixture Pattern

```typescript
// tests/fixtures/extension.ts
import { test as base, chromium, type BrowserContext } from '@playwright/test';

type ExtensionFixtures = {
  context: BrowserContext;
  extensionId: string;
};

export const test = base.extend<ExtensionFixtures>({
  context: async ({}, use) => {
    const extensionPath = path.join(__dirname, '../../dist');
    const context = await chromium.launchPersistentContext('', {
      headless: false,
      args: [
        `--disable-extensions-except=${extensionPath}`,
        `--load-extension=${extensionPath}`,
      ],
    });
    await use(context);
    await context.close();
  },

  extensionId: async ({ context }, use) => {
    let [background] = context.serviceWorkers();
    if (!background) {
      background = await context.waitForEvent('serviceworker');
    }
    const extensionId = background.url().split('/')[2];
    await use(extensionId);
  },
});
```

## Limitations & Workarounds

**Limitations:**
- Headed mode only (can't run headless)
- Slower tests (browser UI overhead)
- Random extension ID per run
- Can't access chrome://extensions page

**Workarounds:**
- Run in CI with Xvfb (virtual display)
- Extract ID dynamically from service worker
- Navigate directly to chrome-extension:// URLs
- Fresh context per test to simulate reload
