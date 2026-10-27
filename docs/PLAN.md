# Master plan: 0% to 100%

Each phase is a shippable increment on its own branch, merged into `main` only with Nour's "yes". Weights add to 100%. Progress is tracked in `docs/PROGRESS.md`.

Every phase uses the process skills (`superpowers:brainstorming`, `superpowers:writing-plans`, `superpowers:executing-plans`, `superpowers:test-driven-development`, `superpowers:systematic-debugging`, `superpowers:verification-before-completion`, `superpowers:requesting-code-review`, `superpowers:receiving-code-review`, `superpowers:finishing-a-development-branch`, `code-review`, `simplify`). Each phase's "Skills:" line lists the extra ones to invoke before starting.

Everything runs locally on kind at $0. A managed cluster is optional (Phase 11) and needs Nour's "yes".

| Phase | Name | Weight | Branch |
|---|---|---|---|
| 0 | Repo bootstrap, CI, conventions | 5% | `phase/00-bootstrap` |
| 1 | Spec confirmation with Nour | 4% | `phase/01-spec` |
| 2 | Design system | 9% | `phase/02-design-system` |
| 3 | Mesh Map prototype on seed data | 12% | `phase/03-ui-prototype` |
| 4 | Local cluster and platform | 9% | `phase/04-cluster-platform` |
| 5 | Stand-in services and Helm charts | 12% | `phase/05-standins-charts` |
| 6 | OpenTelemetry end to end | 11% | `phase/06-telemetry` |
| 7 | Dashboards, SLOs, alerts, runbook | 9% | `phase/07-dashboards-alerts` |
| 8 | Mesh Map live | 8% | `phase/08-mesh-map-live` |
| 9 | Chaos drills | 8% | `phase/09-chaos-drills` |
| 10 | Hardening and CD | 6% | `phase/10-hardening-cd` |
| 11 | Darb Budokai swap-in, optional events, optional managed cluster | 3% | `phase/11-budokai-cloud` |
| 12 | Docs, demo GIF, public launch | 4% | `phase/12-launch` |

---

## Phase 0: Repo bootstrap, CI, conventions (5%)

**Goal:** an empty but disciplined monorepo where every later phase starts green.

**Deliverables:** git repo with Nour's identity, folder skeleton (README map), `.gitignore`, `.env.example`, `.githooks/commit-msg`, agent settings with attribution off, `Makefile` targets (stubs that fail clearly), uv workspace (`standins`, `mesh-map/api`), Angular workspace shell for `mesh-map/web`, chart skeleton (`charts/budokai-service` library + `helm-unittest` wired), config schemas, CI workflow, `ASSETS.md` stub, `LICENSE` (MIT proposed), PR template.

**Tasks (TDD order):**
1. Ask Nour: repo name (`darb-genki` proposed), private while building, licence. Do not create the remote yet.
2. `git init`; `git config user.name "Nour Alden Mousa"`; `git config user.email "nmcryptoinvest@gmail.com"`; `git config core.hooksPath .githooks`.
3. Hook test first (`tests/hooks/test_commit_msg.sh` expects rejection of `Co-Authored-By`, `claude`, `anthropic`, `generated with`); then the hook.
4. `.claude/settings.json` with `"attribution": {"commit": "", "pr": ""}` and `"includeCoAuthoredBy": false`.
5. `make check-emoji`: failing test on a sample file with an emoji, then the script (covers source, YAML, JSON dashboards, Markdown).
6. Python: uv workspace, ruff, mypy strict, pytest; one trivial test per package.
7. Web: `ng new` (Angular version matching Darb Budokai's, standalone, strict) in `mesh-map/web`; ESLint, Prettier, unit test runner, Playwright + `@axe-core/playwright`; a failing app-shell test, then the shell.
8. Charts: `charts/budokai-service` library + a `charts/_example` app chart; a failing `helm-unittest` test asserting `runAsNonRoot`; implement.
9. Config schemas in `config/schema/` + test that validates all YAML.
10. Pin tool versions in `.tool-versions` (mise/asdf): kind, kubectl, helm, helmfile, ct, kubeconform, promtool, sloth, otelcol-contrib, uv, node.
11. CI (`.github/workflows/ci.yml`): Python lint/type/test, web lint/test/e2e, `helm lint`, helm-unittest, kubeconform, `check-emoji`, config schema check.
12. PR template with no attribution line.

**Tests that prove it:** `make test` green; hook test passes; CI green on the branch.

**Definition of done:** clean checkout → `uv sync --all-packages && npm --prefix mesh-map/web ci && make test` green; only Nour in `git log`; ledger updated.

**Skills:** `superpowers:using-git-worktrees`, `run`, `security-review` (CI and hook setup).

---

## Phase 1: Spec confirmation with Nour (4%)

**Goal:** every open question that blocks design or architecture answered and recorded.

**Deliverables:** `docs/specs/YYYY-MM-DD-phase-01-spec.md`, updated `DECISIONS.md`, `OPEN_QUESTIONS.md` with an "Answered" section.

**Tasks:**
1. Run `superpowers:brainstorming`. Ask the questions in `OPEN_QUESTIONS.md` **one at a time**, open-ended first, in order.
2. Present the three art directions (`UI_DESIGN.md` §4) in words; Nour picks one (mocks follow in Phase 2).
3. Confirm machine resources (RAM, CPU, OS, Docker runtime) to choose `full` vs `lite` as the default.
4. Re-read Darb Budokai's `docs/ARCHITECTURE.md` and `EVENT_CONTRACTS.md`; note any changes since this package was written.
5. Write the spec; Nour approves; update `DECISIONS.md`.

**Tests that prove it:** the approved spec (recorded in `PROGRESS.md`).

**Definition of done:** all Phase 1 questions answered; ADR statuses updated.

**Skills:** `superpowers:brainstorming`, `writing-guidelines`.

---

## Phase 2: Design system (9%)

**Goal:** the chosen direction turned into tokens, type, motion, icons and components, chosen with Nour side by side; also the visual rules for Grafana dashboards and runbook pages.

**Deliverables:** tokens (CSS variables generated from `config/theme/*.yaml`), type scale, motion tokens (spring presets), icon set (Solar duotone or Lucide) + custom SVG place landmarks and road-state glyphs, components (TopBar, BottomTabBar, Sheet with detents, Panel, StatTile, Sparkline, AlertRow, Legend, TimeControl, Banner, Toast), `/design` playground, still mock + 10-second motion study for each of the three directions, Grafana style guide (`observability/STYLE.md`: titles, units, colours, descriptions), runbook page template, `ASSETS.md`.

**Tasks (TDD order):**
1. Run `threejs-choose-skills`; record which 3D skills apply.
2. Direction studies on a bare map with demo lights; Nour picks; ADR.
3. Contrast test first (token pairs, WCAG AA), then real tokens.
4. Reduced-motion service test first, then implementation.
5. Each component: test (role, name, keyboard, pressed state, sheet detents and drag-to-dismiss with keyboard equivalents), then build, then playground entry.
6. Lint/test forbidding emoji literals and non-approved icon imports.
7. Axe on `/design`; review with Nour; record approval.

**Tests that prove it:** contrast test, component tests, axe clean, `check-emoji` green.

**Definition of done:** Nour approved tokens, type, icons, components, Grafana style guide and runbook template.

**Skills:** `frontend-design`, `impeccable:impeccable`, `design-taste-frontend`, `build-awwwards-quality-sites`, `design-first-ui-prompting`, `design:design-system`, `design:design-critique`, `design:accessibility-review`, `audit-reference-originality`, `solar-duotone-bold`, `company-logos`, `animation-systems`, `threejs-choose-skills`, `3dviz-pro-max`, `threejs-procedural-materials`, `dataviz`, `writing-guidelines`.

---

## Phase 3: Mesh Map prototype on seed data (12%)

**Goal:** the full clickable Mesh Map on demo data, approved by Nour screen by screen, before any cluster work.

**Deliverables:** demo seed (`config/seed/demo/`: graph built from `config/topology.yaml` + ~300 synthetic traces including a "slow road" episode and an error episode), `DemoSource`, light scheduler, map scene (terrain, places, roads, rivers, ferries, lights, road states), place/road/trace detail, Alerts, Drills, SLOs, all states, 2D SVG fallback, Roads list view, mobile layouts with native feel.

**Tasks (TDD order):**
1. Seed generator (`tools/seed/`) tests: deterministic, traces follow topology, episodes present; implement.
2. Light scheduler tests: span → path and timing, scale factor, density cap with remainder counter, replay window; implement.
3. Road-state tests: thresholds from config produce normal/slow/failing; implement.
4. Map scene: terrain, places, connections, instanced lights, camera rig; visual snapshot tests at a fixed seed; performance check.
5. Roads list and `aria-live` rate limiting: tests, then build.
6. Place, road and trace-journey detail (panel desktop, sheet mobile): tests, then build.
7. Alerts, Drills, SLOs screens from seed: tests, then build (charts with `dataviz`).
8. States: empty, loading, BFF down, partial data, WebGL off (2D SVG map), Demo banner.
9. Playwright e2e for every screen: keyboard, reduced motion, 360px and desktop, axe.
10. Screen-by-screen review with Nour; record verdicts; iterate.

**Tests that prove it:** unit suites, e2e + axe, visual snapshots, 60 fps with 200 lights measured on Nour's laptop (recorded), `check-emoji` green.

**Definition of done:** every screen approved by Nour; demo mode labelled; no hardcoded copy/thresholds/layout.

**Skills:** `frontend-design`, `impeccable:impeccable`, `design-taste-frontend`, `build-awwwards-quality-sites`, `ui-implementer`, `web-design-guidelines`, `design:design-critique`, `design:accessibility-review`, `design:ux-copy`, `design:design-handoff`, `threejs`, `threejs-web-design`, `3dviz-pro-max`, `threejs-bloom`, `threejs-camera-controls-and-rigs`, `threejs-particles-trails-and-effects`, `threejs-procedural-geometry`, `threejs-procedural-materials`, `threejs-exposure-color-grading`, `threejs-compatibility-fallbacks`, `threejs-debugging`, `threejs-visual-validation`, `add-mouse-driven-orbit`, `animation-systems`, `gsap`, `optimize-web-animations`, `dataviz`, `performance-profiling`, `playwright-cli`, `run`.

---

## Phase 4: Local cluster and platform (9%)

**Goal:** one command creates a kind cluster with Gateway, operators and data services ready for Darb Budokai.

**Deliverables:** `cluster/kind.yaml` (+ `k3d.yaml` if wanted), local registry, `platform/helmfile.yaml.gotmpl` (Envoy Gateway, Gateway API CRDs, CloudNativePG, Strimzi, RabbitMQ Cluster Operator, cert-manager if needed by operators), `charts/budokai-data` (CNPG Cluster, Kafka + KafkaNodePool KRaft, RabbitmqCluster), namespaces with Pod Security Admission labels and the chaos label, `make up/down/status`, `full` and `lite` values.

**Tasks (TDD order):**
1. e2e test first (`tests/e2e/test_platform.py`): cluster reachable, Gateway answers on `*.localtest.me:8080`, Postgres accepts a connection, Kafka produces/consumes a test record, RabbitMQ accepts a message. Watch it fail.
2. kind config + local registry; `make up` creates them idempotently.
3. helmfile for operators with pinned chart versions; `helm-unittest`/kubeconform on `budokai-data`.
4. `budokai-data` instances; values per profile.
5. Namespaces + PSA `restricted` + chaos label; test that a privileged pod is rejected in `budokai`.
6. `make status` output (designed, calm, aligned).
7. CI job: kind in GitHub Actions (`helm/kind-action`) runs the platform e2e with `lite`.

**Tests that prove it:** platform e2e green locally and in CI; kubeconform clean.

**Definition of done:** `make down && make up` → platform e2e green from a clean checkout, timings recorded.

**Skills:** `security-review`, `run`, `superpowers:systematic-debugging`.

---

## Phase 5: Stand-in services and Helm charts (12%)

**Goal:** all nine Darb Budokai services (as stand-ins) plus the simulator deployed by Helm, exchanging real events over Kafka and RabbitMQ, matching Darb Budokai's contracts.

**Deliverables:** `config/topology.yaml` transcribed from Darb Budokai's ARCHITECTURE; contract snapshot in `contracts/budokai/` (from Darb Budokai EVENT_CONTRACTS, marked `x-standin-snapshot`) and `make sync-contracts`; `standins/` package (HTTP routes, Kafka consume/produce, outbox relay, inbox, RabbitMQ jobs, Postgres per service, schema validation, fault switches off, actuator-compatible health and metrics, JSON logs); one chart per service on the library chart; umbrella `charts/budokai`; KafkaTopic/Queue/Exchange/Database CRs from topology; NetworkPolicies from topology; simulator with Darb Budokai's HMAC signing.

**Tasks (TDD order):**
1. Topology tests: every service, topic, queue and DB from Darb Budokai's ARCHITECTURE present; consistency (every consumed topic has a producer). Write the YAML.
2. Contract snapshot tests: valid/invalid examples per event type; schemas compile (Draft 2020-12).
3. Stand-in unit tests: behaviour loaded from config; latency distribution sampled within bounds; schema validation rejects bad events; health and metrics endpoints at Darb Budokai's paths and names.
4. Outbox + inbox tests (Testcontainers Postgres): exactly one effect per event under redelivery.
5. Kafka tests (Testcontainers Kafka): consume → effect → DLT on poison after configured retries.
6. RabbitMQ tests (Testcontainers RabbitMQ): job processed; DLX on failure.
7. Simulator tests: HMAC signature format per Darb Budokai ARCHITECTURE §8; scenarios load.
8. Chart tests (helm-unittest): per-service values render the right ports, probes, env, ServiceMonitor, NetworkPolicy rules from topology; image swap via values.
9. e2e: `make deploy` + `make sim` → every effect topic receives records; battlelog job runs; NetworkPolicy blocks a call not in topology.

**Tests that prove it:** pytest unit + Testcontainers suites; helm-unittest; kubeconform; e2e green.

**Definition of done:** a simulated typical day flows through all services in kind; swapping one image tag is a values-only change (demonstrated in a test).

**Skills:** `superpowers:subagent-driven-development` (services and charts are parallel tasks), `security-review`, `run`.

---

## Phase 6: OpenTelemetry end to end (11%)

**Goal:** one connected trace per life event across HTTP, Kafka, outbox, RabbitMQ and WebSocket push; metrics and logs correlated with traces.

**Deliverables:** OTel Collector config (`observability/collector/`) with `memory_limiter`, `k8sattributes`, tail sampling from `config/sampling.yaml`, `spanmetrics` and `servicegraph` connectors; Tempo, Loki, Prometheus (kube-prometheus-stack with remote-write receiver and exemplars), Grafana with datasources and trace↔log↔metric links; stand-in instrumentation with manual Kafka/AMQP propagation where needed; OTel Operator with an `Instrumentation` CR ready for Darb Budokai's Java images.

**Tasks (TDD order):**
1. Unit tests with an in-memory span exporter: HTTP → Kafka produce → consume keeps one trace; outbox relay links to the originating span (span link or parent, decided and documented); RabbitMQ job carries context; `drop_trace_context` fault breaks it (used later by a drill).
2. Collector config validation test (`otelcol-contrib validate`) and a recorded-input test for tail sampling (errors and slow kept, others sampled per config).
3. Install backends via helmfile; datasource provisioning test (Grafana API returns the datasources).
4. e2e broken-trace guard: simulate N events; TraceQL in Tempo finds exactly one root in ingest and spans in every consumer from topology for each.
5. e2e: service graph metrics exist in Prometheus for every topology edge; exemplars present; logs in Loki carry `traceId` and link back.
6. Document "how to read a trace" in `runbook/how-to-read-a-trace.md`.

**Tests that prove it:** unit span tests, collector tests, e2e trace completeness at 100% for simulator events.

**Definition of done:** Nour can open any simulator event in Tempo and follow it end to end, and jump to its logs and metrics.

**Skills:** `superpowers:systematic-debugging`, `superpowers:verification-before-completion`, `run`.

---

## Phase 7: Dashboards, SLOs, alerts, runbook (9%)

**Goal:** dashboards that each answer one question, SLO burn-rate alerts, symptom alerts, and a runbook page for every alert.

**Deliverables:** dashboards as code (`observability/dashboards/`, Grafana Foundation SDK Python) for the seven dashboards in ARCHITECTURE §7; Sloth SLO specs + generated rules; extra alert rules; `promtool` tests; Alertmanager config with the local `alert-sink` receiver (+ optional receiver from env); runbook pages.

**Tasks (TDD order):**
1. Dashboard tests first: generated JSON has the expected panels; every query's metric names exist in the scraped metric list from e2e; thresholds come from config; no emoji; every panel has a description.
2. Generate dashboards; review each with Nour in Grafana (screenshots); record approvals.
3. SLO tests: Sloth output contains multi-window burn rules per SLO in `config/slo.yaml`.
4. Alert unit tests (`promtool test rules`) for each alert: fires on the given series, resolves after.
5. Runbook test: every alert's `runbook_url` points to an existing page with all required sections.
6. Write runbook pages (template from Phase 2).
7. e2e: force one SLO burn with the stand-in `error_rate` switch; alert reaches `alert-sink`; resolves when switched off.

**Tests that prove it:** dashboard tests, `promtool` tests, runbook link test, alert e2e.

**Definition of done:** every dashboard approved by Nour; every alert tested and documented.

**Skills:** `dataviz`, `writing-guidelines`, `design:ux-copy`, `superpowers:verification-before-completion`.

---

## Phase 8: Mesh Map live (8%)

**Goal:** the approved Mesh Map driven by real cluster data.

**Deliverables:** `mesh-map/api` (FastAPI BFF: graph, edges, traces, SSE stream, alerts, drill state; queries from `config/mesh-map/queries.yaml`), `LiveSource` in the web app, chart `charts/mesh-map` with HTTPRoute `map.localtest.me`.

**Tasks (TDD order):**
1. BFF tests with recorded Prometheus and Tempo responses: graph shaping, road states from thresholds, SSE rate cap, Tempo errors degrade gracefully.
2. Contract test: BFF responses validate against the JSON Schemas the web app's `DemoSource` already uses.
3. `LiveSource` tests (mocked SSE); implement.
4. Chart tests; deploy; e2e (Playwright against kind): map shows all places; a simulated slow road turns amber within the configured window.
5. Nour reviews live map vs the approved prototype.

**Tests that prove it:** BFF suite, contract tests, live e2e.

**Definition of done:** live map matches the approved prototype; slow-road detection visible end to end.

**Skills:** `threejs-debugging`, `threejs-visual-validation`, `optimize-threejs-games`, `performance-profiling`, `playwright-cli`, `run`.

---

## Phase 9: Chaos drills (8%)

**Goal:** a library of reproducible drills, each diagnosed from traces and written up.

**Deliverables:** Chaos Mesh installed with namespace filtering; `chaos/drills/*.yaml` for the eight drills in ARCHITECTURE §8; `make drill`, `drill BLIND=1`, `drill-reveal`, `drill-stop`, `drill-close`; Grafana annotations for drill start/stop; at least six write-ups in `runbook/drills/`.

**Tasks (TDD order):**
1. Safety tests first: an experiment targeting `observability` or `kube-system` is rejected; every drill file has a duration and an expected alert.
2. Drill runner tests (dry-run renders the right manifests/patches; blind mode hides the name; stop removes everything).
3. Per drill: e2e asserting the expected alert fires and the expected trace signature exists (TraceQL), then resolves after stop.
4. Nour runs drills (blind where possible), diagnoses with Grafana, Tempo and the Mesh Map; agent records time-to-detect and time-to-diagnose; Nour writes or approves each write-up.
5. Update runbook pages with anything the drills taught.

**Tests that prove it:** safety tests, per-drill e2e, write-ups present and linked from the Drills screen.

**Definition of done:** six or more drills completed with write-ups; every drill reproducible by command.

**Skills:** `superpowers:systematic-debugging`, `writing-guidelines`, `security-review`.

---

## Phase 10: Hardening and CD (6%)

**Goal:** production-grade hygiene a reviewer would expect.

**Deliverables:** multi-stage, non-root, distroless or slim images with SBOMs; Trivy scans (images + charts) gating CI; cosign keyless signing of images on release; Kyverno or `ValidatingAdmissionPolicy` enforcing signed images, resource limits and no `latest` tags (proposed: `ValidatingAdmissionPolicy`, built in); HPA on gateway/ingest with a load test (k6) showing scale-out; PDBs verified during node drain; GitHub Actions CD: on tag, build, sign, push to GHCR (after Nour's yes to publish), and run the full kind e2e; Renovate config for pinned versions; resource right-sizing from measured usage.

**Tasks (TDD order):** each item starts with a failing check (admission test rejecting an unsigned or limitless pod, k6 threshold test, Trivy gate on a known-vulnerable test image, drain test with PDB), then the fix.

**Tests that prove it:** admission tests, k6 report, drain e2e, CI security gates.

**Definition of done:** full `security-review` and `code-review` with findings fixed; Nour approves the CD flow.

**Skills:** `security-review`, `code-review`, `simplify`, `performance-profiling`.

---

## Phase 11: Darb Budokai swap-in, optional events, optional managed cluster (3%)

**Goal:** run real Darb Budokai services if they exist; optionally emit `mesh.*` events; optionally run on a managed cluster for a demo.

**Deliverables:** `values/budokai.yaml` with real images (as available), JVM-aware resources and startup probes; synced contracts; optional adapter for `mesh.*` events; optional `make cloud-up/cloud-down` for the provider Nour picks, with cost logged.

**Tasks:** follow `INTEGRATION.md` §6. For the managed cluster: plan and cost estimate → **ask Nour** → create → deploy with `values/cloud.yaml` → smoke e2e → demo → `make cloud-down` → leftover check. Each step test-first where code is involved (adapter signature/batching tests, values schema tests).

**Tests that prove it:** e2e with at least one real Darb Budokai service; adapter tests; cloud smoke test (if done).

**Definition of done:** whatever subset Nour chose is done and recorded; the rest recorded as deferred rulings (weight moves to Phase 10 if all deferred).

**Skills:** `security-review`, `superpowers:verification-before-completion`.

---

## Phase 12: Docs, demo GIF, public launch (4%)

**Goal:** a public repo that explains itself in 10 seconds and holds up in a platform/SRE interview. **Ask Nour before making anything public.**

**Deliverables:** README (hero GIF of the Mesh Map catching a slow road, architecture diagram, quick start, drill list with write-ups, cost table, "built with" strip using Simple Icons), demo GIF recorded from a real drill on kind, docs pass, Darb Kaioken outline handed over, public repo (after "yes").

**Tasks:**
1. README and docs pass with `writing-guidelines`.
2. Record the GIF from a real drill (no seed data unless labelled).
3. Final `check-emoji`, push checklist (CLAUDE.md §7).
4. **Ask Nour**: make the repo public, publish images.
5. After "yes": `publish-project-to-github`; verify the README renders and CI is green on `main`.

**Tests that prove it:** all suites green on `main`; push checks pass.

**Definition of done:** public repo with only Nour as contributor; README complete.

**Skills:** `publish-project-to-github` (only after Nour's yes), `writing-guidelines`, `design:ux-copy`, `browser-video-recording`, `company-logos`, `audit-reference-originality`, `superpowers:finishing-a-development-branch`.
