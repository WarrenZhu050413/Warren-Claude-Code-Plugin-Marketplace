---
description: Merge changes from a child session into the current branch (project)
allowed_tools: ["Bash", "Read", "Edit", "Glob", "Grep"]
---

# Merge Child Session Changes

I'll help you merge changes from child session `$1` into your current branch.

## Step 1: Review Changes

First, let's see what changes the child session has made:

```bash
git diff HEAD...$1
```

## Step 2: Check for Uncommitted Changes in Child Branch

Let's check if there are uncommitted changes in the child branch that need to be committed first:

```bash
git diff $1
```

If there are uncommitted changes, I'll need to:
1. Check out the child worktree location (typically at `~/.orchestra/worktrees/<repo>/<session-id>/`)
2. Review the changes
3. Commit them with an appropriate message
4. Return to the main branch

## Step 3: Merge the Child Branch

Once all changes are committed in the child branch, I'll merge it into your current branch:

```bash
git merge $1
```

## Step 4: Verify and Clean Up

After merging:
1. Run any tests to ensure nothing broke
2. Confirm the merge looks correct
3. Optionally delete the child branch if no longer needed: `git branch -d $1`

Let me start by reviewing the changes...
