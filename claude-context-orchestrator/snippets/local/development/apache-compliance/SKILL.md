---
name: Apache License 2.0 Compliance
description: Guide for verifying Apache License 2.0 compliance in derivative works. This skill should be used when creating derivative works from Apache-licensed code, checking license compliance, ensuring proper attribution, validating NOTICE/LICENSE files, documenting changes per Apache requirements, or when mentions of "apache", "license", "compliance", "attribution", or "NOTICE" appear in context of software licensing.
license: Apache 2.0 (see LICENSE.txt)
---

# Apache License 2.0 Compliance

Guide for ensuring derivative works comply with Apache License 2.0 requirements.

## When to Use This Skill

Use this skill when:
- Creating derivative works from Apache-licensed code
- Modifying files from Apache-licensed projects
- Redistributing Apache-licensed software
- Checking if attribution is correct
- Validating NOTICE and LICENSE files
- Ensuring change documentation meets Apache requirements
- Reviewing code for license compliance before release

## Apache License 2.0 Overview

The Apache License 2.0 is a permissive license that allows:
- Commercial use
- Modification
- Distribution
- Patent use (with grant)
- Private use

**Key requirement:** Derivative works must comply with Section 4 redistribution requirements.

## Compliance Workflow

Follow this 4-step workflow to ensure Apache 2.0 compliance:

### Step 1: Attribution Requirements (Section 4c)

**Requirement:** Retain copyright, patent, trademark, and attribution notices from the source.

**Checklist:**
```
- [ ] Retained all copyright notices from original files
- [ ] Retained all patent notices from original files
- [ ] Retained all trademark notices from original files
- [ ] Retained all attribution notices from original files
- [ ] Did NOT remove or modify existing attribution
```

**Example - Proper Attribution:**
```python
# Copyright 2024 Original Author
# Copyright 2025 Your Name (modifications)
#
# Licensed under the Apache License, Version 2.0...
```

**Example - WRONG (missing original copyright):**
```python
# Copyright 2025 Your Name
# Licensed under the Apache License, Version 2.0...
```

### Step 2: NOTICE and LICENSE Files (Section 4d)

**Requirement:** Include LICENSE and NOTICE files (if present in original) with redistribution.

**LICENSE File Checklist:**
```
- [ ] LICENSE.txt or LICENSE file exists in distribution
- [ ] Contains complete Apache License 2.0 text
- [ ] File is in root directory or documented location
```

**NOTICE File Checklist (if original work has NOTICE):**
```
- [ ] NOTICE.txt or NOTICE file exists in distribution
- [ ] Includes attribution notices from original NOTICE
- [ ] Added your own attribution notices if applicable
- [ ] NOTICE is in root directory or same location as LICENSE
```

**Example NOTICE File Content:**
```
Project Name
Copyright [year] [Original Copyright Owner]

This product includes software developed by [Original Author/Organization].

[If you made modifications:]
Modifications Copyright 2025 Your Name
- Modified: [brief description]
- Modified: [brief description]
```

### Step 3: Change Documentation (Section 4b)

**Requirement:** Cause modified files to carry prominent notices stating that you changed the files.

**Checklist:**
```
- [ ] All modified files have change notices
- [ ] Change notices are "prominent" (easy to find)
- [ ] Change notices state WHAT was modified
- [ ] Change notices state WHO made modifications
- [ ] Change notices optionally include WHEN
```

**Best Practice - In-File Notice:**
```python
# Modified 2025-10-26 by Your Name
# Changes: Added error handling for edge case X
```

**Best Practice - CHANGELOG/CHANGES File:**
```markdown
## Modified 2025-10-26 by Your Name

**Changes made to derivative work:**

1. **Modified file.py** - Added error handling for edge case X
2. **Modified config.py** - Updated default configuration values
3. **Added new_feature.py** - New module for feature Y

**Original work attribution:**
- Source: [original repository URL]
- License: Apache License 2.0
- Copyright: [Original Copyright Owner]
```

**Where to Document:**
- Option 1: Direct in modified files (preferred for few changes)
- Option 2: CHANGELOG.md or CHANGES.md file (preferred for many changes)
- Option 3: Both (most comprehensive)

### Step 4: Redistribution Compliance (Section 4a)

**Requirement:** Provide copy of Apache License 2.0 with redistributions.

**Checklist:**
```
- [ ] LICENSE file included in source distributions
- [ ] LICENSE file included in binary distributions
- [ ] License reference in file headers (optional but recommended)
- [ ] Documentation mentions Apache License 2.0
```

**Recommended File Header:**
```
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## Quick Compliance Check

Run through this quick checklist before releasing derivative work:

```
Attribution:
- [ ] Original copyright notices retained
- [ ] Original attribution notices retained

Files:
- [ ] LICENSE file present
- [ ] NOTICE file present (if original had one)

Changes:
- [ ] Modified files have change notices
- [ ] CHANGELOG or in-file documentation of changes

Distribution:
- [ ] License included with source distribution
- [ ] License included with binary distribution (if applicable)
```

## Common Scenarios

### Scenario 1: Modified a Few Files

1. Add change notice to each modified file
2. Retain original copyright in files
3. Add your copyright for modifications
4. Ensure LICENSE file is in distribution
5. Update NOTICE if original had one

### Scenario 2: Created Derivative Work (Fork)

1. Keep original LICENSE file
2. Keep original NOTICE file
3. Create CHANGELOG documenting all modifications
4. Add your copyright for new files
5. Update README with attribution to original

### Scenario 3: Incorporated Apache Code into Your Project

1. Copy LICENSE file (or merge into yours)
2. Copy NOTICE file (or merge into yours)
3. Add attribution to your documentation
4. Document which parts came from Apache project
5. Note modifications you made

## Validation Commands

```bash
# Check LICENSE file exists
test -f LICENSE.txt && echo "✓ LICENSE found" || echo "✗ LICENSE missing"

# Check NOTICE file exists (if applicable)
test -f NOTICE.txt && echo "✓ NOTICE found" || echo "✗ NOTICE missing"

# Check for copyright notices in files
grep -r "Copyright" --include="*.py" --include="*.js" .

# Check for Apache License references
grep -r "Apache License" --include="*.py" --include="*.js" .
```

## Reference Materials

For detailed requirements and examples:
- See [compliance-checklist.md](references/compliance-checklist.md) for comprehensive requirements
- See [common-violations.md](references/common-violations.md) for examples of what NOT to do

## External Resources

- [Apache License 2.0 Full Text](https://www.apache.org/licenses/LICENSE-2.0)
- [Apache License FAQ](https://www.apache.org/foundation/license-faq.html)
- [How to Apply Apache License](https://www.apache.org/licenses/LICENSE-2.0.html#apply)

## Notes

**This skill provides guidance only.** For legal advice about license compliance, consult a lawyer. When in doubt about compliance, err on the side of over-attribution rather than under-attribution.
