# Architecture

Status: Kubernetes + Helm, OpenTelemetry tracing across services, Grafana dashboards, alerting, a written runbook, chaos drills, local kind/k3d first, optional managed cluster, and stand-ins built from Darb Budokai's contracts come from Nour's roadmap and the project brief. Operators, backends, languages, names and layout below are **proposed, confirm with Nour in Phase 1**.

Source of truth for Darb Budokai's service shapes: `/Users/zangeel/Documents/GitHub/darb-budokai/docs/ARCHITECTURE.md` (services, ports, topics, queues, databases, observability hooks in §11) and `EVENT_CONTRACTS.md`. If Darb Budokai's docs change, update `config/topology.yaml` and this file.

## 1. Shape in one paragraph

A kind cluster hosts three groups of namespaces. **Platform** (`platform-*`): CloudNativePG, Strimzi Kafka (KRaft), RabbitMQ Cluster Operator and Envoy Gateway. **Darb Budokai** (`budokai`): the nine Darb Budokai services and the simulator, each deployed by a thin Helm chart built on one library chart; until Darb Budokai's images exist, each runs the **stand-in** image configured to take that service's shape. **Observability** (`observability`): OpenTelemetry Operator and Collector, Prometheus + Alertmanager, Tempo, Loki and Grafana. Every service sends OTLP traces to the Collector, which tail-samples, derives span metrics and a service graph, and forwards to Tempo and Prometheus. The **Mesh Map** (`mesh-map`) reads those service graph metrics and recent traces through a small BFF and draws them as Darb Budokai's roads. **Chaos Mesh** injects failures into the `budokai` namespace only.

## 2. Diagram

```
                       http://*.localtest.me:8080  (kind port mapping → Envoy Gateway, Gateway API)
                                       │
          ┌────────────────────────────┼─────────────────────────────────┐
          ▼                            ▼                                 ▼
   map.localtest.me             grafana.localtest.me              budokai.localtest.me
   mesh-map web + api           Grafana 12                        gateway-service /graphql, notification /ws
          │ PromQL/TraceQL            ▲ ▲ ▲                                │
          ▼                           │ │ │                               ▼
┌──────────── observability ─────────┐│ │ │      ┌──────────────── budokai (chaos allowed) ────────────────┐
│ Prometheus ◄── span metrics ──┐    ││ │ │      │ simulator ─HTTP+HMAC─► ingest-service :8082            │
│   ▲  Alertmanager → receiver  │    ││ │ │      │                         │ Kafka budokai.life-events.v1  │
│   │ ServiceMonitors           │    ││ │ │      │       ┌────────────┬────┴──────┬──────────────┐       │
│ Tempo ◄── traces ── OTel Collector ◄─────────────── OTLP from every pod  (traceparent over HTTP,       │
│ Loki  ◄── logs (filelog) ──┘  (tail sampling,│ │ │      │  Kafka headers, AMQP headers)                 │
│ OTel Operator (Instrumentation CR)            │ │ │      │ character quest spellbook inventory  :8083-86 │
└───────────────────────────────────────────────┘ │ │      │       └──── effect topics ────┐               │
                                                  │ │      │ battlelog :8087 ◄─ RabbitMQ budokai.jobs        │
┌──────────── platform-data ──────────────────┐   │ │      │ notification :8088 ─ STOMP ─► browser        │
│ CNPG cluster budokai-pg (one DB+role/service) │◄──┼─┼──────│ gateway :8080 ─REST─► services, identity :8081│
│ Strimzi Kafka budokai-kafka (KRaft, 1 node)   │◄──┼─┼──────└───────────────────────────────────────────────┘
│ RabbitmqCluster budokai-rabbit                │◄──┘ │                ▲
│ (exporters: kafka-exporter, CNPG, rabbitmq) │─────┘                │ Chaos Mesh (NetworkChaos, PodChaos,
└─────────────────────────────────────────────┘                      │ StressChaos, TimeChaos), namespace filter
```

## 3. Cluster

- **kind** (proposed default): `cluster/kind.yaml` with 1 control-plane + 2 workers, `extraPortMappings` 8080→Gateway NodePort, a local registry (`kind-registry:5001`) so `make deploy` pushes images without a remote. Node image pinned to a current Kubernetes 1.34/1.35 release in Phase 0.
- **k3d** alternative: `cluster/k3d.yaml` (Traefik disabled, same Gateway). Kept working by one CI job if Nour wants both (open question).
- **Ingress:** Gateway API with **Envoy Gateway**. Not ingress-nginx, which the Kubernetes project retired in March 2026. Hostnames under `localtest.me` (public DNS that resolves to 127.0.0.1) so no `/etc/hosts` edits.
- **Profiles:** `full` (all components, ~10–12 GB RAM) and `lite` (single replicas, no Loki, smaller limits, ~6 GB). Selected by `PROFILE`, implemented as values files, not code.
- **Bootstrap:** `helmfile` (`platform/helmfile.yaml.gotmpl`) installs operators and observability in dependency order; then `helm upgrade --install budokai charts/budokai`.

## 4. Helm charts

```
charts/
├── budokai-service/      type: library. Templates: Deployment, Service, ServiceAccount, ConfigMap (service config),
│                       HPA, PDB, NetworkPolicy, ServiceMonitor, HTTPRoute (optional), PodMonitor (optional),
│                       OTel Instrumentation annotation, Kafka/Postgres/Rabbit connection env from operator secrets.
├── gateway-service/    application chart: Chart.yaml depends on budokai-service; values.yaml only
├── identity-service/ ingest-service/ character-service/ quest-service/ inventory-service/
├── spellbook-service/ battlelog-service/ notification-service/ simulator/
├── budokai/              umbrella: all of the above + KafkaTopic, KafkaUser, CNPG Database, RabbitMQ Queue/Exchange CRs
├── budokai-data/         CNPG Cluster, Strimzi Kafka + KafkaNodePool, RabbitmqCluster (instances, not operators)
└── mesh-map/           web + api
```

Library chart rules:
- Every pod: `runAsNonRoot`, read-only root filesystem, dropped capabilities, `seccompProfile: RuntimeDefault` (Pod Security Admission `restricted` on the namespace).
- Probes: liveness `/actuator/health/liveness`, readiness `/actuator/health/readiness` (Darb Budokai's paths; stand-ins expose the same).
- Metrics: `ServiceMonitor` on `/actuator/prometheus`.
- `NetworkPolicy`: default deny in `budokai`; allow rules generated from `config/topology.yaml` (who calls whom, who talks to which broker/DB). The topology file is the single source for NetworkPolicies, stand-in behaviour and the Mesh Map layout.
- Image swap: `image.repository`/`tag` per service in values; `values/standins.yaml` vs `values/budokai.yaml`. Moving to real Darb Budokai images is a values change.
- Env for Darb Budokai images: `MANAGEMENT_OTLP_TRACING_ENDPOINT=http://otel-collector.observability:4318/v1/traces`, sampling probability from values, `SPRING_PROFILES_ACTIVE=k8s` (Darb Budokai ARCHITECTURE §11).

Kafka topics and RabbitMQ queues are declared as CRs (`KafkaTopic`, `Queue`, `Exchange`, `Binding`) from `config/topology.yaml`, matching Darb Budokai ARCHITECTURE §4 (topic names, partitions, retention, DLQs).

## 5. Stand-in services (until Darb Budokai exists)

One Python 3.13 image (`standins/`), nine deployments. Each pod reads `STANDIN_ROLE=<service>` and loads its behaviour from `config/standins/<service>.yaml` (mounted ConfigMap):

```yaml
# config/standins/quest-service.yaml (example shape, values proposed)
role: quest-service
port: 8084
http:
  - route: GET /internal/quests/{userId}
    latency_ms: { dist: lognormal, p50: 12, p95: 40 }
    db: { op: select, table: quests }
consumes:
  - topic: budokai.life-events.v1
    group: quest-service
    effects:
      - topic: budokai.quest.effects.v1
        type: quest.progressed
        probability: 0.6
        via_outbox: true
  - queue: quest.generate-daily
publishes_to_ingest: []
faults:                 # off by default; switched on by drills (ConfigMap patch, hot reload)
  slow_db_ms: 0
  error_rate: 0.0
  poison_on_type: null
  hold_db_connections: 0
  drop_trace_context: false
```

- **Built from Darb Budokai's contracts:** stand-ins validate every event they consume and produce against Darb Budokai's JSON Schemas in `contracts/budokai/` (CloudEvents 1.0 envelope + JSON Schema 2020-12, Darb Budokai EVENT_CONTRACTS §1). Until Darb Budokai publishes schema files, Phase 5 writes a **snapshot** from the sketches in Darb Budokai's `EVENT_CONTRACTS.md`, marked `x-standin-snapshot: true`, replaced by `make sync-contracts` once Darb Budokai's repo has them.
- **Same outside shape as Darb Budokai:** ports 8080–8088, Darb Budokai's topics and queues, `/actuator/health/*`, `/actuator/prometheus` with Darb Budokai's business metric names (`budokai_events_ingested_total{type,producer,result}`, `budokai_effects_emitted_total{type}`, `budokai_battlelog_compile_duration_seconds`), JSON logs with `traceId`, `userId`, `eventId`. Dashboards and alerts therefore work unchanged when the real services arrive.
- **Realistic internals that matter for observability:** transactional outbox table + relay (so outbox lag exists), idempotent inbox, Kafka consumer groups with retries and a DLT, RabbitMQ DLX, Postgres via one database and role per service (CNPG `Database` CRs).
- **Libraries:** FastAPI, uvicorn, aiokafka, aio-pika, psycopg 3 (async) + psycopg_pool, `jsonschema`, OpenTelemetry Python SDK with instrumentations for FastAPI, aiokafka, aio-pika, psycopg; manual propagation helpers where an instrumentation is missing. Structlog JSON logs.
- **gateway-service stand-in** serves a small GraphQL schema with Strawberry so GraphQL resolver spans exist; **notification-service** serves a WebSocket (STOMP framing optional, open question).
- **simulator** replays `config/simulator/scenarios/*.yaml` (Darb Budokai's scenario format, Darb Budokai ARCHITECTURE §7) and signs requests with Darb Budokai's HMAC scheme (`X-Budokai-Producer`, `X-Budokai-Signature`).

## 6. Telemetry pipeline

| Signal | Path | Notes |
|---|---|---|
| Traces | SDK (stand-ins) or Micrometer OTel bridge (Darb Budokai) → OTLP → **OTel Collector** (Deployment, `otel/opentelemetry-collector-contrib`) → Tempo | W3C `traceparent`/`tracestate` over HTTP, Kafka record headers and AMQP headers. Collector processors: `memory_limiter`, `k8sattributes`, `resource`, `tail_sampling` (keep 100% of error and slow traces, a configured percentage of the rest; policies in `config/sampling.yaml`), `batch`. |
| Span metrics + service graph | Collector `spanmetrics` and `servicegraph` connectors → Prometheus (remote write receiver) | Feeds RED dashboards and the Mesh Map edges (`traces_service_graph_request_total`, `..._server_seconds_bucket`, `..._failed_total`). Computed **before** tail sampling (separate pipeline) so metrics are complete. |
| Metrics | `/actuator/prometheus` → ServiceMonitor → Prometheus; Strimzi kafka-exporter (consumer lag), CNPG metrics, RabbitMQ Prometheus plugin, kube-state-metrics, node-exporter | Exemplars on, linking latency buckets to trace IDs. |
| Logs | stdout JSON → Collector `filelog` receiver (DaemonSet mode) → Loki | Grafana derived field `traceId` → Tempo; Tempo "trace to logs" → Loki. |
| Auto-instrumentation | OTel Operator `Instrumentation` CR, opt-in by pod annotation | Used for Darb Budokai's Java images if Nour wants the agent instead of Micrometer (open question); stand-ins instrument in code to show manual Kafka propagation. |

**Broken-trace guard:** the e2e suite sends N simulator events and asserts in Tempo (TraceQL) that each has exactly one root span in `ingest-service` and spans in every expected consumer from `config/topology.yaml`.

## 7. Dashboards, SLOs, alerts and runbook

**Dashboards as code** (`observability/dashboards/`), generated with the Grafana Foundation SDK (Python) from `config/dashboards/*.yaml` (panel thresholds, which services, which SLOs), provisioned into Grafana by sidecar ConfigMaps. Proposed set:

| Dashboard | Question it answers |
|---|---|
| Darb Budokai Overview | Are users OK right now? SLO status per journey, error budget left, top failing service |
| Service (templated by `service`) | RED per endpoint and per consumer, saturation, recent slow traces (exemplars), logs |
| Event Flow | Is the event river flowing? ingest accepted/rejected/duplicate, per-topic produce rate, consumer lag per group, outbox backlog, DLT counts |
| Jobs | RabbitMQ queue depth, ack rate, DLX, nightly battlelog compile duration |
| Data | CNPG connections, transaction rate, locks, replication (if any), slow queries |
| Platform | node/pod resources, restarts, OOM kills, collector drops, Tempo/Loki ingestion health |
| Drill | the panels a drill needs, plus annotations for drill start/stop |

**SLOs** (`observability/slo/*.yaml`, Sloth format, targets from `config/slo.yaml`, values proposed):
- Ingest availability: share of `POST /ingest/v1/events` not 5xx.
- Event-to-effect latency: share of life events whose first effect is published within a threshold (from span metrics on the effect publish span with the life event as causation).
- GraphQL query latency and availability at gateway-service.
- Nightly battle log: compile succeeds before the configured morning time.

Sloth generates multi-window multi-burn-rate `PrometheusRule`s. Extra symptom/cause alerts in `observability/alerts/`: consumer lag above threshold for N minutes, DLT messages > 0, outbox backlog growing, pod crashlooping, PVC above threshold, Collector dropping spans, Tempo ingestion errors. Every rule has `runbook_url` → `runbook/alerts/<AlertName>.md` and a `promtool test rules` unit test.

**Alertmanager receivers** (open question): a local `alert-sink` (tiny webhook logger shown in the Mesh Map's alert rail) by default; optional Telegram/Discord/email via env.

**Runbook** (`runbook/`): one page per alert (meaning, user impact, first five minutes, dashboards, ready-to-paste PromQL/TraceQL/LogQL, likely causes ranked, mitigation, rollback, verification), a "how to read a trace" page, and `runbook/drills/` write-ups.

## 8. Chaos drills

Chaos Mesh 2.x installed with namespace filtering; only namespaces labelled `darb-genki/chaos=allowed` can be targeted. Fault switches inside stand-ins cover what Chaos Mesh cannot express (poison messages, connection hoarding, dropped context). Drill definitions in `chaos/drills/<name>.yaml` (experiment manifests or fault-switch patches, duration, expected alert, expected dashboard signal, hypothesis). Proposed starting set:

| Drill | Injection | What the traces should show | Expected alert |
|---|---|---|---|
| `slow-road` | NetworkChaos delay between quest-service and Postgres | long `db` spans under quest consumer spans; Mesh Map road amber | event-to-effect latency burn |
| `poison-message` | stand-in `poison_on_type` on character-service | repeated consumer spans with exceptions, then DLT publish span | DLT messages > 0 |
| `broker-down` | PodChaos kill the Kafka node | producer retry spans, gap then catch-up; outbox backlog | consumer lag, outbox backlog |
| `bad-rollout` | Helm upgrade with a broken env value | no spans from new pods; readiness failing; `helm rollback` | pod crashloop / availability burn |
| `cpu-starved` | StressChaos on battlelog-service | stretched compile spans | nightly compile late |
| `pool-exhaustion` | stand-in `hold_db_connections` on spellbook-service | long waits before `db` spans; gateway timeouts | GraphQL latency burn |
| `clock-skew` | TimeChaos on ingest-service | signature check spans rejecting; `budokai.ingest.rejected.v1` spike | ingest rejection spike |
| `lost-context` | stand-in `drop_trace_context` on inventory-service | traces split in two; service graph shows an `unknown` client | broken-trace check (e2e / recording rule) |

`make drill BLIND=1` picks one at random without saying which; Nour diagnoses from Grafana, Tempo and the Mesh Map; `make drill-reveal` prints the answer. Each drill ends with a write-up in `runbook/drills/YYYY-MM-DD-<name>.md` (hypothesis, timeline, the trace ID and query that found it, fix, follow-ups). Drill start/stop are pushed as Grafana annotations.

## 9. Mesh Map (signature UI)

- **Frontend** (`mesh-map/web/`): Angular (the version Darb Budokai uses) + Three.js, sharing Darb Budokai's design tokens where the chosen art direction allows. Details in `UI_DESIGN.md`.
- **BFF** (`mesh-map/api/`): FastAPI. Endpoints: `GET /api/graph` (nodes and edges with rate, p95, error ratio from Prometheus service-graph metrics, queries in `config/mesh-map/queries.yaml`), `GET /api/edges/{id}` (RED history, slowest recent traces via Tempo TraceQL search), `GET /api/traces/{id}` (spans mapped onto the road network), `GET /api/stream` (Server-Sent Events: a sample of recent traces, re-timed as "lights", rate cap from config), `GET /api/alerts` (Alertmanager API), `GET /api/drill` (current drill, unless blind). Layout positions and road types from `config/topology.yaml` + `config/mesh-map/layout.yaml`.
- **Modes:** `demo` (seed traces from `config/seed/demo/`), `live` (cluster). Demo is labelled.
- The BFF is itself traced but filtered out of the map by config.

## 10. Cost

| Setup | What | Monthly cost (approx., October 2026, verify at purchase) |
|---|---|---|
| **kind / k3d on Nour's machine (default)** | everything | **$0** (needs ~10–12 GB RAM free for `full`, ~6 GB for `lite`) |
| GitHub Actions | CI with kind e2e on public repo | $0 (free minutes for public repos; private repo uses the free monthly allowance) |
| GHCR | container images | $0 for public images |
| Oracle Cloud OKE, Always Free Ampere A1 (4 OCPU, 24 GB) | basic cluster, free control plane | **$0**, but signup friction and capacity limits |
| **GKE Standard, zonal, 2× e2-standard-4 spot nodes** (proposed managed option) | free tier covers one zonal cluster's management fee | **~$35–60** (spot pricing varies) + ~$18 for one external load balancer |
| DigitalOcean DOKS, 2× 4 GB nodes + LB | free control plane | ~$60 |
| Azure AKS free tier, 2× B4ms | free control plane | ~$120 |
| AWS EKS + 2× t3.large | $73 control plane | ~$150–160 |

Recommendation (proposed): stay local; if Nour wants a public live demo, run GKE spot for a demo weekend and delete it (`make cloud-down`), costing a few dollars. Nothing is created without Nour's "yes". Managed config lives in `config/cloud.yaml`; cluster creation uses the provider CLI or Terraform (open question), never click-ops.

**Teardown:** local `make down` (`kind delete cluster --name darb-genki`). Managed `make cloud-down` deletes the cluster, then checks for leftover load balancers and disks (provider CLI listing filtered by the `darb-genki` label) and prints them.

## 11. Config, not code

```
config/
├── topology.yaml            services, ports, routes, topics, queues, DBs, who calls whom (from Darb Budokai docs)
├── standins/<service>.yaml  latency profiles, effect probabilities, fault switches (off)
├── simulator/scenarios/     traffic scenarios (Darb Budokai's format)
├── sampling.yaml            tail sampling policies
├── slo.yaml                 SLO targets and windows
├── alerts.yaml              thresholds for non-SLO alerts
├── dashboards/*.yaml        dashboard content and thresholds
├── mesh-map/layout.yaml     place positions, road types, colours per state
├── mesh-map/queries.yaml    PromQL / TraceQL used by the BFF
├── copy/en/*.yaml           Mesh Map copy
├── cloud.yaml               optional managed cluster settings
└── seed/demo/               demo graph + traces for the UI (labelled "Demo data")
```

Helm values carry environment differences (`values/local.yaml`, `values/lite.yaml`, `values/cloud.yaml`, `values/standins.yaml`, `values/budokai.yaml`). JSON Schemas (`values.schema.json` per chart, `config/schema/*.json`) validate both in CI.

## 12. Local development

```bash
make up              # cluster + platform + observability (helmfile)
make deploy          # build images, push to kind-registry, install charts/budokai with values/standins.yaml
make sim SCENARIO=typical-day
make map grafana
```

Inner loop for one stand-in: `uv run uvicorn standins.app:app --reload` against port-forwarded Kafka/Postgres/Rabbit, or Testcontainers in tests. Inner loop for the Mesh Map: `npm --prefix mesh-map/web start` with `MESH_DATA_MODE=demo` (no cluster needed).

## 13. Testing strategy

| Level | Tool | What |
|---|---|---|
| Chart unit | helm-unittest | every template: security context, probes, NetworkPolicy from topology, image swap, ServiceMonitor, OTel env |
| Chart schema | `values.schema.json`, kubeconform (with CRD schemas for Strimzi, CNPG, RabbitMQ, Gateway API, Chaos Mesh, monitoring.coreos.com) | rendered manifests valid |
| Chart install | chart-testing `ct install` on kind in CI | charts install and pass `helm test` hooks |
| Stand-in unit | pytest + in-memory span exporter | behaviour from config, outbox, inbox idempotency, context propagation on Kafka/AMQP headers, schema validation |
| Stand-in integration | pytest + Testcontainers (Kafka, Postgres, RabbitMQ) | consume → effect → outbox relay; DLT on poison; DLX on job failure |
| Collector config | `otelcol-contrib validate`, plus a test pipeline run with recorded OTLP input | sampling and connectors behave |
| Alerts | `promtool check rules`, `promtool test rules` | every alert fires and resolves as specified |
| Dashboards | pytest over generated JSON | every panel query references existing metrics (checked against a metrics list scraped in e2e), no emoji, thresholds from config |
| BFF | pytest with recorded Prometheus/Tempo responses | graph shaping, edge states, SSE rate cap |
| Mesh Map | Vitest or Jasmine/Karma per Angular setup, Playwright + axe, visual snapshots | screens, keyboard, reduced motion |
| End to end | pytest `tests/e2e` against kind | deploy, simulate, assert connected traces in Tempo, metrics in Prometheus, one drill fires its alert and resolves |
| Chaos safety | pytest | Chaos Mesh rejects experiments outside allowed namespaces; every drill has a duration |

CI never calls external services; images come from public registries only.
