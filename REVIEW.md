# REVIEW.md

Guidance for every reviewer of this repo: the Superpowers code-quality review, `requesting-code-review`, `/code-review`, `/security-review`, and any PR bot. Read it before reviewing a change.

## Always check

- The change follows every principle in the constitution (`.specify/memory/constitution.md`).
- Each acceptance scenario in the feature's spec (`specs/NNN-*/spec.md`) has a test that exercises it.
- No secrets, keys, tokens or real credentials in code, config, tests or fixtures.
- Error handling follows the conventions in `CLAUDE.md`.
- `scripts/check` passes. A change that makes it fail is not done.

## Don't flag

- Style the formatter or linter already enforces.
- Decisions the owner recorded in a spec, plan or ADR (`docs/adr/`). If one looks wrong, say so once as a question, not a finding.
- Anything in this project-specific list:
  - [e.g. Generated files under `src/Generated/`]

## Severity

| Level | Meaning | Blocks merge? |
|-------|---------|---------------|
| Critical | Wrong result, data loss, or a security hole | Yes |
| Important | A bug likely to happen in real use | Yes |
| Minor | Clarity, naming, small cleanups | No |

Only Critical and Important block. Every blocking finding is fixed (test-first) or answered in the PR's "Review findings not fixed" section.

## Review loop limits

- At most 3 review rounds per PR.
- From round 2 on, review only the new diff since the last round.
- Never repeat a finding that was already resolved or dismissed.
- When one bug appears in several places, flag the class once and list every location.

## Learned review rules

<!-- Added by the escaped-bugs loop: when a bug reaches main that a reviewer should have caught, add a one-line rule here, dated, with a link to the entry in docs/state.md. -->
