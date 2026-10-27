# AGENTS.md

This repo's full agent manual is **`CLAUDE.md`**. Every agent tool (Codex, Cursor, Copilot, Gemini, Aider, others) must read and follow it. This is a summary; if anything differs, `CLAUDE.md` wins.

## Non-negotiable rules

1. **No AI contributors.** "Never add "Co-Authored-By" or any other AI attribution line to commit messages, pull request descriptions, or any other text, in any project. Commit messages end with the last line of the actual description." Every commit is authored and committed as `Nour Alden Mousa <nmcryptoinvest@gmail.com>` (`git config user.name/user.email` set in the repo). Never write the word "claude" in a commit message.
2. **No hardcoded data.** Topology, stand-in behaviour, SLO targets, alert thresholds, map layout, copy and seed content live in `config/**.yaml`, Helm values, env vars or the database. Fixtures only in tests and the labelled demo mode.
3. **Secrets** only in env vars, a git-ignored `.env`, or Kubernetes Secrets created from them (never committed); keep `.env.example` current.
4. **Original assets only** (Google Fonts OK). Log third-party assets in `ASSETS.md`.
5. **Ask Nour first** before creating/publicising the repo, pushing to `main`, merging, publishing, creating any paid cluster, or deleting. Local kind clusters are free to create and delete. One branch per phase (`phase/NN-name`), small honest commits.
6. **TDD.** Failing test first. helm-unittest for charts, pytest for stand-ins and BFF, Vitest/Jasmine + Playwright for the UI, kind e2e for the stack. No live third-party services in CI.
7. **UI first.** Design system, then the Mesh Map prototype on seed data approved screen by screen, before cluster work. Responsive, keyboard accessible, reduced motion, WCAG AA. Native feel on mobile, one modern SVG icon set, **no emoji anywhere**.
8. **Skills.** Check the installed skill list before every task and invoke every matching one (table in `CLAUDE.md` §2, per-phase list in `docs/PLAN.md`). Record skills used in `docs/PROGRESS.md`.
9. **Workflow:** brainstorm → spec (`docs/specs/`) → plan (`docs/plans/`) → execute with ledger (`docs/PROGRESS.md`) → whole-branch review → finish.

## Before every push

```bash
git log --format='%an %ae%n%cn %ce' | sort -u          # only: Nour Alden Mousa nmcryptoinvest@gmail.com
git log --format=%B | grep -ciE 'co-authored|claude|anthropic|generated with'   # must be 0
make check-emoji
```

## Resume after a reset

Read `CLAUDE.md`, then `docs/PROGRESS.md`, then `git log --oneline -20`, then the current phase in `docs/PLAN.md`.
