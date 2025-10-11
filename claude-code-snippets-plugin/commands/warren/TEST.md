# Testing Protocol for Feature Implementation

**VERIFICATION_HASH:** `17cb705963a43703`


After implementing ANY feature, follow this comprehensive testing protocol:

## 1. Fix All Existing Test Errors

Before writing new tests, ensure the codebase is clean:

```bash
# Type check (MUST pass with zero errors)
npm run type-check

# If errors exist, fix them before proceeding
# Do NOT skip pre-existing errors
```

## 2. Build Verification

```bash
# Build must complete with zero warnings
npm run build

# Check build output for:
# - Zero TypeScript errors
# - Zero build warnings
# - All imports resolve correctly
```

## 3. Write Comprehensive Tests

### Unit Tests (for services/hooks/utilities)

Create unit tests in `tests/unit/` following existing patterns:

```typescript
// Example: tests/unit/shared/services/myService.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { myService } from '@/shared/services/myService';

describe('myService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should handle feature X correctly', () => {
    // Test implementation
  });

  // Cover ALL functionality:
  // - Happy paths
  // - Error cases
  // - Edge cases
  // - Boundary conditions
});
```

### E2E Tests (for user-facing features)

Create E2E tests in `tests/e2e/` using Playwright:

```typescript
// Example: tests/e2e/my-feature.spec.ts
import { test, expect } from '../fixtures/extension';

test.describe('My Feature', () => {
  test('should work correctly', async ({ context, extensionId }) => {
    const page = await context.newPage();
    await page.goto('chrome-extension://' + extensionId + '/src/canvas/index.html');

    // Test user workflow
    // Verify behavior
    // Check persistence

    await page.close();
  });
});
```

## 4. Run All Tests

```bash
# Unit tests (fast)
npm test

# E2E tests (comprehensive)
npm run test:e2e

# Fix ANY failures before proceeding
```

## 5. Add Tests to Prevent Regressions

**CRITICAL**: Your new tests must be integrated into the existing test suite:

### For Unit Tests:
- Add test file to appropriate directory in `tests/unit/`
- Ensure it runs with `npm test`
- Update test count in documentation if needed

### For E2E Tests:
- Add test file to `tests/e2e/`
- Ensure it runs with `npm run test:e2e`
- Follow naming convention: `{feature-name}.spec.ts`
- Add test description to CLAUDE.md if significant

### Test Coverage Requirements:
- **Shared Services**: 100% coverage (REQUIRED)
- **Shared Hooks**: 80%+ coverage (target)
- **Components**: Critical paths covered
- **E2E**: User workflows covered

## 6. Use feature-implementation-tester-v2 Agent

For complex features, use the specialized testing agent:

```typescript
// Launch the agent with Task tool
{
  "subagent_type": "feature-implementation-tester-v2",
  "description": "Test my new feature",
  "prompt": `
    I have implemented [feature description].

    Please verify this feature ACTUALLY works through comprehensive validation:
    1. Type check and build verification
    2. Unit tests for all services/hooks
    3. E2E tests for user workflows
    4. Compilation and runtime validation
    5. Evidence-based testing (not just presence checks)

    Files changed:
    - [list files]

    Expected behavior:
    - [describe expected behavior]

    Please report:
    - All test results
    - Any failures or issues
    - Recommendations for additional tests
  `
}
```

## 7. Manual Testing Verification

After automated tests pass, perform manual verification:

### Extension Reload:
1. `npm run build`
2. Navigate to `chrome://extensions`
3. Click reload (🔄) on extension
4. Refresh any open Canvas pages

### Feature Verification:
- [ ] Feature works as expected
- [ ] No console errors
- [ ] No console warnings
- [ ] Existing features still work (spot check)
- [ ] Cross-context sync works (if applicable)

### Performance Check:
- [ ] No noticeable lag
- [ ] Debouncing works correctly (if applicable)
- [ ] Storage operations are efficient

## 8. Documentation

Update documentation if needed:

- [ ] Update CLAUDE.md with feature details
- [ ] Add usage examples
- [ ] Document any new configuration
- [ ] Update test coverage stats

## 9. Commit Message Template

```
feat: [Brief feature description]

- [Change 1]
- [Change 2]
- [Change 3]

Tests:
- Added [N] unit tests in [file]
- Added [N] E2E tests in [file]
- All tests passing ✅
- Zero build warnings ✅
- Zero TypeScript errors ✅

Coverage:
- [Service/Component]: [N] tests, [X]% coverage
```

## Quick Test Commands Reference

```bash
# Fast verification (< 1 minute)
npm run type-check && npm run build

# Medium verification (< 5 minutes)
npm run type-check && npm run build && npm test

# Full verification (< 10 minutes)
npm run type-check && npm run build && npm test && npm run test:e2e

# Specific feature test
npm run test:e2e:headed tests/e2e/my-feature.spec.ts

# Watch mode for development
npm run test:watch
```

## Common Testing Pitfalls to Avoid

❌ **Don't skip pre-existing test errors** - Fix them first
❌ **Don't write tests without running them** - Verify they pass
❌ **Don't ignore build warnings** - Fix all warnings
❌ **Don't forget cross-context testing** - Test Canvas + Side Panel sync
❌ **Don't skip manual verification** - Automated tests don't catch everything
❌ **Don't forget regression prevention** - Add tests to prevent future breaks

✅ **Do fix all errors before new tests**
✅ **Do run full test suite before committing**
✅ **Do add comprehensive test coverage**
✅ **Do integrate tests into existing suite**
✅ **Do use feature-implementation-tester-v2 for complex features**
✅ **Do manual verification after automated tests**

---

**Verification Hash**: TEST-SNIPPET-v1-f8a9c2e4d6b7

This snippet ensures thorough testing and regression prevention for all feature implementations.
