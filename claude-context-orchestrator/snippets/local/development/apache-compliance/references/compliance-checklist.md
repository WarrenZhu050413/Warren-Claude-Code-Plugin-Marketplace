# Apache License 2.0 Compliance Checklist

Comprehensive checklist for ensuring Apache License 2.0 compliance in derivative works.

## Section 4: Redistribution Requirements

The Apache License 2.0 Section 4 contains four key requirements (4a, 4b, 4c, 4d) that must be met when redistributing the Work or Derivative Works.

---

## Requirement 4a: Provide License Copy

**Section 4a Text:**
> "You must give any other recipients of the Work or Derivative Works a copy of this License"

### Compliance Checklist

```
Source Distribution:
- [ ] LICENSE file in root directory
- [ ] LICENSE file contains complete Apache License 2.0 text
- [ ] LICENSE file is named LICENSE, LICENSE.txt, or LICENSE.md
- [ ] LICENSE file is readable (not binary or encrypted)

Binary Distribution:
- [ ] LICENSE included in distribution package
- [ ] LICENSE accessible to end users
- [ ] LICENSE in standard location (root, /licenses/, /legal/, etc.)

Documentation:
- [ ] README mentions Apache License 2.0
- [ ] Installation docs note license requirements
- [ ] File headers reference Apache License 2.0 (recommended)
```

### Examples

**✅ Compliant - Source Distribution:**
```
myproject/
├── LICENSE.txt           # Full Apache 2.0 text
├── README.md
└── src/
    └── main.py
```

**✅ Compliant - Binary Distribution:**
```
myapp-installer/
├── LICENSE.txt
├── install.exe
└── docs/
    └── README.txt
```

**❌ Non-Compliant:**
- No LICENSE file included
- LICENSE file contains only a reference/link to license (must include full text)
- LICENSE buried in subdirectory with no documentation

---

## Requirement 4b: Document Changes

**Section 4b Text:**
> "You must cause any modified files to carry prominent notices stating that You changed the files"

### Compliance Checklist

```
Modified Files:
- [ ] Each modified file has a change notice
- [ ] Change notices are "prominent" (near top of file or in header)
- [ ] Change notices state WHAT was modified
- [ ] Change notices identify WHO made the modification
- [ ] Change notices optionally include WHEN modification occurred

Documentation:
- [ ] CHANGELOG or CHANGES file documents modifications
- [ ] Documentation lists which files were modified
- [ ] Documentation describes nature of changes
```

### "Prominent" Means

A notice is "prominent" if:
- It's easy to find when reading the file
- It's near the top of the file or in a standard header location
- It's clearly marked as a modification notice
- It stands out from other comments

### Examples

**✅ Compliant - In-File Notice (Simple):**
```python
# Copyright 2024 Original Author
# Modified 2025-10-26 by Warren Zhu
#
# Licensed under the Apache License, Version 2.0...

def my_function():
    # Modified: Added error handling
    try:
        # ... implementation
    except ValueError:
        # Added exception handling
        pass
```

**✅ Compliant - In-File Notice (Detailed):**
```python
# Copyright 2024 Original Author
#
# Modified by Warren Zhu, 2025-10-26
# Changes:
#   - Added error handling for ValueError
#   - Refactored loop for performance
#   - Updated default parameter values
#
# Licensed under the Apache License, Version 2.0...
```

**✅ Compliant - CHANGELOG File:**
```markdown
# CHANGELOG

## Modified 2025-10-26 by Warren Zhu

**Changes to derivative work:**

### src/main.py
- Added error handling for edge case in process_data()
- Refactored data validation loop for performance
- Updated default timeout from 30s to 60s

### src/config.py
- Modified default configuration values
- Added new configuration option: enable_debug

### src/utils.py
- Fixed bug in date parsing function
- Added support for ISO 8601 format

**Original work attribution:**
- Source: https://github.com/original/project
- License: Apache License 2.0
- Copyright: Original Author
```

**❌ Non-Compliant:**
```python
# Copyright 2024 Original Author
# Licensed under the Apache License, Version 2.0...

# Modified (no information about who, what, or when)
def my_function():
    pass
```

**❌ Non-Compliant:**
```python
# Copyright 2025 Warren Zhu (missing original copyright)
# Licensed under the Apache License, Version 2.0...

def my_function():
    # Changed this function
    pass
```

---

## Requirement 4c: Retain Attribution Notices

**Section 4c Text:**
> "You must retain, in the Source form of any Derivative Works that You distribute, all copyright, patent, trademark, and attribution notices from the Source form of the Work, excluding those notices that do not pertain to any part of the Derivative Works"

### Compliance Checklist

```
Copyright Notices:
- [ ] All original copyright notices retained
- [ ] Your copyright added for modifications (if applicable)
- [ ] Copyright year updated if file significantly modified

Patent Notices:
- [ ] All patent notices from original retained
- [ ] Patent notices retained even if not modifying patent-related code

Trademark Notices:
- [ ] All trademark notices retained
- [ ] Trademark usage complies with original guidelines

Attribution Notices:
- [ ] All attribution notices retained (e.g., "This includes code from...")
- [ ] NOTICE file content preserved (if present in original)

Exclusions:
- [ ] Only removed notices that don't pertain to derivative work
- [ ] Document rationale if any notices removed
```

### What to Retain

**Always retain:**
- Copyright notices (e.g., `Copyright 2024 Author Name`)
- Patent notices (e.g., `Patent No. 1234567`)
- Trademark notices (e.g., `Apache Kafka is a trademark of...`)
- Attribution notices (e.g., `Includes code from Project X`)
- NOTICE file contents

**May exclude:**
- Notices that pertain to portions you completely removed
- Notices for files you entirely deleted (not distributed)

### Examples

**✅ Compliant - Retained Original Copyright:**
```python
# Copyright 2023 Original Author
# Copyright 2024 Another Contributor
# Copyright 2025 Warren Zhu (modifications)
#
# Licensed under the Apache License, Version 2.0...
```

**✅ Compliant - Added Your Copyright:**
```python
# Original work:
# Copyright 2024 Original Author
#
# Derivative work modifications:
# Copyright 2025 Warren Zhu
#
# Licensed under the Apache License, Version 2.0...
```

**❌ Non-Compliant - Removed Original Copyright:**
```python
# Copyright 2025 Warren Zhu
# Licensed under the Apache License, Version 2.0...
```

**❌ Non-Compliant - Modified Original Copyright:**
```python
# Copyright 2024-2025 Original Author and Warren Zhu
# (This changes the original notice)
```

---

## Requirement 4d: Include NOTICE File

**Section 4d Text:**
> "If the Work includes a NOTICE text file as part of its distribution, then any Derivative Works that You distribute must include a readable copy of the attribution notices contained within such NOTICE file... in at least one of the following places: within a NOTICE text file distributed as part of the Derivative Works; within the Source form or documentation, if provided along with the Derivative Works; or, within a display generated by the Derivative Works, if and wherever such third-party notices normally appear."

### Compliance Checklist

```
If Original Has NOTICE File:
- [ ] Checked if original work has NOTICE file
- [ ] Copied NOTICE file to derivative work
- [ ] NOTICE file in same location as original (recommended)
- [ ] NOTICE file is readable and accessible

NOTICE File Content:
- [ ] All attribution notices from original NOTICE retained
- [ ] Added your own attribution notices (if applicable)
- [ ] NOTICE clearly identifies original work
- [ ] NOTICE clearly identifies derivative work modifications

Placement Options:
- [ ] Option 1: NOTICE file in root directory (recommended)
- [ ] Option 2: Attribution in source documentation
- [ ] Option 3: Attribution in runtime display (if applicable)

Your Additions to NOTICE:
- [ ] May add your own attribution notices
- [ ] Your additions clearly separate from original notices
- [ ] Your additions do not modify original notices
- [ ] Your additions do not claim endorsement
```

### NOTICE File Template

**If original has NOTICE, use this structure:**

```
[Original Project Name]
Copyright [year] [Original Copyright Owner]

[Original NOTICE content - DO NOT MODIFY]

=====================================================

Derivative Work Modifications:
Copyright 2025 Warren Zhu

This derivative work includes modifications to the original software.

Modified components:
- [Component 1]: [Brief description of changes]
- [Component 2]: [Brief description of changes]

Original work source: [URL]
Original work license: Apache License 2.0
```

### Examples

**✅ Compliant - Preserved Original NOTICE:**
```
Apache Example Project
Copyright 2024 The Apache Software Foundation

This product includes software developed at
The Apache Software Foundation (http://www.apache.org/).

=====================================================

Derivative Work:
Copyright 2025 Warren Zhu

Modifications made to original Apache Example Project:
- Added feature X
- Modified component Y for performance

Original source: https://github.com/apache/example
```

**❌ Non-Compliant - Missing Original NOTICE:**
```
My Derivative Project
Copyright 2025 Warren Zhu

Based on Apache Example Project.
```

**❌ Non-Compliant - Modified Original NOTICE:**
```
Apache Example Project
Copyright 2024 The Apache Software Foundation
Modified and improved by Warren Zhu 2025  ← WRONG: modifies original notice

This product includes software developed at...
```

---

## Complete Pre-Release Checklist

Run through this checklist before releasing any derivative work:

```
Files:
- [ ] LICENSE file present with full Apache 2.0 text
- [ ] NOTICE file present (if original had one)
- [ ] NOTICE file contains original attributions
- [ ] README or docs mention Apache License 2.0

Attribution:
- [ ] All copyright notices from original retained
- [ ] All patent notices from original retained
- [ ] All trademark notices from original retained
- [ ] Your copyright added for new/modified files

Changes:
- [ ] Modified files have change notices
- [ ] Change notices are prominent (near top of file)
- [ ] CHANGELOG or documentation lists all modifications
- [ ] Change documentation identifies who, what, when

Validation:
- [ ] Run grep for original copyright notices - all present?
- [ ] Check LICENSE file readable and complete
- [ ] Check NOTICE file (if applicable) complete
- [ ] Review README for attribution and license reference

Distribution:
- [ ] Source distributions include LICENSE
- [ ] Binary distributions include LICENSE
- [ ] Documentation package includes LICENSE
- [ ] All distribution formats have license access
```

---

## Automation Scripts

### Check for LICENSE File

```bash
#!/bin/bash
# check-license.sh - Verify LICENSE file exists and is valid

if [ -f "LICENSE" ] || [ -f "LICENSE.txt" ] || [ -f "LICENSE.md" ]; then
    echo "✓ LICENSE file found"

    # Check if it contains Apache License 2.0 text
    if grep -q "Apache License" LICENSE* 2>/dev/null; then
        echo "✓ Contains Apache License text"
    else
        echo "✗ LICENSE file doesn't contain Apache License text"
        exit 1
    fi
else
    echo "✗ LICENSE file not found"
    exit 1
fi
```

### Check for Copyright Notices

```bash
#!/bin/bash
# check-copyrights.sh - Find all copyright notices

echo "Copyright notices in source files:"
grep -r "Copyright" --include="*.py" --include="*.js" --include="*.java" . | head -20

echo -e "\nChecking for modification notices:"
grep -r "Modified" --include="*.py" --include="*.js" --include="*.java" . | head -20
```

### Validate NOTICE File

```bash
#!/bin/bash
# check-notice.sh - Verify NOTICE file if it should exist

# Check if NOTICE exists
if [ -f "NOTICE" ] || [ -f "NOTICE.txt" ]; then
    echo "✓ NOTICE file found"

    # Display content for manual review
    echo -e "\nNOTICE file content:"
    cat NOTICE*
else
    echo "⚠ No NOTICE file found"
    echo "  If original work had NOTICE, you must include it!"
fi
```

---

## FAQs

**Q: Do I need to add my copyright to every file?**
A: Only to files you created or substantially modified. Always retain original copyrights.

**Q: What counts as a "prominent" change notice?**
A: Near the top of the file, in a comment header, clearly stating what changed and who changed it.

**Q: Can I use a different license for my derivative work?**
A: No. Derivative works must remain under Apache License 2.0. You can add additional terms, but can't remove Apache requirements.

**Q: Do I need a NOTICE file if the original didn't have one?**
A: No, but you may create one if you want to add attributions. If original had NOTICE, you must include it.

**Q: What if I only use a small part of Apache-licensed code?**
A: Same requirements apply. Include LICENSE, retain attribution, document changes.

**Q: Can I remove copyright notices from files I deleted?**
A: Yes, if you don't redistribute those files. But retain notices for all files you do distribute.

**Q: How detailed should change documentation be?**
A: Enough to identify what was modified. "Fixed bug" is minimal; "Fixed null pointer in parseData() function" is better.

---

For additional guidance, see [common-violations.md](common-violations.md) for examples of what NOT to do.
