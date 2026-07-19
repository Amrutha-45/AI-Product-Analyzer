# AI Product Analyzer — Implementation Roadmap

**Status:** Ready for build
**Depends on:** PROJECT_CONTEXT.md, ARCHITECTURE.md, DESIGN_SPEC.md, AI_PROMPT_SPEC.md
**Assumption:** ~48-hour hackathon window, 2 engineers (1 backend/AI-focused, 1 frontend-focused) working substantially in parallel, converging at defined integration points. If it's a solo build, treat the two tracks as sequential and roughly double the wall-clock time per sprint.

---

## How this roadmap is structured

Sprints are grouped into **parallel tracks** wherever the work genuinely doesn't depend on the other track's output, and merged into **single tracks** at real integration points. The single most important unlock for parallel work: **the frontend is built against the finalized `ScanResult` JSON schema from Sprint 0, using a mocked response, before the real backend is done.** This is what makes the two tracks genuinely parallel rather than frontend waiting on backend for two days.

```
Sprint 0  ─────────────────────────────  Setup (shared, blocking)
              │
    ┌─────────┴─────────┐
    ▼                     ▼
Sprint 1A               Sprint 1B
(Backend: AI core)      (Frontend: design system + shell)
    │                     │
    ▼                     ▼
Sprint 2A                Sprint 2B
(Backend: enrichment,    (Frontend: landing + upload,
 scoring, persistence)    built against mocked /scan)
    │                     │
    └─────────┬───────────┘
              ▼
         Sprint 3 — Integration
    (Processing + Results wired to REAL backend)
              │
              ▼
         Sprint 4 — Hardening
              │
              ▼
         Sprint 5 — Polish
              │
              ▼
         Sprint 6 — Demo Prep & Deploy
```

---

## Sprint 0 — Project Setup

**Goal:** A deployable "hello world" on both ends, with every config decision made now so no one is debugging environment issues on Day 2.

**Features:** N/A (infrastructure only)

**Tasks:**
- Initialize monorepo per the folder structure in Section "Folder Structure" below
- `frontend/`: Vite + React + Tailwind scaffold, deployed to Vercel with a placeholder page
- `backend/`: FastAPI scaffold with a working `GET /health`, deployed to Render/Railway
- Create Supabase project, capture connection details
- Set up `.env.example` on both ends; real secrets set directly in Vercel/Render dashboards, never committed
- Set up the GitHub Actions CI skeleton (lint/type-check on PR)
- Lock the `ScanResult` JSON schema from AI_PROMPT_SPEC.md as a literal file both tracks reference (`shared/scan-result.schema.json` or equivalent) — this is the contract that makes parallel work possible

**Deliverables:** Deployed frontend placeholder + deployed backend `/health` endpoint + Supabase project live + CI running on PRs.

**Acceptance Criteria:**
- Visiting the deployed frontend URL shows a page (not a 404)
- Visiting `<backend-url>/health` returns `{"status": "ok"}`
- A PR triggers CI and it passes
- Both engineers can run the full stack locally from a fresh clone in under 10 minutes

**Estimated Effort:** 3-4 hours

**Testing checkpoint:** Manual smoke test of both deployed URLs. This is the only sprint where "testing" just means "does it load."

---

## Track A (Backend/AI) — Sprint 1A: AI Core & Extraction Reliability

**Goal:** A working `/scan` endpoint that reliably returns a schema-valid `ScanResult` from real product photos.

**Features:** Image upload validation, Gemini vision integration, structured JSON extraction, schema validation.

**Tasks:**
- Implement `ScanResult`, `Ingredient`, `PackagingSignals` Pydantic models per AI_PROMPT_SPEC.md Section 4 (including the Sprint-relevant additions: `allergens`, `ai_suggested_improvement`, `overall_confidence`, `confidence_reasoning`)
- Implement `VisionProvider` abstract interface + `GeminiProvider` (already scaffolded in prior work — finalize and wire the System/Developer prompt text from AI_PROMPT_SPEC.md Sections 2-3)
- Implement `get_vision_provider()` factory + config-based provider selection
- Implement `POST /scan` route: accepts multipart images, validates mime/size/dimensions, calls the provider, validates the response, returns JSON
- Implement retry-once-on-validation-failure per the spec
- Collect 6-8 real product photos (varied: clear label, dense ingredient list, blurry back label) and iterate on the prompt against them until extraction is consistently reliable

**Deliverables:** `POST /scan` deployed and callable with real images, returning schema-valid JSON.

**Acceptance Criteria:**
- All 6-8 test product photos return a 200 with valid `ScanResult` JSON
- At least one deliberately blurry test image correctly produces `overall_confidence: "low"` with populated `confidence_reasoning`, not a crash or a false-confident guess
- A malformed/non-image file upload returns a clean 400, not a 500
- No hardcoded/mocked data anywhere in this path — every field genuinely comes from the model

**Estimated Effort:** 5-6 hours (this is the highest-risk sprint — budget the most slack here)

**Testing checkpoint:** Run all test images through the deployed endpoint and manually verify every field against the actual photo. This is the sprint most worth a second engineer's eyes before moving on, since prompt quality issues discovered here are cheap to fix now and expensive to discover during Sprint 3 integration.

---

## Track A — Sprint 2A: Enrichment, Scoring, Persistence

**Goal:** Real product grounding, deterministic trust scoring, and durable storage — the backend is now feature-complete.

**Features:** Open Food Facts enrichment, trust score computation, content-hash caching, Supabase persistence, history endpoint.

**Tasks:**
- Implement `openfoodfacts_service.py`: barcode lookup, category search for alternatives
- Implement merge logic: OFF data overrides AI-guessed `product_name`/`brand`/`ingredients` when a match exists; set `source: "openfoodfacts_merged"` accordingly
- Implement `trust_score_service.py`: deterministic scoring formula over `packaging_analysis` signals (document the formula in code comments — you'll need to explain it to judges)
- Implement `cache_service.py` + `utils/hashing.py`: content-hash lookup before calling Gemini
- Run the Supabase schema migration from ARCHITECTURE.md Section 5 (`products`, `scans` tables + indexes)
- Implement persistence: write scan results after response is computed (fire-and-forget, don't block the response on the DB write)
- Implement `GET /scans/{id}` and `GET /scans` (history, device-scoped, offset pagination)
- Implement rate limiting middleware (`slowapi`, per-IP on `/scan`)

**Deliverables:** Fully backend-complete API surface — all four endpoints from ARCHITECTURE.md Section 4 working against the real database.

**Acceptance Criteria:**
- Scanning a product with a recognizable barcode returns `source: "openfoodfacts_merged"` with real OFF data visible in the response
- Scanning the same image twice returns the second result near-instantly (cache hit, verify via logs/timing, not a second Gemini call)
- `GET /scans` returns the correct history for a given `X-Device-Id`, empty array for an unrecognized one
- Trust score is reproducible — same packaging signals always produce the same score
- Hitting `/scan` more than the rate limit in a short window returns 429, not a crash

**Estimated Effort:** 4-5 hours

**Testing checkpoint:** End-to-end test of the full backend pipeline via `curl`/Postman before frontend integration begins — every endpoint, every documented error case from ARCHITECTURE.md Section 4's error table.

---

## Track B (Frontend) — Sprint 1B: Design System & Shell

**Goal:** Every reusable UI primitive built once, styled per DESIGN_SPEC.md, before any page consumes them.

**Features:** Design tokens, core UI components, routing shell, layout.

**Tasks:**
- Configure Tailwind with the design tokens from DESIGN_SPEC.md Section 2 (colors, spacing, radius as theme extensions — not hardcoded hex values scattered through components)
- Build `components/ui/`: Button (primary/secondary/ghost + all states), Card (base + elevated), Chip, Badge, Input, Tooltip, Toast, Modal (stub, likely unused per design spec), Skeleton
- Build `components/layout/`: Navbar (sticky + scroll-condense behavior), Footer, PageShell
- Set up routing (`/`, `/scan`, `/processing`, `/results/:id`, `/history`) and `layouts/PublicLayout` / `layouts/DashboardLayout`
- Set up `context/ScanContext` and `hooks/useDeviceId`
- Set up `services/api/client.ts` (fetch wrapper) — pointed at the real backend URL from Sprint 0, ready to call real endpoints once they exist

**Deliverables:** A running app shell with working navigation and a fully built, storybook-able (even without literal Storybook — just a scratch page rendering every variant) component library.

**Acceptance Criteria:**
- Every button/card/chip/badge state from DESIGN_SPEC.md Section 5 is visually implemented and matches the color palette exactly
- Navigating between routes works, layout persists correctly
- No component in this sprint contains page-specific business logic — everything here is genuinely reusable

**Estimated Effort:** 5-6 hours

**Testing checkpoint:** Visual review against DESIGN_SPEC.md — literally check each component off against Section 5's table.

---

## Track B — Sprint 2B: Landing Page & Upload Flow (against mocked data)

**Goal:** A complete, navigable front-of-app experience, built against a hardcoded mock `ScanResult` so this sprint never blocks on backend completion.

**Features:** Landing page, upload dropzones with validation, mocked scan submission.

**Tasks:**
- Build the Landing Page per DESIGN_SPEC.md Section 4: nav, hero (with the floating mockup card — this can literally render the mocked score data), features grid, how-it-works, benefits, CTA, footer
- Build the Upload Page: dual dropzones, drag/drop + click-to-browse, client-side validation (type/size), image preview states, client-side compression util
- Wire the "Analyze Product" button to call `services/api/scanService.ts` — initially pointed at a mock/stub that returns a hardcoded `ScanResult` after a simulated delay, so the rest of the flow can be built without waiting on Sprint 2A
- Write all UX copy per DESIGN_SPEC.md Section 8 verbatim — don't leave placeholder lorem ipsum, the actual copy is already specified

**Deliverables:** Landing → Upload flow fully clickable end-to-end against mock data.

**Acceptance Criteria:**
- All empty/hover/filled/error dropzone states are implemented and visually correct
- Wrong file type and oversized file both show the correct inline error copy
- "Analyze Product" is disabled until both images are present, matches the specified enable animation
- Landing page matches the hierarchy and copy from DESIGN_SPEC.md Section 4

**Estimated Effort:** 5-6 hours

**Testing checkpoint:** Click through the entire flow on desktop and mobile viewport; verify every UX-writing string against DESIGN_SPEC.md Section 8 exactly.

---

## Sprint 3 — Integration (both tracks converge)

**Goal:** Replace every mock with the real backend. This is the sprint where the two tracks actually meet, and it should be treated as its own dedicated block of time, not an afterthought.

**Features:** Processing screen with real progress, Results Dashboard with real data, alternatives, history.

**Tasks:**
- Build the AI Processing Page: scan-line animation over the real uploaded image, step checklist driven by actual backend progress (short polling against `GET /scans/{id}` status, or an SSE stream if time allows — polling is the safer choice for a hackathon timeline)
- Build the Results Dashboard per DESIGN_SPEC.md Section 4's exact hierarchy: Product Card → Health Score (count-up) → Trust Score → AI Summary → Warning Chips → Ingredient Intelligence (flagged expanded / safe collapsed) → Alternatives (data-backed vs. general-suggestion tagged)
- Swap `scanService.ts` from the mock to the real `POST /scan` call
- Build the History Page (list + empty state) against `GET /scans`
- Remove all mock data paths once real integration is confirmed working

**Deliverables:** A fully working, end-to-end real product scan — upload real photos, see a real AI-generated dashboard.

**Acceptance Criteria:**
- A real product photo, uploaded through the actual UI, produces a Results Dashboard with correct, non-mocked data
- The processing checklist's timing genuinely reflects backend progress, not a fixed timer
- Flagged ingredients render expanded by default, safe ones collapsed, matching DESIGN_SPEC.md exactly
- Alternatives correctly show the "Data-backed" vs "General Suggestion" tag depending on whether OFF matched
- History page shows real past scans for the current device

**Estimated Effort:** 6-7 hours (the largest single sprint — this is where Results Dashboard, the most detailed screen in the design spec, actually gets built)

**Testing checkpoint:** Full end-to-end test with all 6-8 real product photos from Sprint 1A, now through the actual UI rather than curl. This is the point where AI_PROMPT_SPEC.md's Example 3 (blurry image) should be deliberately tested — confirm the low-confidence banner and partial-data UI actually render correctly, not just the happy path.

---

## Sprint 4 — Hardening

**Goal:** Every documented error case actually works when triggered through the real UI, not just in theory.

**Tasks:**
- Trigger and verify every error case from ARCHITECTURE.md Section 4 and AI_PROMPT_SPEC.md Section 6 through the actual frontend: oversized file, wrong file type, blurry image, no barcode, unsupported product, rate limit hit, network timeout
- Verify the retry-once-on-failure path actually recovers from a transient issue rather than just being theoretical
- Load-test lightly (a handful of concurrent requests) to catch obvious race conditions in the cache/persistence layer
- Confirm CORS is locked to the deployed frontend origin, not `*`
- Confirm no secrets are exposed in any client-side network request (check the browser network tab, not just the code)

**Deliverables:** A demo-safe app — nothing crashes or shows a broken/blank state under any tested failure condition.

**Acceptance Criteria:** Every row in the error-handling tables from ARCHITECTURE.md and AI_PROMPT_SPEC.md has been manually triggered and produces the specified UI behavior, not a console error or blank screen.

**Estimated Effort:** 3-4 hours

**Testing checkpoint:** This entire sprint *is* the testing checkpoint — treat it as a structured QA pass against the two error tables, item by item, not open-ended exploratory testing.

---

## Sprint 5 — Polish

**Goal:** The motion, accessibility, and responsive details that separate "functional" from "premium."

**Tasks:**
- Implement all motion specs from DESIGN_SPEC.md Section 6: page transitions, hover states, card entrance stagger, health score count-up/color interpolation, micro-interactions
- Responsive QA pass across desktop/tablet/mobile per DESIGN_SPEC.md Section 7 — actually resize a real browser window and a real phone, don't just trust the CSS
- Accessibility pass per DESIGN_SPEC.md Section 9: contrast check with a real tool (not eyeballing it), keyboard navigation through the entire upload → results flow, `prefers-reduced-motion` support, aria-labels on score rings
- Verify the ingredient "+N more" collapse threshold against a genuinely dense product (25+ ingredients), per the design spec's own self-critique in Section 10

**Deliverables:** A visually polished, accessible, responsive app matching DESIGN_SPEC.md in full.

**Acceptance Criteria:** Every item in DESIGN_SPEC.md Section 10's self-critique list has been explicitly re-checked and resolved, not just designed around on paper.

**Estimated Effort:** 4-5 hours

**Testing checkpoint:** A full click-through on an actual mobile device (not just devtools responsive mode) and a full keyboard-only click-through (no mouse) — both catch issues devtools simulation misses.

---

## Sprint 6 — Demo Prep & Deployment

**Goal:** Zero surprises on demo day.

**Tasks:**
- Final production deploy of both frontend and backend
- Smoke-test the actual deployed URL (not localhost) with all test product photos one more time
- Pick 3 final demo products: one clearly healthy, one clearly processed/flagged, one that exercises the low-confidence/blurry path deliberately — this mirrors AI_PROMPT_SPEC.md's three worked examples exactly, which is not a coincidence, use those as your demo script
- Record a backup demo video in case venue wifi fails
- Prepare answers to the two questions judges are most likely to ask, per prior discussions: "how do you calculate trust score" (point to the deterministic formula) and "are you detecting counterfeits" (no — confidence signal, not a verdict, state this proactively if it doesn't come up)

**Deliverables:** Deployed, demo-ready app + backup video + a rehearsed answer to the two hardest anticipated questions.

**Acceptance Criteria:** The live deployed URL, on a device you haven't tested on yet, successfully completes a full scan with no errors.

**Estimated Effort:** 3 hours

**Testing checkpoint:** One full run-through of the actual demo script, live, on the deployed URL, in front of a teammate acting as a skeptical judge.

---

## Folder/File Structure (finalized, pre-implementation)

This is the structure that should exist — even as empty files/folders — before Sprint 1 begins, so no engineer is making structural decisions mid-sprint:

```
ai-product-analyzer/
├── frontend/
│   └── src/
│       ├── assets/
│       ├── components/{ui,layout,landing,scan,processing,results}/
│       ├── pages/
│       ├── layouts/
│       ├── hooks/
│       ├── services/api/
│       ├── context/
│       ├── constants/
│       ├── types/
│       ├── utils/
│       └── styles/
├── backend/
│   └── app/
│       ├── routes/
│       ├── controllers/
│       ├── services/{vision_providers/}
│       ├── prompts/
│       ├── schemas/
│       ├── models/
│       ├── db/
│       ├── middleware/
│       ├── utils/
│       └── core/
├── shared/
│   └── scan-result.schema.json      # the contract both tracks build against
├── docs/
│   ├── PROJECT_CONTEXT.md
│   ├── ARCHITECTURE.md
│   ├── DESIGN_SPEC.md
│   ├── AI_PROMPT_SPEC.md
│   └── IMPLEMENTATION_ROADMAP.md    # this document
├── prompts/
│   └── extraction_prompt_v1.md
├── assets/brand/
└── .github/workflows/ci.yml
```

(Full per-file breakdown of `frontend/` and `backend/` is already specified in ARCHITECTURE.md Sections 2-3 — not repeated here to avoid drift between two copies of the same tree.)

---

## Reusable Components & Shared Utilities

Building these once, correctly, in Sprint 1 is what prevents rework in Sprints 3-5:

**Frontend:**
- `ui/Card` (base + elevated) — reused by every dashboard card, the product card, and the alternatives cards
- `ui/Chip` / `ui/Badge` — reused by ingredient flags, warnings, status badges, and the data-backed/general-suggestion tag
- `hooks/useCountUpAnimation` — reused by both Health Score and Trust Score rings
- `utils/scoreColor.ts` — the red/amber/green interpolation function, reused anywhere a score needs color, so the mapping is defined exactly once
- `services/api/client.ts` — the single fetch wrapper every service module uses, so auth headers/error handling only need to be correct in one place

**Backend:**
- `VisionProvider` abstraction — already built, the entire point of Sprint 1A is exercising this correctly so Sprint 2A's OFF merge logic can trust its output shape unconditionally
- `utils/image_validation.py` — reused identically by the `/scan` route regardless of which provider is configured
- `utils/hashing.py` — reused by both the cache check and (if added later) deduplication logic
- `middleware/error_handler.py` — one global handler so every route returns errors in the same JSON shape, which the frontend's error-toast logic depends on being consistent

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Gemini extraction quality inconsistent on real-world photos | Medium-High | High | Front-loaded in Sprint 1A specifically so there's runway to iterate on the prompt before it blocks other sprints; test against genuinely varied photos, not just one clean example |
| Frontend blocked waiting on backend | Medium | High | Mitigated structurally — Sprint 2B builds against mocked data using the locked schema from Sprint 0, never blocks |
| Results Dashboard (Sprint 3) is the largest single sprint and overruns | Medium | Medium | It's explicitly budgeted as the largest sprint; if it overruns, the first thing to cut is the History page (Sprint 3's lowest-priority item), not any Results Dashboard content |
| Demo-day API rate limits or quota exhaustion | Low-Medium | High | Caching (Sprint 2A) directly mitigates repeat-scan cost; rate limiting protects against accidental abuse; test with the deployed URL, not just localhost, before demo day |
| Ingredient hallucination or an inappropriate high-risk flag on a real product during the live demo | Low | High | Pre-testing with the actual 3 demo products (Sprint 6) specifically to catch this before it happens live — never demo with a product that hasn't been pre-tested |
| Deployment platform cold-start latency makes the first demo scan slow | Medium | Medium | Do a "warm-up" scan immediately before the live demo starts, not as the first thing judges see |
| Team runs out of time before Sprint 5 (Polish) | Medium | Medium | Every sprint's acceptance criteria are independently demo-viable — an app that's fully functional but less animated (stopped after Sprint 4) is a legitimate fallback demo, not a failure |

---

## Final Implementation Timeline (48-hour hackathon)

| Block | Time | Sprint(s) |
|---|---|---|
| Day 1, AM | 0:00–3:30 | Sprint 0 (both engineers together) |
| Day 1, mid-morning → afternoon | 3:30–9:30 | Sprint 1A (backend) ‖ Sprint 1B (frontend), parallel |
| Day 1, evening | 9:30–14:30 | Sprint 2A (backend) ‖ Sprint 2B (frontend), parallel |
| Day 1, night → Day 2 early AM | 14:30–15:00 | Buffer / sleep break |
| Day 2, AM | 15:00–22:00 | Sprint 3 — Integration (both engineers together) |
| Day 2, midday | 22:00–26:00 | Sprint 4 — Hardening |
| Day 2, afternoon | 26:00–31:00 | Sprint 5 — Polish |
| Day 2, evening | 31:00–34:00 | Sprint 6 — Demo Prep & Deploy |
| Remaining | 34:00–48:00 | Slack / sleep / rehearsal buffer |

This leaves roughly 14 hours of slack across the full 48-hour window, which is deliberate — hackathon estimates that assume zero slippage are the single most common cause of a rushed, broken demo. If Sprint 1A (the highest-risk sprint) runs long, pull from this buffer first before compressing Sprint 5 (Polish) or Sprint 4 (Hardening) — a less-animated but reliable app beats a beautiful one that crashes on stage.
