# Gmail CLI Usability Test Plan

## Test Workflows

1. **View group details with # prefix**
   - Command: `gmail groups show "#me"`
   - Expected: Should display group members

2. **View group details without # prefix**
   - Command: `gmail groups show me`
   - Expected: Should display group members (same as above)

3. **Check examples for groups**
   - Command: `gmail groups examples`
   - Expected: Should show comprehensive examples

4. **List all groups**
   - Command: `gmail groups list`
   - Expected: Should show groups with # prefix display

5. **Dry-run send to group**
   - Command: `gmail send --to "#me" --subject "Test" --body "Hello" --dry-run`
   - Expected: Should preview without sending

6. **Check examples for styles**
   - Command: `gmail styles examples`
   - Expected: Should show style examples

7. **Verify styles list excludes backups**
   - Command: `gmail styles list`
   - Expected: Should not show .backup. files

8. **Check labels examples**
   - Command: `gmail labels examples`
   - Expected: Should show label workflow examples

9. **JSON output for groups**
   - Command: `gmail groups list --output-format json`
   - Expected: Should output valid JSON

10. **Validate group with # prefix**
    - Command: `gmail groups validate "#me"`
    - Expected: Should validate successfully
