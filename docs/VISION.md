# Vision

## 1. Intent

Prove, in public, that Nour can run a real event-driven microservice system on Kubernetes and **find out why it broke** using the traces. Not "I deployed some pods", but "here is a request crossing nine services, two brokers and five databases; here is the drill where I made one road slow; here is the trace that showed me where, and the runbook page I wrote afterwards".

It is also Darb Budokai's home: the place where Darb Budokai's services actually run together, with the observability Darb Budokai's code was built to expose.

## 2. Goals

1. **Darb Budokai on Kubernetes with Helm.** Every Darb Budokai service, plus Postgres, Kafka and RabbitMQ, deployed by charts from one command on a free local cluster.
2. **End-to-end tracing.** One trace follows a life event from the ingest HTTP call, through Kafka, into each domain service, through the outbox, into notification and the nightly RabbitMQ job. No broken traces.
3. **Dashboards, alerts and a runbook that a stranger could use.** SLOs per user-facing path, burn-rate alerts, one runbook page per alert.
4. **Chaos drills.** A library of reproducible failures. Each drill ends with a written diagnosis that cites the trace, query and dashboard used.
5. **The Mesh Map.** A signature live view: requests as light along the roads between Darb Budokai's places; slow roads turn amber.
6. **Works before Darb Budokai exists.** Stand-in services built from Darb Budokai's contracts, swapped for the real images later without changing the charts.

## 3. Non-goals

- Not a re-implementation of Darb Budokai's game logic. Stand-ins mimic shape (endpoints, topics, timings, failure modes), not rules.
- Not a service mesh product (no Istio/Linkerd by default; "Mesh" is the name, not the tool). A sidecar mesh is an open question.
- Not multi-cluster, multi-region or production high availability.
- Not a Grafana plugin or a general observability product.
- No paid SaaS observability (Datadog, Grafana Cloud paid tiers, New Relic).

## 4. Anti-goals (failure even if it works)

- Dashboards nobody can read: walls of default panels with no question they answer.
- Alerts without a runbook, or alerts that fire on causes (CPU) instead of symptoms users feel.
- Drills that are staged: the answer known in advance and the trace screenshot faked. Every drill write-up must be reproducible with `make drill NAME=...`.
- Traces that break at the broker boundary, so the "end-to-end" claim is false.
- A Mesh Map that animates fake traffic in live mode. Demo data is always labelled.
- A surprise cloud bill.
- Charts that only work on Nour's laptop (hardcoded hostnames, image tags, sizes).

## 5. Why this stack for the Israeli junior market

From 431 Israeli listings: Cloud 256, Kubernetes 146, Microservices 127, Kafka 61, AWS 191, GCP 95. Nour's GitHub today is ~90% Next.js/Supabase/TypeScript, with no Kubernetes, Helm or observability.

- **Kubernetes + Helm** is the most requested infrastructure skill after "cloud" itself, and juniors rarely show it beyond a tutorial deployment.
- **OpenTelemetry + Grafana** is the vendor-neutral standard most Israeli companies are moving to; tracing across Kafka is a hard, interview-worthy detail.
- **Microservices + Kafka** ties directly to Darb Budokai, so the system being observed is real and non-trivial.
- **SRE practice** (SLOs, runbooks, chaos drills, postmortems) is rare in junior portfolios and is exactly what platform, DevOps and backend teams ask about.
- The **Mesh Map** keeps Nour's frontend strength visible.

## 6. Success measures (proposed, confirm with Nour in Phase 1)

- `make up && make deploy` from a clean checkout to a working stack in under 15 minutes on Nour's machine.
- 100% of simulator-generated life events produce one connected trace (asserted by the e2e suite).
- At least 6 drills, each with a reproducible write-up, diagnosed from traces.
- Every alert has a passing `promtool` test and a runbook page.
- Mesh Map at 60 fps with 200 lights in flight on Nour's laptop.
- Swapping one stand-in for a real Darb Budokai image is a values change only.
