# Darb Genki

**Role in the universe:** the roads between places.

Darb Genki runs all of Darb Budokai's microservices on Kubernetes with Helm. Every request is traced across services with OpenTelemetry, from the HTTP call into ingest, through Kafka and RabbitMQ, into each domain service and out to the browser push. Grafana dashboards, SLO-based alerts and a written runbook sit on top. Then it breaks things on purpose: chaos drills inject latency, kill brokers and poison queues, and Nour diagnoses each one from the traces alone.

The signature is the **Mesh Map**: a live map of the services drawn as places in Darb Budokai's world. Each real request travels as a point of light along the roads between them, and a road that gets slow turns amber.

Darb Budokai (`/Users/zangeel/Documents/GitHub/darb-budokai/`) does not exist as running code yet. Until it does, Darb Genki deploys **stand-in services** built from Darb Budokai's contracts: one small, config-driven service image that takes the shape of each Darb Budokai service (same names, ports, topics, queues, health and metrics endpoints). When Darb Budokai's real images exist, the same Helm charts deploy them instead.

Status: planning package. Nothing is built yet. Progress lives in `docs/PROGRESS.md`.

## Stack

| Layer | Choice | Status |
|---|---|---|
| Cluster (local, free) | kind (Kubernetes 1.34+), k3d as the alternative | fixed: local first on kind/k3d |
| Packaging | Helm (v4 if all charts work with it, else 3.19+), a library chart + one chart per service, an umbrella chart, helmfile for the stack | Helm fixed; layout proposed |
| Platform operators | CloudNativePG (Postgres 17), Strimzi (Kafka 4, KRaft), RabbitMQ Cluster Operator, Envoy Gateway (Gateway API) | proposed, confirm with Nour in Phase 1 |
| Telemetry | OpenTelemetry (SDKs, Operator auto-instrumentation, Collector contrib with tail sampling, span metrics and service graph connectors) | fixed: OpenTelemetry |
| Backends | Prometheus + Alertmanager (kube-prometheus-stack), Tempo, Loki, Grafana 12 | Grafana fixed; rest proposed |
| SLOs and alerts | Sloth (SLO YAML → multi-window burn-rate PrometheusRules) | proposed |
| Chaos | Chaos Mesh 2.x + fault switches inside the stand-ins | fixed: chaos drills; tool proposed |
| Stand-in services | Python 3.13, FastAPI, aiokafka, aio-pika, psycopg 3, OpenTelemetry | proposed |
| Mesh Map | Angular (Darb Budokai's version) + Three.js frontend, FastAPI backend-for-frontend over Prometheus and Tempo APIs | proposed |
| CI/CD | GitHub Actions: lint, unit tests, image build (multi-stage), `helm lint`, chart-testing, kind end-to-end, kubeconform, Trivy, cosign; GHCR for images | proposed |

## Expected cost

- **Local (default): $0.** Everything runs on kind on Nour's machine. Needs about 10–12 GB of free RAM for the full stack, about 6 GB for the "lite" profile.
- **Managed cluster (optional, only after Nour's "yes"):** roughly **$0 to $160 per month** depending on provider; the proposed choice is GKE Standard zonal with spot nodes at about **$35–60/month**, run only when needed. Table in `docs/ARCHITECTURE.md` §10.

Teardown: `make down` (local, deletes the kind cluster). Managed: `make cloud-down` (ask Nour first).

## Folder map (target, created from Phase 0)

```
darb-genki/
├── cluster/                 kind and k3d configs, bootstrap scripts
├── charts/
│   ├── budokai-service/       library chart (Deployment, Service, probes, HPA, PDB, ServiceMonitor, NetworkPolicy, OTel annotations)
│   ├── <service>/           one thin chart per Darb Budokai service (values only + templates from library)
│   └── budokai/               umbrella chart (all services)
├── platform/                helmfile + values for operators, Gateway, observability stack, Chaos Mesh
├── standins/                Python stand-in service (one image, behaviour from config)
├── mesh-map/
│   ├── web/                 Angular + Three.js Mesh Map
│   └── api/                 FastAPI BFF (Prometheus + Tempo queries from config)
├── observability/
│   ├── dashboards/          dashboards as code → JSON
│   ├── slo/                 Sloth SLO specs
│   ├── alerts/              extra PrometheusRules
│   └── collector/           OTel Collector config
├── chaos/                   Chaos Mesh experiments + drill definitions
├── runbook/                 one page per alert, drill write-ups (postmortems)
├── contracts/budokai/         snapshot of Darb Budokai's JSON Schemas (synced, pinned)
├── config/                  YAML: topology, stand-in behaviour, SLOs, map layout, copy, seed
├── tests/e2e/               kind-based end-to-end tests
└── Makefile                 up, down, deploy, drill, test
```

## How to start

Open Claude Code in this folder and say:

> start Phase 0

The agent reads `CLAUDE.md`, then `docs/PLAN.md`, and works phase by phase. It asks Nour before anything outward-facing (repo creation, pushing to main, any paid cluster).

## Planning docs

| File | What |
|---|---|
| `CLAUDE.md` | Agent operating manual. The law. |
| `AGENTS.md` | Pointer for non-Claude agents |
| `docs/VISION.md` | Goals, non-goals, anti-goals, why this stack |
| `docs/ARCHITECTURE.md` | Cluster, charts, telemetry, stand-ins, chaos, cost |
| `docs/UI_DESIGN.md` | Mesh Map signature, screens, motion, art directions |
| `docs/INTEGRATION.md` | What it consumes from Darb Budokai and the optional events it emits |
| `docs/PLAN.md` | Phases 0 to 12, 0% to 100% |
| `docs/PROGRESS.md` | Ledger |
| `docs/DECISIONS.md` | ADR log |
| `docs/OPEN_QUESTIONS.md` | What only Nour decides |
| `docs/CONVENTIONS.md` | Code style, layout, tests, commits, PRs |

## How it fits the universe

Darb Budokai is the RPG Nour's real life powers. Its docs say Darb Budokai itself ships no Kubernetes or dashboards; it exposes hooks (health probes, Prometheus metrics, OTLP traces, JSON logs with trace IDs) for Darb Genki (Darb Budokai `docs/ARCHITECTURE.md` §11). Darb Genki is where those hooks become a running, observable system. It reads Darb Budokai's contracts, deploys Darb Budokai's services, and can optionally report finished drills to Darb Budokai as events (`docs/INTEGRATION.md`). It works fully without Darb Budokai thanks to the stand-ins.
