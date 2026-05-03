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
| [software-design-principles](software-design-principles/) | 2026-05-03 | Provides a situational reference for software design — principles, trade-off calibration, examples, and common failure modes. |
| [software-design-review](software-design-review/) | 2026-05-03 | Reviews code against software design principles with a team of reviewers; returns triaged findings (no edits). |
| [swarm-test](swarm-test/) | 2026-05-03 | Dispatches a swarm of small agents to test docs, implementations, or designs. Modes: `review` and `evaluate`. |

## License

[MIT](LICENSE)
