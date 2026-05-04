---
name: superpowers-brain
description: >
  Routes the Superpowers workflow skill family for planning, execution,
  debugging, review, and git-worktree or subagent workflows.
  Use when the imported Superpowers methodology is relevant or when a
  `superpowers-brain:*` subskill is explicitly requested.
---

# Superpowers Brain

Imported Superpowers skill family, kept under one grouped namespace so the
original cross-references stay intact.

## Families

### Orientation

- `using-superpowers` — introduction to the overall Superpowers workflow and
  skill-discipline posture.

### Design And Planning

- `brainstorming` — explores ideas before implementation
- `writing-plans` — writes implementation plans
- `writing-skills` — creates or refines skills

### Execution

- `executing-plans` — executes a written plan inline
- `subagent-driven-development` — executes a plan with per-task review gates
- `subagent-driven-development-light` — lighter plan execution with one final
  review
- `using-git-worktrees` — sets up isolated worktrees
- `finishing-a-development-branch` — closes out completed implementation work
- `dispatching-parallel-agents` — coordinates independent parallel tasks

### Review And Quality

- `requesting-code-review` — requests focused review
- `receiving-code-review` — handles review feedback rigorously
- `systematic-debugging` — drives bug investigation
- `test-driven-development` — enforces TDD during implementation
- `verification-before-completion` — verifies claims before calling work done

## Routing

- Start with the overall Superpowers methodology or want its strict
  skill-discipline posture → `using-superpowers`
- Need to explore or shape before building → `brainstorming`
- Need to turn requirements into an implementation plan → `writing-plans`
- Need to execute a plan yourself → `executing-plans`
- Need to execute a plan with fresh-context subagents → `subagent-driven-development`
  or `subagent-driven-development-light`
- Need review, debugging, TDD, or verification discipline → go directly to the
  matching subskill

When a subskill is selected, read and follow that subskill's `SKILL.md`.
