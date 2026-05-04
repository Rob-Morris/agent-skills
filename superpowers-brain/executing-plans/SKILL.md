---
name: executing-plans
description: >
  Executes a written implementation plan in a separate session with review
  checkpoints.
  Use when a plan already exists and work should follow it task by task.
---

# Executing Plans

## Overview

Load plan, review critically, execute all tasks, report when complete.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

**Plan state management (Brain mode):** In a Brain vault (a `.brain/` directory exists at the project root), this skill owns the plan's `status` field. It sets `implementing` before Step 2 starts and `completed` at the end of Step 3 — whether or not a development branch was created. No other skill moves these statuses.

**Note:** Tell your human partner that Superpowers works much better with access to subagents. The quality of its work will be significantly higher if run on a platform with subagent support (such as Claude Code or Codex). If subagents are available, use superpowers-brain:subagent-driven-development instead of this skill.

## The Process

### Step 1: Load and Review Plan

**Locate the plan:**
- If you have the plan's file path, read it directly.
- **In Brain mode**, if your human partner refers to the plan by title or subject rather than path, use `brain_list(type="plans")` to enumerate plans or `brain_search(query="<subject>", type="temporal/plans")` for relevance-ranked matches. Confirm the match with your human partner before proceeding if ambiguous.

**Load and review:**
1. Read plan file
2. Review critically - identify any questions or concerns about the plan
3. If concerns: Raise them with your human partner before starting
4. If no concerns: Create TodoWrite and proceed

**In Brain mode, mark the plan as implementing before moving to Step 2:**
- `brain_edit(resource="artefact", path="<plan path>", operation="edit", frontmatter={"status": "implementing"})` (omit `body` — frontmatter-only change)

### Step 2: Execute Tasks

For each task:
1. Mark as in_progress
2. Follow each step exactly (plan has bite-sized steps)
3. Run verifications as specified
4. Mark as completed

### Step 3: Complete Development

After all tasks complete and verified:
- Announce: "I'm using the finishing-a-development-branch skill to complete this work."
- **REQUIRED SUB-SKILL:** Use superpowers-brain:finishing-a-development-branch
- Follow that skill to verify tests, present options, execute choice

**In Brain mode, mark the plan as completed once finishing-a-development-branch returns:**
- `brain_edit(resource="artefact", path="<plan path>", operation="edit", frontmatter={"status": "completed"})`
- This applies whether or not a development branch was created — `completed` means "execution is finished", not "branch is merged".

## When to Stop and Ask for Help

**STOP executing immediately when:**
- Hit a blocker (missing dependency, test fails, instruction unclear)
- Plan has critical gaps preventing starting
- You don't understand an instruction
- Verification fails repeatedly

**Ask for clarification rather than guessing.**

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**
- Partner updates the plan based on your feedback
- Fundamental approach needs rethinking

**Don't force through blockers** - stop and ask.

## Remember
- Review plan critically first
- Follow plan steps exactly
- Don't skip verifications
- Reference skills when plan says to
- Stop when blocked, don't guess
- Never start implementation on main/master branch without explicit user consent

## Integration

**Required workflow skills:**
- **superpowers-brain:using-git-worktrees** - REQUIRED: Set up isolated workspace before starting
- **superpowers-brain:writing-plans** - Creates the plan this skill executes
- **superpowers-brain:finishing-a-development-branch** - Complete development after all tasks
