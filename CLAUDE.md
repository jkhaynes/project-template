# CLAUDE.md

<!-- Keep this file short. It loads into every session. Put detail in docs/ and link to it. -->

## Project
**[PROJECT_NAME]**: [One sentence on what this is and who it's for.]
Full product context: `docs/prd.md`. Current status and next step: `docs/state.md`.

## Commands
```bash
# Build:   [e.g. dotnet build]
# Test:    [e.g. dotnet test]
# Run:     [e.g. dotnet run --project src/Api]
# Lint:    [e.g. dotnet format --verify-no-changes]
# Check: ./scripts/check.sh               # format, lint, test, build; the one definition of green
```

## Stack
[e.g. .NET 9 / C#, SQL Server, Angular 19. Keep to one or two lines; the why lives in docs/adr/.]

## Conventions
<!-- Top 5 or so rules Claude would otherwise get wrong. Delete what doesn't apply. -->
- [Folder layout / where new code goes]
- [Naming conventions]
- [Error handling pattern]
- [Data access pattern]
- Never commit secrets. Config goes in [appsettings.Development.json / .env], both gitignored.

## Where things live
| Need | Read |
|------|------|
| What we're building and why | `docs/prd.md` |
| How the system fits together | `docs/architecture.md` |
| Why a past decision was made | `docs/adr/` (index in `docs/adr/README.md`) |
| How to test | `docs/testing.md` |
| Non-negotiable engineering rules | `.specify/memory/constitution.md` |
| What reviewers check, severity, loop limits | `REVIEW.md` |
| Feature specs, plans, tasks | `specs/NNN-feature-name/` |

Read these when the task needs them, not up front.

## Workflow

This project uses **Spec Kit for design** and **Superpowers for implementation**.

**1. Pick the track by size of change**
- **Feature** (new behavior, touches several files, worth remembering why): full Spec Kit track below.
- **Small change** (bug fix, tweak, refactor): skip Spec Kit. Use Superpowers directly (systematic-debugging for bugs, test-driven-development for everything else).
- **Spike / experiment**: Superpowers brainstorming, throwaway branch, no spec. If it survives, promote it to a feature.

**2. Feature track: design (Spec Kit owns this)**
1. `/speckit-specify` : what and why, no tech choices
2. `/speckit-clarify` : resolve ambiguity before planning
3. `/speckit-plan` : technical approach
4. `/speckit-tasks` : ordered task list
5. `/speckit-analyze` : consistency check across spec, plan, tasks

During these steps Spec Kit is the source of truth. Do not run Superpowers brainstorming or writing-plans on top of a Spec Kit feature; that creates a second, competing plan.

**3. Feature track: implementation (Superpowers owns this)**
Do NOT use `/speckit-implement`. Instead, for `specs/NNN-*/tasks.md`:
1. using-git-worktrees : isolated branch/worktree for the feature
2. subagent-driven-development : one fresh subagent per task from tasks.md, test-first (red, green, refactor), spec-compliance review then code-quality review
3. requesting-code-review : before merge. Then run `/code-review`, then `/security-review`, on the branch. Fix each finding test-first, or write why not in the PR's "Review findings not fixed".
4. Open a PR, wait for `gh pr checks --watch` to be green, then merge. The merge-gate hook (`.claude/hooks/merge-gate.py`) blocks merging on red, pushing to `main`/`master`, and local merges that fail `scripts/check`.

If implementation reveals the spec was wrong, stop and update spec.md/plan.md first, then continue.

**4. Before ending a session**
- Update `docs/state.md` (what changed, what's next, any blockers).
- Made a real architectural decision (library, data store, pattern, trade-off)? Add an ADR in `docs/adr/`.
- Changed how components connect? Update `docs/architecture.md`.
- Did a bug reach main? Log it under Escaped bugs in `docs/state.md` and close the loop.

## Learned rules

<!-- Short rules from owner corrections, dated. -->

