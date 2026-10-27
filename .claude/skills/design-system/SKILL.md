---
name: design-system
description: Create or change the app's design system in design/ (tokens.css, components.css, an interactive style.html, design-system.md), reviewed and approved by the owner in Lavish. Use during /new-project, when the user types /design-system, before the first prototype if design/ doesn't exist yet, or whenever the look of the app should change (new color, font, component or theme).
---

# Design system

You decide the app's look with the owner once, as files every prototype and the real app use. `docs/design.md` has the files, the rules and the Lavish review loop; read it first. Ask one question per message. Every choice that lands in `design-system.md` comes from the owner's words or an option they picked.

## New design system

For an app that already has a brand or styling, use "An app that already has a look" below instead. Skip this whole skill if the app has no UI (a CLI, a library, an API with no pages). Say so and stop.

1. **Ask what they bring.** One open question: what should this feel like, and do they have anything to show (a few words, links or screenshots of apps they like, a logo or brand colors, or nothing yet)? Read the PRD first so the question and the directions fit the users and purpose. Also settle the themes: light, dark, or both.
2. **Directions.**
   - If they brought a lot (clear words plus references or brand colors), build one direction.
   - If they brought little or nothing, build two or three clearly different directions. One of them is always the owner's house style: deep navy ground (`#111a2e`), panel `#19243f`, raised `#22304f`, border `#34426a`, text `#eef1f8`, muted text `#aab5cf`, muted pink accent `#e6a9bc`, cozy and soft. Name each direction in two or three words.
   - Each direction is one page, `design/directions/<letter>-<name>.tmp.html` (gitignored), with its tokens inline, the core components and the same sample screen from this app's PRD, so the owner compares like with like.
   - Open each in Lavish (`docs/design.md`, Reviewing in Lavish). The owner picks one, mixes ("A's colors with B's type"), or rejects all and says why. Repeat until one direction stands.
3. **Build the system** from the chosen direction:
   - `design/tokens.css`: CSS custom properties on `:root`, with each theme under `[data-theme="..."]` and the default theme following `prefers-color-scheme` when there are two. Cover color (ground, surfaces, text, muted text, border, accent, success, warning, danger, focus ring), type (families, a size scale, weights, line heights), spacing scale, radius, shadow and motion (durations, easing, and `prefers-reduced-motion`). Fonts from Google Fonts or system stacks only.
   - `design/components.css`: buttons (primary, secondary, quiet, danger), inputs, select, checkbox, radio, switch, field labels, help and error text, cards, dialog, toast, nav, tabs, table, empty state, skeleton loader, spinner. Only tokens, no raw values. Hover, focus-visible, active, disabled, busy and error states for each that has them.
   - `design/style.html`: links both files, starts in explore mode (`<html data-lavish-annotate="off">`), shows every component in every state, each theme side by side, a type and color reference, and one or two realistic sample screens from the PRD. A theme toggle at the top. Text contrast at least 4.5:1 in every theme; check it.
4. **Review** `style.html` in Lavish until the owner approves it.
5. **Write `design/design-system.md`**:
   ```markdown
   # Design system

   Version: 1
   Approved: YYYY-MM-DD

   ## What the owner brought
   <their words, links, colors; or "Nothing; chose from directions">

   ## Direction
   <the chosen direction, what was mixed in, and why, in the owner's words where possible>

   ## Themes
   <light / dark / both, and which is default>

   ## Changelog
   - v1 YYYY-MM-DD: first version
   ```
6. Delete the `design/directions/*.tmp.html` files with a plain `rm` on each. Commit `design/` with `docs(design): design system v1`.

## An app that already has a look

When the app already has a brand or styling (brand docs CLAUDE.md points to, theme or token files, global stylesheets, shipped screens), don't offer directions: the look is decided, it just isn't written down as a system yet.

1. Read the brand docs and the app's styling, and look at the main screens in the running app.
2. Build `design/tokens.css`, `components.css` and `style.html` from what is actually there, with the same coverage as above. Where the app is inconsistent (three greys for one job, two button shapes), list each case and ask the owner which one wins.
3. Review `style.html` in Lavish until approved, then write `design-system.md` as above, with "What the owner brought" naming the brand docs and existing styles it was taken from. Commit `docs(design): design system v1` on its own branch and PR.
4. Moving the app's own styles onto `design/` is a separate change: suggest it as its own feature or small change, so this step doesn't touch app code.

## Changing the design system

1. Ask what should change and why. If it's for one feature, check it really belongs in the system rather than being a one-off.
2. Edit `design/tokens.css`, `design/components.css` and `style.html` so the change shows there.
3. Review `style.html` in Lavish until approved.
4. In `design-system.md`: bump `Version`, set `Approved:` to today, add a changelog line saying what changed and why.
5. Commit `docs(design): design system vN` on its own branch and PR, like any change to the default branch. Tell the owner the dashboard will flag features whose prototype was approved on an older version; each needs `/prototype` to copy the new files in and a quick re-approval.
