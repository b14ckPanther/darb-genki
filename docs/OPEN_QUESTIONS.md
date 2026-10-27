# Open questions (only Nour can decide)

The agent asks these in Phase 1, **one at a time**, open-ended first, in this order. Record each answer here (move it to "Answered" with the date) and in `DECISIONS.md`.

## Open-ended (ask first)

1. When you open the Mesh Map, what do you want to understand in the first five seconds? What would make you keep it open while you work on Darb Budokai?
2. Who should be impressed by this repo: platform/DevOps teams, backend teams, or SRE interviewers? What should they think after reading the README?
3. Which art direction in `UI_DESIGN.md` §4 (Ember Atlas Roads, Transit Diagram, Night Flight) feels right, or what would you change?
4. What does a good drill feel like for you: a timed blind challenge, or a guided lesson? Do you want a score?
5. Should keeping Darb Budokai's roads healthy matter inside Darb Budokai's game? If yes, how (see the optional `mesh.*` events in `INTEGRATION.md` §2)?

## Scope

6. Do you want the optional `mesh.*` events at all, given Darb Budokai's docs currently say Darb Genki emits none?
7. Should the Mesh Map ever be publicly hosted (needs a managed cluster or a recorded "replay" mode on a static host), or is a GIF and local run enough?
8. Is a sidecar service mesh (Linkerd or Istio ambient) wanted as an extra later, or explicitly out of scope?
9. Which drills from `ARCHITECTURE.md` §8 matter most to you? Any failure you have seen in real work that you want to rehearse?

## Machine and tools

10. What machine will run the cluster (RAM, CPU, macOS/Linux, Docker Desktop, OrbStack or Colima)? This decides the default `full` vs `lite` profile.
11. kind only, or keep k3d working too?
12. Alert delivery: local `alert-sink` only, or also Telegram, Discord or email?

## Stack

13. Stand-ins in Python (proposed) or another language?
14. Mesh Map frontend in Angular (matches Darb Budokai, proposed) or React?
15. Dashboards as code: Grafana Foundation SDK in Python (proposed) or Grafonnet?
16. When Darb Budokai's real images exist: OTel Java agent through the Operator, or Darb Budokai's built-in Micrometer OTel bridge?

## Cloud and cost

17. Managed cluster: never, demo weekends only, or always on? Which provider (GKE spot ~$35–60/month proposed; Oracle Always Free $0; DOKS ~$60; EKS ~$150)?
18. If managed: create it with the provider CLI (simpler) or Terraform (more to show, overlaps with Darb Ki)?
19. Publish images publicly on GHCR at launch: yes or no?

## Repo

20. Repo name `darb-genki`, private while building, MIT licence: OK?

## Answered

| # | Date | Answer | ADR |
|---|---|---|---|
| | | | |
