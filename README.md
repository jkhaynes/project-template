# Project Template: Spec Kit + Superpowers

Starter repo for new projects built with Claude Code. **Spec Kit** handles design (spec, plan, tasks) and **Superpowers** handles implementation (one worktree per feature, TDD, subagent execution, review). Quality gates (a local check script, CI, review passes and a merge-gate hook) keep red code out of the default branch.

> Replace this README with the real project README once the project has a name and a purpose. The workflow details live in `CLAUDE.md`, so nothing is lost.

## What's in here

```
CLAUDE.md                     Agent instructions + workflow (short, points to docs)
AGENTS.md                     Pointer for non-Claude agents (Copilot, Codex, Cursor)
REVIEW.md                     What every reviewer checks, severity, loop limits, review panel
docs/
  prd.md                      Product-level requirements, goals, NON-goals
  architecture.md             Current system shape across all features
  testing.md                  Test levels, locations, rules, commands
  state.md                    Session-to-session status and next steps
  worktrees.md                One worktree per feature: starting, watching, finishing
  design.md                   Design system, clickable prototypes, reviewing in Lavish
  ai-workflow.html            The whole AI workflow as one diagram (open in a browser)
  adr/                        One file per architectural decision + index
.specify/                     Spec Kit (templates, Python scripts, constitution)
  memory/constitution.md      Pre-filled starter: TDD, Superpowers owns implementation
.claude/
  settings.json               Enables Superpowers, allows Spec Kit scripts, registers hooks
  hooks/merge-gate.(sh|py)    Blocks merging on red CI and pushing to main/master
  hooks/format-file.py        Formats each edited file using hooks/format.json
  hooks/format.json           Extension to formatter map (empty; see format.example.json)
  agents/reviewer-*.md        Review panel lenses: security, code, ux, ui (add files to extend)
  agents/fixer.md, approver.md  Fixes CHANGES findings; writes the APPROVE or ESCALATE decision
  skills/review-panel/        /review-panel: reviewers in parallel, fix loop, approver
  skills/design-system/       /design-system: the app's look, decided once, in design/
  skills/prototype/           /prototype: a clickable prototype per UI feature, approved before the spec
  skills/speckit-*            Spec Kit skills (/speckit-specify, /speckit-plan, ...)
.github/
  workflows/ci.yml            Runs scripts/check.sh on every PR and on the default branch
  pull_request_template.md    Summary, spec, testing, risk, revert, unfixed findings
scripts/check.(sh|ps1)        The one definition of green: format, lint, test, build
scripts/dashboard.(py|html)   Live, read-only board of every feature (python3 scripts/dashboard.py)
scripts/tests/                Tests for the dashboard (python3 -m unittest discover -s scripts/tests)
scripts/init-project.(ps1|sh) One-time placeholder fill + Superpowers install
design/                       Created by /design-system: tokens.css, components.css, style.html, design-system.md
specs/                        Created by /speckit-specify, one folder per feature
```

## Prerequisites

- [Claude Code](https://code.claude.com)
- Python 3, callable as `python3` (Spec Kit's skills use it)
- Node.js, for `npx` (the design system and prototypes are reviewed in [Lavish](https://github.com/kunchenguid/lavish-axi), pinned in `docs/design.md`)
- [uv](https://docs.astral.sh/uv/) and the Spec Kit CLI (only needed for upgrades):
  `uv tool install specify-cli --from git+https://github.com/github/spec-kit.git`

## Starting a new project

1. On GitHub: **Use this template** > **Create a new repository**, then clone it.
2. Run the init script from the repo root:
   ```powershell
   ./scripts/init-project.ps1 -Name "MyProject"
   ```
   ```bash
   ./scripts/init-project.sh "MyProject"
   ```
   This fills `[PROJECT_NAME]` and date placeholders and installs Superpowers at user scope.
3. Write `docs/prd.md` yourself (or with Claude in chat). Non-goals matter most.
4. In Claude Code: `/speckit-constitution` to tailor the rules to this project.
5. Fill in **Commands** and **Stack** in `CLAUDE.md` once they exist, and the same commands at the top of `scripts/check.sh` and `scripts/check.ps1`. Uncomment the setup step for your stack in `.github/workflows/ci.yml`, and map file extensions to formatters in `.claude/hooks/format.json` if you want format-on-edit. In `.claude/agents/reviewer-ux.md` and `reviewer-ui.md`, set `review-paths` to your UI folders so those reviewers skip back-end-only changes, and in `reviewer-smells.md` to your source folders so it skips docs-only changes.
6. If the app has UI: `/design-system` to decide its look.
7. First feature: a worktree (`docs/worktrees.md`), `/prototype` if it has UI, then `/speckit-specify`.

## Which track?

| Situation | Track |
|-----------|-------|
| New behavior, several files, worth remembering why | Spec Kit design, then Superpowers implementation |
| Bug fix, refactor, small tweak | Superpowers only (TDD or systematic-debugging) |
| Spike or experiment | Superpowers brainstorming on a throwaway branch |
| Existing repo without this setup | Copy `docs/`, `CLAUDE.md`, `AGENTS.md`, `REVIEW.md`, `scripts/check.*`, `.claude/hooks/`, `.claude/settings.json` and `.github/`, then `specify init --here --integration claude --script py` |

Full step-by-step is in `CLAUDE.md` under **Workflow**. For the picture, open `docs/ai-workflow.html` in a browser.

## Quality gates

Adapted from Anthropic's write-up on [solving code review](https://claude.dev/blog/solving-code-review-at-anthropic/). Everything here is free to run: no API keys or paid CI. The review panel uses your Claude subscription.

| Where | What | Cost |
|-------|------|------|
| Local, while editing | `format-file.py` hook formats each edited file (once `format.json` is filled in) | Free |
| Local, before the PR | `scripts/check` (format, lint, test, build); Superpowers reviews; `/review-panel` (security, code, UX and UI reviewers in parallel, a fix loop of at most 3 rounds, then an approver that escalates risky changes to you) | Free (subscription) |
| Watching | `python3 scripts/dashboard.py --open`: every feature by stage, with task progress, reviewer verdicts, the decision, CI and the files, refreshed every 2 seconds | Free |
| CI, on every PR | `ci.yml` job `check` runs `scripts/check.sh` | Free (Actions minutes) |
| Merge | `merge-gate.py` blocks `gh pr merge` until `gh pr checks` is green, blocks pushes to `main`/`master`, and lets a local `git merge`/`git pull` of a branch into them through only if that branch's PR checks are green (CI ran `scripts/check.sh` on it). If Python can't start, `merge-gate.sh` still blocks merges | Free |
| After merge | Escaped bugs in `docs/state.md` get a regression test and, when a reviewer should have caught them, a rule in `REVIEW.md` | Free |

On a private repo on the free GitHub plan, branch protection isn't available, so CI shows red or green but can't stop a merge. The merge-gate hook is the real gate there, and it only runs inside Claude Code. For a repo with no CI, set `MERGE_GATE_ALLOW_NO_CHECKS=1`.

## Notes and gotchas

- **One worktree per feature.** Each feature is built in `.worktrees/NNN-feature-name` while the main checkout stays on the default branch, so several features can run at once. `docs/worktrees.md` covers starting one and watching its changes in Claude, VS Code or a terminal.

- **Hooks need Python 3 on PATH as `python3`.** Both hooks are Python scripts. If `python3` isn't found, the merge gate blocks every merge and push and format-on-edit does nothing.

- **Don't use `/speckit-implement`.** Implementation goes through Superpowers (see constitution principle III). The skill is left installed because Spec Kit manages its own files; deleting it would come back on upgrade.
- **Plan mode:** if Claude Code switches into plan mode during Spec Kit or Superpowers planning steps, exit it. Both tools write their own plan files and plan mode fights them.
- **Superpowers install:** `.claude/settings.json` enables it for the project, but project-scoped plugins have been flaky, which is why the init script also installs it at user scope. If skills don't show up, run `/plugin install superpowers@claude-plugins-official` inside Claude Code.
- **Upgrading Spec Kit:** `specify self upgrade`, then `specify integration upgrade` from the repo root. Check `git diff` afterward, especially `.specify/memory/constitution.md`.
- **Optional bridge extension:** Spec Kit's catalog has a community "Superpowers Implementation Bridge" extension that formalizes the handoff. This template does the same thing through the constitution and CLAUDE.md, with no extra dependency.

Scaffolded with Spec Kit 1.0.14.dev0.
