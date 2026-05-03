# Working on this repo

This is a collection of agent skills. Each skill lives in its own top-level directory with a `SKILL.md` (YAML frontmatter + body) and any supporting files.

## Before committing, review each changed skill

For every skill touched by the change, check:

1. **Clear name.** The skill's `name` in frontmatter matches the directory and reads as a concise label for what the skill is.
2. **Specific description with key terms.** The `description` in frontmatter is concrete, not generic. It uses the words a future agent or user would search for when looking for this skill.
3. **Description structure: what, then when, in third person.** The description first says *what the skill does*, then *when to use it*. Written in third person — "Reviews changed code…", not "I review…" or "Use this to review…".

## Maintain the README index

The `README.md` has a Skills index table with one row per top-level skill. When a skill is added, removed, or changed:

- Add or remove its row.
- Update its **last-updated date** (today's date) every time the skill is changed.
- Keep the description in the index aligned with the skill's frontmatter description (short, third person, what-then-when).
