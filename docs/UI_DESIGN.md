# UI design

Fixed by Nour's roadmap: "A live map of your services. Each request travels as a light along the roads, and a slow road turns amber." Quality bar: "jaw-dropping", never a default Grafana or a generic node-graph look.

Everything else here (art directions, layouts, names, motion values) is **proposed, confirm with Nour in Phase 1**. Phase 2 turns the chosen direction into a design system. Phase 3 builds every screen on demo data, approved one screen at a time.

## 1. The signature moment

**"The roads at night."** The Mesh Map opens on Darb Budokai's world seen from above at a slight tilt: each service is a **place** with its own small landmark (ingest is the city gate, character the citadel, quest the guild hall, spellbook the archive tower, inventory the market, battlelog the chronicler's hall, notification the beacon tower, gateway the harbour, identity the seal house). Places sit on a dark contour-line terrain.

Between them run three kinds of connection, drawn differently because they behave differently:
- **Roads** (synchronous HTTP/GraphQL/REST): fine paved lines.
- **Rivers** (Kafka topics): wider, slowly flowing bands that branch to every consumer. Consumer lag shows as water backing up behind a weir.
- **Ferry routes** (RabbitMQ jobs): dashed lines across a lake, with small boats for queued jobs.

Every real request is a **point of light**. A life event enters at the city gate, flows down the river, splits into each consumer's place, and new lights leave as effects. The light's speed is the real span duration (re-timed to a watchable scale, the scale shown on screen). When a road's p95 latency rises above its SLO threshold, the road **warms to amber**; when errors cross their threshold, it turns a deeper alarm colour with a broken-line pattern and an icon, never colour alone. Lights crawl visibly on a slow road, so the problem is obvious before you read a number.

**Click a light** and the map dims except that one journey: the trace replays as the light's path across places, with each span as a labelled stop and its duration. A compact waterfall slides in beside it. One more click opens the trace in Grafana Tempo.

**During a drill** a quiet banner says "Drill in progress" (or nothing, in blind mode), and the alert rail lights up when an alert fires, linking straight to its runbook page.

**Why it lands:** it turns abstract service graphs into a place you already know from Darb Budokai, and it makes a real performance problem visible in one glance.

## 2. Screens and surfaces

| # | Screen | Purpose | Key content |
|---|---|---|---|
| 2.1 | **Mesh Map (home)** | The signature view | Map, live lights, road states, alert rail, time control (live / last 15 min replay), legend (roads, rivers, ferries, states), data-mode indicator |
| 2.2 | **Place detail** | One service | RED summary, saturation, recent slow traces, current alerts, its SLOs, links to Grafana service dashboard and runbook. Side panel on desktop, sheet with detents on mobile |
| 2.3 | **Road detail** | One edge | Rate, p50/p95/p99 history, errors, slowest recent traces, "why amber" explanation from thresholds in config |
| 2.4 | **Trace journey** | One trace on the map | Path across places, waterfall, span attributes (redacting user IDs to short hashes), open in Tempo |
| 2.5 | **Alerts** | What is firing | List with severity, since, summary, runbook link, silence status (read-only) |
| 2.6 | **Drills** | Drill history and current | List of drills with write-up links, last run date, result (diagnosed in N minutes); current drill state (unless blind) |
| 2.7 | **SLOs** | Error budgets | Each SLO with budget remaining and burn rate, styled to the art direction (built with `dataviz`) |
| 2.8 | **States** | | Empty (no traffic: "the roads are quiet"), loading, BFF unreachable, Prometheus/Tempo unreachable (degraded mode with what still works), WebGL unavailable (2D SVG map with the same data), persistent "Demo data" banner |
| 2.9 | **Grafana dashboards** (operational surface) | | Not a screen we draw, but designed: consistent titles, units, thresholds from config, one question per row, descriptions on every panel, no emoji, theme colours aligned to the chosen palette where Grafana allows |
| 2.10 | **Runbook pages** (operational surface) | | Same structure on every page, scannable in an incident: first five minutes at the top, copy-paste queries in code blocks |
| 2.11 | **Drill CLI output** (operational surface) | | `make drill` prints a short, calm, aligned summary: what was injected (unless blind), for how long, which dashboards to open, how to stop |

Navigation: desktop uses a slim top bar (Map, Alerts, SLOs, Drills). Mobile uses a bottom tab bar with the same four, large collapsing titles on list screens; the map is full-bleed under translucent bars.

## 3. Interaction and motion rules

- **Motion encodes data.** Light speed = span duration (scaled, scale shown); light density = request rate (capped, with a counter for the remainder); river flow speed = throughput; backed-up water = consumer lag. No decorative motion.
- **One focus at a time.** Selecting a light or place dims everything else; the rest of the map keeps updating quietly.
- **Springs, not linear.** Panels and sheets use spring presets from the motion tokens. Camera moves ease; lights follow road curves at constant real-time-scaled speed.
- **Pressed-state feedback:** controls scale to about 0.97 on press with a spring return.
- **Camera:** gentle tilt and pan; drag to pan, scroll/pinch to zoom in limits, double-click a place to frame it. Keyboard: arrows pan, `+`/`-` zoom, `Tab` cycles places in a logical order (gate → river → consumers → gateway), `Enter` opens detail, `Esc` closes, `t` toggles live/replay, `.` and `,` step through the replay.
- **Time control:** live by default; scrub the last 15 minutes (window from config) to watch an incident unfold again.
- **Sound:** none by default. Not planned.
- **Performance budget:** 60 fps with 200 lights in flight on Nour's laptop; instanced lights; pause rendering when hidden; DPR capped at 2.

### Reduced motion (`prefers-reduced-motion: reduce`)

- No travelling lights: each road shows a static throughput thickness and a numeric rate label that updates every few seconds.
- Road state changes cross-fade over 200 ms instead of pulsing.
- Trace journey shows the full path at once with numbered stops instead of animating.
- Camera moves become instant.

## 4. Art direction: three candidates (Nour picks one in Phase 1)

All three avoid: generic node-link graphs with circles and arrows, neon "cyberpunk" grids, gradient blobs, Kubernetes wheel imagery, default Grafana styling.

### A. "Ember Atlas Roads" (proposed default)

Direct continuation of Darb Budokai's proposed "Ember Atlas" (Darb Budokai `docs/UI_DESIGN.md` §1): deep ink terrain with contour lines, places as small sculpted silhouettes, brass hairline UI, ember light for traffic. Healthy roads glow bone-white, slow roads warm to amber (`--ember-400`-adjacent, distinct from the healthy tone), failing roads use Darb Budokai's `--blood-400` with a broken dash and an icon. Type: Cormorant (headings), Inter Tight (UI), JetBrains Mono (numbers). Makes Mesh feel like a layer of Darb Budokai.

### B. "Transit Diagram"

A clean transit-map abstraction: 45-degree lines, rivers and roads as coloured lines with station-like places, on warm off-white paper (dark mode available). Lights are small moving dots like trains. Type: IBM Plex Sans + IBM Plex Mono. Maximally legible, very credible to an SRE audience, easiest to keep accessible.

### C. "Night Flight"

A cinematic, slightly more 3D view: the world as a dark relief seen from a slowly drifting aircraft, places as lit settlements, lights as long-exposure streaks with bloom. Type: Space Grotesk + DM Mono. Most striking in a demo GIF; heaviest to keep at 60 fps and to make accessible.

Each candidate gets a still mock and a 10-second motion study in Phase 2. All assets original or Google Fonts; licences in `ASSETS.md`.

## 5. Native feel on mobile, icons, no emoji

Nour: "the apps must feel as native as a SWIFT UI when it comes to mobile apps... use only modern elements and icons and SVGs ... emojis and low quality icons are forbidden".

- **SwiftUI-like web on phones:** safe-area insets (`env(safe-area-inset-*)`), large collapsing titles on Alerts, SLOs and Drills, a bottom tab bar, sheets with detents (peek, half, full) and drag-to-dismiss for place, road and trace details, spring physics everywhere (no linear easing), pressed-state scale feedback, 44pt minimum touch targets, system-like translucent materials (`backdrop-filter` with a solid fallback) on bars and sheets, native-style lists with swipe actions (swipe an alert to open its runbook, a drill to open its write-up).
- **Icons:** one consistent modern SVG set chosen in Phase 2: Solar via Iconify (skill `solar-duotone-bold`) or Lucide. Place landmarks and road-state glyphs are custom SVG drawn in-repo in the same stroke weight. Tool logos (Kubernetes, Helm, Grafana, OpenTelemetry) only in the README strip via Iconify Simple Icons (skill `company-logos`).
- **Emojis are forbidden** in the UI, Grafana dashboards, alert titles and messages, runbook pages, notifications, docs and commits. No raster clip-art, no mixed icon styles.

## 6. Accessibility requirements

- **Text alternative to the map:** a "Roads" list view (toggle, and always available to screen readers) with every place and connection, its state, rate and p95, sortable. State changes are announced through an `aria-live="polite"` region, rate-limited (from config) and only for state transitions, never per light.
- **Keyboard:** everything reachable; visible focus ring with 3:1 contrast; logical order (§3); skip link to the Roads list.
- **Colour:** road state never by colour alone: amber roads also get a slowed dash rhythm and a "slow" label on focus/hover and in the list; failing roads a broken dash and an icon. WCAG AA contrast: 4.5:1 body, 3:1 large text and UI components. Automated contrast test over tokens in Phase 2.
- **Reduced motion:** §3.
- **Responsive:** 360px up. On small screens the map is full-bleed and details open as sheets.
- **WebGL off:** 2D SVG map fallback with the same data and controls.
- **Axe:** zero serious or critical violations in Playwright on every screen in demo mode.

## 7. Frontend architecture (mesh-map/web)

- Angular (Darb Budokai's version, standalone components, signals), TypeScript strict. Three.js scene in a service + component boundary (`MapRenderer`), so Angular change detection never runs per frame.
- Data sources behind one interface: `DemoSource` (seed JSON), `LiveSource` (BFF REST + SSE). Chosen by `MESH_DATA_MODE`.
- A pure TypeScript "light scheduler" maps trace spans to light paths and times (unit-tested without WebGL).
- Copy, colours, thresholds and layout from config JSON built from `config/` at build time; no literals in components (lint rule).
- If Nour prefers React for the Mesh Map (open question), the same structure applies with React Three Fiber.
