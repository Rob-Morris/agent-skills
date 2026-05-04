# Superpowers Brain

Imported Superpowers skill family for this repo, kept under a grouped
`superpowers-brain` namespace so the original skill references stay intact.

This is a Brain-compatible adaptation of the Superpowers workflow skill
library. The imported family preserves the original planning, execution,
debugging, review, and subagent workflows, but is adapted for Brain-oriented
use:

- Brain remains the system of record for durable outputs such as plans,
  designs, and vault-local skills
- Brain-oriented workflow expectations are preserved where the imported skills
  already include them
- The grouped `superpowers-brain` namespace keeps upstream cross-references
  intact without flattening the family into many unrelated top-level skills

## Source

Adapted from the `Rob-Morris/superpowers` fork, which is itself adapted from
the upstream `obra/superpowers` project:

- Fork: <https://github.com/Rob-Morris/superpowers>
- Upstream: <https://github.com/obra/superpowers>
- Upstream license: MIT

This repo carries additional local adaptations for Brain compatibility and for
this repo's grouped skill layout and metadata conventions.
