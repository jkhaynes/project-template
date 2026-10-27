# Design: the design system and prototypes

How the app's look is decided once, and how each feature with UI gets a clickable prototype the owner approves before `/speckit-specify`.

## The design system

Lives in `design/` at the repo root, made by `/design-system` (normally during `/new-project`):

| File | What it is |
|------|------------|
| `design/tokens.css` | CSS custom properties: color, type, spacing, radius, shadow, motion, for every theme the app supports |
| `design/components.css` | The shared components (buttons, inputs, cards, dialogs, nav, toasts, ...), styled only with tokens |
| `design/style.html` | One interactive page: every component in every state, each theme side by side, and a sample screen or two |
| `design/design-system.md` | `Version: N`, `Approved: YYYY-MM-DD`, what the owner brought, which direction won and why, and a changelog |

Rules:
- The app imports `design/tokens.css` and `design/components.css` from where they are (the first feature's plan decides how its build picks them up). Never copy them into the app's source.
- No hard-coded colors, font sizes or one-off components in features or prototypes. A missing token or component is added to `design/` first and shows up on `style.html`.
- Any change to `design/` bumps `Version`, adds a changelog line, and needs a fresh `Approved:` date from the owner after reviewing `style.html`. The dashboard then flags features whose prototype was approved against the older version.

## Prototypes

Any feature with new or changed UI gets one, made by `/prototype` in the feature's worktree:

| File | What it is |
|------|------------|
| `specs/NNN-*/mockup/prototype.html` | One self-contained, clickable HTML file: the whole flow with fake data and no backend |
| `specs/NNN-*/mockup/tokens.css`, `components.css` | Copies of `design/` at the version the prototype was built on. Never edit them; change `design/` and copy again |
| `specs/NNN-*/mockup/review-ux.md` | The UX reviewer's pass on the prototype, before the owner sees it |
| `specs/NNN-*/mockup.md` | `Approved: YYYY-MM-DD`, `Design system: vN`, and the screens and states the owner approved |

Every prototype has:
- **The full flow, end to end**, including back, cancel halfway, refresh, and arriving on a screen with no data yet.
- **A state switcher**, a small panel marked `data-proto-ui` that is not part of the design. It jumps to any screen and flips the current one between its states: empty, loading, slow, error, too much data, very long text, and any the feature adds. Hash routing (`prototype.html#screen/state`) makes every state linkable, so feedback and reviewers can point at one exactly.
- **Real details**: validation messages, disabled and busy buttons, focus moving where it should, what you see right after saving, and how fast feedback appears.

A prototype is throwaway. Its code never goes into the app; implementation rebuilds it properly from the spec.

## Reviewing in Lavish

The owner reviews `style.html` and every prototype in [Lavish](https://github.com/kunchenguid/lavish-axi), a local editor that runs the page and lets the owner annotate it. Ctrl+I switches between using the page (explore) and leaving notes (annotate); in annotate mode, Ctrl+click follows a link.

The loop, run by Claude:
1. `npx -y lavish-axi@0.1.94 <file>` opens it in the owner's browser. Pages start in explore mode (`<html data-lavish-annotate="off">`).
2. `npx -y lavish-axi@0.1.94 poll <file>` waits for the owner's notes. Read the whole output: reading it consumes the notes.
3. Revise the file, then poll again with `--agent-reply "<what changed>"`.
4. When the owner ends the session or says it's approved, record the `Approved:` date. `npx -y lavish-axi@0.1.94 end <file>` when done.

If `poll` reports `browser_disconnected`, ask the owner whether to reopen or stop. If it reports `ended`, stop polling and don't reopen unless asked.

Rules:
- Never `share`. It publishes the page publicly to a third-party host. (`.claude/settings.json` denies it.)
- Telemetry is off: `.claude/settings.json` sets `LAVISH_AXI_TELEMETRY=0`.
- Lavish is pinned to one version. Upgrade on purpose by changing the version here and in `.claude/settings.json`.
