# Nigeria Federal Budget Analytics — Design System

This is the **single source of truth** for the look, feel, and motion of the BudgetIQ dashboard. Any new page, component, or feature must use only the tokens and patterns defined here. If something you need isn't listed, raise it before inventing a new value — the whole point is consistency.

> **Color lineage:** scheme derived from eyemark.ng. Typography is Filson Pro. Motion is GSAP-driven with a `prefers-reduced-motion` fallback.

---

## 1. Foundations

### 1.1 Typography

**Family:** `'Filson Pro', sans-serif` — loaded from `fonts/` as local woff2. Weights available: 350 (Book), 400 (Regular), 500 (Medium), 700 (Bold), 800 (Heavy). **Never use system fonts or import new fonts.**

**Base:** `html { font-size: 14px }`. All type scales below are absolute `px`, not `rem`, to match the codebase.

| Role                      | Size     | Weight | Letter-spacing | Example use                |
|---------------------------|----------|--------|----------------|----------------------------|
| Hero / big score          | 64px     | 700    | —              | `.scorecard .score-value`  |
| Pulse metric              | 26px     | 700    | -0.5px         | `.pulse-value`             |
| Overview stat             | 24px     | 700    | —              | `.overview-stat-value`     |
| Stat card value           | 22px     | 700    | —              | `.stat-card-value`         |
| Header title              | 20px     | 700    | -0.2px         | `.header-title`            |
| Treemap value, MDA name   | 18px     | 700    | —              | `.mda-name`, `.treemap-value` |
| Logo title                | 17px     | 700    | 0.3px          | `.logo-title`              |
| Section title             | 16px     | 700    | —              | `.section-title`           |
| Zone amount               | 15px     | 700    | —              | `.zone-amount`             |
| Body / nav link           | 13–13.5px| 400–600| —              | `.nav-link`, `.analytics-tab` |
| Table cell, mono number   | 12.5–13px| 500–600| —              | `.data-table td`, `.mono`  |
| Stat label (caps)         | 12px     | 600    | 0.5px / UPPER  | `.stat-card-label`         |
| Small label, footer       | 11–11.5px| 500–600| varies         | `.zone-name`, `.header-date` |
| Section / nav caps label  | 10–11px  | 600–700| 0.8–1.2px / UPPER | `.nav-section-label`, `.tab-group-label` |

**Rules:**
- Caps labels (nav sections, stat labels, tab groups) are always `text-transform: uppercase` + letter-spacing ≥ 0.5px.
- Numeric values in tables use class `.mono` (still Filson Pro, but tightened for tabular feel).
- Body line-height is `1.5`, hero values override to `1.15` or `1`.

### 1.2 Color tokens

All colors live as CSS custom properties in `:root` (see `styles.css` lines 43–95). **Never hardcode hex values in new CSS** — always reference the variable.

**Primary greens** (brand + interactive):
```
--green-core:      #4BAA73   ← primary brand, active states, CTAs
--green-light:     #6EBB8E
--green-muted:     #86C6A1
--green-mid-dark:  #3D9A63   ← primary hover
--green-deep:      #357951   ← active nav text
--green-darkest:   #217042   ← zone amounts, strongest accent
```

**Green tints** (backgrounds, hover fills):
```
--green-tint-100:  #F0F9F4   ← subtle hover bg (table rows, zones)
--green-tint-200:  #EAF5EE   ← section header bottom border
--green-tint-300:  #D7F4E3   ← status "active/ongoing" badge bg
--green-tint-400:  #C7E5D3
--green-tint-500:  #ACD8BE
```

**Gold / amber accents:**
```
--gold-primary:    #FFCC00   ← user avatar bg
--gold-amber:      #FFB300   ← warning traffic light
--gold-orange:     #FF9500
--gold-dark:       #F57F17   ← delayed/amber text
--gold-light:      #F9C466
--gold-warm-bg:    #FCFAF7   ← delayed/on-hold status bg
```

**Structural / text:**
```
--text-primary:    #252117   ← main text, active state text (DEFAULT)
--text-navy:       #19486A
--text-dark:       #1A1A1A
--text-charcoal:   #212B36
```

**Neutrals:**
```
--grey-body:       #5E5E5E   ← secondary text, nav default
--grey-muted:      #9CA3AF   ← tertiary text, placeholders, subtitles
--grey-disabled:   #C8C8C8
--border-standard: #F4F4F4   ← card borders
--border-light:    #EDEEEF   ← dividers, table rows, header bottom
--bg-white:        #FFFFFF
--bg-offwhite:     #F9F9F9   ← table headers
--bg-light:        #F4F4F4   ← tab-bar bg, stat-bar track
--bg-card:         #F6F7F7   ← fiscal pulse, alt cards
```

**Additional neutrals used in tab bar** (hardcoded — the only exception):
```
#A0AFBF  ← inactive tab text, inactive tab-group label (the "mid" grey)
#C8D4DE  ← fully faded tab-group label when another group is active
```

**Status:**
```
--status-error:    #E22034 / bg #FEE2E2   ← stalled, abandoned
--status-info:     #226AF5
--status-warning:  #F1C40F
--status-success:  #07BC0C
```

**"Completed" status** uses hardcoded blues `#E0F2FE` / `#0369A1` (only place — kept for WCAG contrast).

### 1.3 Spacing

No explicit `--space-*` scale — the codebase uses a **4px base implicit grid**. Stick to these values:

| Token (px) | Typical use                                   |
|-----------:|-----------------------------------------------|
| 2          | Micro gaps inside badges                      |
| 4          | Badge internal padding, tight gaps            |
| 8          | Default gap between inline items, icon gaps   |
| 12         | Trigger padding, range-body inner             |
| 16         | Card body padding, grid gap, nav padding      |
| 24         | Chart card padding, section gap               |
| 32         | Header horizontal padding, fiscal pulse padding |
| 64         | Scorecard padding                             |

**Grid gap default:** `16px` everywhere. Section bottom margin: `24px`. Content container padding: `24px 32px` desktop, `16px` mobile.

### 1.4 Borders & radius

| Token | Use |
|------:|-----|
| `4px`  | Small badges (status, analytic, pulse-delta) |
| `6px`  | Mini buttons, dropdown options, range selects, section badge |
| `8px`  | **Default radius** — cards, tables (`.table-wrap`), nav links, search bar, filter tabs, year dropdown, zone cards, inputs |
| `10px` | Stat cards, chart cards, treemap cells, insight cards, overview stats, full-width charts |
| `12px` | MDA header card |
| `14px` | Fiscal pulse banner, scorecard |

**Borders:**
- Cards: `1px solid var(--border-standard)` (#F4F4F4)
- Inputs / dropdowns: `1px solid var(--border-light)` (#EDEEEF)
- Focus/active: `1px solid var(--green-core)` + optional `box-shadow: 0 0 0 2-3px rgba(75, 170, 115, 0.12)`
- Insight cards: use **4px left accent border** colored by semantic (`insight-green`, `insight-amber`, `insight-red`).

### 1.5 Shadows

Only two levels exist. Keep it that way.

```css
/* Resting card */
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);

/* Hover (applied by GSAP, not CSS) */
box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);

/* Dropdown popover */
box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);

/* Treemap hover */
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
```

---

## 2. Layout

### 2.1 Shell

```
┌─────────────────────────────────────────────────────┐
│ .layout (display:flex, min-h:100vh)                 │
│ ┌──┬──────────────────────────────────────────────┐ │
│ │SB│ .main                                        │ │
│ │  │ ┌──────────────────────────────────────────┐ │ │
│ │  │ │ .header  (sticky, 60px, edge-to-edge)    │ │ │
│ │  │ ├──────────────────────────────────────────┤ │ │
│ │  │ │ .analytics-tab-bar (edge-to-edge)        │ │ │← injected only on Analytics
│ │  │ ├──────────────────────────────────────────┤ │ │
│ │  │ │ .content (max-width 1440px, centered)    │ │ │
│ │  │ │     #page-content                        │ │ │
│ │  │ └──────────────────────────────────────────┘ │ │
│ └──┴──────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

- **Sidebar:** fixed left, collapsed width `56px`, expanded `260px`. Toggles via click (GSAP spring physics on chevron). Expands/collapses with `transition: width 250ms ease-out`. `.main` margin-left follows via `.sidebar.expanded ~ .main`.
- **Header:** sticky, 60px tall, `padding: 0 32px`, `border-bottom: 1px solid var(--border-light)`, bg white. Contains `.header-title` (left) and `.header-right` with year-filter + live-badge + date (right).
- **Tab bar (Analytics only):** DOM-injected by `pageAnalytics.render()` as a direct child of `.main` between `.header` and `.content` — this is what makes it edge-to-edge. `padding: 0 32px`, bg `#F4F4F4`, min-height `48px`, horizontal scroll if overflow.
- **Content:** `max-width: 1440px`, centered, padding `24px 32px`. Holds all page content including stat rows and grids.

### 2.2 Responsive breakpoints

Only two:

- **1200px**: stat rows collapse from 4 → 2 cols, `.grid-7-5` and `.grid-5-7` stack, zones 3 → 2 cols, treemap 12 → 6 cols.
- **768px**: sidebar hidden, header padding `0 16px`, content padding `16px`, everything stacks to 1 col, fiscal pulse switches to column direction, header date hidden, tab-bar padding `0 16px`.

Don't invent new breakpoints.

---

## 3. Components

Each component below has a **class name**, an **HTML skeleton**, and the **rules** for building it. When adding new HTML, match these exactly.

### 3.1 Stat card

Small KPI tile. Used in `.stat-cards-row` (4-col grid) or as project-overview stat.

```html
<div class="stat-card anim-card">
  <div class="stat-card-header">
    <span class="stat-card-label">LABEL IN CAPS</span>
    <!-- optional icon / delta -->
  </div>
  <span class="stat-card-value">₦17.81T</span>
  <div class="stat-card-footer">
    <span class="stat-pct">80% of goal</span>
    <span class="stat-absorption">High</span>
  </div>
  <div class="stat-bar"><div class="stat-bar-fill" style="width: 80%; background: var(--green-core);"></div></div>
</div>
```

- Always `.anim-card` so GSAP picks it up on page reveal.
- Value is the only place the count-up animation runs — `.stat-card-value` is one of the scanned selectors.
- Bar fill color encodes semantic: green-core (good), gold-amber (watch), status-error (bad).

### 3.2 Chart card

```html
<div class="chart-card anim-card">
  <div class="chart-card-header">
    <span class="chart-title">Revenue vs Expenditure</span>
    <span class="analytic-badge">ANALYTIC</span>
  </div>
  <div class="chart-wrap"><canvas></canvas></div>
  <div class="chart-legend">
    <div class="legend-item"><span class="legend-dot" style="background: var(--green-core)"></span>Revenue</div>
  </div>
</div>
```

- `.chart-wrap` height is **always 280px** (default), `.chart-wrap-doughnut` 260px, `.chart-wrap-hbar` 320px.
- Never put raw canvases without a `.chart-wrap*` container — GSAP's reveal needs it.
- Legend lives below the chart, `flex-wrap` so it wraps on narrow cards.
- `.analytic-badge` is a rounded 4px green pill in the header for editorial labels.

### 3.3 Fiscal pulse banner

Hero banner on the dashboard page. One per page max.

```html
<div class="fiscal-pulse">
  <div class="pulse-glow pulse-glow-1"></div>
  <div class="pulse-glow pulse-glow-2"></div>
  <div class="pulse-metric">
    <span class="pulse-label">TOTAL BUDGET 2025</span>
    <span class="pulse-value">₦17.81T</span>
    <span class="pulse-delta delta-green">+12.3%</span>
  </div>
  <div class="pulse-divider"></div>
  <!-- more pulse-metric blocks -->
</div>
```

- Background is `#F6F7F7` (bg-card) with two absolute `.pulse-glow` radial gradients — **do not replace** these with solid colors; they're animated by `Anim.startAmbient()`.
- Delta classes: `delta-green` (positive/good), `delta-amber` (neutral/watch), `delta-neutral` (static).
- Dividers between metrics are 1px × 64px `#EDEEEF`.
- Always comes first in the page after section header.

### 3.4 Section header

```html
<div class="section-header">
  <h2 class="section-title">
    <span class="section-badge">A</span>
    Section Title
  </h2>
</div>
```

- Letter badges run **A, B, C, D, E, F, G, H** across pages — reuse this alphabet, don't restart per page.
- Badge: 26×26px, 6px radius, green-core bg, white 12px 700 text.
- Bottom border: `2px solid var(--green-tint-200)` — this is the page's structural rhythm line.

### 3.5 Tables

```html
<div class="table-wrap">
  <table class="data-table">
    <thead><tr><th>MDA</th><th>Allocation</th></tr></thead>
    <tbody>
      <tr><td>Education</td><td class="mono">₦1.2T</td></tr>
    </tbody>
  </table>
</div>
```

- **Always** wrap in `.table-wrap` — that's what gives the 8px rounded corners (via `overflow:hidden` + border).
- `border-collapse: separate` + `border-spacing: 0` — **do not** change to `collapse`, it breaks the border-radius.
- Last row has `border-bottom: none` (handled by CSS — don't override).
- Numeric columns use `class="mono"` on the `<td>`.
- Row hover bg: `var(--green-tint-100)`.
- Header row bg: `var(--bg-offwhite)`.

### 3.6 Status badges

```html
<span class="status-badge status-active">Active</span>
```

Variants — **use these exact classes**:
- `status-active`, `status-ongoing` → green
- `status-completed` → blue
- `status-delayed`, `status-on-hold` → gold/amber
- `status-stalled`, `status-abandoned` → red

Never add a new status color without adding it to `styles.css` first.

### 3.7 Tab bar (Chrome-style groups)

The most distinctive UI in the app. Used only on the Analytics page.

```html
<div class="analytics-tab-bar">
  <div class="tab-group has-active expanded">
    <button class="tab-group-label">GROUP A</button>
    <div class="tab-group-tabs">
      <button class="analytics-tab active">Tab 1</button>
      <button class="analytics-tab">Tab 2</button>
    </div>
  </div>
  <div class="tab-group">
    <button class="tab-group-label">GROUP B</button>
    <!-- ... -->
  </div>
</div>
```

**Four-tier visual hierarchy** (do not break this):
1. **Active tab** — `#252117`, weight 600, 3px green-core underline from `::after`.
2. **Active group label** — `#252117`, weight 700, uppercase, 11px, letter-spacing 0.8px.
3. **Inactive tabs inside active group** — `#A0AFBF`, weight 400.
4. **Inactive group labels** (any other group) — `#C8D4DE` (faded).

- Collapsed group with the active tab: shows green underline on the label itself (`.tab-group.has-active:not(.expanded) .tab-group-label::after`).
- Expanded group without active tab: shows grey `#A0AFBF` full-group underline.
- Tab click triggers `Anim.slideTabUnderline(newTab)` — animated, not a class swap.

### 3.8 Sidebar nav link

```html
<a href="#/dashboard" data-page="dashboard" class="nav-link active">
  <svg><!-- 18x18 --></svg>
  <span class="nav-text">Dashboard</span>
</a>
```

- Icon is always 18×18 SVG with `currentColor` stroke.
- Active state: `color: var(--green-deep)`, bg `rgba(75, 170, 115, 0.1)`, plus a 3px green-core pill on the left edge (`::before`).
- `.nav-text` hidden when sidebar is collapsed.
- Nav link padding shifts from centered (collapsed) to `8px 16px` flex-start (expanded).

### 3.9 Year filter dropdown

Custom select with three modes: single year, "All Years", custom range. Lives in `.year-selector`. Don't replace with native `<select>` — the custom look is load-bearing. Refer to `initYearFilter()` in `app.js` for the state machine.

### 3.10 Additional patterns (reference only — keep using, don't redesign)

- **Zone cards** (`.zone-card`) — regional breakdown grid, FCT gets `.zone-card-fct` full-width variant.
- **Treemap cells** (`.treemap-cell`) — 12-col grid, hover lifts `translateY(-1px)`.
- **MDA header card** (`.mda-header-card`) — avatar + name + role + contact, 12px radius.
- **Engagement card, insight card, scorecard** — see `styles.css` lines 1325–1468 for exact values.
- **Export button** (`.export-btn`) — the only place padding is `16px 32px`; everything else sticks to smaller scales.

---

## 4. Motion

All motion is GSAP-driven. Vanilla CSS `transition` is only used for **sub-150ms hover/focus polish** (border colors, tiny opacity shifts). Everything interactive — page entry, card reveal, number count-up, tab slide, hover lift, button press — goes through the `Anim` module in `app.js`.

### 4.1 Global defaults

```js
gsap.defaults({ ease: 'power3.out', duration: 0.6 });
gsap.registerPlugin(Flip, ScrollTrigger);
```

**Accessibility:** if `prefers-reduced-motion: reduce` matches, `Anim.enabled = false` and `gsap.globalTimeline.timeScale(20)` — effectively killing all intros while keeping state changes intact. **Every animation method in the Anim module checks `Anim.enabled` first.** Do the same for any new animation.

### 4.2 Easing vocabulary

Pick from this list. **Don't introduce new curves.**

| Easing            | Use                                               |
|-------------------|---------------------------------------------------|
| `power3.out`      | Default. Most entries, transforms, settles.       |
| `power3.inOut`    | Cross-fade transitions, tab underline slide.      |
| `power2.in`       | Exits (opacity out, y -15).                       |
| `power2.out`      | Count-up numbers, hover lift.                     |
| `back.out(1.7)`   | Card reveal entrance (signature bounce).          |
| `back.out(1.4)`   | Below-fold scroll-triggered reveal.               |
| `elastic.out(1, 0.4)` | Button release (press bounce-back).           |
| `sine.inOut`      | Ambient breathing (pulse dot, glow drift).        |
| `none`            | Parallax scrub only.                              |

### 4.3 Signature animations

**Card reveal** (above-fold, on page enter):
```js
gsap.fromTo(cards,
  { opacity: 0, y: 30, scale: 0.97 },
  { opacity: 1, y: 0, scale: 1, duration: 0.6, ease: 'back.out(1.7)', stagger: { amount: 0.5, from: 'start' } }
);
```

**Card reveal** (below-fold, scroll-triggered):
```js
ScrollTrigger.batch(cards, {
  onEnter: batch => gsap.to(batch, { opacity: 1, y: 0, stagger: 0.08, duration: 0.6, ease: 'back.out(1.4)' }),
  start: 'top 88%',
  once: true
});
```

**Count-up numbers** — proxy value object, `snap` to decimal precision, 1.2s `power2.out`, locale-formatted thousand separators. Selectors: `.pulse-value, .stat-card-value, .overview-stat-value`. Fires 350ms after cards reveal (so the settle frame matches visually).

**Chart curtain reveal** — `clipPath: inset(0 100% 0 0)` → `inset(0 0% 0 0)`, 0.8s `power3.inOut`, ScrollTrigger `top 85%`, `once: true`. Runs on `.chart-wrap, .chart-wrap-hbar, .chart-wrap-doughnut`.

**Parallax depth** — chart cards drift `y: -10` or `-18` (alternating odd/even), `ease: none`, `scrub: 0.5`. Keep scrub exactly 0.5 — it's tuned.

**Ambient breathing** — the `.pulse-dot` scales 1 → 1.4 with opacity 1 → 0.5, `duration: 1.5`, `sine.inOut`, `repeat: -1`, `yoyo: true`. Glow orbs drift ±10px over 4–5s with `repeat: -1, yoyo: true`. **Start once, never stack** — the module uses `_gsapBreathing` / `_gsapDrift` sentinels to prevent re-attachment.

**Tab underline slide** — creates a floating `<div>` at the old tab's position, animates `left/width` to the new tab over 0.35s `power3.inOut`, then removes itself and sets the `.active` class on completion. Returns `true/false` so the caller knows whether to manually swap classes.

**Sub-tab content transition** — old content exits `opacity: 0, y: -15, duration: 0.2, ease: power2.in, stagger: 0.02` first, then `onComplete` clears and re-renders + `Anim.animatePage()` on the new content.

**Hover lift** (delegated on `.main`): `y: -4, box-shadow: 0 8px 25px rgba(0,0,0,0.08), duration: 0.25, ease: power2.out`. Release: `y: 0, shadow: 0 1px 3px rgba(0,0,0,0.06), duration: 0.35, ease: back.out(1.7)`.

**Button press** (delegated): mousedown `scale: 0.96, duration: 0.08, ease: power2.in`; mouseup `scale: 1, duration: 0.4, ease: elastic.out(1, 0.4)`. Targets: `button, .nav-link, .filter-btn, .export-btn`.

### 4.4 Rules

1. **Always gate on `Anim.enabled`.** Reduced-motion users see a static UI.
2. **Always `killScrollTriggers()` before navigating** between pages — `navigate()` handles this; new pages should not add triggers before teardown.
3. **Always call `Anim.animatePage(container)`** from a page's `init()` method. This orchestrates `revealCards → revealCharts → addParallax → startAmbient → countUpNumbers` in order.
4. **Never animate layout props** (width, height, margin) outside of Flip. Use transforms (`x`, `y`, `scale`) and `clipPath`.
5. **Never stack a repeating tween on an element that already has one** — use the `_gsapXxx` sentinel pattern from `startAmbient`.
6. Hover/press micro-interactions are attached **once** globally via event delegation on `.main` (see `attachMicroInteractions`). Don't add per-element hover handlers — they'll conflict.
7. `.anim-card` starts at `opacity: 0` via CSS; GSAP reveals it. A page full of un-revealed cards means `Anim.init()` didn't run or `animatePage()` wasn't called — debug from there.

---

## 5. Charts (Chart.js 4.4.7)

Defaults are set globally in `app.js` lines 28–39. **Never override these per-chart unless absolutely necessary.**

```js
Chart.defaults.font.family = "'Filson Pro', sans-serif";
Chart.defaults.font.size = 11;
Chart.defaults.color = '#5E5E5E';               // grey-body
Chart.defaults.plugins.legend.display = false;  // we render our own .chart-legend
Chart.defaults.plugins.tooltip.backgroundColor = '#252117';
Chart.defaults.plugins.tooltip.cornerRadius = 6;
Chart.defaults.scale.grid.color = '#F0F0F0';
```

**Rules:**
- **No Chart.js legend** — always use a `.chart-legend` div for visual control.
- Series colors pull from `C.greenCore` / `C.greenLight` / `C.greenMuted` / `C.goldPrimary` / `C.goldAmber` (see `app.js` line 6). Multi-series charts use greens for primary, golds for secondary, greys for tertiary.
- Tooltip corners are 6px, bg is `text-primary`, title is 600 weight. Never change.
- Grid lines are `#F0F0F0` — the one place this hardcoded grey appears. Treat as a token.
- Always destroy a chart (`destroyCharts()` pattern) before re-rendering — the page-swap animation relies on clean teardown.

---

## 6. Interaction rules

- **Hover**: all elevated surfaces (`.stat-card`, `.chart-card`, `.zone-card`, `.insight-card`) get the GSAP hover lift. Don't add CSS `:hover { transform: ... }` — it will double up.
- **Active state color**: active nav = `--green-deep` text on `rgba(75, 170, 115, 0.1)` bg. Active tab = `--text-primary` text with green underline. Active filter tab = white on `--green-core`.
- **Focus**: inputs get `border-color: var(--green-core)` + optional 2–3px green glow. No outline resets without a replacement — keyboard accessibility matters.
- **Cursor**: `pointer` on all interactive elements (buttons, nav, tab groups). `default` on cards (`.zone-card` sets it explicitly — don't make cards look clickable unless they are).
- **Selection**: disabled via `user-select: none` on decorative cards (treemap, zone, stat, chart) to prevent accidental text highlights. Text content in tables and articles remains selectable.

---

## 7. Accessibility

- **`prefers-reduced-motion: reduce`** — honored in `Anim.init()`. Motion drops to a static snap (timeScale 20). Test this before shipping animation changes.
- **Keyboard focus** — all interactive elements use `<button>` or `<a>`, inheriting native focus. Focus rings are green via `border-color` + box-shadow. Don't use `outline: none` without a visible replacement.
- **Color contrast** — all text/bg pairings hit WCAG AA. If you add a new color combination, verify contrast (the greens are light — use `--green-darkest` or `--text-primary` for text on white, not `--green-core`).
- **SVG icons** — stroke via `currentColor`, 1.5–1.8 stroke width. Inherit from parent text color so state changes propagate.
- **Font loading** — Filson Pro uses `font-display: swap`. No FOIT.

---

## 8. Forbidden patterns

Things that exist in common boilerplates but should never appear here:

- ❌ Tailwind, emotion, styled-components, CSS-in-JS — **this project is vanilla CSS only**.
- ❌ React, Vue, JSX, templating libraries — **this project is vanilla JS with the `el()` helper** (`app.js` line 295).
- ❌ Inline `style="..."` attributes — use a class. Exception: dynamic dimensions (progress bar widths, tab underline positions during animation).
- ❌ New CSS variables that shadow or replace an existing one.
- ❌ New font families. Filson Pro handles every weight you need.
- ❌ New easing curves or durations outside the vocabulary in §4.2 / §4.3.
- ❌ `border-collapse: collapse` on any table (breaks radius).
- ❌ CSS `@keyframes` — motion goes through GSAP.
- ❌ CSS hover `transform: translateY(-2px)` on cards (conflicts with GSAP hover lift).
- ❌ `console.log` left in committed code.
- ❌ Hardcoded hex colors in new CSS. (The only "allowed" hardcodes are `#A0AFBF`, `#C8D4DE`, `#F0F0F0`, `#F4F4F4` inside tab-bar/chart-grid rules — and even those are documented here.)

---

## 9. File map

| File                          | What lives here                                     |
|-------------------------------|-----------------------------------------------------|
| `budget-dashboard/index.html` | Shell, CDN scripts (Chart.js 4.4.7, GSAP 3.12.7 Core+Flip+ScrollTrigger), sidebar + header skeleton |
| `budget-dashboard/styles.css` | All design tokens (`:root`), component classes, responsive breakpoints. **Source of truth for visual tokens.** |
| `budget-dashboard/app.js`     | Palette mirror (`C`), Chart.js defaults, `Anim` module, `el()` DOM builder, page modules, `navigate()` router |
| `budget-dashboard/fonts/`     | Filson Pro woff2 files (5 weights)                  |
| `budget-dashboard/DESIGN_SYSTEM.md` | This document                                 |
| `budget-dashboard/CLAUDE.md`  | AI-specific rules pointing back to this doc         |

---

## 10. When in doubt

1. **Search `styles.css` for an existing class.** If something similar exists, use it — don't create a parallel version.
2. **Search `app.js` for an existing pattern.** `el()` usage, `Anim` method calls, page module structure — match the established form.
3. **Reference a variable, not a hex.** If the variable doesn't exist, that's a signal to talk before adding one.
4. **Match the rhythm.** 16px gaps, 24px section margins, 8/10/12/14px radius, Filson Pro 13px body. If your new component breaks the rhythm, there's probably an existing pattern you missed.

The entire point of this doc is that any two pages should feel like they were designed by the same person on the same afternoon. Any divergence is a bug.
