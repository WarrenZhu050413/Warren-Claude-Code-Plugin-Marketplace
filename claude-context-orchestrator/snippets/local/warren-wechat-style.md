---
name: "Warren WeChat Message Style"
description: "Guide for writing WeChat messages in Warren's professional Chinese style - for deployment updates, feature explanations, polite replies, and business coordination"
pattern: "\\b(WECHAT|微信)\\b[.,;:!?]?"
---

# Warren's WeChat Message Writing Guide

Use this guide when drafting WeChat messages for Warren in professional Chinese contexts.

## Core Style Principles

### 1. Plain Text (No Markdown)

WeChat does NOT render markdown. Write plain text only.

- ❌ **bold**, *italic*, `code`, [links](url), # headers
- ✓ Use line breaks and spacing for structure
- ✓ Use 1. 2. 3. or - for lists (plain text, not markdown)
- ✓ Use「quotes」or （parentheses）for emphasis instead of **bold**

### 2. Formality & Warmth

- Always use 您 (formal "you"), never 你
- Team references: Use "这边我们..." or "我们这边..." (on our end)
- Acknowledge first, then proceed: Start with "好的收到" or "好的谢谢" before adding content
- No excessive emojis - only occasional [Joyful] if appropriate

### 3. Common Opening Patterns

| Situation                  | Opening             |
| -------------------------- | ------------------- |
| Acknowledging info         | 好的收到 / 好的谢谢 |
| Greeting someone           | 您好 / @Name 您好   |
| After they share something | 收到。谢谢！        |
| Starting new topic         | 这边我看一下...     |

### 4. Common Closing Patterns

| Situation                  | Closing                                      |
| -------------------------- | -------------------------------------------- |
| Routine updates            | (No closing needed - just end with content)  |
| Large/complex issues ONLY  | 有任何问题直接ping我们                       |
| Promising action           | 我们这边尽快排查                             |
| Scheduling                 | 您们方便大概...点...钟左右我们可以快快开个会 |
| Gratitude                  | 感谢！/ 谢谢您                               |

## Message Templates by Type

### Type 1: Deployment/Technical Update

```
好的收到
这边我们检查一下
是有[具体变化]方面设置的更新。[简短说明]
```

Or longer:

```
这边我们加了一个[功能名]
[1-2句功能说明]
您也可以在 [URL] 这里查看。这是我的测试机。
```

### Type 2: Feature Walkthrough

```
我写一个文档给您们看一下。同时我们这边今天讨论了[主题]

[要点1]：
[简短说明]

[要点2]：
[简短说明]

这边我们在对比一下各个方案。您们方便大概[时间]左右我们可以快快开个会，对接一下。
```

### Type 3: Issue Apology + Resolution

```
抱歉！我们这边尽快排查
因为这个理论上应该不会有问题的。但是有可能[可能原因]。我们不确定
这边可以给我们[需要的权限/信息]吗？
这样我们这边可以debug一下
```

### Type 4: Polite Acknowledgment/Reply

```
好的收到
这样可以的
```

Or with next step:

```
好的收到。谢谢！
这边我们接进来
```

### Type 5: Requesting Access/Info

```
请问这些[东西]有一个[具体需求]我们可以测试一下吗？
我看一下我们具体需要哪一些权限
谢谢您
```

### Type 6: Scheduling/Coordination

```
这边我们在对比一下各个方案。您们方便大概早上10点十一点钟左右我们可以快快开个会，对接一下。讨论完以后可以再出几个版本，我们可以快速迭代
```

### Type 7: Asking Technical Questions

```
您好，我们了解一下现在[系统]用的是什么[技术细节]？
并且之前[系统]升级的时候业务端出现了什么错误？
```

## Key Vocabulary

| Chinese | Usage                                          |
| ------- | ---------------------------------------------- |
| 这边    | "On this end" - use to refer to your team      |
| 方便    | "Convenient" - use when making polite requests |
| 排查    | "Investigate/troubleshoot"                     |
| 对接    | "Sync up / align"                              |
| 接进来  | "Integrate / connect"                          |
| 快快    | "Quickly" - casual urgency                     |
| 迭代    | "Iterate"                                      |
| ping    | Acceptable English loanword in tech context    |

## Anti-Patterns (Avoid)

- ❌ Using markdown formatting (WeChat doesn't render it)
- ❌ Starting with just "您好" without context (too abrupt)
- ❌ Using 你 instead of 您
- ❌ Excessive apologies without action plan
- ❌ Long paragraphs - use short sentences
- ❌ Too many emojis
- ❌ Ending routine updates with "有任何问题直接ping我们" (overused, save for large issues)
- ❌ Adding unnecessary closings to simple messages

## Context-Specific Adjustments

**When addressing seniors/clients:** More 谢谢, 感谢, 抱歉
**When addressing peers:** Can be more direct, use "快快"
**When urgent:** "这边我们尽快..." / "我们这边今天..."
**When uncertain:** "有可能..." / "我们不确定"

---

## Real Examples (Reference)

### System Update Announcement

```
这边做出来了一个版本。您们看一下
我写一下文档。等我一下
```

```
这边我们更新了一下后台系统，加了三个独立的入口：

1. 管理后台（admin）：https://8.129.82.75/admin/app/
2. 项目经理工作台（PM）：https://8.129.82.75/pm/app/
3. 管家对话界面（butler）：https://8.129.82.75/butler/app/chat/

测试账号：
- 管理员：admin / Baozheng2026AISuccess
- 项目经理：shenlan-pm / shenlangongyu20260201
- 管家：shenlan-butler / shenlangongyubutler2026
```

### Quick Confirmations & Estimates

```
您们觉得这个有需要我们20分钟就可以做出来
我先做一个版本放在我的测试服务器里面
可以对比一下
```

```
嗯好的。这个可以的。
```

### User Model Explanation

```
嗯。这边我们的用户模型为：

用户1:总部管理人员。这个人员有极高的权限。能够看到所有项目里面的对话，并且可以管理所有的项目以及人员权限现在暂时没有分开
项目经理可以从工作台和AI管家助手界面一键切入
```

### Clarifying Technical Details

```
好的。我之前的理解是SR现在是在机房托管的，而ECS是阿里云的服务。这边自建是在机房托管但是也是阿里云的服务吗？
```

```
我们之前以为是ECS。还在想这个怎么做的
现在了解了
```

### Asking Technical Questions

```
我也想问一下 @皮哥阳 bx_bop_fcs_db_uat 是测试的表吗？
```

