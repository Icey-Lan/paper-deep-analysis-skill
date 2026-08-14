# Implementation status

Updated: 2026-08-14

## Baseline audit

The source `agent-paper-tracker` implementation was a repository-internal,
arXiv-first workflow. Reusable strengths were JSON-first rendering, escaped
HTML, explicit full-text/abstract boundaries, and visible model disclosure.

It was not standalone because it required Tracker database paths, required an
arXiv identifier, hardcoded Agent/product fields, and had no guarded URL/local
PDF resolver, claim-level evidence schema, public-safe source manifest, or
Agent-learning export. Existing Tracker changes were protected in local commit
`98fe22c`; untracked run data remains in the original Codex worktree.

## Standalone v0.1 phases

| Phase | Status | Verification |
|---|---|---|
| Contract and safety boundary | Complete | Skill metadata, schemas, safety/copyright docs, trigger eval set |
| Source preparation | Complete for v0.1 | Live local PDF, arXiv ID, and direct public URL resolved to the same hash; guarded/mocked failures |
| Canonical analysis | Complete, under review | Generic schema plus general/agent-systems/data-agent/custom profiles |
| HTML and JSONL artifacts | Complete, under visual review | Editorial layout, reading progress, current-section TOC, paper-centered executive summary, Introduction narrative, experiment evidence, six-dimensional critique, dynamic profile, concepts, 72-record live example |
| Automated quality suite | Complete for v0.1 code paths | 60 tests passed; 83% measured code coverage; no accuracy claim |
| Visual and print QA | Partially complete | Owner approved the current desktop report; automated capture remains blocked and mobile/print review is still required |
| Cross-client package | Complete for format compatibility | One canonical Skill, Claude Code symlink entry, deterministic 29-file ZIP, three `skills-ref` validations |
| Public release audit | Complete locally, awaiting owner release action | 60 candidate files pass license, secret, path, symlink, archive, and checksum checks; nothing pushed |

## Current limitations

- OCR is detected but not bundled.
- Landing-page PDF discovery is conservative.
- The host Agent, not a bundled model API, performs semantic analysis.
- The live DataClawEval example has not rerun the benchmark.
- Scientific fidelity still needs human review even after schema validation.
- Visual screenshot evidence is pending because the selected Product Design
  browser could not open the local report under its security policy.

See [DESIGN_DENSITY_REVIEW.md](DESIGN_DENSITY_REVIEW.md) for the design
regression analysis and the new deterministic visual contract.
