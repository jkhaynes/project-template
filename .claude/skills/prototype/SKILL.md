---
name: prototype
description: Build the clickable prototype for a feature with new or changed UI, have the UX reviewer try it, then get the owner's approval in Lavish and record it in specs/NNN-*/mockup.md. Feature design step 1, before /speckit-specify. Use when the user types /prototype, asks for a mockup or prototype of a feature, or a prototype must be refreshed after the design system changed.
---

# Prototype

You build one throwaway, clickable HTML prototype of the feature, styled only with the design system, so the owner can catch bad experiences before any real code exists. `docs/design.md` has the file layout, the rules and the Lavish review loop; read it first.

## Before you start

1. **Worktree.** You must be in the feature's worktree (`.worktrees/NNN-name`, CLAUDE.md design step 0), not on `main` or `master`. The feature folder is `specs/<branch>/`; create it if it doesn't exist.
2. **Design system.** Read `design/design-system.md`. If it doesn't exist or has no `Approved:` date, stop and run `/design-system` first: a prototype with no system invents a look.
3. **What the feature is.** Read `docs/prd.md` (its capability row) and anything the owner has said. Ask, one question per message, until you can list the screens, the path through them, who uses it (signed out, new with no data, returning, each role) and what can go wrong. Play the list back and get a yes before building.

## Build

1. Copy `design/tokens.css` and `design/components.css` into `specs/NNN-*/mockup/`. Never edit the copies.
2. Write `specs/NNN-*/mockup/prototype.html`:
   - One file: vanilla HTML, CSS and JavaScript, linking only `./tokens.css`, `./components.css` and the system's fonts. Fake data inline. No backend, no build step, no other libraries.
   - Starts in explore mode: `<html data-lavish-annotate="off">`.
   - Uses only the system's tokens and components. If something is missing, stop and change the system with `/design-system` first.
   - Hash routing, `#<screen>/<state>`, so every screen and state has its own link and works on refresh.
   - The whole flow works: navigation, back, cancel halfway, dialogs, forms that validate, saving that shows its result, a fake delay on anything that would hit a server.
   - The state switcher (`docs/design.md`): a small fixed panel marked `data-proto-ui`, visually distinct from the design, that jumps to any screen and flips the current one between empty, loading, slow, error, too much data, very long text, plus any state this feature adds. The `?` key hides and shows it.
   - Works at phone width (390 px) as well as desktop, and with the keyboard alone.

## UX pass before the owner

Spawn the `reviewer-ux` agent in prototype mode: give it the feature folder, the worktree, the output file `specs/NNN-*/mockup/review-ux.md` and port `5000 + n` (feature `008` -> 5008). When it's done, fix every Critical and Important finding in the prototype, and add a line under each finding in your reply to the owner saying what you changed. Leave Notes for the owner to judge.

## Owner review

1. Open `prototype.html` in Lavish (`docs/design.md`, Reviewing in Lavish). Tell the owner in one line what to try: the main path, then the state switcher.
2. Loop: poll, revise, reply, until the owner approves or ends the session saying it's approved.
3. Write `specs/NNN-*/mockup.md`:
   ```markdown
   # Prototype: <feature name>

   Approved: YYYY-MM-DD
   Design system: v<N from design/design-system.md>
   Prototype: mockup/prototype.html

   ## Screens and states
   - <screen>: <states it has, e.g. empty, loading, error, long text>

   ## What was approved
   <the flow in a few lines, and decisions the owner made during review>
   ```
4. Commit the feature folder with `docs(NNN): approved prototype`. Then the next step is `/speckit-specify`: pass it `mockup.md`, and say every screen and state listed there needs an acceptance scenario.

## Refreshing after a design system change

When the dashboard says the prototype predates the design system: copy `design/tokens.css` and `components.css` into `mockup/` again, fix anything the change broke, show the owner in Lavish, then update `Approved:` and `Design system:` in `mockup.md`.
