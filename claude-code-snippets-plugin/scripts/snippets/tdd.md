---
SNIPPET_NAME: TDD
ANNOUNCE_USAGE: true
---

**INSTRUCTION TO CLAUDE**: At the very beginning of your response, before any other content, you MUST announce which snippet(s) are active using this exact format:

📎 **Active Context**: TDD

If multiple snippets are detected (multiple ANNOUNCE_USAGE: true directives in different snippets), combine them into a single announcement:

📎 **Active Contexts**: snippet1, snippet2, snippet3

---

# Test-Driven Development (TDD) Guidelines

**VERIFICATION_HASH:** `ebc8b36cdd9efb51`

## Overview

You are to follow Test-Driven Development (TDD) methodology for all implementation tasks. TDD is a software development approach where you write tests before writing the actual code, ensuring high-quality, reliable, and maintainable software.

## The Red-Green-Refactor Cycle

TDD follows a repetitive three-phase cycle:

### 1. RED Phase - Write a Failing Test
- Write a test for the next bit of functionality you want to add
- The test should define a specific behavior or functionality that doesn't exist yet
- **The test MUST fail initially** - this confirms the test is actually checking something
- Keep tests simple and focused on a single aspect
- Think about edge cases and potential bugs before writing code

**Guidelines:**
- Each test should focus on ONE specific behavior
- Use descriptive test names that explain what behavior is being tested
- Avoid overly intricate tests - start with the simplest test possible
- Pick tests that are easy to implement and move you closer to your goal

### 2. GREEN Phase - Make It Pass
- Write the **minimum amount of code** necessary to make the test pass
- Focus solely on functionality, not perfection
- Don't worry about code quality yet - just make it work
- Be disciplined: write ONLY enough code to pass the current test

**Guidelines:**
- Resist the urge to implement extra features not covered by the test
- Keep moving forward and gaining confidence
- If you find yourself writing complex code, your test might be too ambitious

### 3. REFACTOR Phase - Clean It Up
- Refactor both new and old code to make it well-structured
- Improve code quality, remove duplication, apply best practices
- **CRITICAL:** Ensure all tests still pass after refactoring
- Do NOT change functionality or introduce breaking changes

**Guidelines:**
- Apply SOLID principles and design patterns where appropriate
- Eliminate code duplication (DRY principle)
- Improve naming, structure, and readability
- **NEVER skip this step** - it's the most commonly neglected but crucial phase

## Core TDD Principles

### 1. Write Tests First
**Always write the test before the implementation code.**

Benefits:
- Ensures the application is written for testability
- Guarantees every feature has tests
- Leads to deeper understanding of requirements early
- Forces you to think about the API and design before implementation

### 2. Test Behavior, Not Implementation
- Focus on **what** the code should do, not **how** it does it
- Tests should verify observable behavior and outcomes
- Avoid testing internal implementation details
- This allows safe refactoring without breaking tests

### 3. Keep Tests Small and Focused
- One test per behavior/requirement
- Tests should be independent of each other
- Improves readability, maintainability, and debugging
- Makes it clear what broke when a test fails

### 4. Incremental Development
- Take small steps - one test at a time
- Build up functionality gradually
- Each cycle should take minutes, not hours
- Commit working code frequently

## Best Practices for Modern TDD (2024-2025)

### Testing Strategy

1. **Start with the Simplest Test**
   - Begin with basic happy path scenarios
   - Gradually add edge cases and error conditions
   - Build complexity incrementally

2. **Use Meaningful Test Names**
   ```typescript
   // ❌ Bad
   test('test1', ...)

   // ✅ Good
   test('should return 401 when JWT token is expired', ...)
   test('should calculate total price including tax for multiple items', ...)
   ```

3. **Avoid Over-Mocking**
   - When every collaborator is mocked, refactors become painful
   - Prefer narrow integration points (seams)
   - Use contract tests that exercise real integrations where practical
   - Mock only external dependencies (APIs, databases, file systems)

4. **Integration with CI/CD**
   - Integrate test suite with development environment
   - Set up continuous integration pipelines to run tests automatically
   - Tests should run on every code change
   - Catch regressions early

5. **Test Coverage as a Guide, Not a Goal**
   - High coverage is a side effect of good TDD, not the objective
   - Focus on testing important behaviors
   - 100% coverage doesn't guarantee bug-free code

### Code Organization

1. **Separation of Concerns**
   - TDD naturally promotes modular, testable code
   - Keep business logic separate from infrastructure
   - Use dependency injection for better testability

2. **Follow SOLID Principles**
   - Single Responsibility: Each class/function has one reason to change
   - Open/Closed: Open for extension, closed for modification
   - Liskov Substitution: Subtypes must be substitutable
   - Interface Segregation: Many specific interfaces over one general
   - Dependency Inversion: Depend on abstractions, not concretions

### Team Collaboration

1. **Review Tests Together**
   - Share effective testing techniques
   - Catch bad testing habits early
   - Ensure consistent testing standards across the team

2. **Pair Programming on Complex Features**
   - One person writes the test, other writes the code
   - Rotate roles frequently
   - Improves code quality and knowledge sharing

## Common Pitfalls to Avoid

### ❌ Skipping the Refactor Step
**The most common TDD mistake.** Never neglect refactoring - it keeps code clean and maintainable.

### ❌ Writing Tests After Code
This defeats the purpose of TDD. Tests written after are often biased toward the implementation and miss edge cases.

### ❌ Testing Implementation Details
Tests should verify behavior, not how it's implemented. Implementation-focused tests break during refactoring even when behavior hasn't changed.

### ❌ Writing Overly Complex Tests
If a test is hard to write, the design might be wrong. Simplify your approach or break down the functionality.

### ❌ Not Running Tests Frequently
Run tests after every small change. Fast feedback is essential to TDD's effectiveness.

### ❌ Ignoring Failing Tests
Never commit code with failing tests. Either fix the code or fix the test - don't leave it broken.

### ❌ Writing Too Much Code at Once
Resist the urge to implement multiple features. Stay disciplined: one test, one minimal implementation, then refactor.

## Practical Implementation Guidelines

### When Starting a New Feature

1. **Understand Requirements Thoroughly**
   - Clarify acceptance criteria
   - Identify edge cases
   - Define expected behaviors

2. **Write Your First Test**
   ```
   Describe what you're testing
   → Write test that fails
   → Verify it fails for the right reason
   → Implement minimal code
   → Watch test pass
   → Refactor
   ```

3. **Build Incrementally**
   - Add one test at a time
   - Keep all tests passing
   - Commit frequently with passing tests

### Test Organization

```
tests/
├── unit/           # Fast, isolated tests
├── integration/    # Tests with real dependencies
└── e2e/           # End-to-end user scenarios
```

- **Unit tests:** Fast, test single units in isolation
- **Integration tests:** Test multiple units working together
- **E2E tests:** Test complete user workflows

### TDD with Different Approaches

Modern software development often combines methodologies:

- **TDD + BDD:** Combine technical tests (TDD) with behavior specifications (BDD)
- **TDD + DDD:** Use TDD to implement domain-driven designs
- **TDD + Agile:** TDD fits naturally into agile sprints and iterations

## Benefits You'll Experience

1. **Higher Code Quality**
   - Bugs caught early in development
   - Code is inherently testable
   - Comprehensive test coverage

2. **Better Design**
   - Forces modular, decoupled architecture
   - Clearer separation of concerns
   - More maintainable code

3. **Confidence in Changes**
   - Refactor fearlessly with test safety net
   - Instant feedback when something breaks
   - Regression prevention

4. **Living Documentation**
   - Tests document expected behavior
   - Examples of how to use the code
   - Always up-to-date (unlike comments)

5. **Faster Development (Long-term)**
   - Slower at first, but speeds up over time
   - Less debugging time
   - Fewer production bugs
   - Easier to add new features

## Expected Challenges

1. **Steeper Learning Curve**
   - Requires discipline and practice
   - New teams may experience slower velocity initially
   - Patience and persistence needed

2. **More Code to Maintain**
   - Tests are code too
   - Keep tests clean and refactored
   - Treat test code with same care as production code

3. **Resistance to Change**
   - Different from traditional development
   - Requires mindset shift
   - Team buy-in is essential

## Your TDD Workflow Checklist

For every new feature or bug fix:

- [ ] Write a failing test that describes the desired behavior
- [ ] Run the test and confirm it fails for the right reason
- [ ] Write the minimum code to make the test pass
- [ ] Run the test and confirm it passes
- [ ] Refactor the code while keeping all tests passing
- [ ] Run all tests to ensure no regressions
- [ ] Commit your changes
- [ ] Repeat for the next behavior

## Remember

> "The act of writing a unit test is more an act of design than verification. It is also more an act of documentation than verification." - Robert C. Martin

**TDD is not just about testing - it's a design and development methodology that leads to better software through disciplined practice.**

When in doubt: **Red → Green → Refactor → Repeat**
