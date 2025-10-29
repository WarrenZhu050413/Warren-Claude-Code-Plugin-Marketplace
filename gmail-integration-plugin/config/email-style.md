# Email Style Configuration

This file defines the default style for emails drafted by Claude.

## Tone and Formality

**Default Tone**: Professional but warm
**Formality Level**: Semi-formal (adjust based on recipient relationship)

## Greeting Patterns

**Professional**:
- "Hi [Name],"
- "Hello [Name],"

**Formal**:
- "Dear [Name],"
- "Dear Professor [Last Name],"

**Casual** (for known colleagues/friends):
- "Hey [Name],"
- "[Name],"

## Closing Patterns

**Professional**:
- "Best,"
- "Best regards,"
- "Thanks,"
- "Thank you,"

**Formal**:
- "Sincerely,"
- "Respectfully,"
- "With regards,"

**Casual**:
- "Cheers,"
- "Talk soon,"

## Body Style

### Principles
1. **Clarity first**: Get to the point quickly
2. **Conciseness**: Respect recipient's time
3. **Structure**: Use paragraphs for readability
4. **Action items**: Make requests/next steps clear

### Formatting
- Short paragraphs (2-3 sentences)
- Bullet points for lists
- Bold for emphasis (sparingly)
- No excessive exclamation marks

### Common Patterns
- Start with context if needed
- State main point/request clearly
- Provide relevant details
- End with clear next step or call to action

## Recipient-Specific Patterns

Claude will analyze previous emails to recipients and learn:
- Typical greeting/closing combinations
- Formality level used
- Response patterns
- Subject line style

These learned patterns are stored in `learned-patterns/` and take precedence over defaults.

## Language Preferences

- **Brevity**: Prefer shorter sentences
- **Active voice**: Avoid passive constructions
- **Directness**: Be clear about requests and expectations
- **Politeness**: Use "please" and "thank you" appropriately

## Example Templates

### Quick Request
```
Hi [Name],

Quick question: [question]?

Thanks,
Warren
```

### Follow-up
```
Hi [Name],

Following up on [topic]. [Brief context if needed].

[Question or action item]

Let me know. Thanks!

Warren
```

### Professional Update
```
Hi [Name],

[Opening sentence with context]

[Main update or information in 1-2 paragraphs]

[Closing with next steps or call to action]

Best,
Warren
```

## Notes

- These are defaults - Claude adapts based on context
- Edit this file to customize your email style
- Use `gmail config edit-style` or the new `gmail styles` commands
- Learned patterns from actual sent emails override these defaults
