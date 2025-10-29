# Common Apache License 2.0 Violations

Examples of common mistakes when working with Apache-licensed code and how to fix them.

---

## Violation 1: Removing Original Copyright

### ❌ What NOT to Do

```python
# Original file had:
# Copyright 2024 Original Author
# Licensed under the Apache License, Version 2.0...

# Your derivative work:
# Copyright 2025 Your Name
# Licensed under the Apache License, Version 2.0...
```

**Problem:** Original copyright removed, violating Section 4c (retain attribution notices).

### ✅ How to Fix

```python
# Copyright 2024 Original Author
# Copyright 2025 Your Name (modifications)
#
# Licensed under the Apache License, Version 2.0...
```

**Key:** Always retain original copyright. Add your copyright alongside it, not instead of it.

---

## Violation 2: No Change Documentation

### ❌ What NOT to Do

```python
# Copyright 2024 Original Author
# Copyright 2025 Your Name
#
# Licensed under the Apache License, Version 2.0...

def process_data(data):
    # Completely rewrote this function
    # But didn't document that it was modified
    return transformed_data
```

**Problem:** Modified file without prominent notice stating changes, violating Section 4b.

### ✅ How to Fix

**Option 1: In-file notice**
```python
# Copyright 2024 Original Author
# Modified 2025-10-26 by Your Name
# Changes: Rewrote process_data() to use streaming instead of batch processing
#
# Licensed under the Apache License, Version 2.0...

def process_data(data):
    # Modified implementation
    return transformed_data
```

**Option 2: CHANGELOG file**
```markdown
## Modified 2025-10-26 by Your Name

### src/processor.py
- Rewrote process_data() function to use streaming
- Changed from batch processing to real-time processing
- Updated error handling
```

---

## Violation 3: Missing LICENSE File

### ❌ What NOT to Do

```
myproject/
├── README.md
└── src/
    ├── main.py (uses Apache-licensed code)
    └── utils.py (modified from Apache project)
```

**Problem:** No LICENSE file included, violating Section 4a (must provide license copy).

### ✅ How to Fix

```
myproject/
├── LICENSE.txt          # ← Add this!
├── README.md
└── src/
    ├── main.py
    └── utils.py
```

**LICENSE.txt must contain:**
- Complete Apache License 2.0 text
- Not just a link or reference

---

## Violation 4: Ignoring NOTICE File

### ❌ What NOT to Do

**Original project has:**
```
original-project/
├── LICENSE
├── NOTICE              # Original has NOTICE
└── src/
```

**Your derivative work:**
```
my-derivative/
├── LICENSE             # You included LICENSE
└── src/               # But forgot NOTICE!
```

**Problem:** Original had NOTICE file, but derivative doesn't include it, violating Section 4d.

### ✅ How to Fix

```
my-derivative/
├── LICENSE
├── NOTICE              # ← Must include this!
└── src/
```

**NOTICE file content:**
```
[Original NOTICE content - copy verbatim]

=====================================================

Derivative Work Modifications:
Copyright 2025 Your Name

Modified components:
- [List your changes]
```

---

## Violation 5: Vague Change Documentation

### ❌ What NOT to Do

```python
# Modified by Someone
# Changes: Updated the code
```

**Problem:** Change notice lacks detail - who is "Someone"? What was "Updated"? When?

### ✅ How to Fix

```python
# Modified 2025-10-26 by Jane Smith <jane@example.com>
# Changes:
#   - Added null check in parseInput()
#   - Refactored error handling for clarity
#   - Updated default timeout from 30s to 60s
```

**Key elements:**
- **Who:** Full name or identifier
- **What:** Specific changes made
- **When:** Date of modification (optional but recommended)

---

## Violation 6: LICENSE Link Instead of Full Text

### ❌ What NOT to Do

**LICENSE file contains:**
```
This project is licensed under Apache License 2.0.
See: http://www.apache.org/licenses/LICENSE-2.0
```

**Problem:** LICENSE file must contain full license text, not just a link (Section 4a).

### ✅ How to Fix

**LICENSE file must contain complete text:**
```
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

   [... full license text ...]
```

---

## Violation 7: Modifying Original NOTICE Content

### ❌ What NOT to Do

**Original NOTICE:**
```
Apache Example Project
Copyright 2024 The Apache Software Foundation

This product includes software developed at
The Apache Software Foundation (http://www.apache.org/).
```

**Your modified NOTICE:**
```
Apache Example Project
Copyright 2024 The Apache Software Foundation
Enhanced and improved by Your Name 2025  ← WRONG!

This product includes software developed at
The Apache Software Foundation (http://www.apache.org/).
```

**Problem:** Modified original attribution text, violating Section 4d.

### ✅ How to Fix

```
Apache Example Project
Copyright 2024 The Apache Software Foundation

This product includes software developed at
The Apache Software Foundation (http://www.apache.org/).

=====================================================

Derivative Work:
Copyright 2025 Your Name

Modifications and enhancements to the original software.
```

**Key:** Original NOTICE content must remain unchanged. Add your notices separately.

---

## Violation 8: Claiming Original as Your Own

### ❌ What NOT to Do

**README.md:**
```markdown
# My Awesome Project

Created by Your Name, 2025.

This project does amazing things...
```

**Problem:** No mention of original Apache-licensed work or attribution.

### ✅ How to Fix

**README.md:**
```markdown
# My Awesome Project

Created by Your Name, 2025.

This project is based on [Original Project](url) by Original Author,
licensed under Apache License 2.0.

## Modifications

This derivative work includes:
- Feature X
- Enhancement Y
- Bug fix Z

## License

This project is licensed under Apache License 2.0.
See LICENSE file for details.

## Attribution

Original work: [Original Project](url)
Copyright: Original Author
License: Apache License 2.0
```

---

## Violation 9: Incomplete Binary Distribution

### ❌ What NOT to Do

**Source distribution has LICENSE, but binary doesn't:**

```
myapp-1.0-binary.zip
├── myapp.exe
├── README.txt
└── config.ini
```

**Problem:** Binary distribution must include LICENSE (Section 4a).

### ✅ How to Fix

```
myapp-1.0-binary.zip
├── LICENSE.txt         # ← Add this!
├── NOTICE.txt          # ← If original had NOTICE
├── myapp.exe
├── README.txt
└── config.ini
```

---

## Violation 10: No Change Notice in CHANGELOG

### ❌ What NOT to Do

**CHANGELOG.md:**
```markdown
# Changelog

## v2.0.0 - 2025-10-26

- Added feature X
- Fixed bug Y
- Improved performance
```

**Problem:** No indication that this is derivative work, who made changes, or attribution to original.

### ✅ How to Fix

**CHANGELOG.md:**
```markdown
# Changelog

## Modified 2025-10-26 by Your Name

**Derivative Work Based on Original Project v1.0**

Changes to derivative work:
- Added feature X
- Fixed bug Y in data processing
- Improved performance of query handler

**Original work attribution:**
- Source: https://github.com/original/project
- License: Apache License 2.0
- Copyright: Original Author

---

[Original changelog below]

## v1.0.0 - 2024-01-01 (Original Release)
...
```

---

## Violation 11: Selectively Retaining Copyright

### ❌ What NOT to Do

```python
# Kept copyright from main.py:
# Copyright 2024 Original Author

# But removed copyright from utils.py because "I rewrote most of it":
# Copyright 2025 Your Name (modifications)
```

**Problem:** Must retain ALL original copyright notices, even for heavily modified files.

### ✅ How to Fix

```python
# main.py:
# Copyright 2024 Original Author
# Licensed under the Apache License, Version 2.0...

# utils.py (even though heavily modified):
# Copyright 2024 Original Author
# Copyright 2025 Your Name (modifications)
# Licensed under the Apache License, Version 2.0...
```

**Key:** Retain original copyright regardless of how much you modified the file. If you modified it substantially, add your copyright alongside original.

---

## Violation 12: Wrong License File Location

### ❌ What NOT to Do

```
myproject/
├── README.md
├── src/
│   └── main.py
└── legal/
    └── licenses/
        └── apache/
            └── LICENSE.txt  ← Too buried!
```

**Problem:** LICENSE file is hard to find, not "prominent."

### ✅ How to Fix

**Option 1: Root directory (best)**
```
myproject/
├── LICENSE.txt         # ← Easy to find!
├── README.md
└── src/
    └── main.py
```

**Option 2: If you must use subdirectory, document it**
```
myproject/
├── README.md           # README mentions: "See legal/LICENSE.txt"
├── src/
│   └── main.py
└── legal/
    └── LICENSE.txt
```

---

## Violation 13: Generic "Based On" Without Details

### ❌ What NOT to Do

```markdown
# README.md

Based on some Apache-licensed code.
```

**Problem:** Vague attribution doesn't meet Apache requirements.

### ✅ How to Fix

```markdown
# README.md

## Attribution

This project is a derivative work based on:

**Original Work:** [Project Name](https://github.com/original/project)
**Original Author:** Original Author Name
**Original Copyright:** Copyright 2024 Original Author
**License:** Apache License 2.0

**Modifications:** See CHANGELOG.md for complete list of changes.
```

---

## Violation 14: Forgetting File Headers

### ❌ What NOT to Do

```python
# main.py - no license header

def my_function():
    pass
```

**Problem:** While not strictly required, missing file headers make it unclear what license applies to individual files.

### ✅ How to Fix (Recommended Best Practice)

```python
# Copyright 2024 Original Author
# Copyright 2025 Your Name (modifications)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

def my_function():
    pass
```

---

## Quick Violation Check

Run this checklist to avoid common violations:

```
LICENSE File:
- [ ] LICENSE file in root or documented location
- [ ] Contains FULL Apache 2.0 text (not just a link)
- [ ] Included in both source AND binary distributions

Copyright Notices:
- [ ] ALL original copyright notices retained
- [ ] Did NOT modify any original copyright text
- [ ] Added your copyright alongside (not replacing) original

Change Documentation:
- [ ] Modified files have change notices
- [ ] Change notices include: who, what, when
- [ ] CHANGELOG or in-file documentation exists
- [ ] Attribution to original work is clear

NOTICE File:
- [ ] If original had NOTICE, yours includes it
- [ ] Original NOTICE content is UNCHANGED
- [ ] Your additions are clearly separated
- [ ] NOTICE file is in prominent location

README/Documentation:
- [ ] Mentions Apache License 2.0
- [ ] Attributes original work with specifics
- [ ] Links to original source
- [ ] Documents your modifications
```

---

## Real-World Example: Correct Derivative Work

Here's a complete example of a properly licensed derivative work:

```
my-derivative-project/
├── LICENSE.txt                    # Full Apache 2.0 text
├── NOTICE.txt                     # Preserved original + additions
├── CHANGELOG.md                   # Documents all changes
├── README.md                      # Attribution & license info
└── src/
    ├── main.py                   # Proper file headers
    └── utils.py                  # Change notices
```

**LICENSE.txt:**
```
[Complete Apache License 2.0 text]
```

**NOTICE.txt:**
```
Original Project Name
Copyright 2024 Original Author

[Original NOTICE content - unchanged]

=====================================================

Derivative Work:
Copyright 2025 Your Name

This derivative work includes modifications to the original software.
See CHANGELOG.md for details.

Original source: https://github.com/original/project
```

**CHANGELOG.md:**
```markdown
# CHANGELOG

## Modified 2025-10-26 by Your Name

**Changes to derivative work:**

### src/main.py
- Added error handling for network timeouts
- Refactored data processing loop
- Updated logging format

### src/utils.py
- Added new utility function: validate_input()
- Fixed bug in date parsing

**Original work attribution:**
- Source: https://github.com/original/project
- License: Apache License 2.0
- Copyright: Original Author
```

**README.md:**
```markdown
# My Derivative Project

## Description
This project is based on Original Project and adds features X, Y, Z.

## License
Licensed under Apache License 2.0. See LICENSE.txt.

## Attribution
This is a derivative work based on:
- **Original Project:** [link]
- **Copyright:** Original Author
- **License:** Apache License 2.0

See CHANGELOG.md for complete modification history.
```

**src/main.py:**
```python
# Copyright 2024 Original Author
# Modified 2025-10-26 by Your Name
#
# Changes:
#   - Added error handling for network timeouts
#   - Refactored data processing loop
#
# Licensed under the Apache License, Version 2.0 (the "License");
# [... full license header ...]

def main():
    pass
```

---

## Summary

**Most common violations:**
1. Removing original copyright
2. No change documentation
3. Missing LICENSE file
4. Ignoring NOTICE file requirements
5. Vague or missing attribution

**Golden rules:**
- **Retain** all original notices
- **Document** all changes prominently
- **Include** LICENSE in all distributions
- **Preserve** NOTICE file (if original had one)
- **Attribute** original work clearly

**When in doubt:** Over-attribute rather than under-attribute. It's better to be too thorough with attribution than to risk license violation.
