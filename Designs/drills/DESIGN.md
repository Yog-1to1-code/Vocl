---
name: Executive Terminal
colors:
  surface: '#131315'
  surface-dim: '#131315'
  surface-bright: '#39393b'
  surface-container-lowest: '#0e0e10'
  surface-container-low: '#1b1b1d'
  surface-container: '#1f1f21'
  surface-container-high: '#2a2a2c'
  surface-container-highest: '#353437'
  on-surface: '#e5e1e4'
  on-surface-variant: '#bccbb7'
  inverse-surface: '#e5e1e4'
  inverse-on-surface: '#303032'
  outline: '#869583'
  outline-variant: '#3d4a3b'
  surface-tint: '#47e266'
  primary: '#55ee71'
  on-primary: '#003910'
  primary-container: '#30d158'
  on-primary-container: '#00541b'
  inverse-primary: '#006e26'
  secondary: '#aac7ff'
  on-secondary: '#003064'
  secondary-container: '#3e90ff'
  on-secondary-container: '#002957'
  tertiary: '#ffc78c'
  on-tertiary: '#482900'
  tertiary-container: '#ffa11a'
  on-tertiary-container: '#683e00'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6cff82'
  primary-fixed-dim: '#47e266'
  on-primary-fixed: '#002106'
  on-primary-fixed-variant: '#00531a'
  secondary-fixed: '#d6e3ff'
  secondary-fixed-dim: '#aac7ff'
  on-secondary-fixed: '#001b3e'
  on-secondary-fixed-variant: '#00468d'
  tertiary-fixed: '#ffddbb'
  tertiary-fixed-dim: '#ffb868'
  on-tertiary-fixed: '#2b1700'
  on-tertiary-fixed-variant: '#673d00'
  background: '#131315'
  on-background: '#e5e1e4'
  surface-variant: '#353437'
typography:
  screen-title:
    fontFamily: Geist
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 34px
    letterSpacing: -0.02em
  screen-title-mobile:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 30px
    letterSpacing: -0.02em
  card-title:
    fontFamily: Geist
    fontSize: 17px
    fontWeight: '600'
    lineHeight: 22px
    letterSpacing: -0.01em
  body-default:
    fontFamily: JetBrains Mono
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: -0.005em
  label-micro:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.04em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-mobile: 0.75rem
  margin: 1.5rem
  margin-mobile: 1rem
  space-xs: 0.5rem
  space-sm: 0.75rem
  space-md: 1rem
  space-lg: 1.25rem
  space-xl: 1.5rem
---

## Brand & Style

The design system embodies the high-pressure, hyper-focused reality of senior technical engineering assessments. Built around an ultra-minimalist, audio-first operational posture, the visual signature strips away ornamental design in favor of pure technical utility, instantaneous legibility, and tactile precision. 

The aesthetic draws heavily from modern developer command interfaces, professional audio workstations, and executive-tier IDEs. Rather than relying on simulated depth or soft atmospheric effects, visual hierarchy is achieved entirely through razor-sharp hairline dividers, precise spatial density, and intense contrast between the true-black void and semantic status signals. The emotional target is calm control: an interface that feels like high-grade instrumentation, respecting the engineer's cognitive bandwidth during live problem-solving drills.

## Colors

The palette is engineered for OLED power efficiency and zero-distraction focus during intensive auditory drills. 

- **Pure Canvas (`#000000`):** Absolute black base eliminating backlight bleeding and anchoring visual focus to active elements.
- **Surface Level 1 (`#141416`):** Deep charcoal applied to resting card containers, input backgrounds, and modal bases.
- **Elevated Surface Level 2 (`#1C1C1E`):** Distinct layer for interactive states, focused items, and active telemetry panels.
- **Structural Hairline (`#262629`):** A strict 1px boundary layer replacing drop shadows across the interface.
- **Primary Signal Green (`#30D158`):** The primary execution state. Designates active user input, successful audio capture, optimal complexity ratings, and safe confirmations.
- **Semantic Accents:**
  - **Electric Blue (`#0A84FF`):** Designates synthesis, active audio response, AI query states, and keyboard focus outlines.
  - **Telemetry Amber (`#FF9F0A`):** Used for tool-call activations, algorithmic warnings, hint affordances, and medium-complexity indicators.
  - **Signal Red (`#FF453A`):** Destructive actions, session termination, runtime exceptions, missed edge cases, and high-complexity flags.
  - **Crimson Pink (`#FF375F`):** Dedicated analytical telemetry, specifically communication clarity, audio articulation metrics, and soft-skill pacing indicators.
- **Text Tiers:**
  - Primary text: `#F5F5F7`
  - Secondary/Supporting text: `#8E8E93`
  - Muted/Inactive text: `#48484A`

## Typography

The typographic hierarchy is intentionally constrained to a disciplined 4-step scale, guaranteeing immediate scannability under time-sensitive constraints.

- **Geist (Display & Headings):** Used for structural navigation and framing. Offers machined neo-grotesque clarity with tight tracking for `screen-title` and `card-title`.
- **JetBrains Mono (Body & Telemetry):** Anchors all operational content, audio transcriptions, algorithmic questions, metric readouts, and chronometers. All instances displaying numerical data, timestamps, or complexity ratings must use `font-feature-settings: "tnum" 1` to prevent baseline shifting during real-time counters.
- **Micro Labels & Badges:** `label-micro` is strictly uppercase with `+0.04em` tracking to provide clean, crisp separation between metadata headers and core data streams.

## Layout & Spacing

The interface adheres to an 8-point spatial rhythm (`8px`, `12px`, `16px`, `20px`, `24px`) with fluid single-column execution on mobile viewports and structured multi-column inspection consoles on desktop displays.

- **Thumb-Zone Optimization:** In audio sessions, core actionable triggers (push-to-talk, interrupt AI, advance hint, terminate) must inhabit the bottom 30% of the screen. Non-interactive telemetry and historical conversation transcripts live in the upper 70% scrollable viewport.
- **Touch Bounds:** Any tappable component maintains a strict minimum bounding box of 48×48px, even if the visible container is styled as a micro-pill or hairline icon trigger.
- **Adaptive Breakpoints:**
  - `Mobile (< 768px)`: Unified vertical stack, full-width thumb actions anchored to bottom sheet, 16px lateral canvas margins.
  - `Tablet / Desktop (≥ 768px)`: Constrained master view (maximum container width 720px for drill interfaces; 1080px for dual-pane retrospective dashboards) with 24px structural gutters.

## Elevation & Depth

This design system completely forbids drop shadows, ambient blur halos, and diffuse lighting. Dimensional relationships are communicated exclusively through surface shade shifts and hairline borders:

1. **Base Layer (Elevation 0):** Pure `#000000` canvas background.
2. **Structural Container (Elevation 1):** `#141416` surface bounded by a continuous `1px solid #262629` hairline border. Used for static question blocks, historical audio logs, and metric containers.
3. **Elevated & Focused Elements (Elevation 2):** `#1C1C1E` background. Utilized for floating control bars, active audio drawers, and hovered cards.
4. **Active State Indication:** When an element gains priority (e.g., active listening, AI streaming), depth is reinforced by replacing the `#262629` hairline border with the corresponding 1px semantic color (`#30D158` for user, `#0A84FF` for model response) accompanied by an interior 1px inset boundary rather than external glow.

## Shapes

The geometric framework follows a controlled soft-terminal style (`roundedness: 1`):

- **Standard Containers & Cards:** `0.25rem` (`4px`) border radius. Conveys structured stability reminiscent of low-level debugging consoles.
- **Interactive Buttons & Form Fields:** `0.25rem` (`4px`) border radius, preserving hard-edged architectural cohesion.
- **Pills & Status Chips:** `0.25rem` (`4px`) for square badges or explicit full-pill geometry (`9999px`) reserved uniquely for persistent audio mode tags (e.g., `LISTENING`, `THINKING`) to distinguish real-time device states from clickable interface tiles.

## Components

### Buttons & Trigger Affordances
- **Primary Execution (User/Proceed):** Solid `#30D158` background with `#000000` text in `Geist` semibold. Hairline border omitted or matched to primary. Hover transitions to `#28B84D`.
- **Secondary / Operational:** Surface `#141416` with a `1px solid #262629` border and `#F5F5F7` text. Active touch state transitions background to `#1C1C1E`.
- **Destructive (End Session):** Surface `#141416` with `1px solid #FF453A` and `#FF453A` text.
- **Minimum Dimensions:** 48px height across all primary interactive drill actions.

### Audio Waveform & Status Indicators
- **State Visualizers:** A clean multi-bar audio reactive canvas centered inside `#141416` containers.
- **Signal States:**
  - AI Output: Bars oscillate in `#0A84FF`.
  - User Recording: Bars oscillate in `#30D158`.
  - Inference/Tool Fetch: Amber `#FF9F0A` pulse loader bar across top border hairline.

### Chips & Semantic Tags
- **Micro Badges:** Styled using `label-micro` typography.
- **Visual Pattern:** Background rendered at 10% opacity of the semantic color, surrounded by a 1px solid border at 30% opacity, paired with full-intensity text (e.g., Easy tag: `rgba(48, 209, 88, 0.1)` bg, `rgba(48, 209, 88, 0.3)` border, `#30D158` text).

### Cards & Drill Containers
- Base `#141416`, `1px solid #262629`, 16px interior padding.
- Card titles utilize `card-title` in `#F5F5F7`, with technical descriptors in `body-default` `#8E8E93`.
- No outer shadows under any interaction state.

### Input Fields & Terminal Prompts
- Background `#000000` set within an elevation-1 `#141416` container.
- Height: 48px. Typography: `body-default` in JetBrains Mono.
- Border: `1px solid #262629`. Focus state cleanly switches border to `1px solid #0A84FF` with zero outline offset.

### Telemetry & Chronometer Panels
- JetBrains Mono numeric displays with `tabular-nums` formatting.
- Metric highlights (e.g., complexity tracking, communication score) pair 12px uppercase micro-labels with high-contrast colored values (`#FF375F` for pacing/clarity, `#30D158` for correctness).