# Deleting Skills

Guidance for safely removing Agent Skills from Claude Code.

## Quick Deletion Process

### 1. Locate the Skill

```bash
# Personal skills
ls ~/.claude/skills/

# Project skills
ls .claude/skills/

# Find specific skill
find ~/.claude/skills -name "SKILL.md" -path "*/my-skill/*"
```

### 2. Create Backup (Recommended)

Before deleting, create a backup:

```bash
# Backup entire skill directory
cp -r ~/.claude/skills/my-skill ~/.claude/skills/my-skill.backup

# Or backup to a dedicated location
cp -r ~/.claude/skills/my-skill ~/skill-backups/my-skill-$(date +%Y%m%d)
```

### 3. Delete the Skill

```bash
# Personal skill
rm -rf ~/.claude/skills/my-skill

# Project skill
rm -rf .claude/skills/my-skill
```

### 4. Verify Removal

Restart Claude Code and verify the skill is no longer available:

Ask Claude: "What skills are available?"

## Deletion Scenarios

### Delete Personal Skill

```bash
# Check it exists
ls ~/.claude/skills/my-skill/SKILL.md

# Backup
cp -r ~/.claude/skills/my-skill ~/.claude/skills/my-skill.backup

# Delete
rm -rf ~/.claude/skills/my-skill

# Verify
ls ~/.claude/skills/
```

No restart needed for personal skills if Claude Code wasn't using them.

### Delete Project Skill

For skills in `.claude/skills/` that are committed to git:

```bash
# Backup first
cp -r .claude/skills/my-skill ~/skill-backups/my-skill-backup

# Remove from git
git rm -rf .claude/skills/my-skill

# Commit
git commit -m "Remove my-skill: no longer needed"

# Push
git push
```

**Important**: Notify team members so they can pull the changes and restart Claude Code.

### Delete Plugin Skill

Plugin skills are managed by the plugin system. To remove:

**Option 1: Disable the plugin**
```
/plugin disable plugin-name@marketplace-name
```

**Option 2: Uninstall the plugin**
```
/plugin uninstall plugin-name@marketplace-name
```

You cannot delete individual skills from plugins. To modify plugin skills, fork the plugin or contact the plugin author.

## Bulk Deletion

### Delete Multiple Personal Skills

```bash
# List all personal skills
ls ~/.claude/skills/

# Backup all before deletion
cp -r ~/.claude/skills ~/skill-backups/all-skills-$(date +%Y%m%d)

# Delete specific skills
rm -rf ~/.claude/skills/skill1
rm -rf ~/.claude/skills/skill2
rm -rf ~/.claude/skills/skill3
```

### Delete All Unused Skills

```bash
# Backup first
cp -r ~/.claude/skills ~/skill-backups/all-skills-$(date +%Y%m%d)

# Review each skill before deleting
for skill in ~/.claude/skills/*; do
    echo "Skill: $(basename $skill)"
    echo "Description:"
    head -n 10 "$skill/SKILL.md"
    read -p "Delete this skill? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$skill"
        echo "Deleted: $(basename $skill)"
    fi
done
```

## Backup Strategies

### Before Major Cleanup

Create a timestamped backup of all skills:

```bash
# Backup all personal skills
tar -czf ~/skill-backups/personal-skills-$(date +%Y%m%d-%H%M%S).tar.gz \
    -C ~ .claude/skills

# Backup all project skills (from project root)
tar -czf ~/skill-backups/project-skills-$(date +%Y%m%d-%H%M%S).tar.gz \
    .claude/skills
```

### Restore from Backup

```bash
# Restore all personal skills
tar -xzf ~/skill-backups/personal-skills-20251016-143022.tar.gz \
    -C ~

# Restore specific skill
cp -r ~/skill-backups/my-skill-20251016 ~/.claude/skills/my-skill
```

## Version Control Best Practices

### For Project Skills

When deleting project skills from git repositories:

```bash
# Create feature branch
git checkout -b remove-unused-skills

# Remove skill
git rm -rf .claude/skills/old-skill

# Commit with explanation
git commit -m "Remove old-skill: replaced by new-skill

The old-skill has been superseded by new-skill which provides
better performance and additional features.

Team members should:
1. Pull this change
2. Restart Claude Code
3. The skill will no longer be available"

# Push and create PR
git push origin remove-unused-skills
```

### Document Removal

Update project documentation:

```markdown
# Changelog

## 2025-10-16

### Removed
- **old-skill**: Replaced by new-skill. See migration guide below.

### Migration Guide
If you were using old-skill:
1. Update your workflows to use new-skill instead
2. Key differences: [list changes]
3. See examples: [link to new-skill examples]
```

## Common Deletion Scenarios

### Skill No Longer Needed

```bash
# Simple removal
rm -rf ~/.claude/skills/deprecated-skill
```

### Skill Replaced by Better Version

```bash
# Backup old version (might need reference)
cp -r ~/.claude/skills/old-skill ~/skill-backups/old-skill-reference

# Delete old version
rm -rf ~/.claude/skills/old-skill

# The new version is already in place
ls ~/.claude/skills/new-skill
```

### Skill Conflicts with Another

If two skills activate on similar triggers:

```bash
# Review both skills
cat ~/.claude/skills/skill-a/SKILL.md | head -n 10
cat ~/.claude/skills/skill-b/SKILL.md | head -n 10

# Decide which to keep (usually the more specific one)
# Delete the less useful one
rm -rf ~/.claude/skills/skill-b
```

### Experimental Skill Didn't Work Out

```bash
# No backup needed for failed experiments
rm -rf ~/.claude/skills/experiment-skill
```

## Safety Checks

### Before Deleting, Ask:

1. **Is this skill used by others?**
   - For project skills, check with team
   - For personal skills, just you

2. **Is there a migration path?**
   - If replacing, document new approach
   - If removing, explain alternatives

3. **Have I backed it up?**
   - Can I restore if needed?
   - Do I have the content archived?

4. **Will this break workflows?**
   - Check dependencies
   - Update documentation
   - Notify affected users

### Validation Checklist

Before deleting a project skill:

- [ ] Created backup
- [ ] Checked for dependents (other skills referencing this one)
- [ ] Notified team members
- [ ] Updated documentation
- [ ] Committed to version control with clear message
- [ ] Verified skill is not critical to current workflows

## Troubleshooting

### Skill Still Appears After Deletion

**Problem**: Deleted skill still shows up in available skills

**Solution**: Restart Claude Code to refresh skill registry

### Cannot Delete (Permission Denied)

```bash
# Check permissions
ls -la ~/.claude/skills/my-skill/

# Fix permissions if needed
chmod -R u+w ~/.claude/skills/my-skill/

# Then delete
rm -rf ~/.claude/skills/my-skill
```

### Accidentally Deleted Important Skill

**If you have a backup**:
```bash
# Restore from backup
cp -r ~/skill-backups/my-skill ~/.claude/skills/my-skill

# Restart Claude Code
```

**If no backup**:
- Check git history (for project skills)
- Check Time Machine or system backups
- Recreate from memory or documentation

### Team Member Still Has Deleted Skill

**For project skills**:

```bash
# Team member should pull latest changes
git pull

# Remove any local-only changes
rm -rf .claude/skills/deleted-skill

# Restart Claude Code
```

## Post-Deletion Cleanup

### Verify Skill List

After deletion, verify skills are as expected:

Ask Claude: "What skills are available?"

Or check filesystem:

```bash
# Personal skills
ls ~/.claude/skills/

# Project skills
ls .claude/skills/
```

### Update Documentation

If maintaining skill documentation:

```markdown
# Available Skills

## Active Skills
- skill-a: Description
- skill-b: Description

## Deprecated Skills
- ~~old-skill~~: Removed 2025-10-16, replaced by new-skill
```

### Clean Up References

Check for references to deleted skills in:
- Documentation files
- README files
- Other skills that might reference it
- Workflow documentation

```bash
# Find references
grep -r "old-skill" .claude/
grep -r "old-skill" docs/
```
