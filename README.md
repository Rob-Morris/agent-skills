# agent-skills

A collection of useful agent skills that I've written.

## Layout

Skills live in their own directories, each containing a `SKILL.md` (with YAML frontmatter describing `name` and `description`) and any supporting files.

## Install or update local skills

The cross-platform updater requires Python 3 and synchronises this repository's top-level skills to the local Codex and Claude skill directories. It records ownership and content hashes, preserves modified copies unless explicitly replaced, and leaves Brain-managed adapters untouched. It works on macOS, Linux, and Windows.

```sh
# Inspect the current installation without changing anything.
python3 scripts/sync_client_skills.py --check

# Refresh the two design-review skills for both clients. `--replace` archives
# the pre-existing un-managed copies on first use.
python3 scripts/sync_client_skills.py --skill software-design-principles --skill software-design-review --replace
```

On Windows, use `python` in place of `python3`. Omit `--skill` to synchronise every top-level skill. Use `--dry-run` to preview changes.

## Skills

| Skill | Last updated | Description |
| --- | --- | --- |
| [colour-palette](colour-palette/) | 2026-05-03 | Guides colour and palette selection — CSS themes, UI components, terminal configs, status bars, brand identity. |
| [shaping](shaping/) | 2026-08-25 | Shapes documents and other artefacts through adaptive, structured Q&A, with a revisable plan for shaping style, completion bar, and persistence. Use when developing an idea, design, plan, or other artefact whose purpose, decisions, content, or exploratory understanding need to be worked through collaboratively. |
| [software-design-principles](software-design-principles/) | 2026-08-21 | Provides guidance on good software design principles, with trade-off calibration, examples, and common failure modes. Use when making decisions while writing, designing, or refactoring code, or evaluating code for clarity, maintainability, and common mistakes. |
| [software-design-review](software-design-review/) | 2026-08-21 | Reviews code and software designs against established design principles, and returns triaged findings. Use when reviewing code or software designs that are complex or important, for clearer, easier to maintain software that avoids common mistakes. |
| [superpowers-brain](superpowers-brain/) | 2026-07-28 | Routes the Superpowers workflow skill family for planning, execution, debugging, review, and git-worktree or subagent workflows. Use when the imported Superpowers methodology is relevant or when a `superpowers-brain:*` subskill is explicitly requested. |
| [swarm-test](swarm-test/) | 2026-05-03 | Dispatches a swarm of small agents to test docs, implementations, or designs. Modes: `review` and `evaluate`. |

## License

[MIT](LICENSE)
