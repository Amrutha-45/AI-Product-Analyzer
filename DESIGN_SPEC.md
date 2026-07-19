# AI Product Analyzer — UI/UX Design Specification

**Status:** Design phase, ready for frontend implementation
**Depends on:** PROJECT_CONTEXT.md, ARCHITECTURE.md

---

## 1. Brand Identity

**Logo concept**
A rounded-square app-icon mark: a single diagonal gradient scan-line crosses a simplified product silhouette, and the negative space where the line exits forms a subtle checkmark. It should read as "verification," not "magnifying glass" — a magnifying glass implies detective/counterfeit-hunting, which contradicts the "we are not a counterfeit detector" product decision. A scan-line implies *analysis in progress*, which is the honest story.

Wordmark: "AI Product Analyzer" set in a geometric sans (Inter/Geist), tight tracking, sentence case rather than all-caps (all-caps on a long descriptive name reads shouty). Treat "AI" in the accent green, set in the monospace face — a small typographic signal that repeats the "AI = precise/technical" association everywhere the wordmark appears, including in headers and loading states.

**Tagline** — three options, recommendation marked:
-  *"Know what you're actually buying."* — plainest, most honest, matches the product's non-hype positioning
- *"See past the label."* — more evocative, slightly more marketing-forward
- *"Understand before you buy."* — safest, most literal, least memorable

Recommend the first — it's the one a judge would repeat back to a teammate, which is the actual bar for a good tagline.

**Brand personality**
Precise, calm, quietly confident. Never alarmist (a "10/10 DANGER" red-flashing UI would undercut the "not a counterfeit detector, not a fearmongering app" positioning). Think: a well-designed lab report, not a security alarm. The brand should feel like it respects the user's ability to make their own decision — it presents evidence, not verdicts.

**Design language**
Dark canvas, glass surfaces, restrained motion, one accent color carrying all "trust/positive" signaling so it's never diluted. No mascots, no illustrations of cartoon food or shopping carts — that reads as consumer-app-cute, working against the "premium AI tool" positioning. Iconography stays strictly line-based.

**Visual identity**
- Consistent 1.5–2px stroke line icons (Lucide-style), never filled/solid icons except inside colored badges where fill communicates status
- Photography (if any — e.g. hero mockups) always shows real product packaging shots, never stock "person holding phone" imagery
- Every screen keeps the same dark base + glass surface treatment — no screen should suddenly go light or flat, consistency is the premium signal

---

## 2. Design System

### Color Palette
| Token | Value | Use | Why |
|---|---|---|---|
| `bg-base` | `#0B0D12` | App background | Near-black, not pure black — pure black against white text causes halation/eye strain; this off-black is easier to sit with for a full dashboard read |
| `surface-glass` | `rgba(255,255,255,0.04)` fill + `blur(20px)` | Card backgrounds | The glassmorphism layer; low opacity keeps it subtle rather than "frosted bathroom glass" |
| `border-hairline` | `rgba(255,255,255,0.08)` | Card/input borders | Defines edges without a hard line — cards should feel like they're floating, not boxed |
| `accent-primary` | `#00E5A0` (electric green) | Primary actions, "safe" signal, brand accent | One accent only — blue is the exhausted default for every AI product; green also does double duty as the "safe" semantic color, reinforcing trust visually every time it appears |
| `risk-safe` | `#00E5A0` | Safe ingredient indicators | Same as accent — safe = brand color = "this is the good state" |
| `risk-moderate` | `#FFB020` (amber) | Moderate risk | Standard amber, universally read as caution |
| `risk-high` | `#FF4D4F` (red) | High risk | Reserved *only* for genuinely flagged items — never used decoratively, so it retains urgency |
| `text-primary` | `#F5F5F7` | Headlines, primary content | Off-white, not pure white — softer on a dark background |
| `text-secondary` | `#9CA3AF` | Supporting text, captions | Muted enough to create hierarchy without disappearing |
| `text-tertiary` | `#6B7280` | Disabled/placeholder | Lowest-emphasis tier |

### Typography
- **UI face:** Inter or Geist — geometric, neutral, excellent at small sizes for dashboard density
- **Data face:** JetBrains Mono — used *exclusively* for numbers that represent extracted/measured data: scores, barcodes, dates, batch numbers. This is a deliberate signal: mono type = "this came from data," sans = "this is UI chrome." Once a user learns this pattern (in seconds, unconsciously), it reinforces trust in the data-backed fields.
- **Scale:** Display 40px/48px (landing hero only) → H1 32px → H2 24px → H3 18px → Body 15px → Caption 13px. Tight but not extreme line-height (1.15 for headings, 1.5 for body) — dashboards need density, marketing sections need air, so the two contexts use different vertical rhythm even with the same type scale.

### Spacing System
4px base unit: 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64. Cards use 24px internal padding minimum — glassmorphism reads as premium specifically when content has room to breathe against the blurred surface; cramped glass panels look like a bug, not a style.

### Border Radius
- Large surfaces (cards, panels, modals): **20–24px** — this is the single biggest lever for "premium Vercel-feel" vs. "generic dashboard feel"
- Buttons: **12px**
- Inputs: **14px**
- Chips/badges: **fully rounded (pill)** — small status elements read faster as pills than as slightly-rounded rectangles

### Shadows
Standard black drop-shadows are nearly invisible on a `#0B0D12` background — don't use them as the primary depth cue. Instead:
- Depth comes from the glass fill + hairline border, not shadow
- Interactive elements use a **colored glow** on hover/focus (`box-shadow: 0 0 24px rgba(0,229,160,0.15)`) — this reads as "premium AI product" far more than a gray drop-shadow ever will on dark backgrounds

### Cards
Two elevation states only — resist adding a third, it dilutes the signal:
- **Base:** glass fill, hairline border, no glow
- **Elevated (hover/active):** fill brightens slightly (`rgba(255,255,255,0.06)`), border brightens, subtle accent glow appears

### Buttons
- **Primary:** solid `accent-primary` fill, dark text (`#0B0D12`) for contrast — accent-on-dark-background reads as a highlight, but accent-with-dark-text-on-top is what makes it feel like a physical, pressable object rather than a colored label
- **Secondary:** glass fill + hairline border, text in `text-primary`
- **Ghost:** text-only, no fill, used for tertiary actions ("Skip", "Cancel")
- States: hover (brighten + glow), active (scale 0.98, instant), disabled (40% opacity, no hover response), loading (label replaced by a small spinner, button width locked to prevent layout shift)

### Inputs
Dark glass fill, hairline border, `text-primary` value text, `text-tertiary` placeholder. Focus state: border shifts to `accent-primary` + a soft glow ring — never rely on the browser's default blue focus ring, it will visually clash with the whole palette.

### Icons
Lucide (or equivalent) line icon set exclusively. 20px default, 24px for primary nav/section headers. Inherit `currentColor` so icons always match their text context, except semantic risk icons which carry their own fixed color regardless of surrounding text color.

### Badges
Small pill, low-opacity color fill matching semantic meaning + full-opacity text in the same hue (e.g. `Valid` badge: `rgba(0,229,160,0.12)` fill, `#00E5A0` text). Used for: product status (Valid/Expired/Unclear), data source (Data-backed/AI Estimate).

### Chips
Ingredient warning chips: pill, colored border + low-opacity fill by risk level, small icon + label, tappable to expand/collapse the full explanation beneath.

### Progress Indicators
- **Score rings** (circular, `stroke-dasharray` animated) for Health Score and Trust Score — magnitude data gets a ring, always
- **Step checklist** (not a percentage bar) for AI processing — a percentage bar implies false precision about an LLM call's progress; a checklist of real named steps feels more honest and more "intelligent system," and doubles as a way to communicate *what* the AI is doing, which builds trust

### Charts
Deliberately minimal — this product's value is explanation, not data visualization. The only chart-like elements are the two score rings. Resist the urge to add a nutrient bar chart or radar chart "for polish" — an extra unfamiliar chart type near launch is more likely to need last-minute debugging than to add real demo impact.

### Score Components
- **HealthScoreRing:** large (120–160px), animated count-up 0→value over ~900ms, ring color interpolates along the safe→moderate→high gradient as it lands, one-line AI reasoning beneath in `text-secondary`
- **TrustScoreCard:** smaller, numeric badge + 2–3 line bullet list of the actual signals behind it (barcode valid, text clarity, etc.) — this is the card that carries the "confidence signal, not a guarantee" framing, stated explicitly in a caption, every single time it's shown

---

## 3. User Journey

```
Landing Page
   │  CTA: "Analyze a Product"
   ▼
Upload Page
   │  Drop/select front image → live preview
   │  Drop/select back image → live preview
   │  Both present → "Analyze Product" activates
   ▼
AI Processing Page
   │  Real backend progress drives step checklist
   │  (Reading → Extracting → Analyzing → Generating)
   │  On completion → auto-navigate, no manual "continue" click
   ▼
Results Dashboard
   │  Health Score ring animates in (count-up)
   │  AI Summary fades in
   │  Ingredient cards stagger in (flagged expanded, safe collapsed)
   │  User can: expand/collapse any ingredient
   │            tap "?" on Trust Score for signal breakdown
   │            scroll to Alternatives
   │            tap "Save Scan" → toast confirmation, added to History
   │            tap "Scan Another" → returns to Upload Page, state reset
   ▼
(optional) History Page
   │  List of past scans (device-scoped), tap any → Results Dashboard
```

**Every interaction, mapped:**
- Landing CTA click → route to `/scan`, no modal/interstitial
- File drop/select → immediate client-side validation → preview or inline error, no page reload
- Both images present → primary CTA transitions from disabled (grey, helper text) to active (accent fill, subtle bounce-in) — this transition itself is a satisfying micro-confirmation that the user did the right thing
- Analyze click → immediate navigation to Processing page (don't block on the same page with a spinner — a full page dedicated to processing sets the expectation that this takes a moment, which reduces perceived wait vs. a spinner on the upload page)
- Processing complete → auto-navigate to Results (no "View Results" button — a manual click here adds friction with zero benefit)
- Ingredient card tap → expand/collapse in place (accordion), never a modal — keeps the user's scroll position and mental model intact
- Trust Score "?" tap → tooltip/popover with the signal list, not a full modal — this is supporting detail, not a new screen's worth of content
- Save Scan → optimistic UI (button shows "Saved" immediately) + toast, backend write happens async
- Error at any step → inline, in-context message + retry action, never a dead-end page

---

## 4. Screen-by-Screen Design

### Landing Page

**Navigation:** Sticky, glass surface, transparent at page top and gaining blur+fill as the user scrolls past ~80px (subtle, not jarring). Logo left, two text links center-right ("How it Works", "About"), primary CTA button far right ("Analyze a Product"). On mobile, links collapse into the CTA only — cut the hamburger menu entirely, this app has almost no navigation depth, don't manufacture the need for one.

**Hero:** Left-aligned headline (the tagline or a close variant, large display type), one-sentence subheadline explaining the mechanism ("Upload a photo of any product and get an instant, plain-language breakdown of what's really in it"), primary CTA button. Right side: a floating glass mockup card showing a *real-looking* partial results view (a Health Score ring mid-animation, one ingredient chip) — this single element does more to communicate the product than any amount of hero copy, because it shows rather than tells.

**Features:** 3–4 card grid, each with an icon, short title, one-sentence description. Recommended set: *Ingredient Intelligence* (plain-language explanations), *Health Score* (one number, real reasoning), *Packaging Trust Signals* (confidence, not guesswork), *Smart Alternatives* (data-backed suggestions when available). Keep each description under 15 words — feature grids fail when they turn into paragraphs.

**How It Works:** Horizontal 3-step flow (Upload → Analyze → Understand), connected by a thin line, each step numbered and iconified. This section exists specifically to pre-empt the "wait, how does this actually work" hesitation before the CTA — keep it visual-first, minimal text.

**Benefits:** A short list reframing value in user terms, not feature terms: "No signup required", "Results in seconds", "Plain language, not chemistry jargon". This section directly defuses friction objections (signup, speed, complexity) before they become reasons not to click.

**CTA (repeat):** Full-width glass panel, headline + button, positioned right before the footer — standard, effective, don't over-design this section.

**Footer:** Minimal — logo, 2–3 links, and a single-line disclaimer: *"AI Product Analyzer provides AI-generated informational insights and does not guarantee product authenticity or replace professional medical or safety advice."* This line matters more than it looks like it does — it's the plain-English version of the guardrails already locked into the product decisions, and it protects the credibility of the whole app.

**Hierarchy logic:** headline → CTA → visual proof (the mockup card) → scroll-driven trust-building (features → how it works → benefits) → second CTA chance. The visual proof appearing *before* any explanation is deliberate — people believe a screenshot faster than they believe copy.

---

### Upload Page

Two dropzones, side-by-side on desktop/tablet, stacked on mobile — labeled clearly "Front of Product" and "Back of Product" (the back one should note "Where ingredients are usually listed" as a hint, since users may not intuitively know why both are needed).

**States per dropzone:**
- **Empty:** dashed hairline border, centered icon + "Drop image here or click to browse", small example thumbnail illustrating good framing (flat, well-lit, text readable) — this single visual hint measurably improves input quality, which measurably improves AI extraction quality
- **Drag-over:** border shifts to `accent-primary`, background lightens slightly — clear, immediate feedback that the drop target is live
- **Filled:** dropzone replaced by the actual image thumbnail, small "×" remove button top-right, subtle checkmark badge bottom-right confirming it's ready
- **Error:** border shifts to `risk-high` red, inline message directly beneath *that* dropzone only (e.g. "File too large — please use an image under 8MB") — never a page-level toast for a field-level problem, the user needs to know exactly which image failed

**Primary CTA:** "Analyze Product" — disabled/grey with helper text ("Upload both images to continue") until both dropzones are filled, then activates with a brief scale bounce (180ms) to mark the state change clearly.

---

### AI Processing Page

Centered glass panel. The uploaded front image is shown, with a thin gradient scan-line sweeping top-to-bottom on a continuous loop — using the *real* uploaded image (not a generic illustration) keeps the moment grounded in what the user actually submitted, which reads as more "real AI happening" than an abstract animation would.

Below the image: a 4-item step checklist — *Reading Product* → *Extracting Ingredients* → *Analyzing Health* → *Generating Report*. Each step: dimmed/grey while pending, a pulsing dot while active, an animated checkmark draw-in on completion. **These steps must be driven by real backend signals** (lightweight polling or SSE), not a fixed timer — a fake progression is the single fastest way to make an AI product feel fraudulent the moment a judge notices the timing doesn't vary with actual load.

A small rotating caption beneath the checklist ("Analyzing ingredient safety using AI vision…") gives the eye something to read during the wait without overpromising specific progress.

---

### Results Dashboard

This is the most important screen — the layout below is intentionally ordered as **answer → context → evidence → action**, not as a flat grid of equally-weighted cards.

1. **Product Card** (thin top strip) — thumbnail, product name, brand, category, status badge (Valid/Expired/Unclear). Small, functional, oriented — this is context, not the point of the screen.
2. **Health Score** (hero) — large ring, count-up animation, one-line plain-language reasoning directly beneath. This is the first thing the eye lands on and the first thing a user will screenshot.
3. **Packaging Trust Score** (secondary, visually smaller than Health Score) — ring/badge + short signal list + the explicit "confidence signal, not a guarantee" caption, every time, no exceptions.
4. **AI Summary** — 2–3 sentence plain-language synthesis sitting directly under the two scores, functioning as the "answer" a user reads before deciding whether to scroll further.
5. **Warning Chips** — a horizontal row of the top-level flags (High Sugar, Contains Palm Oil, etc.), positioned as a scannable strip above the full ingredient list, so a user in a hurry gets the headline risks in under 2 seconds without reading a single ingredient card.
6. **Ingredient Intelligence** (hero content section) — flagged ingredients rendered as expanded cards by default (name, risk level, plain-language explanation visible immediately); safe ingredients collapsed into a compact chip row with a "+N more" pattern once past ~8 chips, expandable on tap. This is the deep-dive section and should have the most generous spacing of anything on the page.
7. **Healthier Alternatives** — card row (horizontal scroll on mobile), each card tagged either "Data-backed" (from Open Food Facts, real product name) or "General Suggestion" (AI category-level advice, no named brand) — the tag is not optional, it's the honesty mechanism agreed on earlier.
8. **Confidence Level** — deliberately *not* a separate section; folded into the Trust Score card as a sub-label. A third standalone number on this screen would dilute the two that actually matter.

**Information hierarchy principle, stated plainly:** big emotional number first (Health Score), immediate context second (Summary), full evidence third (Ingredients), next action last (Alternatives). This is the same "answer, then sources" pattern established for individual ingredient cards, just applied at the whole-screen level — the dashboard should feel like one consistent design idea repeated at two scales, not two different ideas stitched together.

---

## 5. Component Library

| Component | Behavior |
|---|---|
| **Navbar** | Sticky, transparent→glass on scroll, condenses height slightly past 80px scroll |
| **Button** (primary/secondary/ghost) | See Design System states; loading state locks width to prevent layout shift |
| **Upload Card** (dropzone) | Empty/drag-over/filled/error states as specified above; keyboard-accessible (Enter/Space opens file picker) |
| **Product Card** | Static display, no interaction beyond the thumbnail (no click-to-zoom in MVP — cut for scope) |
| **Score Card** (ring-based) | Animates in via IntersectionObserver so it replays if the user scrolls it into view fresh (e.g. returning from an ingredient expand) |
| **Warning Card/Chip** | Tappable, toggles an inline expansion beneath it; icon + label always visible even before expansion, never relies on color alone |
| **Ingredient Chip** (collapsed) → **Ingredient Detail Card** (expanded) | Single component with two visual states, animated height transition between them (not a hard cut) |
| **Recommendation Card** | Static, with the source tag (Data-backed/General) always visible, no interaction beyond an optional external link if OFF data included one |
| **Modal** | Reserved for rare, deliberate interruptions only — MVP has essentially none (image preview zoom could use one if time allows, otherwise cut) |
| **Toast** | Bottom-right, auto-dismiss ~4s, used for background confirmations (Save Scan) and non-blocking errors, never for primary flow errors (those are inline) |
| **Loading Skeleton** | Glass-shimmer placeholders matching the exact shape of the card they'll become — used only if a screen has to fetch after initial paint (e.g. History page) |
| **Tooltip** | Triggered by a small "?" icon, used for Trust Score signal breakdown and any score's methodology |
| **Progress Bar** | Used only for file-read progress on Upload; the Processing page deliberately uses the step-checklist pattern instead, never a percentage bar |

---

## 6. Motion Design

- **Page transitions:** fade + 8px upward slide, ~220ms ease-out, applied consistently on every route change — consistency here matters more than cleverness
- **Hover effects:** cards lift 2–4px + border/glow brighten; buttons scale to 1.02; both under 150ms so they read as responsive, not sluggish
- **Upload animation:** dropzone border pulses gently on drag-over; on successful drop, the empty-state icon morphs into a checkmark rather than hard-cutting to the thumbnail
- **AI scan animation:** scan-line sweep, continuous loop, paired with a very subtle grid/particle shimmer in the background of the processing panel — ambiance only, never the primary progress signal (the checklist is)
- **Health score count-up:** numeric tween 0→value over ~900ms (easeOutExpo — fast start, settles gently), ring stroke-dasharray animates in lockstep, ring color interpolates through the safe→moderate→high gradient stops as the value lands, so the color and the number arrive at their final state together
- **Card entrance animations:** staggered fade+slide-up, ~60–80ms stagger per card, triggered by IntersectionObserver so below-the-fold content animates on scroll rather than all firing at mount (which would feel chaotic on a content-dense dashboard)
- **Micro-interactions:** expand chevrons rotate 180° on toggle; a "Saved" state briefly replaces the Save button label with a checkmark before settling

**Governing principle:** every animation must communicate a state change — loading, success, error, expansion. None should be purely decorative. This is what separates "premium" motion from "distracting" motion, and it's the test to apply before adding any new animation during implementation.

---

## 7. Responsive Design

- **Desktop (≥1024px):** Full dashboard layout as specified; ingredient cards in a 2-column grid where space allows; upload dropzones side-by-side.
- **Tablet (768–1023px):** Single-column dashboard (cards full-width, stacked in the hierarchy order above); upload dropzones remain side-by-side down to ~600px, then stack.
- **Mobile (<768px):** Everything single-column. Health Score ring shrinks proportionally but stays full-width and remains the visual anchor of the screen. Alternatives become a horizontal-scroll carousel rather than wrapping. Nav collapses to logo + single CTA (no hamburger, per the earlier note — there's nothing to hide). Upload page gets a sticky bottom CTA bar once both images are present, so the primary action stays within thumb reach without requiring a scroll back up.

---

## 8. UX Writing

**Buttons**
- Primary CTA (landing): "Analyze a Product"
- Upload page (inactive): "Analyze Product" *(helper text beneath: "Upload both images to continue")*
- Upload page (active): "Analyze Product"
- Results: "Save Scan", "Scan Another"
- Retry: "Try Again"

**Upload instructions**
- Front dropzone: "Drop the front of the product here, or click to browse"
- Back dropzone: "Drop the back here — this is usually where ingredients are listed"

**Loading messages** (processing steps)
- "Reading product…"
- "Extracting ingredients…"
- "Analyzing health impact…"
- "Generating your report…"

**Warnings**
- "This product is high in added sugar."
- "Contains preservatives some people choose to avoid."
- "We couldn't fully verify the expiry date from this image — try a clearer photo of the back label."

**Success messages**
- "Scan saved." *(toast)*
- "Analysis complete." *(rarely shown as text — usually implied by the auto-navigation to Results)*

**Error messages**
- Upload, wrong file type: "Please upload a JPG, PNG, or WEBP image."
- Upload, file too large: "This image is over 8MB — try a smaller photo."
- Analysis failure: "We couldn't analyze this image. A clearer, well-lit photo usually helps — want to try again?"
- Network/timeout: "That took longer than expected. Please try again."

**Empty states**
- History page, no scans yet: "You haven't analyzed any products yet. Your scan history will show up here."
- Alternatives, no data-backed match found: "We couldn't find a verified alternative for this specific product, but here's a general tip:" *(followed by the category-level AI suggestion)*

**Tone throughout:** plain, warm, never clinical-cold and never hype-y. No exclamation points on error states. No "Oops!" — treat the user like a capable adult who wants information, not reassurance theater.

---

## 9. Accessibility

- **Contrast:** verify all text-on-glass combinations meet WCAG AA (4.5:1 body, 3:1 large text) against the actual composited background, not just against `#0B0D12` — glass blur + low-opacity fills can quietly drop contrast below the base color's numbers
- **Score rings:** must carry an `aria-label` stating the value in words ("Health Score: 4.5 out of 10"), not rely on the visual ring alone — screen reader users get nothing from an SVG arc
- **Color independence:** risk level is never communicated by color alone — every risk chip pairs color with an icon and a text label ("High Risk", not just a red dot)
- **Keyboard navigation:** upload dropzones are focusable and operable via Enter/Space; ingredient card expand/collapse is a real `<button>`, not a `<div>` with a click handler, so it's keyboard- and screen-reader-operable by default
- **Focus states:** visible accent-colored focus rings everywhere — never suppress the default outline without replacing it, and never use the browser default blue, which will clash with the palette
- **Reduced motion:** respect `prefers-reduced-motion` — disable the count-up tween and scan-line loop, replace with instant/near-instant state changes; this isn't optional polish, some users have vestibular conditions triggered by exactly this kind of motion
- **Live regions:** the processing checklist's step completions should be announced via `aria-live="polite"` so screen reader users get the same sense of progress sighted users get visually
- **Touch targets:** minimum 44×44px for every tappable element on mobile, including the ingredient chip expand targets

---

## 10. Final Review — self-critique before implementation

**Score fatigue risk.** Health Score, Trust Score, and Confidence Level as three separate numbers would overwhelm the hero section and dilute the impact of the one number that matters most (Health Score). Fixed by folding Confidence into the Trust Score card as a sub-label rather than a third standalone element — worth re-checking during implementation that this discipline holds and a fourth "score" doesn't creep in later.

**Glassmorphism contrast risk.** Heavy blur-and-transparency treatments are a common way dark-theme dashboards accidentally fail contrast checks. The mitigation here — reserving true glass blur for card *backgrounds* only, and keeping all text on a sufficiently opaque layer above it — needs to be verified with an actual contrast checker against the composited render, not assumed from the token values alone.

**Ingredient wall-of-chips risk.** A product with 25+ ingredients could turn the safe-ingredient chip row into an overwhelming block. The "+N more" collapse pattern at ~8 chips handles this, but this threshold should be sanity-checked against a real dense-ingredient product (e.g. a packaged snack) before the demo, not just a simple product with 6 ingredients.

**Processing animation overstaying its welcome.** If the real backend pipeline ever takes longer than ~8–10 seconds (e.g. a cold-start on the hosting platform), a looping scan-line animation with no percentage indicator can start to feel like it's stuck rather than working. Worth adding a soft fallback: if a single step is active for more than ~6 seconds, the rotating caption line should shift to something like "Still working — complex labels can take a little longer," so the user gets a signal that things are progressing even without a step change.

**Alternatives section blank-state honesty.** Originally this section risked either fabricating a specific alternative (rejected earlier for hallucination risk) or awkwardly disappearing when no data-backed match exists. The explicit empty-state copy ("We couldn't find a verified alternative for this specific product, but here's a general tip") is the fix — it's worth confirming during build that this state is actually tested, since it's easy to only ever demo with products that *do* have a match and never notice the empty state looks broken.

**No light theme.** Deliberately dark-only for MVP — a light theme would roughly double the design and QA surface for a hackathon timeline, and dark is core to the brand identity here, not an interchangeable preference. Flagging this as a known limitation rather than an oversight: if a judge happens to view the deployed link in a context that fights the dark UI (e.g. an unusually bright room via a projector), that's an accepted tradeoff for this timeline, not a bug to chase.

---

This specification is written to be handed directly to implementation — every screen, component, and state above has enough detail to build from without further design decisions needing to be made mid-development.
