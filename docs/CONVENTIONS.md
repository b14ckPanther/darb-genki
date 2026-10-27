# Conventions

## 1. Code style

### Helm and Kubernetes YAML
- Charts follow the Helm best practices guide: lowercase names, `app.kubernetes.io/*` labels on everything, `values.schema.json` for every chart, no environment literals in templates.
- Every workload: requests and limits, liveness and readiness probes, `runAsNonRoot`, read-only root filesystem, dropped capabilities, `seccompProfile: RuntimeDefault`, a PDB if replicas > 1, a NetworkPolicy.
- Image tags pinned (digest or exact version). Never `latest`.
- Comments explain why, not what. `helm lint`, `ct lint`, kubeconform and yamllint clean.

### Python (stand-ins, mesh-map/api, tools)
- Python 3.13, uv workspace. ruff (lint and format, line length 100), mypy --strict.
- Async throughout (FastAPI, aiokafka, aio-pika, psycopg 3 async).
- Behaviour from `config/` only. Constants allowed: 0, 1 and protocol facts.
- Pydantic 2 models for config and events; JSON Schema validation for Darb Budokai contracts.
- Structured JSON logs (structlog) with `traceId`, `spanId`, `userId`, `eventId`.

### TypeScript (mesh-map/web)
- Angular standalone components and signals, TypeScript strict, ESLint (angular-eslint), Prettier.
- Three.js code isolated in services under `src/app/map/`, never touched by change detection per frame.
- No string, colour or threshold literals in components; no emoji (lint + `check-emoji`). Icons only from the set chosen in Phase 2 and in-repo SVGs.

### PromQL, TraceQL, LogQL
- Queries live in config files (`config/mesh-map/queries.yaml`, dashboard configs, runbook code blocks) with a comment line stating the question they answer.
- Recording rules named `level:metric:operations` (Prometheus convention).

### Shell and Make
- `set -euo pipefail`, shellcheck clean. Make targets are thin wrappers over scripts in `scripts/`.

## 2. Project layout

```
cluster/                     kind.yaml, k3d.yaml, registry setup
platform/                    helmfile.yaml.gotmpl, values/<component>/{local,lite,cloud}.yaml
charts/<chart>/              Chart.yaml, values.yaml, values.schema.json, templates/, tests/ (helm-unittest)
standins/src/standins/{app,config,http,kafka,rabbit,db,outbox,inbox,faults,telemetry,contracts}/  standins/tests/{unit,integration}/
mesh-map/api/src/mesh_api/   mesh-map/api/tests/
mesh-map/web/src/app/{map,screens,design,data,scheduler}/   mesh-map/web/e2e/
observability/{collector,dashboards,slo,alerts}/   observability/tests/
chaos/{drills,experiments}/   chaos/tests/
runbook/{alerts,drills}/   runbook/how-to-read-a-trace.md
contracts/{budokai,mesh}/
config/   tools/seed/   scripts/   tests/e2e/   docs/{specs,plans}/
```

## 3. Testing conventions

- TDD always: failing test first, seen failing, then code (CLAUDE.md §1.8).
- Test names state behaviour: `test_outbox_relay_publishes_each_effect_once_under_redelivery`, `it("turns a road amber when p95 exceeds its threshold")`.
- helm-unittest suites per chart in `charts/<chart>/tests/*_test.yaml`.
- Testcontainers for Kafka, Postgres, RabbitMQ; no broker mocks in integration tests.
- Recorded Prometheus/Tempo/Alertmanager responses under `mesh-map/api/tests/fixtures/`.
- `promtool test rules` file per alert group in `observability/tests/`.
- e2e (`tests/e2e/`, pytest) runs against kind; marked `@pytest.mark.e2e`, run by `make e2e` and the CI kind job.
- Visual snapshots with a fixed seed and reduced motion on.
- Coverage targets (proposed): 85% lines on stand-ins and BFF, 100% of chart templates exercised by at least one unit test.

## 4. Commits

- Imperative, plain English, first line under 72 characters, optional body explaining **why**. Examples:
  - `Generate NetworkPolicies from topology config`
  - `Keep trace context across outbox relay with span links`
  - `Add failing test for amber road threshold` (only if the next commit makes it pass)
- Small and honest: one working step per commit. Many commits are welcome; never fake or backdate.
- **No AI attribution.** "Never add "Co-Authored-By" or any other AI attribution line to commit messages, pull request descriptions, or any other text, in any project. Commit messages end with the last line of the actual description." Never write the word "claude" in a commit message (the push check greps for it). No emoji.
- Author and committer: `Nour Alden Mousa <nmcryptoinvest@gmail.com>` only.

## 5. Branches

- One per phase: `phase/NN-short-name` (see `PLAN.md`).
- Optional short-lived sub-branches: `phase/NN-short-name--topic`, merged into the phase branch locally.
- `main` only receives merges approved by Nour.

## 6. Pull request template

Save as `.github/pull_request_template.md` in Phase 0:

```markdown
## What

<!-- one or two sentences -->

## Why

<!-- link the phase in docs/PLAN.md and the spec in docs/specs/ -->

## How it was tested

- [ ] Failing test written first, seen failing
- [ ] `make test`
- [ ] `make e2e` (if charts, telemetry or platform changed)
- [ ] `make promtool` (if alerts changed) and runbook page added/updated
- [ ] `make check-emoji`

## Cluster impact

- [ ] Resource requests/limits, probes, NetworkPolicy, security context present
- [ ] No environment literals in templates; values schema updated
- [ ] Chaos experiments (if any) have a duration and target allowed namespaces only

## Screens or dashboards (if changed)

<!-- screenshots, mobile and desktop; Nour's approval noted in docs/PROGRESS.md -->
```

The template has no attribution line, and none may be added to PR bodies.
