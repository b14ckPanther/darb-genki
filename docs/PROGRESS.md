# Progress ledger

Agents update this file after **every** task (one row) and at every phase boundary. It is the first thing read after a context reset. `git log` is the truth if they ever disagree; fix this file first.

**Overall:** 0% · **Current phase:** 0 (not started) · **Current branch:** none · **Last updated:** YYYY-MM-DD

**Cluster state:** none · **Managed cluster:** none (cost $0) · **Darb Budokai images in use:** none (stand-ins)

## Phases

| Phase | Name | Weight | Status | Branch | Commit range | Skills used | Merged (Nour OK) |
|---|---|---|---|---|---|---|---|
| 0 | Repo bootstrap, CI, conventions | 5% | not started | `phase/00-bootstrap` | | | |
| 1 | Spec confirmation with Nour | 4% | not started | `phase/01-spec` | | | |
| 2 | Design system | 9% | not started | `phase/02-design-system` | | | |
| 3 | Mesh Map prototype on seed data | 12% | not started | `phase/03-ui-prototype` | | | |
| 4 | Local cluster and platform | 9% | not started | `phase/04-cluster-platform` | | | |
| 5 | Stand-in services and Helm charts | 12% | not started | `phase/05-standins-charts` | | | |
| 6 | OpenTelemetry end to end | 11% | not started | `phase/06-telemetry` | | | |
| 7 | Dashboards, SLOs, alerts, runbook | 9% | not started | `phase/07-dashboards-alerts` | | | |
| 8 | Mesh Map live | 8% | not started | `phase/08-mesh-map-live` | | | |
| 9 | Chaos drills | 8% | not started | `phase/09-chaos-drills` | | | |
| 10 | Hardening and CD | 6% | not started | `phase/10-hardening-cd` | | | |
| 11 | Darb Budokai swap-in, optional events, optional managed cluster | 3% | not started | `phase/11-budokai-cloud` | | | |
| 12 | Docs, demo GIF, public launch | 4% | not started | `phase/12-launch` | | | |

Status values: `not started`, `in progress`, `blocked`, `in review`, `done`.
Overall % = sum of weights of `done` phases + (weight × completed tasks / total tasks) for the phase in progress.

## Task ledger (current phase)

| # | Phase | Task | Status | Commits (first..last) | Tests run → result | Skills used | Notes |
|---|---|---|---|---|---|---|---|
| 0.1 | 0 | Confirm repo name, visibility, licence with Nour | not started | | | | |

Example row:
`| 6.1 | 6 | Keep one trace across Kafka produce/consume | done | a1b2c3d..e4f5a6b | uv run pytest standins/tests/test_propagation.py → 7 passed | superpowers:test-driven-development | context in Kafka headers via W3C propagator |`

## Rulings (decisions made without Nour)

Every time an agent decides something Nour has not decided. If "cost if wrong" is high, stop and ask instead.

| Date | Phase | Ruling | Why | Cost if wrong (low/med/high + what breaks) | Confirmed by Nour? |
|---|---|---|---|---|---|
| | | | | | |

## Cloud actions (managed cluster create/delete, image publishing)

| Date | Action | Nour's "yes" (where/when) | Provider/region | Estimated / actual cost | Result |
|---|---|---|---|---|---|
| | | | | | |

## Drills

| Date | Drill | Blind? | Time to detect | Time to diagnose | Correct? | Write-up |
|---|---|---|---|---|---|---|
| | | | | | | |

## UI and dashboard approvals

| Date | Screen or dashboard | Screenshot path | Nour's verdict | Follow-ups |
|---|---|---|---|---|
| | | | | |

## Blockers and waiting on Nour

| Since | What | Asked how | Status |
|---|---|---|---|
| | | | |

## Session log

Short notes per session (2 to 4 lines): what was done, where it stopped, next step.

- YYYY-MM-DD:
