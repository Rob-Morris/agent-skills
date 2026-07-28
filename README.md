# agent-skills

A collection of useful agent skills that I've written.

## Layout

Skills live in their own directories, each containing a `SKILL.md` (with YAML frontmatter describing `name` and `description`) and any supporting files.

## Skills

| Skill | Last updated | Description |
| --- | --- | --- |
| [code-review](code-review/) | 2026-05-03 | Reviews changed code and produces a triaged list of findings (no edits). For fixes, see `code-review:fix`. |
| [colour-palette](colour-palette/) | 2026-05-03 | Guides colour and palette selection — CSS themes, UI components, terminal configs, status bars, brand identity. |
| [shaping](shaping/) | 2026-05-03 | Shapes an artefact through structured Q&A — routes to `brainstorm`, `refine`, or `discover`. |
| [software-design-principles](software-design-principles/) | 2026-05-08 | Provides guidance on good software design principles, with trade-off calibration, examples, and common failure modes. Applies when making decisions while writing, designing, or refactoring code, or evaluating trivial code for clarity, maintainability, and common mistakes. |
| [software-design-review](software-design-review/) | 2026-05-08 | Reviews code with a team against established software design principles, and returns triaged findings (no edits). Use when evaluating code, or after writing or refactoring complex code, systems or technical designs, for code that is clearer, easier to maintain, and avoids common mistakes. |
| [superpowers-brain](superpowers-brain/) | 2026-07-28 | Routes the Superpowers workflow skill family for planning, execution, debugging, review, and git-worktree or subagent workflows. Use when the imported Superpowers methodology is relevant or when a `superpowers-brain:*` subskill is explicitly requested. |
| [swarm-test](swarm-test/) | 2026-05-03 | Dispatches a swarm of small agents to test docs, implementations, or designs. Modes: `review` and `evaluate`. |

## License

[MIT](LICENSE)
