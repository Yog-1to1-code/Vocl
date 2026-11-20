---
name: apple-interface-design
description: Professional Apple-platform interface design and review skill distilled from the complete Apple Human Interface Guidelines (173 chapters, 2026 edition). Use it to design, specify, critique or audit iOS, iPadOS, macOS, tvOS, visionOS and watchOS interfaces, and to justify every decision with Apple's rules, numbers and platform conventions.
version: 1.1.0
source: https://developer.apple.com/design/human-interface-guidelines/
---

# Apple Interface Design — Agent Skill

A working design system and review rubric for software that should look and behave like it belongs on Apple platforms. Written for an AI agent: every section is a **rule you apply**, a **number you use**, or a **test you run**. When you produce UI, code, specs or critique, obey the rules and cite the section that drove each decision.

**Depth rule.** Never answer an Apple-platform design question with generic "clean, minimal, accessible" advice. Name the platform, the component, the metric and the violation. Apple's guidance is specific — 44×44 pt hit targets, 4.5:1 contrast at ≤17 pt, a 34 pt Large Title with 41 pt leading, a 35% dimming layer behind clear Liquid Glass over bright media. Be that specific.

---

## 0. How to use this skill

### 0.1 Operating order for any design task

1. **Identify the platform and idiom** — iOS, iPadOS, macOS, tvOS, visionOS, watchOS, or a deliberate multi-platform app. Platform is decided by where people use it, not by the framework you happen to know.
2. **State the job** in one sentence, in the person's words. Design starts with intention (Purpose).
3. **Choose a system pattern before inventing one.** Navigation → tab bar / sidebar / split view / navigation stack. Actions → toolbar, buttons, menus, context menu. Choice → picker, segmented control, action sheet. Interruption → alert. Scoped task → sheet. These exist so people don't have to learn your app.
4. **Lay out with system structure** — safe areas, layout margins, size classes, Dynamic Type. No absolute layouts that collapse at AX5.
5. **Apply materials and color semantically.** Liquid Glass belongs to the functional layer (bars, sidebars, popovers), never the content layer.
6. **Write the words last, out loud.** Verb-first buttons, sentence-case body, no blame in errors, no "we", no "oops".
7. **Run the audit in §15** before delivering.

### 0.2 Non-negotiables (if any fail, it is not shippable)

- Tappable controls ≥ 44×44 pt on iOS/iPadOS/watchOS, ≥ 60×60 pt visionOS, ≥ 66×66 pt tvOS, ≥ 28×28 pt macOS (absolute minimums: 28, 28, 56, 20).
- Text contrast ≥ 4.5:1 up to 17 pt; ≥ 3:1 at 18 pt or bold; aim for 7:1 on small custom text.
- Dynamic Type supported; layout survives the largest accessibility size without clipping or overlap.
- Nothing communicates meaning by color alone.
- No controls under the Dynamic Island, hardware cutouts, or outside the safe area.
- One prominent (filled, accented) button per view; two at most.
- Destructive actions are red, never the primary/default button, and offer Cancel when the loss is unexpected.
- Alerts only for critical, actionable information — never onboarding, marketing, or at launch.
- VoiceOver can describe every element: labels, traits, grouping, announced changes.
- Reduce Motion, Increase Contrast, Reduce Transparency, Bold Text and Larger Text all leave the UI usable.

### 0.3 Vocabulary discipline

Use Apple's terms, not web terms: view, sheet, popover, alert, action sheet, tab bar, sidebar, toolbar, navigation bar, list, table, collection, disclosure indicator, grabber, detent, ornament, Liquid Glass, SF Symbol, Dynamic Type, point (pt). Sizes are in **points**, not CSS pixels. Say "tap" on touch devices, "click" on pointer devices, "select" when the input method is unknown.

---

## 1. Design principles

Apple's eight principles are decision tools for breaking ties, not slogans.

### Purpose — make something meaningful
- **Create value.** At every stage ask what the product is for and whether the design serves it.
- **Keep focused.** Prioritize the features people actually want and make those great.
- **Find new ways to solve the problem.** Study existing solutions and deliberately differ where it matters.

### Agency — let people do things their own way
- **Stay out of the way.** Get people to the task or content; the best designs are unobtrusive and present only when needed.
- **Give freedom to explore.** No dead-end flows or locked modes; if a guided flow is necessary, make skipping and escaping easy.
- **Help people recover.** Reversibility makes an interface inviting; undo beats confirmation for reversible mistakes.

### Responsibility — act in people's best interest
- **Be transparent** about what the product does and why; explain the rationale before asking permission; state what data you collect and how it's used.
- **Keep information safe.** Collect only what the product needs and anticipate misuse.

### Familiarity — build on what people know
- **Use known concepts** — physical-world metaphors and platform conventions.
- **Keep visuals and interactions consistent.** Establish a behavior once, apply it everywhere.
- **Provide clear feedback** for state changes, availability and results.

### Flexibility — adapt to diverse contexts and needs
- **Design for everyone.** Accessibility is a priority from the start, not a retrofit.
- **Preserve context** across devices and window sizes: same content and controls in predictable places, natural transitions.
- **Support many inputs** — touch, voice, keyboard, pointer, eyes, remote, controller, Pencil.
- **Approach each platform with intention**; don't ship one layout everywhere and call it universal.

### Simplicity — be clear and direct
- **Include just what's necessary.** Simplicity is focus, not minimalism.
- **Be concise.** The simplest phrasing is usually the most universal.
- **Establish hierarchy** so people know where they are and what comes next.

### Craft — care about every detail
- **Quality sets the tone**: visuals, animation, wording, audio, performance.
- **Experiment and iterate**; prototype early and discard what doesn't work.
- **Maintain craft after shipping**; keep pace with platform capabilities.

### Delight — make it human
- **Identify the emotion** the product should inspire (energize, calm, thrill) and let it shape the design.
- **Create defining moments** — a press, a completion, an error can all carry character.
- **Don't mistake delight for decoration.** Never trade task completion for whimsy.
- **Delight is the sum** of agency, safety, familiarity and flexibility — it emerges, it isn't added.

### Branding — identity that defers to content
- **Carry the brand in voice and tone** in everything you display, while keeping the platform's structure: distinctive words inside standard navigation, controls and gestures.
- **Apply the accent color judiciously.** Brand color spread across every control overwhelms the interface and dilutes its impact; reserve it for the primary action and for status (badges, the selected tab's icon) and move brand expression into the content layer instead.
- **A custom font must earn its place**: legible at every size, compatible with Bold Text and Dynamic Type, and paired with system fonts for body copy and captions, which are tuned for small sizes.
- **Customize appearance, never behaviour.** If you restyle a familiar component, sizing, placement and interaction must stay intact or it stops being familiar.
- **Branding never competes with content.** Screen space spent on an asset that does no work is space taken from the thing people came for.
- **Don't repeat the logo** throughout the app — people know which app they are in — unless it establishes real context, as in a document or a shared canvas.
- **Never use the launch screen as a branding opportunity.** It disappears too fast to communicate anything, and it exists to make startup feel instant.
- **Apple trademarks never appear in your app name, icon or imagery**; check Apple's trademark list before using any Apple mark.

---

## 2. Platform mental models

Design the same feature differently per platform. These are expectations Apple states explicitly.

### iOS — one hand, one task, immediate
- Limit onscreen controls; make secondary detail discoverable with minimal interaction.
- Adapt to orientation, Dark Mode and Dynamic Type without losing the design.
- Put controls where a thumb reaches: middle and bottom of the display. Swipe-back and swipe actions on rows are expected.
- Use device capabilities (Apple Pay, biometrics, location, camera) to remove typing — with permission.
- Navigation: floating bottom tab bar on Liquid Glass, navigation stack with interactive back swipe, search as its own tab or a toolbar field.

### iPadOS — big canvas, many inputs, fluid windows
- Elevate content; minimize modal interfaces and full-screen transitions.
- Let viewing distance and input mode set size and density.
- Support Multi-Touch, keyboard, trackpad, Apple Pencil, and combinations of them.
- Adapt to orientation, multitasking, Dark Mode, Dynamic Type, and running inside macOS (iPhone Mirroring, resizable windows).
- Navigation: tab bar near the top that can convert to a sidebar; three-column split views for depth; popovers for compact contextual tasks.

### macOS — precision, parallelism, permanence
- More content in fewer nested levels and with less modality, at comfortable density.
- Windows resize, move, hide and go full screen.
- The menu bar must expose **every** command in the app, including those also in context menus and toolbars.
- Support keyboard shortcuts and keyboard-only workflows; honor the standard set in §13.2.
- Optimize density for pointer and keyboard, but support touch input on Macs with a touch display.
- Allow personalization: customizable toolbars, window/tab configuration, colors and fonts.
- Never place critical controls or information at the bottom edge of a window (people move windows below the screen edge) or behind the camera housing at the top edge.

### tvOS — ten feet away, focus-driven, cinematic
- Interactions come from the Siri Remote; use its familiar gestures and the focus system.
- Focus highlights and slightly expands items so people always know where they are. Design the focused state as carefully as the resting state, and leave enough spacing that expansion never overlaps neighbors.
- Edge-to-edge artwork, fluid animation, engaging audio, legible across a room.
- Multi-user: make sign-in easy and infrequent, handle shared sign-in, switch profiles when the viewer changes.

### visionOS — space, comfort, eyes and hands
- Choose the **minimum** immersion that serves each moment: window → volume → Full Space.
- Windows are planes in space with familiar controls; dynamic scaling keeps content legible near and far.
- Prioritize comfort: keep content within the field of view, prefer horizontal layouts to avoid neck strain, avoid rapid attention shifts between locations, slow peripheral motion, never anchor content to the head, minimize large repetitive gestures.
- Input is eyes (look) plus hands (tap, pinch), with voice, keyboard, pointer and accessibility pointer control. Provide audio feedback — the system does not play haptics.
- Buttons need a visible contrasting background; keep centers ≥ 60 pt apart; add 4 pt padding around buttons ≥ 60 pt; circular for icon-only, capsule or rounded rectangle for text.

### watchOS — glanceable, single screen, wrist-raised
- Quick, glanceable, single-screen interactions; one or two gestures to a targeted action.
- Minimize navigation depth; use the Digital Crown for vertical navigation.
- Anticipate needs with on-device context; offer timely, actionable content.
- Complications carry live data on the watch face; notifications deliver high-value information with inline actions.
- Text: 16 pt default, 12 pt minimum; support enlargement of at least 140% (iOS/iPadOS: 200%).

### Games (all platforms)
- Look stunning on every display: design for the full range of screens, HDR and refresh rates; test on real TVs and devices.
- Enable intuitive interactions per input: touch, controller, keyboard, remote, eyes and hands.
- Welcome everyone: onboarding, difficulty options, remappable controls, captions and subtitles, colorblind-safe palettes.
- Maintain 30–60 fps as the baseline for smooth motion, scaling quality by device.
- Handle interruptions (calls, notifications, loss of focus) without losing progress; pause and save sensibly.

### iPhone Duo (foldable) — poses and reserved regions
- Treat device poses as first-class states; check reserved regions (hinge, camera) before placing controls.
- Support dynamic layouts: when the display splits, use split views rather than stretching one pane across the fold.
- Keep vertical controls reachable in each pose; test folded and unfolded.

---

## 3. Layout

### 3.1 Visual hierarchy
- **Order by importance** in reading order: most important content top and leading. Prefer standard components so right-to-left flips correctly.
- **Align to make scanning easy; indent to express hierarchy.** People assume aligned items relate and indented items are subordinate.
- **Group related items** with negative space, containers or separators; ungroup unrelated ones.
- **Use progressive disclosure.** Hide detail behind disclosure controls, menus, nested views or scrollable sections instead of showing everything at once.
- **Differentiate controls from content** with Liquid Glass rather than solid backgrounds under bars. Prefer a scroll edge effect over an opaque bar background.
- **Let full-screen content extend under** sidebars, toolbars and tab bars. If that hides something important, use a background extension effect (mirror + blur adjacent content beneath the component) instead of shrinking the artwork.

### 3.2 Adaptability — what your layout must survive
- Compact and regular horizontal and vertical size classes.
- Different screen sizes, orientations and aspect ratios.
- Dynamic Island, external displays, Display Zoom, resizable windows on iPad and Mac.
- Dynamic Type text-size changes.
- Locale: RTL layout, date/time/number formats, font variation, text-length growth.

Rules:
- **Design against size classes, not device type or orientation.** Size classes describe available space; idiom describes the device. A resized iPad window is not a phone.
- **Consider every size-class combination**; a landscape-phone layout must still use extra height when the window becomes tall.
- **Keep functionality identical as size classes change**; change only how much is visible on screen (tab bar → sidebar, expose actions that were in an overflow).
- **Keep layout changes recognizable to the platform**, even when resizing.
- **Respect safe areas and layout margins.** Safe area excludes hardware and system UI: Dynamic Island, status bar, toolbars, tab bars, home indicator.
- **Scale background artwork to fill; never change its aspect ratio.** Crop/letterbox artifacts mean the artwork needs different sizing, not a different aspect ratio.
- **Survive Dynamic Type**: adjacent horizontal views stack vertically, rows grow in height, single-line rows become multi-line, text never clips or overlaps.
- **Test the largest and smallest layouts first**, then localizations, then sizes in between.

### 3.3 Layout guides and margins
- Layout guides define rectangular regions for margins and readable line length; use them rather than ad-hoc padding.
- Prefer standard margins around content; constrain text width for readability on iPad and Mac.
- **tvOS safe area: inset content 60 pt from top and bottom, 80 pt from leading and trailing.**
- visionOS: keep windows inside the comfortable field of view; never anchor UI to the head.

### 3.4 tvOS grids (unfocused content width / horizontal spacing / minimum vertical spacing)

| Columns | Content width | H-spacing | Min V-spacing |
|---|---|---|---|
| 2 | 860 pt | 40 pt | 100 pt |
| 3 | 560 pt | 40 pt | 100 pt |
| 4 | 410 pt | 40 pt | 100 pt |
| 5 | 320 pt | 40 pt | 100 pt |
| 6 | 260 pt | 40 pt | 100 pt |
| 7 | 217 pt | 40 pt | 100 pt |
| 8 | 184 pt | 40 pt | 100 pt |
| 9 | 160 pt | 40 pt | 100 pt |

Horizontal spacing is 40 pt and minimum vertical spacing is 100 pt at every column count. This spacing exists so focused items can scale up without overlapping neighbors.

### 3.5 Control sizing and spacing

| Platform | Default control size | Minimum control size |
|---|---|---|
| iOS, iPadOS | 44×44 pt | 28×28 pt |
| macOS | 28×28 pt | 20×20 pt |
| tvOS | 66×66 pt | 56×56 pt |
| visionOS | 60×60 pt | 28×28 pt |
| watchOS | 44×44 pt | 28×28 pt |

- About **12 pt padding** around elements with a bezel; about **24 pt** around the visible edges of bezel-less elements.
- Buttons need a hit region ≥ 44×44 pt (60×60 pt visionOS) whatever the input method.
- visionOS: button centers ≥ 60 pt apart; 4 pt padding around buttons ≥ 60 pt so hover effects don't collide; avoid stacking mini or small buttons.

### 3.6 visionOS spatial layout and field of view
- **Keep content inside the field of view**, positioned relative to the person's head. If they must turn their head, change position or stand up to reach something, the layout is wrong. Prefer horizontal layouts to vertical ones, which cause neck strain.
- **Windows default to 1280×720 pt.** When one first opens the system places it about **2 m in front**, giving it an apparent width of about **3 m**. Empty space inside a window makes it look gratuitously large and obscures what is behind it — size the initial window to its content.
- **Depth is hierarchy, not decoration.** Place content at comfortable distances, avoid z-axis stacks that force constant refocusing, and never anchor content to the head (this also blocks Pointer Control and other assistive technologies).
- **Let dynamic scaling work.** Content near and far stays legible because the system scales it; fixed type sizes and fixed artwork fight that.
- **Spacing:** at least **16 pt of margin around each interactive item, or centers at least 60 pt apart**. Never let controls overlap other controls or views — eyes make small involuntary jumps, and crowded targets are hard to select.
- **Immersion boundaries:** in `progressive` and `full` styles the system defines an approximately **1.5 m** boundary; the Digital Crown adjusts immersion inside a default **120–360°** range (or a custom range you define). Dimmed passthrough is black-tinted by default and can be given a custom tint.
- **Displays are not screens:** image pixels need not line up 1:1 with display pixels, and surrounding surfaces tint what people see, so validate color on device.

---

## 4. Typography

### 4.1 System typefaces
- **San Francisco (SF)** — SF Pro, SF Compact (watchOS), SF Arabic, SF Armenian, SF Georgian, SF Hebrew, SF Mono, plus rounded variants of each for softer interfaces.
- **New York (NY)** — serif family for reading and editorial voice; works alone or beside SF.
- Both are variable fonts with dynamic optical sizing: one file interpolates weight, width and optical size, so you never pick discrete Text/Display cuts.
- **Never embed system fonts.** Use the platform APIs (`Font.system`, `UIFont.systemFont`, `NSFont.systemFont`) so Dynamic Type, Bold Text and language coverage work.
- Weights run Ultralight → Black; SF also has Condensed/Expanded widths. SF Symbols match text weights exactly.

### 4.2 Legibility thresholds

| Platform | Default body size | Minimum text size |
|---|---|---|
| iOS, iPadOS | 17 pt | 11 pt |
| macOS | 13 pt | 10 pt |
| tvOS | 29 pt | 23 pt |
| visionOS | 17 pt | 12 pt |
| watchOS | 16 pt | 12 pt |

- Avoid Ultralight, Thin and Light, especially at small sizes; thin custom faces need *larger* sizes than these defaults.
- Test at each real viewing distance (a TV at 3 m is not a phone at 30 cm).
- Support enlargement of at least **200%** on iOS/iPadOS and **140%** on watchOS.

### 4.3 Conveying hierarchy
- Change **weight, size and color** together; keep relative hierarchy intact when text scales.
- **Minimize typefaces** — one family in several weights beats three families.
- **Prioritize content when type grows.** Larger text enlarges what people read, not chrome: tab titles, transient hit-damage numbers and similar labels need not scale with body copy.
- Leading: loose for long passages and wide columns; tight only to save height for one or two lines, never for three or more.

### 4.4 Dynamic Type — iOS/iPadOS (point size / leading)

| Style | xSmall | Small | Medium | Large (default) | xLarge | xxLarge | xxxLarge |
|---|---|---|---|---|---|---|---|
| Large Title | 31/38 | 32/39 | 33/40 | **34/41** | 36/43 | 38/46 | 40/48 |
| Title 1 | 25/31 | 26/32 | 27/33 | **28/34** | 30/37 | 32/39 | 34/41 |
| Title 2 | 19/24 | 20/25 | 21/26 | **22/28** | 24/30 | 26/32 | 28/34 |
| Title 3 | 17/22 | 18/23 | 19/24 | **20/25** | 22/28 | 24/30 | 26/32 |
| Headline | 14/19 | 15/20 | 16/21 | **17/22** | 19/24 | 21/26 | 23/29 |
| Body | 14/19 | 15/20 | 16/21 | **17/22** | 19/24 | 21/26 | 23/29 |
| Callout | 13/18 | 14/19 | 15/20 | **16/21** | 18/23 | 20/25 | 22/28 |
| Subhead | 12/16 | 13/18 | 14/19 | **15/20** | 17/22 | 19/24 | 21/28 |
| Footnote | 12/16 | 12/16 | 12/16 | **13/18** | 15/20 | 17/22 | 19/24 |
| Caption 1 | 11/13 | 11/13 | 11/13 | **12/16** | 14/19 | 16/21 | 18/23 |
| Caption 2 | 11/13 | 11/13 | 11/13 | **11/13** | 13/18 | 15/20 | 17/22 |

Emphasized variants: Large Title, Title 1 and Title 2 → **Bold**; Title 3, Headline, Body, Callout, Subhead, Footnote and both Captions → **Semibold**. Headline is Semibold by default.

### 4.5 Dynamic Type — larger accessibility sizes (iOS/iPadOS)

| Style | AX1 | AX2 | AX3 | AX4 | AX5 |
|---|---|---|---|---|---|
| Large Title | 44/52 | 48/57 | 52/61 | 56/66 | 60/70 |
| Title 1 | 38/46 | 43/51 | 48/57 | 53/62 | 58/68 |
| Title 2 | 34/41 | 39/47 | 44/52 | 50/59 | 56/66 |
| Title 3 | 31/38 | 37/44 | 43/51 | 49/58 | 55/65 |
| Headline | 28/34 | 33/40 | 40/48 | 47/56 | 53/62 |
| Body | 28/34 | 33/40 | 40/48 | 47/56 | 53/62 |
| Callout | 26/32 | 32/39 | 38/46 | 44/52 | 51/60 |
| Subhead | 25/31 | 30/37 | 36/43 | 42/50 | 49/58 |
| Footnote | 23/29 | 27/33 | 33/40 | 38/46 | 44/52 |
| Caption 1 | 22/28 | 26/32 | 32/39 | 37/44 | 43/51 |
| Caption 2 | 20/25 | 24/30 | 29/35 | 34/41 | 40/48 |

At AX sizes layouts must reflow: stack, wrap, grow rows, drop decorative columns. A design that only works at Large is broken.

### 4.6 macOS built-in text styles (size / line height)

| Style | Weight | Size/Height | Emphasized |
|---|---|---|---|
| Large Title | Regular | 26/32 | Bold |
| Title 1 | Regular | 22/26 | Bold |
| Title 2 | Regular | 17/22 | Bold |
| Title 3 | Regular | 15/20 | Semibold |
| Headline | Bold | 13/16 | Heavy |
| Body | Regular | 13/16 | Semibold |
| Callout | Regular | 12/15 | Semibold |
| Subheadline | Regular | 11/14 | Semibold |
| Footnote | Regular | 10/13 | Semibold |
| Caption 1 | Regular | 10/13 | Medium |
| Caption 2 | Medium | 10/13 | Semibold |

### 4.7 tvOS built-in text styles (size / leading)

| Style | Weight | Size/Leading |
|---|---|---|
| Title 1 | Medium | 76/96 |
| Title 2 | Medium | 57/66 |
| Title 3 | Medium | 48/56 |
| Headline | Medium | 38/46 |
| Subtitle 1 | Regular | 38/46 |
| Callout | Medium | 31/38 |
| Body | Medium | 29/36 |
| Caption 1 | Medium | 25/32 |
| Caption 2 | Medium | 23/30 |

### 4.8 watchOS Dynamic Type — default (Large; 40/41/42 mm)

| Style | Weight | Size/Leading |
|---|---|---|
| Large Title | Regular | 36/38.5 |
| Title 1 | Regular | 34/36.5 |
| Title 2 | Regular | 28/30.5 |
| Title 3 | Regular | 19/21.5 |
| Headline | Semibold | 16/18.5 |
| Body | Regular | 16/18.5 |
| Caption 1 | Regular | 15/17.5 |
| Caption 2 | Regular | 14/16.5 |
| Footnote 1 | Regular | 13/15.5 |
| Footnote 2 | Regular | 12/14.5 |

Small (38 mm) runs one step smaller; xLarge (44/45/49 mm) one step larger (Body 17 pt); AX1–AX3 raise Body to 21, 22 and 23 pt. Full tables in `chapters/029-typography.md`.

### 4.9 Tracking (letter-spacing)
The system adjusts tracking at every size; you only need values when reproducing Apple's look in a static mock. SF Pro on iOS/iPadOS/visionOS, anchors in points:

| Size | Tracking | Size | Tracking | Size | Tracking |
|---|---|---|---|---|---|
| 11 pt | +0.06 | 17 pt | −0.43 | 24 pt | +0.07 |
| 12 pt | 0.0 | 18 pt | −0.44 | 28 pt | +0.38 |
| 13 pt | −0.08 | 19 pt | −0.45 | 34 pt | +0.40 |
| 15 pt | −0.23 | 20 pt | −0.45 | 48 pt | +0.35 |
| 16 pt | −0.31 | 22 pt | −0.26 | 96 pt | 0.0 |
| 44 pt | +0.37 | 56 pt | +0.30 | 64 pt | +0.22 |

Tracking is tightest around 18–20 pt (−0.45) and eases outward as size grows, reaching 0 at 96 pt. The families differ measurably:

- **SF Pro Rounded** is much looser (+0.37 at 17 pt, +0.51 at 6 pt).
- **New York** tightens steadily: −0.15 at 19 pt, −0.62 at 44 pt, −16/1000 em (−1.50 pt) at 96 pt.
- **SF Compact** and **SF Compact Rounded** (watchOS) run tighter than SF Pro: −20/1000 em at 44 pt and −28/1000 em (−2.62 pt) at 96 pt.
- macOS, tvOS and watchOS each publish their own tracking tables in `chapters/029-typography.md` — never reuse the iOS values across platforms.

### 4.10 Custom fonts
- Must stay legible at the minimum sizes and must implement Dynamic Type and accessibility responses (Bold Text, etc.).
- Provide a weight range that can match adjacent symbols, or pair symbols with a matching SF weight instead.
- Never use a custom face for critical small print or dense data labels.

---

## 5. Color

### 5.1 Rules
- **Never use one color for two meanings.** If red means destructive, red cannot also be brand decoration.
- **Use semantic, system colors** where possible; they carry variants for light, dark and increased contrast, and adapt in Liquid Glass contexts.
- Custom colors need light, dark and increased-contrast variants, even if the app ships in one appearance, so Liquid Glass adaptation works.
- **Test under real light** — outdoor sun dims and mutes color; a dark room oversaturates. On visionOS, surrounding surfaces tint what people see.
- **Test on multiple devices**: True Tone shifts white point; test tvOS apps on several TV brands; check P3 and sRGB on Mac.
- **Artwork changes everything nearby.** Translucent bars and photo backgrounds alter perceived color; a map switches palettes between map and satellite modes.
- If people can pick colors, use system color controls (`ColorPicker`) so choices are consistent and reusable.

### 5.2 Inclusive color
- **Never rely on color alone** to differentiate objects, indicate interactivity or convey state. Add text, glyph shape or pattern.
- Avoid pairings that fail for color blindness (red/green, blue/orange) as the only distinction.
- Contrast minimums: 4.5:1 up to 17 pt, 3:1 at 18 pt or bold; 7:1 is the target for small custom text. If you don't meet it by default, at least meet it when Increase Contrast is on — and check both appearance modes.
- Colors carry cultural meaning (red = danger in some places, celebration in others); confirm intent before shipping internationally.

### 5.3 System colors (default light / default dark, R,G,B)

| Color | Light | Dark |
|---|---|---|
| Red | 255,56,60 (#FF383C) | 255,66,69 (#FF4245) |
| Orange | 255,141,40 (#FF8D28) | 255,146,48 (#FF9230) |
| Yellow | 255,204,0 (#FFCC00) | 255,214,0 (#FFD600) |
| Green | 52,199,89 (#34C759) | 48,209,88 (#30D158) |
| Mint | 0,200,179 (#00C8B3) | 0,218,195 (#00DAC3) |
| Teal | 0,195,208 (#00C3D0) | 0,210,224 (#00D2E0) |
| Cyan | 0,192,232 (#00C0E8) | 60,211,254 (#3CD3FE) |
| Blue | 0,136,255 (#0088FF) | 0,145,255 (#0091FF) |
| Indigo | 97,85,245 (#6155F5) | 109,124,255 (#6D7CFF) |
| Purple | 203,48,224 (#CB30E0) | 219,52,242 (#DB34F2) |
| Pink | 255,45,85 (#FF2D55) | 255,55,95 (#FF375F) |
| Brown | 172,127,94 (#AC7F5E) | 183,138,102 (#B78A66) |

Each also has increased-contrast light and dark variants (for example Red becomes 233,21,45 light and 255,97,101 dark) — full matrix in `chapters/016-color.md`. visionOS uses the dark values. iOS/iPadOS also define system grays — use these for fills, separators and grouped backgrounds instead of inventing neutrals. Each has an increased-contrast variant in `chapters/016-color.md`.

| Name | Default light | Default dark |
|---|---|---|
| systemGray | 142,142,147 | 142,142,147 |
| systemGray2 | 174,174,178 | 99,99,102 |
| systemGray3 | 199,199,204 | 72,72,74 |
| systemGray4 | 209,209,214 | 58,58,60 |
| systemGray5 | 229,229,234 | 44,44,46 |
| systemGray6 | 242,242,247 | 28,28,30 |

`systemGray` is identical in both appearances; 2–6 invert direction — lighter than the background in light mode, darker in dark mode. visionOS uses the dark system colors throughout.

### 5.4 Liquid Glass color
- By default Liquid Glass has **no inherent color**; it takes color from what is behind it. Color applied to it looks like stained glass.
- **Apply color sparingly** — status indicators, primary actions. To emphasize a primary action, color the **background**, not the symbol or label (what prominent buttons do).
- On bars and tab bars the system adapts between light and dark glass based on the content beneath, and symbols/text stay monochrome; never color several control backgrounds at once.
- If the content layer is colorful, keep control labels monochrome or pick an accent with clear separation; if content is neutral, the brand accent is a good app accent.
- Sidebars and other large glass surfaces are more opaque to keep text legible over rich content.

### 5.5 Right-to-left and localization

- System components and standard layouts flip automatically in an RTL context; use them and you inherit mirroring, leading/trailing semantics and correct control order.
- **Mirror alignment with the interface:** if content is left-aligned in LTR, right-align it in RTL.
- **Align a paragraph by its language, not the interface.** A paragraph is three or more lines — right-aligning English text inside an RTL app makes the start of each line hard to find. One- and two-line blocks follow the context direction; paragraphs follow their own script.
- **Reverse the alignment of every item in a list**, including items rendered in another script, so scanning stays consistent.
- Numbers, currencies and mathematical symbols vary by locale inside RTL languages — use locale-aware formatters rather than hard-coded separators or Western digits.
- Arabic and Hebrew have no uppercase, so RTL text can look too small beside all-caps Latin: raise the RTL size by about **2 pt** to balance mixed rows.
- Icons that encode direction (back, forward, next) mirror; icons that encode a physical object (a camera, a musical note) do not. Never mirror logos, trademarks or glyphs whose meaning is orientation-independent.

---

## 6. Materials, Dark Mode and Motion

### 6.1 Liquid Glass — the functional layer
- Liquid Glass is for **controls and navigation** (tab bars, toolbars, sidebars, popovers, ornaments). It floats above content so content can scroll and peek beneath.
- **Never use Liquid Glass in the content layer.** Use standard materials (blur, vibrancy) for app backgrounds and content surfaces. The exception: a control in the content layer that becomes transiently interactive (slider thumb, toggle) may take a glass appearance while active.
- **Use glass effects sparingly.** System components adopt it automatically; custom controls should use it only if they are among the most important functional elements.
- Two variants: **regular** blurs and adjusts luminance, used by most components and wherever text volume is high (alerts, sidebars, popovers); **clear** is highly translucent, for controls floating over media so the content stays prominent.
- With clear glass over **bright** content, add a **dark dimming layer at ~35% opacity**; over sufficiently dark content (or with AVKit's own dimming) no layer is needed.
- Standard materials (blur, vibrancy, blending modes) carry semantic meaning: pick by use case, not by the color they appear to add. Use vibrant system colors on top of a material.

### 6.2 Dark Mode
- **Don't offer an app-specific appearance switch.** Respect the system setting, including Auto.
- Design both appearances, and test Dark Mode with Increase Contrast and Reduce Transparency, separately and together.
- Dark palettes are dimmer backgrounds and brighter foregrounds — not mechanical inversions.
- Use semantic colors that adapt (`labelColor`, `separator`, `UIColor.label`), or Color Sets with light/dark variants; avoid hard-coded values.
- Contrast: at least 4.5:1; 7:1 for small custom text.
- Slightly darken images that contain white backgrounds so they don't glow.
- SF Symbols adapt automatically; draw separate light/dark versions of custom icons only when a shape genuinely needs it.

### 6.3 Motion
- **Add motion purposefully**; gratuitous animation distracts and can cause discomfort.
- **Make motion optional** — never the only carrier of important information; pair with haptics and audio.
- Feedback motion should follow gestures and expectations (a view that slides down from the top should not dismiss sideways).
- Keep feedback animations brief and precise; avoid animating frequent interactions, since the system already animates standard controls.
- **Let people cancel motion**: never block input until an animation ends.
- Respect Reduce Motion: tighten springs to cut bounce, track gestures directly, avoid z-axis depth changes, replace x/y/z transitions with fades, never animate into or out of blurs.
- Games: target 30–60 fps for smoothness; avoid flashing and blinking that can trigger photosensitivity or dizziness.

### 6.4 Haptics

- Standard controls already play haptics — switches, sliders and pickers on supported iPhones, the Taptic Engine patterns on Apple Watch, Force Touch trackpads on the Mac. Don't add your own on top of them.
- **Use system patterns for their documented meanings**: *notification* (success, warning, error), *impact* (light, medium, heavy, rigid, soft) and *selection*. If a pattern's documented meaning doesn't fit, use a different pattern rather than redefining this one.
- Two shapes of custom feedback: **transient** (a brief tap or impulse, like the Flashlight button) and **continuous** (a sustained vibration, like message effects).
- Haptics reinforce, never carry, information: pair with visual and audio feedback, and never make a haptic the only signal.
- Haptic hardware varies: game controllers on iPadOS, macOS, tvOS and visionOS; Apple Pencil Pro and some trackpads on certain iPads; the Mac trackpad while dragging or force-clicking. Design so the app is complete without any of it.
- Avoid long, repetitive or surprising haptics — they drain the battery and read as errors.

---

## 7. Icons, symbols and images

### 7.1 App icons — specifications

| Platform | Layout shape | Shape after masking | Size | Style | Appearances |
|---|---|---|---|---|---|
| iOS, iPadOS, macOS | Square | Rounded rectangle | 1024×1024 px | Layered | Default, dark, clear light, clear dark, tinted light, tinted dark |
| tvOS | Rectangle (landscape) | Rounded rectangle | 800×480 px | Layered (parallax) | — |
| visionOS | Square | Circle | 1024×1024 px | Layered (3D) | — |
| watchOS | Square | Circle | 1088×1088 px | Layered | — |

- Provide a single square master; the system masks corners and scales all smaller variants (Settings, notifications, Spotlight).
- Supported color spaces: sRGB, Gray Gamma 2.2, Display P3 (P3 on all but visionOS's own use case).
- Give icons the full six appearance variants on iOS-family platforms; design layers so the system can compose depth and tint.
- **One square master per platform.** The system masks corners (or the circle on visionOS/watchOS) and generates every smaller rendition — Settings, notifications, Spotlight, search results.
- tvOS icons are landscape (800×480 px) and animate with parallax, so keep important content away from the edges that parallax reveals.
- Do not bake the mask, corner radius, drop shadow or a background bezel into the artwork.

### 7.2 Interface icons
- **Simplify aggressively** — a recognizable metaphor beats detail at 20 pt.
- **Consistent size, stroke weight, detail and perspective** across the whole set; adjust dimensions so weight looks optically equal.
- Match icon weight to adjacent text weight unless one is intentionally emphasized.
- Add padding or nudge asymmetric icons for optical (not geometric) centering.
- SF Symbols first: they scale, adapt to Dark Mode and vibrancy, match text weights, and support four rendering modes — **monochrome** (one color), **hierarchical** (one color, opacity per layer), **palette** (two or more colors, one per layer) and **multicolor** (intrinsic colors that carry meaning, e.g. red `trash.slash`).
- Verify the chosen rendering mode at the actual size and background; use `automatic` but inspect the result.
- Symbols support variable color (for progress/level), weight/scale variants, and animations; use animation to explain change, not to decorate.

### 7.3 Images
- **Resolution:** supply assets at the resolutions devices need; never upscale at runtime.
- **Formats:** photographic content as high-quality compressed JPEG/HEIC, images with transparency as PNG, vector or PDF for scalable glyph-like artwork. Always include a color profile.
- **Test on real devices** at real sizes: what looks crisp in the editor can pixelate, stretch or compress on device.
- On tvOS supply layered artwork (image stack) so focus and parallax look right; on visionOS avoid baking perspective into flat images.
- **Scale factors:** @1x = 1 px per pt, @2x = 2, @3x = 3. Supply each density; never let the system upscale. Higher density is not a license to add detail — it is a license to keep the same design crisp.
- **visionOS:** images can appear at a far larger range of sizes than on any other platform and the system rescales resolution to match; because images sit at angles in the room, image pixels need not map 1:1 to display pixels.
- **watchOS:** prefer autoscaling PDFs sized for the 40 mm and 42 mm screens at @2x; WatchKit rescales them per screen size — 38 mm 90%, 40 mm 100%, 41 mm 106%, 42 mm 100%, 44 mm 110%, 45 mm 119%, 49 mm 119%.

### 7.4 Document icons (macOS)
- A document icon can display as small as **16×16 px**, so the design must stay recognizable at that size; simplify or drop details in the smallest renditions (in the 16 px version you may remove fine internal lines entirely).
- Supply the standard ladder: **512×512 (@1x) / 1024×1024 (@2x)**, 256/512, 128/256, 32/64, 16/32.
- A center image measures **half the canvas** (a 32×32 icon gets a 16×16 center-image canvas), supplied at 256/512, 128/256, 32/64 and 16/32.
- Keep a margin of about **10%** of the canvas and let the image occupy about **80%** of it — in a 256×256 canvas the artwork fits roughly 205×205 px. Parts may extend into the margin for optical alignment.
- Use uncomplicated shapes and a reduced palette of distinct colors; a background fill, a center image, or both.

### 7.5 Artwork for tvOS shelves and lockups
- Top Shelf and lockup artwork is authored in points and pixels at once; supply @1x and @2x.
- **Poster (2:3):** actual 404×608 pt, focused/safe zone 380×570 pt, unfocused 333×570 pt.
- **Square (1:1):** 608×608 / 570×570 / 500×500 pt.
- **16:9:** 908×512 / 852×479 / 782×440 pt.
- **Scrolling inset banner:** 1940×692 / 1740×620 / 1740×560 pt.
- If you offer no full-screen Top Shelf content, supply a static fallback of **2320×720 pt**; tvOS flips and blurs it to fit 1920 px at 16:9.
- Mixing sizes in one row rescales everything to the tallest item (a 16:9 image becomes 500 px high next to a poster), so keep a row to one aspect.

---

## 8. Accessibility

An accessible interface is **intuitive** (familiar, consistent interactions), **perceivable** (never dependent on one sense) and **adaptable** (responds to system settings).

### 8.1 Vision
- Support larger text: at least 200% on iOS/iPadOS, 140% on watchOS, through Dynamic Type or custom scaling.
- Follow the default and minimum type sizes in §4.2; thin weights need larger sizes.
- Meet contrast minimums (§5.2) in both appearances and with Increase Contrast.
- Prefer system colors, which ship accessible variants.
- **Convey information beyond color**: shapes, icons, patterns, text.
- Label everything for VoiceOver: concise label, correct trait (button, header, image), grouped row content, value for adjustable controls, announcements for changes.

### 8.2 Hearing
- Captions for synchronized audible information; subtitles for dialogue in a chosen language; audio descriptions for visual-only information; transcripts for long-form media.
- Pair audio cues with haptics and with visual cues (vibration + onscreen sign).
- Games: subtitle all dialogue, including incidental barks and offscreen events.

### 8.3 Mobility
- Meet control sizes and spacing (§3.5): 12 pt padding around bezeled elements, ~24 pt around bezel-less ones.
- **Support simple gestures** for frequent actions; avoid custom multi-finger and multi-hand gestures.
- **Always offer a non-gesture alternative** — if swipe deletes, provide an Edit mode with a Delete button.
- Support Voice Control (label every element), Full Keyboard Access, Switch Control, AssistiveTouch and Pointer Control.
- Integrate Siri and Shortcuts so tasks can be done by voice, the Action button, or a shortcut.

### 8.4 Speech
- Let the keyboard alone drive navigation and interaction; never override system shortcuts.
- Every element reachable by keyboard must be focusable, with a visible focus ring.

### 8.5 Cognitive
- Keep actions simple and consistent; prefer system behaviors over invented gestures.
- **Minimize time-boxed UI** — avoid auto-dismissing views; prefer explicit dismissal.
- Let people control audio and video: no autoplay without visible controls and a global opt-out.
- Honor Dim Flashing Lights and Reduce Motion.
- Games: difficulty and assist options (reduce success thresholds, adjust reaction time, control assistance).
- **Assistive Access** (iOS/iPadOS): strip noncritical workflows, break multi-step flows into one interaction per screen, confirm twice before hard-to-recover actions like deletion.

### 8.6 visionOS accessibility
- Pointer Control by hand or head, and Zoom, must work with your layout.
- Keep everything in the field of view; reduce animation speed and intensity, especially peripherally; avoid head-anchored content; minimize large repetitive gestures.

---

## 9. Writing

### 9.1 Voice and structure
- **Consider each screen's purpose:** most important information first, one idea per screen, clear flow across screens.
- **Be action oriented.** Label buttons and links with verbs ("Send", not "Let's do it!"; "Learn more about X", not "Click here").
- **Build language patterns** and reuse them; choose title case or sentence case per element type and stay consistent.
- **Guide multi-step flows**: "Get Started" → "Continue"/"Next" → "Done", used consistently.
- **Use possessive pronouns sparingly** ("Favorites", not "Your Favorites"); **avoid "we"** — "Unable to load content" beats "We're having trouble loading this content".
- **Write for the device**: "tap" on iPhone/iPad, "click" on Mac; brevity on watch and TV; assume TV text is visible to a room of people.
- **Empty states** should explain what goes here and offer the action that fills it; never put crucial information in a temporary state.
- **Error messages** sit close to the problem, avoid blame, and say how to fix it: "Choose a password with at least 8 characters", not "That password is too short". Drop "oops" and "uh-oh".
- If wording can't fix a recurring error, redesign the interaction.

### 9.2 Component-specific copy
- **Buttons:** title case, verb-first, 1–3 words; ellipsis when the control opens another window or view.
- **Alerts:** title states what happened and why in ≤ 2 lines; body only if it adds value; button titles describe the result ("Erase", "Delete", "Convert"), "Cancel" always spelled "Cancel"; no "Yes"/"No"; "OK" only for purely informational alerts.
- **Settings and labels:** sentence case, no trailing punctuation, no jargon, no abbreviations people wouldn't recognize.
- **Notifications:** short title, one clear sentence, action verbs in actions.

---

## 10. Components

Rules below are the ones that separate Apple-quality UI from approximation. When in doubt, use the system component unmodified.

### 10.1 Navigation — tab bars, tab views, sidebars, toolbars, search

**Tab bar (iOS/iPadOS)**
- Navigation only, never actions. Actions belong in a toolbar.
- Keep it visible; hiding it makes people lose their place (a covering modal is the exception).
- Prefer fewer tabs. Trailing overflow becomes a "More" tab, which hides content and should be avoided.
- **Never disable or hide tabs when content is empty** — explain the empty state instead.
- Always include labels, single words where possible; prefer filled SF Symbols.
- Badges are for critical, new information only (red oval, white text, number or `!`).
- 5 or fewer default tabs when people can customize; iOS floats the bar on Liquid Glass; iPadOS places it near the top and can convert to a sidebar; visionOS tab bars are vertical along the leading side and require both symbol and label.
- **If people can choose their own tabs, default to five or fewer** so the set survives the transition between compact and regular widths.
- In tvOS a tab bar is **68 pt tall with its top edge 46 pt from the top of the screen**; neither value is changeable. The bar is translucent and only the focused tab is opaque, with a drop shadow to mark selection.
- tab views (macOS): **never more than six** — beyond six, choose another structure.

**Tab view (macOS)**
- Closely related panes only; each pane self-contained.
- Noun labels, title case; never more than six tabs; never a pop-up button as a substitute.

**Sidebar**
- For navigable hierarchy; group with disclosure controls when content is deep.
- Let people customize contents when the app has many areas.
- Extend content beneath it (horizontal scroll or background extension effect); sidebars are more opaque glass.

**Toolbar**
- Deliberate items only; define which move to overflow as width shrinks (the system adds overflow automatically — never add one manually).
- A More menu holds genuinely secondary actions.
- Let people customize toolbars in iPadOS and macOS when the app has many items or advanced functionality.
- Avoid custom toolbar backgrounds and tinted controls; they fight the system's glass and scroll edge effects.
- Titles: prefer no title in iOS where the large title carries context; keep navigation and actions on opposite ends consistent with platform convention.
- **Three zones:** the *leading edge* holds navigation (back/forward, sidebar toggle), the view title, and a document menu; these are never customizable so they stay available. The *center* holds common controls and can be customized in macOS and iPadOS, and collapses into the system overflow as the window narrows. The *trailing edge* holds inspectors, an optional search field, the More menu, and the primary action (Done) — it stays visible at every window size.

**Search**
- Give search a primary position when it matters (its own tab, or a bottom toolbar field).
- One clearly identified global search; local search acts as a filter on the current view.
- Show scope (placeholder, scope bar, or title).
- Start filtering as people type; show recents and predictive suggestions; rank most relevant results first and allow filtering.

**Search field anatomy and placement**
- The field ships with a search icon, a Clear button and placeholder text. The placeholder states the scope ("Search all mailboxes"); it is not the field's label.
- **iOS entry points.** A *search tab* in the tab bar, in one of two styles: **standard** (uniform with the other tabs; tapping lands on a search page that can show suggestions and promoted content) or **button appearance** (focuses the field and raises the keyboard immediately, then returns people to their previous tab). Or a **bottom toolbar** field/button — best when search is a priority and there is room, because it stays in reach — or a **top toolbar** button when content at the bottom must not be covered, or an **inline field** directly above the list it filters, optionally pinned to the toolbar as the list scrolls.
- **iPadOS and macOS.** Trailing side of the toolbar for split-view apps that search across columns; top of the sidebar when search filters navigation; a dedicated sidebar or tab-bar item when suggestions and categories need room. Focus the field when someone navigates to a dedicated search area — except on iPad with only a virtual keyboard, where an unfocused field avoids the keyboard covering the view. Keep search in the same relative place across iPad and Mac, and re-place it deliberately when the window narrows to a compact width.
- **A scope bar** filters among clearly defined categories; default to the broadest scope so people see the full result set before narrowing. **Tokens** turn a chosen term into an editable chip that filters the rest of the search; pair tokens with suggestions, since people can't guess which tokens exist.
- **tvOS:** a search screen is a keyboard screen with results below it — supply popular, contextual and recent suggestions, because nobody wants to type on a remote.
- **watchOS:** tapping the field opens a full-screen text-input control; the app returns to the field only after Search or Cancel.

### 10.2 Content — lists, collections, charts, text and media

**Lists and tables**
- Prefer text; if items vary wildly in size or are mostly images, use a collection instead.
- Let people edit (reorder) when it makes sense; in iOS/iPadOS selection requires an edit mode.
- Give selection feedback: navigation lists keep the row highlighted to show the path; option lists flash then show a checkmark.
- Keep row text short; preserve readability when truncated (middle ellipsis can help), and use descriptive column headings (nouns, title case, no punctuation).
- Grouped style with headers/footers for groups (iOS/iPadOS); bordered style with alternating rows for wide Mac tables; watchOS elliptical style.
- **Info button (ⓘ) only reveals more information** — never use it to drill into a row; use a disclosure indicator for navigation.
- Don't add an index when rows have trailing controls; they collide.
- macOS: clicking a column heading sorts, clicking again reverses; allow column resizing; use outline views for hierarchy.
- tvOS: rows scale on focus and corners round — account for that in artwork, never add your own masks.

**Split views** — two or three adjacent panes showing several hierarchy levels at once; the usual shape is a sidebar plus content plus optional detail. Persistently highlight the current selection in **every** pane that leads to the detail view, let people drag content between panes, and collapse to a single column when width runs out rather than squeezing panes. Rarely, panes can surround the main canvas (Keynote's navigator, notes and inspector) — but that is a document layout, not navigation.

**Collections** — grids of visual items; keep cells consistent, reuse cell layouts, and let content (not the grid) set the emphasis.

**Charts**
- **Chart only when the shape of the data is the message.** If people just need the values, a sortable, searchable list or table serves them better.
- **One message per chart**, stated in its title, subtitle or annotation; let people drill in for detail instead of drawing everything at once.
- **Prefer familiar forms** — bar, line, area, scatter, and pie only for parts of a whole with few slices. An unfamiliar form needs teaching, the way Activity animates each ring the first time a watch pairs.
- **Label axes and units**, and start a value axis at zero for magnitude comparisons; never truncate an axis to exaggerate a difference.
- **Distinguish series by more than hue** — shape, pattern, direct labels, position — and check the palette under deuteranopia and Increase Contrast.
- **Keep charts of the same dataset visually identical** (type, colors, annotations, layout) so people know the dataset didn't change; signal a new perspective with size and detail, not a new style.
- **Size a chart to its interactivity**: readable labels and annotations come first, then room for selection, scrubbing and drill-down; a glanceable chart can be small, an explorable one cannot.
- **Accessibility:** every mark and series needs a label and a value, plus accessibility elements so VoiceOver can step through the data instead of announcing an image.
- **No 3D and no gratuitous effects**; marks must stay legible at the smallest supported width and at large text sizes.

**Text views, web views, image views**
- Text views for long-form input; text fields for short values.
- Web views are for web content only; never use them to fake native UI.
- Image views: respect aspect ratio (fill or fit, never distort), provide meaningful alternative descriptions.

**Lockups** — cards, caption buttons, monograms, posters used in TV/music browsing; keep text overlays inside safe text zones, and use consistent ratio and corner treatment per platform.

### 10.3 Buttons, menus and actions

**Buttons**
- Three attributes decide everything: **style** (size, color, shape), **content** (symbol, label, or both), **role** (normal, primary, cancel, destructive).
- Hit region ≥ 44×44 pt (60×60 pt visionOS) with visible space around it.
- **Every custom button needs a press state.** No press state feels broken.
- **One prominent button per view (two at most).** Prominence is a *style*, not a size — never resize a button to emphasize it.
- Primary = the most likely choice, responds to Return, may auto-dismiss the enclosing sheet or alert. **Never make a destructive action primary.**
- Destructive actions use system red and are never the default button.
- Content: prefer a familiar symbol (`square.and.arrow.up` = share); use a short verb-first label when words are clearer than an icon.
- Don't repeat the content layer's color in button labels; keep them monochrome over colorful backgrounds.
- iOS/iPadOS: show an activity indicator inside the button for actions that don't finish instantly, optionally with a changed label ("Checkout" → "Checking out…").
- macOS: push buttons (append "…" when opening a window/view), square gradient buttons inside a view for view-related actions (never in toolbars), help buttons (one per window, circular "?"), image buttons (~10 px padding around the image). Support spring loading where useful.
- visionOS: three shapes — circle (icon-only), rounded rectangle or capsule (text), capsule (icon + text); sizes 28/32/44/52/64 pt; visible contrasting background; audio feedback; no custom hover effects.
- watchOS: inline buttons are capsules; full-width buttons for primary actions; equal heights in a stack.
- macOS image buttons: about **10 px of padding** between the image and the button edges, because that padding is part of the clickable area; don't add a system border to them.
- macOS help buttons: circular "?" — **at most one per window**.

**Activity views (share sheets)**
- Use one for sharing or acting on the current item; the system presents the standard destinations.
- A custom activity's **custom icon is centered in an area of about 70×70 px**; prefer an SF Symbol.

**Menus, the menu bar and menus inside apps**
- Menu labels: title case, short, verb-first for commands; symbol + label where it helps recognition.
- Organize by task, not by chronology; group with separators; keep submenus to one level.
- Use checkmarks for toggled items, never change a menu item's meaning based on state without also updating its title.
- **macOS menu bar is mandatory**: App menu, File, Edit, Format, View, app-specific menus, Window, Help. Include every command, even those in toolbars or context menus; disable (don't hide) unavailable items, and use `…` for items that need more input.
- Context menus: relevant, short, consistent throughout the app; every item also reachable in the main UI; one level of submenu maximum.
- Pull-down vs pop-up buttons: pull-down performs an action from a list; pop-up chooses a value and shows the current selection.
- Edit menus: standard Cut/Copy/Paste/Select All plus app-specific items; never reuse standard shortcuts for different actions.
- Dock menus (macOS), Home Screen quick actions, and Dock-only shortcuts should expose the same top tasks the app's main UI does.
- **The macOS menu bar is 24 pt tall.** Menu bar extras draw with black and clear only, so the system can tint them on light, dark and selected menu bars.
- iPadOS menus come in three presentations: **small** (a top row of four symbol-only items above a list), **medium** (three items, symbol above a short label) and **large** (the default — a single list).

**Action sheets (iOS/iPadOS/watchOS)**
- For choices about an intentional action; not for problems (that's an alert).
- Short single-line title; message only if necessary; Cancel at the bottom (or upper-leading on watchOS); destructive option styled red.

### 10.4 Presentation — alerts, sheets, popovers, panels, windows

**Alerts**
- Only for critical, actionable information. Never at launch, never for marketing, never for routine undoable actions.
- Title: what happened, in context, and why — ≤ 2 lines; sentence case if a full sentence, title case if a fragment.
- Up to three buttons; the most likely is trailing (or top of a stack); Cancel lives leading (or bottom); destructive styled red only when the person didn't deliberately choose the destructive path.
- Provide Esc / Command-Period / Menu-button cancellation where the platform allows.
- No scrolling alerts; no text fields unless input is required to resolve the situation.
- macOS may add an app icon, a suppression checkbox, an accessory view and a Help button; use the caution symbol sparingly.
- **Up to three buttons** on every platform; a visionOS accessory view must be no taller than **154 pt** and use a **16 pt corner radius**.

**Sheets**
- For a scoped task tied to the current context. Modal in macOS, tvOS, visionOS, watchOS; can be nonmodal in iOS/iPadOS.
- One sheet at a time from the main interface; closing a sheet returns to the parent, never to another sheet (close the first before showing a second).
- Provide **Cancel** (or Close) and **Done**; **Back** navigates within a flow. Never show Cancel, Done and Back together. Done alone implies the only exit is completion.
- iOS/iPadOS: Cancel leading in the toolbar, Done trailing; multi-step flows may move them. Support the medium detent for progressive disclosure, include a **grabber**, support swipe-to-dismiss, and confirm with an action sheet if there are unsaved changes.
- **Detents:** the system defines *large* (fully expanded) and *medium* (about half the expanded height). Sheets support large automatically; adding medium lets the sheet rest at both heights, while specifying only medium prevents expansion to full height. Custom detents are allowed.
- A **grabber** tells people the sheet is draggable, and tapping it cycles through the detents.
- macOS: titleless card over a dimmed parent, sensible default size, resizable when useful, other windows stay reachable.
- visionOS: centered in the field of view, never sliding from the bottom edge; keep it smaller than the window and let people resize.
- watchOS: full-screen, material-blurred, brief and occasional.

**Popovers** — for contextual choices anchored to a control (iPadOS, macOS, visionOS); never for critical information, which needs an alert; dismiss on outside tap; arrow must point at the source.

**Panels (macOS)** — persistent auxiliary windows for repeated input-and-observe work (inspectors, find and replace); float above their document, don't steal focus.

**Windows**
- Support resizing, and remember size and position per document when it matters.
- Use split views for hierarchy instead of stacking nested navigation on large screens.
- macOS windows: minimum sensible size, avoid critical content at the bottom edge; iPadOS: support multiple scenes and window resizing; visionOS: place windows in front of people at a comfortable distance and scale — the default is **1280×720 pt** at about 2 m.

**visionOS ornaments**
- An ornament floats in a plane parallel to its window and slightly in front of it; it moves with the window and does not scroll with content.
- Keep it visible; hide it only when people dive into content (video, photos). Keep its width equal to or narrower than the window. The default background is glass, so borderless buttons work.
- Toolbars and tab bars are ornaments automatically — build a custom one only when you need something the system doesn't provide.

**Scroll views**
- Respect scroll edge effects (blur + fade under bars) instead of opaque separators.
- Support the platform's scroll indicators; never hide scrollability behind custom chrome.
- Keep scroll position on rotation/resize; use paging only for discrete full-screen content (page controls, carousels).

**Page controls** — for flat, ordered sets of a few pages; show dots, not numbers; place below or beside content; never for deep hierarchies.

### 10.5 Selection and input controls

**Text fields**
- For small amounts of information (name, email, search term); use a text view for long-form input.
- Show placeholder text *and* a persistent label when the field's purpose isn't obvious; placeholders vanish as people type.
- **Always use a secure field for passwords**; never disable paste.
- Size the field to the expected input length; stack multiple fields vertically with consistent widths and even spacing.
- Validate inline, near the field, in plain language; keep entered text on error.

**Toggles**
- For two opposing values affecting state ("on/off"), not for choices among many.
- The surrounding label must make clear what is being turned on or off.
- State must differ by more than color (fill, shape, checkmark or knob position).
- In macOS use checkboxes for independent options and switches for immediate-effect settings.

**Sliders**
- Minimum at the leading edge (bottom for vertical), maximum at the trailing edge (top).
- Show range endpoints with icons or labels when the effect isn't obvious.
- Pair with a text field and stepper when precise values matter.

**Segmented controls**
- Closely related choices affecting an object, state or view; keep the grouping visible at all sizes.
- Never mix actions and selection in one control.
- About 5–7 segments in a wide interface, about 5 on iPhone; keep segment widths consistent.

**Pickers**
- Medium-to-long ordered lists; short lists use a pull-down button, very long lists use a list or table.
- Predictable ordering (alphabetical, chronological); display in context, not by switching views.
- Date pickers: reduce minute granularity to a divisor of 60 (5, 15, 30) when precision isn't needed.

**Steppers, digit entry, color wells, combo boxes, token fields**
- Steppers for small, precise increments next to the value they change.
- Digit entry views for numeric codes (PIN, passcode) with clear per-digit feedback.
- Color wells open the system color picker; store and restore custom colors.
- Combo boxes combine typing with a list; token fields turn selections into removable chips.

**Virtual keyboards**
- Never obscure the field being edited; scroll content so the field and its label stay visible.
- Match keyboard type to input (`emailAddress`, `numberPad`, `URL`), provide a return-key label that matches the action ("Search", "Send").
- Custom input views only when they genuinely speed input; always keep an escape to the standard keyboard.

### 10.6 Status and progress

- **Prefer determinate progress**; be accurate and even in advancement (90% in 5 seconds then 10% in 5 minutes feels deceptive).
- Keep indicators moving; a frozen indicator reads as a hang.
- Switch indeterminate → determinate once duration is known; never switch circular → bar mid-task.
- **Show something immediately** instead of an empty screen; use placeholders that turn into content.
- Gauges and activity rings: label units, keep the value legible at a glance, support colorblind-safe differentiation.
- Rating indicators: show the average plus the count, allow clearing a rating, never force a rating mid-task.
- Status bars: hide only for immersive media or games, and restore on tap.

### 10.7 Specialised controls

**Boxes** — group logically related content with a border or background. Keep a box small relative to its container; as it approaches the window size it stops communicating grouping. Do **not** nest boxes for subgroups — use padding and alignment. A short sentence-case title helps VoiceOver predict the contents (colon only in settings panes). iOS/iPadOS fill boxes with the secondary and tertiary background colors; macOS puts the title above. Not available on tvOS or watchOS.

**Column views (browsers)** — macOS only. One column per hierarchy level, parents marked with a triangle. Show the root in the first column; show a preview of the selection when it has no children; let people resize columns. Use a split view instead on iPadOS and visionOS.

**Path controls** — macOS only, always in the window body, never in the toolbar or status bar. *Standard* style is a linear root-to-selection list that hides intermediate names when space runs out; *pop-up* style shows the selected item and opens a menu of ancestors with a Choose command when editable. Dragging an item onto an editable control selects it.

**Disclosure controls** — hide detail until relevant; keep the most-used controls at the top of the hierarchy. A **disclosure triangle** points inward from the leading edge when collapsed and down when expanded; a **disclosure button** points down when hidden and up when visible. Use **at most one disclosure button per view**, place it beside the content it reveals, and label it ("Advanced Options").

**Combo boxes** — macOS only: a text field fused with a pull-down button. Default the field to a meaningful value from the list (not necessarily the first), keep list items no wider than the field, and label in title case ending with a colon.

**Image wells** — macOS only, an editable image view: paste, delete, or drop an image without selecting first. Restore a default image if the well requires one, and keep Cut/Copy/Paste working.

**Steppers** — place beside the value they change (the control displays no value); on macOS support Shift-click for roughly 10× the increment; pair with a text field when the range is wide. Not available on watchOS or tvOS.

**Page controls** — dots, never numbers, for a flat ordered set; place below or beside the content; keep each page to about one screen height and put variable-height pages after fixed-height ones.

**Segmented controls** — about **5–7 segments** in a wide interface and about **5** on iPhone; keep widths consistent; never mix actions and selection.

**Pickers** — date and time pickers offer *compact*, *inline*, *wheels* and *automatic* styles in date, time, date-and-time and countdown modes. Countdown maxes at **23 h 59 min** and is unavailable in the inline and compact styles. Other pickers: ordered lists, predictable sorting, shown in context.

**Sliders** — horizontal for fixed start and end (opacity 0–100%), circular for values that repeat or continue (rotation 0–360°, or 1440° for four spins). Minimum at the leading edge, maximum at the trailing edge; label the endpoints when the effect isn't obvious; pair with a field for exact values.

---

## 11. Patterns

### 11.1 Launching
- Launch fast and land on content; never show a splash screen or logo animation as a delay.
- Launch screens should look like the first frame of the app (background + static UI), not marketing.
- Restore the previous state where it helps continuity.

### 11.2 Onboarding
- **Teach through interactivity**, not slides.
- Prefer context-specific tips delivered in place over one long onboarding flow (TipKit).
- Any prerequisite flow must be brief, skippable, and not require memorizing steps.
- Never ask for permissions, accounts or ratings before people understand the value.

### 11.3 Loading
- Show content placeholders immediately; replace them as data arrives.
- Let people keep working while content loads in the background.
- If a wait is unavoidable, give something useful to read (tips, hints, feature previews) and estimate the remaining time honestly.

### 11.4 Feedback
- Make every feedback channel accessible: color + text + sound + haptics.
- Keep status feedback in place (near the item it describes) rather than interrupting.
- Reserve alerts for critical, actionable problems.
- Warn before unexpected, irreversible data loss — and only then.

### 11.5 Modality
- Use modality only with a clear benefit; keep modal tasks short, simple, single-path.
- Never build an "app inside an app": no deep hierarchies in a sheet.
- Full-screen modal for immersive content or complex editing (video, photos, camera, markup).
- Always give an obvious way out that doesn't discard work without asking.

### 11.6 Searching
See §10.1. Additionally: search should be forgiving (diacritics, plurals, typos), retain recent searches, and never return an unexplained empty list — offer spelling help or scope suggestions.

### 11.7 Settings
- Prefer sensible defaults over settings; every option is a decision you pushed onto the person.
- Group general settings, then task-specific options; put app preferences in your own settings, not in the system Settings app unless required.
- Changes apply immediately and visibly; no Save button in preferences.

### 11.8 Offering help
- Provide help in context (tooltips on macOS/visionOS, contextual tips); keep one help button per window on macOS.
- Help content should answer the actual task, not restate the UI.

### 11.9 Undo and redo
- Support undo for destructive edits; on iOS/iPadOS use shake-to-undo and a three-finger swipe, plus an onscreen path; on macOS provide Edit > Undo/Redo with ⌘Z / ⇧⌘Z.
- Undo should be specific ("Undo Delete") and should survive navigation within the document.

### 11.10 Files, printing and full screen
- Use document browsers for open/save, keep recent documents, autosave and versions where the platform offers them, and show Quick Look previews.
- Printing uses the system panel; paginate and preview accurately.
- Full screen on macOS/iPadOS for immersive content; provide an obvious exit and keep essential controls reachable.

### 11.11 Drag and drop
- Support drag for content people expect to move or copy; provide a preview image of what's being dragged.
- Show valid drop targets by highlighting them; give feedback on drop (insertion line, snap, animation).
- Accept multiple representations (text, image, URL, file) and multiple items; support spring loading and multi-item drags.
- Never make drag the only way to do something.

### 11.12 Collaboration and sharing
- Use the share sheet (`square.and.arrow.up`) for sharing; don't invent a parallel share UI.
- Share the smallest useful unit (one item, one link) with sensible metadata (title, thumbnail).
- In collaborative apps, show who is present and what changed, and keep conflict handling understandable.

### 11.13 Notifications
- Ask for permission only when the value is clear, ideally after a relevant action.
- Content: short title, one clear sentence, optional image; actions that work without opening the app.
- **Never use notifications for marketing without explicit opt-in**; keep them timely and high-value.
- Respect Focus; group related notifications; badge only for genuinely new, important information.
- Clearing a notification must not lose data.

### 11.14 Accounts and authentication
- Let people use the app before creating an account wherever possible; defer sign-up until it's needed.
- Support Sign in with Apple alongside other providers, using the system buttons (correct label, size, spacing) or an approved custom button.
- Make sign-out and account deletion findable, explain what deletion removes, and never hide it behind support.
- Store credentials in the keychain; use biometrics (Face ID/Touch ID/Optic ID) instead of repeated passwords.

### 11.15 Ratings and reviews
- Ask only after a positive moment (completed task, achievement), never at launch or during a failure.
- Use the system review prompt sparingly (Apple allows a limited number of prompts per year); never gate features behind a rating.
- Never incentivize ratings or pre-fill reviews.

### 11.16 Privacy and permission requests
- Ask in context, immediately before the feature needs the data.
- Explain the benefit in one sentence on a **pre-permission screen** when the system prompt alone isn't self-explanatory; then let the system prompt appear.
- Request the minimum scope (while-in-use location, limited photos, one-time access).
- Provide a location button for one-off location use instead of full permission.
- Never collect data you don't need; never sell it; state retention.

### 11.17 Multitasking and continuity
- Handle iPad Slide Over/Split View and Stage Manager, Mac window resizing, and visionOS multiple windows without losing state.
- Restore state across launches; hand off between devices only with clear value.

### 11.18 Workouts and live activity in fitness apps

- On watchOS an active workout session keeps the app on screen between wrist raises, so show the metrics people care about continuously — elapsed or remaining time, calories, distance — plus the controls they need mid-set (lap, pause, end).
- On iPhone and iPad, workouts are usually guided sessions; use familiar components for metrics and keep controls reachable with one hand.
- Never lose an in-progress workout to an interruption, a call or a wrist drop; resume exactly where the person was.

### 11.19 Live-viewing apps (TV, sports, channels)

- Treat the interface as an overlay on the video: darken it so text stays legible and channels stay distinct from the content playing behind.
- Badge or tint the thumbnail that represents what is playing so the current selection is unmistakable.
- Keep the content footer's categories identical to the electronic program guide (EPG), and make invoking and dismissing the footer symmetrical (if swiping up opens it, swiping down closes it).
- Cloud DVR and recorded content belong in the same browsing structure as live content, labelled clearly.

### 11.20 Entering data
- **Gather before you ask.** Prefill from the system — account name, email, address, location, calendar — and never make people type what a permission or a setting can supply.
- **Say what the field wants**: a prompt ("username@company.com") or a persistent label ("Email"), plus a sensible default where one honestly exists.
- **Prefer choosing to typing** — picker, menu, stepper, segmented control — and accept drag and drop and paste wherever the data allows it.
- **Validate as people type**, not on submit: keep their text, say what is wrong and how to fix it, and format numbers with a formatter rather than parsing strings yourself.
- **Gate the flow visibly.** Keep Next/Continue unavailable until the required values exist, and state which fields are required before people start.
- **Passwords** always use a secure field, are never prepopulated, and never disable paste; offer biometrics or the keychain instead of retyping.
- **macOS:** let an expansion tooltip reveal the full value of a clipped field on pointer rest.

---

## 12. System experiences

These surfaces live outside your app's window. Each has its own size budget, rendering modes and update rules; getting them wrong is the fastest way to look non-native.

### 12.1 Widgets

**Families and sizes.** System families are small, medium, large, extra large and extra large portrait; accessory widgets are circular, rectangular and inline. On a 430×932 pt iPhone:

| Family | Size (pt) |
|---|---|
| Small | 170×170 |
| Medium | 364×170 |
| Large | 364×382 |
| Accessory circular | 76×76 |
| Accessory rectangular | 172×76 |
| Accessory inline | 257×26 |

Smaller phones step down: 393×852 → 158/338×158/338×354; 375×667 → 148/321×148/321×324; 320×568 → 141/292×141/292×311 with no accessory sizes. iPad publishes a *canvas* size and a smaller *device* size per family (1024×1366 → canvas small 170×170 / device 160×160; extra large canvas 795×378.5 / device 748×356). On Apple Vision Pro widgets are 3D objects: small 158×158, medium 338×158, large 338×354, extra large 450×338 (portrait 338×450). In the watchOS Smart Stack: 40 mm 152×69.5, 41 mm 165×72.5, 42 mm 176×72.5, 44 mm 173×76.5, 45 mm 184×80.5, 46 mm 194×80.5, 49 mm Ultra 1/2 191×81.5, Ultra 3/4 198×81.5.

**Margins and type.** Standard margin is **16 pt**; **11 pt** is the tight setting for graphics, buttons or background shapes; macOS and the Lock Screen use smaller margins still. Never set text below **11 pt**.

**Appearances.** Light and dark are full color; *clear* desaturates and adds translucency, highlights and Liquid Glass; *tinted* desaturates then applies the person's chosen tint. On the Lock Screen widgets are monochrome with no tint; in StandBy and on the HomeView modular face they scale up with the background removed and turn monochrome red when ambient light falls below a threshold. visionOS adds a glass- or paper-like coating that responds to lighting.

**Rendering modes.** *Full color* changes nothing. *Accented* removes the background, substitutes a tint or Liquid Glass, and splits views into an accent group and a primary group, each flat-filled. *Vibrant* desaturates text, images and gauges for the Lock Screen and StandBy.

**Behaviour.** Glanceable content, not a shrunken app: the most useful data for the current time and context. Updates are scheduled and budgeted — never design as if you had a live feed. Placeholders must use the real layout, never a blank rectangle. Offer configuration with real previews.

### 12.2 Live Activities

- For **bounded events** people track without opening the app. They work best for activities under **eight hours**; on the Lock Screen, in the Mac menu bar and in the watchOS Smart Stack they persist for up to **four hours**.
- Presentations: **compact** (leading and trailing views beside the Dynamic Island), **minimal** (one glyph), **expanded** (pulled down from the island), Lock Screen, StandBy and CarPlay.
- **Lock Screen layout margin is 14 pt.** Tighter margins are acceptable for graphics or buttons, but never crowd the edges.
- Adapt compact and minimal views to fit a **28 pt diameter circle** where width is limited (the Dynamic Island in landscape): abbreviate, or use a glyph instead of a string.
- iPhone 430×932: compact **62.33×36.67**, minimal **36.67–45 × 36.67**, expanded and Lock Screen **408 × 84–160**; 393×852 → compact 52.33×36.67, expanded 371×84–160. iPad Lock Screen **425×84–160** (**500×84–160** at 1366 wide). CarPlay: widescreen **1920×720**, portrait **900×1200**, standard **800×480**.
- watchOS Smart Stack: 40 mm 152×69.5 → 49 mm Ultra 3/4 198×81.5.
- One glance = one status line plus the single most important value. Animate only meaningful changes. Offer the one or two actions needed mid-event, and **end the activity when the event ends** — never leave a stale one running.

### 12.3 Complications (watchOS)

- Families: **circular, corner, inline, rectangular, extra large**; legacy templates (circular small, modular small/large, utilitarian, graphic) still appear on older faces.
- Support as many families as you can, consider several complications per family with a **different deep link for each**, and fall back to your app icon in families that cannot show useful data so the tap still launches.
- Type is Rounded, and sizes vary by case size:

| Family | Type size (40 / 41 / 44 / 45–49 mm) | Weight |
|---|---|---|
| Circular | 12 / 12.5 / 13 / 14.5 pt | Medium |
| Circular, large value | 34.5 / 36.5 / 36.5 / 41 pt | Medium |
| Corner | 10 / 10.5 / 11 / 12 pt | Semibold |
| Rectangular | 16.5 / 17.5 / 18 / 19.5 pt | Medium |

- Image slots: circular and bezel **42×42 pt** (40 mm) up to **50×50 pt** (49 mm); extra large **120×120 pt** up to **143×143 pt**; corner circular **32×32 → 38×38 pt**; rectangular large-image-with-title **150×47 pt → 178.5×56 pt**; rectangular text gauge **12×12 → 14.5×14.5 pt**.
- Gauges: *closed* for a percentage of a whole (battery), *open* for arbitrary minimum and maximum (speed), *segmented* for an app-defined range with rapid change (noise).
- Supply a tinted-mode treatment: the same information must survive desaturation, so never encode meaning in color alone. Replace an image with a tinted-mode variant if the full-color one fails when desaturated.
- **Privacy:** the Always-On display is visible to others — keep sensitive values off the face.

### 12.4 Controls, App Shortcuts, Siri and snippets

- **Controls** (Control Center, Lock Screen, Action button): one tap to a clear action, symbol plus short label. Control Center shows symbol with title and value at larger sizes; the Lock Screen shows the symbol only; the Action button shows the symbol and value in the Dynamic Island on press-and-hold.
- **App Shortcuts and Siri:** expose the app's top tasks with natural phrasing, include example phrases, and answer inside Siri or Shortcuts without forcing a launch when the task allows it. Describe the action, not the app ("Start a workout", not "Open Fitness").
- **Snippets:** a spoken dialogue line plus a custom view. A confirmation snippet adds a secondary Cancel and a primary button with your label; a result snippet ends with a single Done. Use snippets for static information or a decision, and Live Activities for anything that keeps changing.

### 12.5 Top Shelf and watch faces

- Top Shelf artwork sizes are in §7.5. A carousel adds two buttons and optional details; a row can hold focusable content or scrolling banners.
- Watch faces belong to the system and the person: supply complications rather than a face of your own.

### 12.6 Notifications on the watch

- **Short look** on wrist raise, **long look** on tap, and actions available without opening the app. watchOS notifications are for high-value, actionable information; anything that only needs a glance belongs in a complication.

### 12.7 Always On

- iPhone dims the Lock Screen while keeping widgets and Live Activities visible; Apple Watch dims the face while the frontmost app keeps running. Keep contrast and legibility in the dimmed state, avoid large bright fills, and never increase refresh rate just because the display is on.

---

## 13. Inputs

### 13.1 Standard gestures — never redefine these

| Gesture | Supported on | Common action |
|---|---|---|
| Tap | all platforms | Activate a control; select an item |
| Swipe | all platforms | Reveal actions/controls, dismiss views, scroll |
| Drag | all platforms | Move a UI element |
| Touch (or pinch) and hold | all platforms | Reveal additional controls or functionality |
| Double tap | all platforms | Zoom in / out; primary action on Apple Watch Series 9+ and Ultra 2+ |
| Zoom (pinch) | iOS, iPadOS, macOS, tvOS, visionOS | Zoom a view; magnify content |
| Rotate | iOS, iPadOS, macOS, tvOS, visionOS | Rotate a selected item |

macOS trackpad / touch display equivalents: primary click / tap selects, double click / double tap opens, two-finger slide / one-finger slide scrolls, pinch zooms, two-finger rotate rotates, secondary click / touch and hold opens a context menu, click-and-drag / touch-hold-drag moves.

**Custom gestures:** only when nothing standard works, never for frequent actions, never multi-hand, never the only route to a core feature; make them discoverable and teachable.

### 13.2 Keyboards and shortcuts
- Never override system shortcuts; respect the standard set, including ⌘Z/⇧⌘Z (undo/redo), ⌘C/⌘V/⌘X (copy/paste/cut), ⌘A, ⌘F, ⌘N, ⌘O, ⌘S, ⌘W, ⌘Q, ⌘, (settings), Space/Return (activate), Esc (cancel), Tab/⇧Tab (focus).
- Provide Full Keyboard Access support: every interactive element reachable by Tab, visible focus indicator, logical order, no keyboard traps.
- Show shortcuts in menus (macOS) and in a discoverable shortcuts overlay on iPadOS (hold ⌘).
- Don't use modifier-heavy custom shortcuts for common actions; don't invent shortcuts that shadow text editing.

### 13.3 Pointing devices, Pencil, and other input
- Show hover effects only where they communicate affordance; never gate essential function on hover.
- Pointer: use system pointer shapes and hover effects; on iPadOS support trackpad gestures and scroll.
- Apple Pencil: hover previews on supported devices, double tap for tool switching, squeeze, and Scribble in text fields. Never require Pencil for core tasks.
- Digital Crown (watchOS, visionOS): vertical navigation and precise value adjustment; don't fight its direction conventions.
- Remotes (tvOS): use focus movement, Menu to go back, Play/Pause to control media; don't require complex swipes.
- Game controllers: support the standard MFi layouts, remap controls, show correct button glyphs per controller.
- Eyes and hands (visionOS): targets should be large enough to look at comfortably; avoid dense clusters of small controls and avoid hover-only information.
- Near-field interactions (proximity handoff): only as an enhancement, never a requirement.
- **Motion sensors** (gyroscope, accelerometer, Core Motion): use them only for a tangible benefit — a workout's activity feedback, a game's control scheme — and never merely to have the data. Access requires a permission prompt carrying your reason. Outside active gameplay, never make tilting the device the way to manipulate the interface: motion gestures are hard to repeat precisely, physically difficult for some people, and costly in battery.
- **iPadOS pointer effects:** *highlight* for a group of controls inside a Liquid Glass container, *lift* for a standalone glass control or a small opaque element, *hover* for large elements with custom scale, tint and shadow. Use the system's effect for anything that behaves like a standard control; a custom one that behaves differently reads as broken.
- **Pointer hit regions:** pad them until comfortable and make adjacent bar buttons contiguous — a gap makes the highlight flicker as the pointer crosses it, and an oversized region makes targeting feel sluggish. Accessories (resize arrows, badges) are secondary indicators, never the target.
- **Never gate a hidden control on hover alone.** On a Mac with a touch display, reveal it by tapping its location and from a context menu, keep the current selection when it appears, and hide it again when the person is done.
- **Keep custom pointer shapes simple and effects purposeful**; no instructional text in a pointer, and scaling only for elements with room to grow.

### 13.4 Eyes and gaze (visionOS)
- **People look to target.** The system highlights a looked-at element with a hover effect before the tap; use system components and their hover effects rather than inventing your own feedback.
- **visionOS gives you no gaze location before a tap**, by design. Never infer attention, build heat maps, or gate content on where someone looked.
- **Comfort first:** keep everything the task needs inside the field of view (§3.6), place content people read or use for a while at least **1 m** away, and avoid putting anything very close unless it is used only briefly.
- **Space items apart.** Eyes make small involuntary movements, so crowded controls cause mis-targeting; use the minimum spacing in §3.5 rather than the smallest gap that fits.
- **Round interactive shapes** — the eye is drawn to corners — and give a multi-element control (image plus caption) one containing shape so the whole region highlights as a unit.
- **Avoid full-field repeating patterns and textures** (the eye can lock onto elements and read false depth) and avoid peripheral motion, which pulls gaze away from the task.
- **Custom hover effects** are for a special moment, not for every element: no delay for a subtle invitation, a short delay to let people act before an expansion, at least one primary view unchanged during the animation, and always tested on device.
- **Focus effects** (keyboard, game controller) are separate from hover effects — support both without conflating them.

---

## 14. Technologies — quick design rules

Each entry below carries the constraint that most often gets broken. Numbers are Apple's.

### 14.1 Payments and commerce

**Apple Pay**
- Use the system buttons (or approved artwork); they scale proportionally, localize automatically, keep VoiceOver labels, and allow corner-radius customization only.
- **Minimum button size 100×30 pt**; the longer captions — Book with, Buy with, Check Out with, Donate with, Set Up, Subscribe with Apple Pay — need **140×30 pt**. Minimum margin around a button is **1/10 of its height**.
- The Apple Pay mark needs clear space of **1/10 of its height**, and must not share a border with another graphic or button. Supply it at **60×60 pt (120×120 px @2x, 180×180 px @3x)**.
- Show the sheet promptly; validate data before presenting it; report validation and processing problems in place, with the next step.
- Support subscriptions and donations with the same button set; never restyle or recolor the mark.

**Wallet passes**
- Pass styles: boarding pass (airline and non-airline), coupon, event ticket (including poster), store card, generic (including poster).
- Field order: logo/logo text, header, primary, secondary, auxiliary, footer, back. **Logo and header stay visible when the pass is collapsed**; the primary field is the one thing people need; secondary/auxiliary are supporting; footer carries category; back holds details.
- Image sizes (pt): `logo` 50–160 wide × 50; `primaryLogo` 30–126 × 30; `secondaryLogo` 12–135 × 12; `icon` 38×38; `strip` 375×144 (coupon, store card); `thumbnail` 60–90 × 90 (event ticket, generic); `background` 343×503 (event ticket); `artwork` 358×448 (poster styles); `footer` 268×15 (airline boarding pass).
- Never place critical information where a strip can be cropped; keep essential fields inside the safe area.
- Order tracking: give a direct carrier link as well as a tracking number, a scannable barcode for pickup, and clear collection instructions. Merchant and product images are **300×300 px**, PNG or JPEG, **nontransparent** background.

**In-App Purchase** — consumable, non-consumable, auto-renewable and non-renewing products. The signup screen must state the subscription name, duration, what each period provides, and the **localized price**, and must offer sign-in/restore for existing subscribers. One-time-use codes suit small or restricted distribution; custom codes suit mass campaigns.

**Tap to Pay on iPhone** — educate merchants in context, keep checkout fast, handle PIN entry (including accessibility mode) and Strong Customer Authentication, and always offer another payment method plus a clear result screen with a retry.

### 14.2 Identity

**Sign in with Apple**
- Offer it wherever another sign-in method exists, with the system button or an approved custom one.
- **Minimum size 140×30 pt**, margin **1/10 of the button's height**. Logo-only buttons are always 1:1 and already padded — don't add horizontal padding.
- PNG logo artwork is only for **44 pt** tall buttons; use SVG or PDF for any other height.
- Titles are limited to *Sign in with Apple*, *Sign up with Apple*, *Continue with Apple*; logo and title must both be black or both white.
- Never ask again for the name or email you already received; respect Hide My Email (let people view their relay address and point them to Settings › Apple Account › Password & Security › Apps using Apple Account); handle credential revocation.

**ID Verifier** — use a **Display Only** request to confirm identity visually (data never leaves system UI); use **Data Transfer** only with a legal requirement and the extra entitlement.

### 14.3 Media

**Video**
- Aspect-fill (full screen, slight cropping) is the default for wide video **2:1 through 2.40:1**; fit-to-screen (letterbox/pillarbox) is the default for **4:3, 16:9, up to 2:1**, and for ultrawide above 2.40:1.
- Scrubbing thumbnails: **160 px** wide each.
- Interactive overlays: wait at least **0.5 s** of playback before pausing to show one, and always offer dismiss-and-resume.
- **watchOS:** clips no longer than **30 s**; H.264 High Profile, **160 kbps** up to 30 fps, **208×260 px** portrait or **320×180 px** 16:9, audio 64 kbps HE-AAC.
- visionOS: let people choose when playback starts, prefer a small resizable window, and keep their surroundings visible.

**Audio** — pause indefinitely for primary audio interruptions (music, podcasts, audiobooks); duck or pause briefly for short ones (navigation prompts) and restore afterwards. tvOS and visionOS need explicit handling of the route and of shared listening.

**AirPlay** — use the system icon in black, white or custom color as supplied; never redraw or recolor it, and refer to it as AirPlay, not "screen mirroring".

**Live Photos, photo editing, ShazamKit** — reuse the system UI and terminology; ShazamKit suits syncing graphics or captions to known audio, not for identifying arbitrary sound in the background.

### 14.4 Health, home and research

**HealthKit** — never show health data without explicit consent and a plain-language rationale; the Apple Health icon needs clear space of **1/10 of its height** and must not be composited onto another graphic.

**HomeKit** — get the vocabulary right: homes › rooms › zones › accessories, services, characteristics › scenes › automations. Accessory names may contain only alphanumerics, spaces and apostrophes, must start and end with an alphanumeric, and must not contain emoji.

**CareKit / ResearchKit** — CareKit views cover tasks, charts and contacts; research flows run **introduction → eligibility → informed consent → data permission**, with an exit always available. Surveys: state the number of questions and the expected time, **one question per screen**, show progress, keep each survey short (several short ones beat one long one), use a slightly smaller font for explanatory text, and confirm completion.

### 14.5 Intelligence

**Generative AI** — be transparent about what is generated and what it is based on; don't train on personal data without consent; disclose model limits; make outputs correctable and undoable; show confidence where it changes the decision; never fabricate authority or a citation; keep a human in the loop for destructive or high-stakes output.

**Machine learning** — decide five things before designing the UI: critical or complementary, private or public, proactive or reactive, visible or invisible, dynamic or static. Then support explicit feedback ("Suggest less…", "Mute for a week"), implicit feedback, calibration (ask for a few high-value facts, never for things people must look up), mistakes (anticipate, mitigate, learn), corrections, multiple options with confidence, attribution, and stated limitations.

**Siri and App Shortcuts** — expose top tasks with natural phrases, return answers in place where possible, and describe the action rather than the app.

### 14.6 Gaming and shared experiences

**Game Center** — access point or custom UI, achievements and leaderboards. Image specs: achievement **512×512 pt (1024 px @2x)** with a **512 pt (1024 px)** mask diameter; leaderboard **320×320 pt (640 px @2x)** with a **200 pt (400 px)** mask; activity image **659×371 pt (1318×742 px)**, focused 618×348, unfocused 548×309; wide activity **1920×1080 pt (3840×2160 px)** cropped to **1465×767 pt**; small banner **600×180 pt (1200×360 px)**. Formats PNG/TIF/JPG, sRGB or P3, **72 DPI minimum**.
- Classic leaderboards never reset; recurring leaderboards reset on an interval (daily, weekly, seasonal).
- Multiplayer: let players join late, leave and return; show the party code and allow manual entry.

**SharePlay** — shared activities need a clear "start together" affordance, personas for participants, and spatial templates that keep everyone's view coherent; handle late joiners and drop-outs without losing state.

### 14.7 Platform transitions and system integrations

**Mac Catalyst** — the default iPad idiom scales everything to **77%** (a 17 pt iPad baseline becomes 13 pt on the Mac). Choose the idiom deliberately, then adopt Mac navigation (split views over tab bars), the menu bar, keyboard and pointer behaviour, window management, inspectors instead of popovers, and Mac-sized layout.

**App Clips** — one focused task, small binary, no full-app navigation. The App Clip card image is **1800×1200 px**, PNG or JPEG, **no transparency**. Codes: printed diameter at least **3/4 inch (1.9 cm)**; digital at least **256×256 px** (PNG or SVG); an embedded NFC tag at least **35 mm**; scan-distance-to-size ratio no worse than **20:1** (**10:1** preferred); rasterize at **600 ppi** and print at **300 dpi**. Never gate the core task behind notifications, an account or the full app.

**CarPlay** — fixed resolutions **800×480 (5:3)**, **960×540 (16:9)**, **1280×720 (16:9)**, **1920×720 (8:3)**; icons **120×120 @2x / 180×180 @3x**. One glance, one tap: no keyboards where voice works, no long lists, no video, and always a clear error state.

**Maps** — the *default* style is fully saturated and matches the Maps app; *muted* desaturates so your content stands out. Overlays sit *above roads* (default) or *above labels*. Keep the Apple logo and legal link fixed while the map moves, with **7 pt of padding at the sides and 10 pt above and below**; they are hidden on maps smaller than **200×100 px**. Place cards: automatic, callout (full or compact), caption, sheet.

**iCloud** — sync without blocking the UI, show per-item status honestly, resolve conflicts understandably, and never use iCloud as a silent backup of data people think is local.

**NFC** — in-app tag reading needs a visible reason and an explicit scan; background reading surfaces a banner. Never require a scan where typing would do.

**Augmented reality** — coach placement, react to surfaces and lighting, allow multiuser sessions, handle interruptions and lost tracking, and never trap someone in an experience they can't exit.

---

## 15. Audit — run this before shipping or answering

Answer every line with **pass / fail / not applicable**, and for each fail name the fix.

**Purpose and structure**
1. Can the primary task be completed without reading documentation?
2. Is there exactly one obvious primary action per screen?
3. Does every screen have a clear entry, a clear exit, and a reachable back path?
4. Are secondary features discoverable without cluttering the first view?
5. Does the app show useful content immediately at launch?

**Layout**
6. Do all layouts use safe areas and layout margins rather than fixed offsets?
7. Do layouts adapt across compact/regular size classes, both orientations, and iPad multitasking?
8. Do layouts survive AX5 text without clipping, truncation or overlap?
9. Are controls in thumb reach (iOS) and within the field of view (visionOS, tvOS safe area)?
10. Are focus states designed and tested (tvOS), with spacing that prevents overlap on expansion?
11. Does background artwork scale without distortion, with background extension where needed?

**Typography**
12. Are all text styles system styles (or custom ones that scale)?
13. Is no text smaller than the platform minimum?
14. Is the hierarchy readable with at most one extra weight/color jump?
15. Are long strings localized and do layouts tolerate +30% length?

**Color and materials**
16. Are colors semantic and defined for light, dark and increased contrast?
17. Does every text/background pair hit 4.5:1 (or 3:1 for 18 pt/bold)?
18. Is Liquid Glass confined to the functional layer?
19. Is clear glass over bright media dimmed (~35%)?
20. Is color never the sole carrier of meaning?

**Accessibility**
21. Do all controls meet the minimum hit size and spacing?
22. Does VoiceOver produce a sensible, ordered reading of every screen, with labels and traits?
23. Is every gesture-only action available another way?
24. Do Voice Control, Full Keyboard Access and Switch Control work?
25. Are Reduce Motion, Reduce Transparency, Increase Contrast, Bold Text and Larger Text all honored?
26. Do media have captions/subtitles/transcripts where relevant, and are autoplaying media controllable?
27. Are flashing/animated effects safe for photosensitivity?

**Components**
28. Are tab bars used for navigation only, with labels, and never hidden or disabled?
29. Is there exactly one prominent button, and is it non-destructive?
30. Does every custom control have pressed, focused, disabled and selected states?
31. Are alerts reserved for critical, actionable situations with specific button titles?
32. Do sheets have Cancel/Close and Done (never all three of Cancel, Done and Back) and swipe-to-dismiss with unsaved-change confirmation?
33. Are list rows showing the right accessory (disclosure indicator for navigation, ⓘ for information)?
34. Do macOS windows avoid critical content at the bottom edge, and does the menu bar contain every command?
35. Do search fields show scope, suggestions and forgiving results?

**Content and writing**
36. Are button labels verbs, title case, and free of "OK"/"Yes"/"No" except where Apple allows?
37. Do error messages appear in place, avoid blame, and state the fix?
38. Are empty states explanatory and actionable?
39. Is "tap"/"click"/"select" used correctly per platform?
40. Is every permission requested in context with a stated benefit?

**Performance and polish**
41. Does the interface respond within one frame to touch/click, with no blocked animations?
42. Are loading states shown immediately, with determinate progress where possible?
43. Does motion explain change and respect Reduce Motion?
44. Do haptics and audio reinforce (not replace) visual feedback?
45. Is state restored after backgrounding, rotation, resize and relaunch?

---

## 16. How to report a design review

Use this shape so the output is actionable:

1. **Verdict** — one sentence: shippable as is, shippable with fixes, or blocked.
2. **Blocking issues** — numbered, each with: what violates Apple's guidance, the exact metric or rule, the file/screen where it appears, and the concrete fix.
3. **Should-fix issues** — same format, ranked by user impact.
4. **What is already right** — two or three lines; it tells the author what to preserve.
5. **Platform gaps** — anything designed for one platform that will break on another (Dynamic Type, RTL, tvOS focus, visionOS field of view, macOS menu bar).
6. **Open questions** — only where Apple's guidance depends on product intent you cannot infer.

Never write "improve spacing" or "make it cleaner". Write "the toolbar's primary action is 28 pt tall; raise it to 44 pt and keep 12 pt clear space around it".

---

## 17. Source map

This skill was distilled from a local scrape of the complete Human Interface Guidelines, 2026 edition:

- `chapters/INDEX.md` — the 173 chapters in reading order.
- `chapters/001-human-interface-guidelines.md` … `173-wallet.md` — full chapter text, with live URLs to Apple's site, images and videos intact.
- `ios-pathway/INDEX.md` — the companion Develop in Swift tutorial series (80 pages) covering the app design cycle, prototyping, testing and validation.

### 17.0 Chapter-to-section map

Every one of the 173 chapters appears in the table below, so nothing in the scrape is unmapped. Where a chapter's rules are split (for example charts, which are both a pattern and a component), the chapter is listed once, under its primary section.

| Section | Chapters |
|---|---|
| §0 orientation | 001 Human Interface Guidelines, 002 Getting started |
| §1 principles and branding | 003 Design principles, 015 Branding |
| §2 platform mental models | 004–011 iOS, iPadOS, macOS, tvOS, visionOS, watchOS, games, iPhone Duo |
| §3 layout | 012 Foundations, 022 Layout, 028 Spatial layout, 038 Going full screen, 045 Multitasking |
| §4 typography | 029 Typography |
| §5 color | 016 Color, 017 Dark Mode, 021 Inclusion, 026 Right to left |
| §6 materials, motion, haptics | 020 Immersive experiences, 023 Materials, 024 Motion, 049 Playing haptics |
| §7 icons, symbols, images | 014 App icons, 018 Icons, 019 Images, 027 SF Symbols |
| §8 accessibility | 013 Accessibility, 135 Eyes, 172 VoiceOver |
| §9 writing | 030 Writing |
| §10 components overview | 057 Components |
| §10.1 navigation and search | 073 Tab views, 087 Navigation and search, 088 Path controls, 089 Search fields, 090 Sidebars, 091 Tab bars, 092 Token fields |
| §10.2 content | 058 Content, 059 Charts, 060 Image views, 061 Text views, 062 Web views, 063 Layout and organization, 065 Collections, 068 Labels, 069 Lists and tables, 070 Lockups, 071 Outline views, 072 Split views |
| §10.3 actions | 074 Menus and actions, 075 Activity views, 076 Buttons, 077 Context menus, 078 Dock menus, 079 Edit menus, 080 Home Screen quick actions, 081 Menus, 082 Ornaments, 083 Pop-up buttons, 084 Pull-down buttons, 085 The menu bar, 086 Toolbars |
| §10.4 presentation | 093 Presentation, 094 Action sheets, 095 Alerts, 097 Panels, 098 Popovers, 099 Scroll views, 100 Sheets, 101 Windows |
| §10.5 selection and input | 102 Selection and input, 105 Digit entry views, 107 Pickers, 108 Segmented controls, 109 Sliders, 110 Steppers, 111 Text fields, 112 Toggles, 113 Virtual keyboards |
| §10.6 status and progress | 114 Status, 115 Activity rings, 116 Gauges, 117 Progress indicators, 118 Rating indicators, 126 Status bars |
| §10.7 specialised controls | 064 Boxes, 066 Column views, 067 Disclosure controls, 096 Page controls, 103 Color wells, 104 Combo boxes, 106 Image wells |
| §11 patterns | 031 Patterns, 032 Charting data, 033 Collaboration and sharing, 034 Drag and drop, 035 Entering data, 036 Feedback, 037 File management, 039 Launching, 040 Live-viewing apps, 041 Loading, 042 Managing accounts, 043 Managing notifications, 044 Modality, 046 Offering help, 047 Onboarding, 048 Playing audio, 050 Playing video, 051 Printing, 052 Ratings and reviews, 053 Searching, 054 Settings, 055 Undo and redo, 056 Workouts |
| §11.16 privacy | 025 Privacy |
| §12 system experiences | 119 System experiences, 120 App Shortcuts, 121 Complications, 122 Controls, 123 Live Activities, 124 Notifications, 125 Snippets, 127 Top Shelf, 128 Watch faces, 129 Widgets, 146 Always On |
| §13 inputs | 130 Inputs, 131 Action button, 132 Apple Pencil and Scribble, 133 Camera Control, 134 Digital Crown, 136 Focus and selection, 137 Game controls, 138 Gestures, 139 Gyroscope and accelerometer, 140 Keyboards, 141 Nearby interactions, 142 Pointing devices, 143 Remotes |
| §14 technologies | 144 Technologies, 145 AirPlay, 147 App Clips, 148 Apple In-App Purchase, 149 Apple Pay, 150 Augmented reality, 151 CareKit, 152 CarPlay, 153 Game Center, 154 Generative AI, 155 HealthKit, 156 HomeKit, 157 iCloud, 158 ID Verifier, 159 iMessage apps and stickers, 160 Live Photos, 161 Mac Catalyst, 162 Machine learning, 163 Maps, 164 NFC, 165 Photo editing, 166 ResearchKit, 167 SharePlay, 168 ShazamKit, 169 Sign in with Apple, 170 Siri, 171 Tap to Pay on iPhone, 173 Wallet |
| §17 sources | `chapters/` (this map) and `ios-pathway/` 004–015 for the design cycle: explore, ask questions, organize features, prototype, test, validate, iterate |

### 17.1 Figure provenance

Every figure in this file was checked against the chapter text during the November 2026 expansion pass. Where a number appears in more than one chapter (control sizes, minimum type sizes) the chapters agree, and the table below records the check.

| Figure group | Chapter(s) | Result |
|---|---|---|
| Control sizes 44/28, 28/20, 66/56, 60/28, 44/28 | 010, 013 | identical in both |
| Minimum text sizes 17/11, 13/10, 29/23, 17/12, 16/12 | 010, 013, 029 | identical in all three |
| Contrast 4.5:1 (≤17 pt), 3:1 (18 pt or bold), 7:1 target | 013, 017 | confirmed |
| 12 pt padding with bezel, 24 pt without | 013, 142 | confirmed twice |
| tvOS grids 2–9 columns, 40 pt / 100 pt | 022 | confirmed |
| tvOS safe area 60 pt top/bottom, 80 pt sides | 022 | confirmed |
| iOS Dynamic Type Large and AX5 rows | 029 | row-by-row match |
| macOS, tvOS, watchOS text styles | 029 | row-by-row match |
| Tracking anchors 11–96 pt; SF Rounded, New York, SF Compact | 029 | confirmed |
| 12 system colors, light and dark | 016 | confirmed |
| System grays 1–6 | 016 | confirmed |
| ~35% dimming under clear glass | 023 | confirmed |
| App icon sizes 1024, 800×480, 1088 | 014 | confirmed |
| Document icon ladder, 10% margin, 80% fill | 018 | confirmed |
| watchOS image autoscaling 90–119% | 019 | confirmed |
| tvOS tab bar 68 pt / 46 pt | 091 | confirmed |
| visionOS buttons 28/32/44/52/64 pt, 60 pt centers, 4 pt padding | 076 | confirmed |
| visionOS 16 pt / 60 pt item spacing | 028, 135 | confirmed |
| visionOS window 1280×720 pt at 2 m, ~3 m wide | 101 | confirmed |
| Immersion boundary 1.5 m, 120–360° | 020 | confirmed |
| macOS menu bar 24 pt; one help button per window | 085, 076 | confirmed |
| Alert limit of three buttons; visionOS accessory 154 pt / 16 pt | 095 | confirmed |
| Sheet detents large/medium, grabber | 100 | confirmed |
| Segmented 5–7 (5 on iPhone); tab view ≤6; default 5 tabs | 108, 073, 091 | confirmed |
| Activity icon 70×70 px; image button 10 px padding | 075, 076 | confirmed |
| Widget sizes, 16/11 pt margins, 11 pt minimum text | 129 | confirmed |
| Live Activity 8 h limit, 4 h on Lock Screen/Smart Stack, 14 pt margin, 28 pt circle | 123 | confirmed |
| Complication text and image sizes | 121 | confirmed |
| Top Shelf artwork sizes | 127 | confirmed |
| Apple Pay 100×30 / 140×30, 1/10 margins, 60×60 mark | 149 | confirmed |
| Sign in with Apple 140×30, 44 pt PNG, 1/10 margin | 169 | confirmed |
| Wallet pass image sizes, 300×300 merchant art | 173 | confirmed |
| iMessage sticker sizes 300/408/618; 1024 App Store icon | 159 | confirmed |
| App Clip card 1800×1200, code sizes, 20:1 ratio | 147 | confirmed |
| CarPlay resolutions and icons | 152 | confirmed |
| Game Center image specifications | 153 | confirmed |
| Mac Catalyst 77% scaling, 17 pt → 13 pt | 161 | confirmed |
| Maps 7/10 pt padding, 200×100 px threshold | 163 | confirmed |
| Video aspect thresholds, 160 px thumbnails, 0.5 s overlay delay, watch limits | 050 | confirmed |
| HomeKit naming rules, HealthKit 1/10 clear space | 156, 155 | confirmed |
| visionOS content at least 1 m away; hover-effect delay options | 135 | stated in prose, no numerals table |

Two figures could not be matched token-for-token because the chapters spell them out in words rather than numerals — the tvOS tab bar's *46 points* and the image button's *10 pixels* of padding. Both were confirmed by reading the sentence. Nothing in this file is a guess; if a number is not in the table above it came from the same chapters' prose and should be re-checked there before it ships in a spec.

When a detail here is not specific enough, open the chapter: it contains Apple's exact sentence, image and video reference. When this file and the live HIG disagree, the live HIG wins.
