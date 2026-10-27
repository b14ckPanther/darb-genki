# Decisions (ADR log)

Format: each ADR has a status (`accepted` = fixed by Nour's roadmap or the hard rules; `proposed` = confirm with Nour in Phase 1), context, decision and consequences. New ADRs are appended; superseded ones are marked, never deleted.

---

## ADR-001: Darb Budokai's services on Kubernetes with Helm
**Status:** accepted (roadmap)
**Decision:** one library chart, one thin chart per service, an umbrella chart; helmfile for the platform.

## ADR-002: OpenTelemetry tracing across all services
**Status:** accepted (roadmap)
**Decision:** W3C trace context over HTTP, Kafka headers and AMQP headers; OTel Collector as the only telemetry entry point. Darb Budokai already plans Micrometer OTel bridge + OTLP (Darb Budokai ARCHITECTURE §11).

## ADR-003: Grafana dashboards, alerting and a written runbook
**Status:** accepted (roadmap)
**Decision:** dashboards and alert rules as code; every alert has a test and a runbook page.

## ADR-004: Chaos drills diagnosed from traces
**Status:** accepted (roadmap)
**Decision:** Chaos Mesh + stand-in fault switches; drill write-ups are part of the deliverable.

## ADR-005: Local first on kind/k3d; managed cluster optional
**Status:** accepted (brief); kind as default proposed
**Consequences:** $0 by default; charts must not assume cloud load balancers or storage classes.

## ADR-006: Stand-in services built from Darb Budokai's contracts until Darb Budokai exists
**Status:** accepted (brief)
**Decision:** one config-driven image taking each service's shape (ports, topics, queues, health and metrics names); real images swap in via values.

## ADR-007: Stand-ins in Python 3.13 (FastAPI, aiokafka, aio-pika, psycopg 3)
**Status:** proposed
**Context:** Spring Boot stand-ins would duplicate Darb Budokai and need ~3–4 GB RAM for nine JVMs on kind; Python is in 178 Israeli listings and light enough.
**Consequences:** manual Kafka/AMQP propagation is visible in code (good for learning and interviews).

## ADR-008: Platform via operators: CloudNativePG, Strimzi (KRaft), RabbitMQ Cluster Operator
**Status:** proposed
**Context:** operators are how teams run stateful services on Kubernetes; Bitnami charts changed distribution terms in 2025.

## ADR-009: Gateway API with Envoy Gateway, not ingress-nginx
**Status:** proposed
**Context:** ingress-nginx was retired by the Kubernetes project in March 2026.

## ADR-010: Backends: Prometheus + Alertmanager (kube-prometheus-stack), Tempo, Loki, Grafana
**Status:** proposed (Grafana fixed)

## ADR-011: Tail sampling in the Collector; span metrics and service graph computed before sampling
**Status:** proposed
**Consequences:** RED metrics are complete while storage stays small; errors and slow traces are always kept.

## ADR-012: SLOs with Sloth multi-window burn-rate alerts
**Status:** proposed

## ADR-013: Dashboards as code with the Grafana Foundation SDK (Python)
**Status:** proposed
**Alternative:** Grafonnet (Jsonnet) if Nour prefers.

## ADR-014: Mesh Map in Angular + Three.js with a FastAPI BFF
**Status:** proposed
**Context:** Angular matches Darb Budokai's client (and 55 Israeli listings); the BFF keeps Prometheus/Tempo off the public edge and shapes data.

## ADR-015: `config/topology.yaml` is the single source for stand-in wiring, NetworkPolicies, broker CRs and map layout
**Status:** proposed

## ADR-016: Universe events (optional) as CloudEvents 1.0 + JSON Schema 2020-12, outbox first
**Status:** accepted for format (matches Darb Budokai's proposed ADR-016); `mesh.*` event types proposed and optional
**Note:** Darb Budokai's EVENT_CONTRACTS §3.7 currently says Darb Genki emits no domain events; changing that needs a Darb Budokai doc update.

## ADR-017: Config, not code
**Status:** accepted (hard rule 2)

## ADR-018: UI first
**Status:** accepted (hard rule 3)
**Decision:** design system (Phase 2) and Mesh Map prototype on seed data (Phase 3) before cluster work; dashboards and runbook pages are designed surfaces too.

## ADR-019: No AI attribution; Nour is the only author and committer
**Status:** accepted (hard rule 1)

## ADR-020: Ask before paid or public actions; chaos only in allowed namespaces
**Status:** accepted (hard rules 6 and 9)

## ADR-021: TDD with helm-unittest, Testcontainers, promtool tests and kind e2e; no live third-party calls in CI
**Status:** accepted (hard rule 7); tools proposed

## ADR-022: Native feel on mobile, one modern SVG icon set, no emoji (including dashboards and alerts)
**Status:** accepted (rule 11)

## ADR-023: Managed cluster option: GKE Standard zonal with spot nodes, only for demos
**Status:** proposed
**Consequences:** about $35–60/month if left running; intended to run for days, not months.
