# Integration with the universe

Darb Genki is the runtime home for Darb Budokai's services, so it depends on Darb Budokai's **contracts** (service shapes, topics, schemas). It does **not** depend on Darb Budokai's **code** existing: stand-ins cover that. Sending events into Darb Budokai is a **later, optional phase** (Phase 11 in `PLAN.md`).

## 1. What Darb Genki consumes

| From | What | How | Where |
|---|---|---|---|
| Darb Budokai `docs/ARCHITECTURE.md` §3–§5 | services, ports, owned DBs, Kafka topics (partitions, retention, DLTs), RabbitMQ exchange/queues/DLX | transcribed into `config/topology.yaml` (Phase 5); re-checked when Darb Budokai changes | stand-ins, NetworkPolicies, KafkaTopic/Queue CRs, Mesh Map layout |
| Darb Budokai `docs/EVENT_CONTRACTS.md` | CloudEvents 1.0 envelope with Darb Budokai extensions (`budokaiuserid`, `budokaievidence`, `budokaimode`, `causationid`, `correlationid`, `rulebookversion`), JSON Schema 2020-12 payloads, ingest API with HMAC headers | `make sync-contracts` copies `contracts/events/**` from Darb Budokai's repo at a pinned ref into `contracts/budokai/`; until Darb Budokai has schema files, a snapshot is written from the doc and marked `x-standin-snapshot: true` | stand-ins validate everything they consume and produce; simulator signs requests |
| Darb Budokai `docs/ARCHITECTURE.md` §11 | observability hooks: `/actuator/health/{liveness,readiness}`, `/actuator/prometheus`, OTLP via `MANAGEMENT_OTLP_TRACING_ENDPOINT`, Kafka/Rabbit observation, ECS JSON logs with `traceId`, `userId`, `eventId`, business metrics `budokai.events.ingested`, `budokai.effects.emitted`, `budokai.battlelog.compile.duration`, `budokai.sm2.reviews` | stand-ins expose the same; charts wire the env | dashboards, alerts, Mesh Map |
| Darb Budokai topic `budokai.ingest.rejected.v1` | audit trail of rejected events (Darb Budokai notes it is for "ops visibility; Darb Genki later") | Kafka consumer in the observability tooling is **not** needed: kafka-exporter rates + a small stand-in metric `budokai_ingest_rejected_total{reason}` | Event Flow dashboard, ingest rejection alert, `clock-skew` drill |
| Darb Budokai simulator scenarios | `config/simulator/scenarios/*.yaml` format | same format; copied scenarios from Darb Budokai when they exist | traffic generation |
| Darb Budokai container images (later) | `ghcr.io/b14ckpanther/budokai-<service>:<tag>` (proposed) | `values/budokai.yaml` replaces stand-in images service by service | Phase 11 |

Darb Budokai's `EVENT_CONTRACTS.md` §3.7 currently says: "Darb Genki: No domain events. Consumes OpenTelemetry traces, metrics and logs." The optional events below would change that; if Nour wants them, Darb Budokai's doc is updated in Darb Budokai's repo first.

## 2. Events emitted (optional, proposed, confirm with Nour in Phase 1)

Game meaning (proposed): keeping Darb Budokai's roads healthy is engineering work; a diagnosed drill is a fought battle. Rewards go to **diagnosis and recovery**, never to causing outages.

Source: `urn:budokai:producer:darb-genki`. Producer scope: `mesh.*`. Envelope per Darb Budokai's EVENT_CONTRACTS §1, with `budokaievidence.tier = "verified"` and `ref` pointing to the drill write-up path or commit. IDs are UUIDv5 over the natural key.

### `genki.drill.completed` v1

Written when Nour closes a drill with `make drill-close NAME=... DIAGNOSED=yes|no MINUTES=n`, which also requires the write-up file to exist.

```json
{
  "drillId": "2026-11-03-slow-road",
  "drill": "slow-road",
  "blind": true,
  "startedAt": "2026-11-03T19:02:00+02:00",
  "detectedAt": "2026-11-03T19:05:40+02:00",
  "diagnosedAt": "2026-11-03T19:11:10+02:00",
  "recoveredAt": "2026-11-03T19:13:00+02:00",
  "diagnosedCorrectly": true,
  "alertsFired": ["BudokaiEventToEffectLatencyBurn"],
  "writeUpUrl": "https://github.com/b14ckPanther/darb-darb-genki/blob/main/runbook/drills/2026-11-03-slow-road.md"
}
```
Required: `drillId`, `drill`, `blind`, `startedAt`, `diagnosedCorrectly`. Natural key: `drillId`.

### `genki.slo.breached` v1 and `genki.slo.recovered` v1

From Alertmanager webhook (SLO burn alerts only), for the battle log's "the roads were blocked" moments. Optional.

```json
{ "slo": "event-to-effect-latency", "window": "1h", "burnRate": 14.4, "firedAt": "2026-11-03T19:05:40Z", "alertName": "BudokaiEventToEffectLatencyBurn" }
```
Natural key: `alertName + firedAt`. `recovered` adds `resolvedAt`.

## 3. Files in this repo

```
contracts/
├── budokai/                          synced from Darb Budokai (read-only here; never edited by hand)
└── mesh/
    ├── genki.drill.completed/v1.schema.json   + examples/valid-*.json, invalid-*.json
    ├── genki.slo.breached/v1.schema.json
    └── genki.slo.recovered/v1.schema.json
```

Versioning follows Darb Budokai's rules: additive optional fields stay in `v1`; anything else is a new `v2` beside `v1`, plus an ADR.

## 4. Outbound adapter

- An outbox table in a small SQLite file on the `mesh-map-api` pod's persistent volume (proposed) holds events. They are always written, whether Darb Budokai runs or not.
- `mesh-map/api` contains the adapter: wraps events in the CloudEvents envelope, signs with `X-Budokai-Producer` and `X-Budokai-Signature: t=<unix>,v1=<hex HMAC-SHA256(secret, t + "." + body)>`, posts to Darb Budokai's `POST /ingest/v1/events:batch` (in-cluster: `http://ingest-service.budokai:8082`), treats 202 duplicates as success, retries with backoff.
- Disabled unless `REALM_INGEST_URL`, `REALM_PRODUCER_KEY_ID`, `REALM_PRODUCER_SECRET` are set.
- Tests use `pytest-httpserver` as a fake ingest; in the kind e2e, the **stand-in** ingest-service receives them, which proves the path before Darb Budokai exists.

## 5. Siblings

- **Darb Budokai**: the system being run and observed.
- **Darb Enmacho** may later read the same Kafka topics in its own consumer group; Darb Genki would host that consumer only if Nour wants Darb Enmacho's GCP connector to run in the cluster (out of scope by default).
- **Darb Kaioken** publishes drill write-ups and the Mesh Map as an explorable post.
- **Darb Ki** is unrelated at runtime (separate AWS stack).

## 6. Integration phase checklist (Phase 11)

1. Ask Nour whether Darb Budokai has published images and contract files.
2. `make sync-contracts` at Darb Budokai's tag; remove `x-standin-snapshot` files that now have real counterparts; run all tests.
3. Swap one service at a time in `values/budokai.yaml` (start with `ingest-service`); run `make e2e`; compare dashboards before/after; fix chart gaps (e.g. JVM memory settings, startup probes for Spring Boot).
4. Decide with Nour whether to use the OTel Java agent (Operator `Instrumentation` CR) or Darb Budokai's built-in Micrometer OTel bridge.
5. If Nour wants the optional events: PR in Darb Budokai's repo adding `mesh.*` to `EVENT_CONTRACTS.md`, producer key scope, rulebook entries; then enable the adapter.
