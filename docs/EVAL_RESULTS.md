# Evaluation results

Updated: 2026-08-14

## What was actually run

- 60 local automated tests after the summary-readability and layout refactor.
- 83% measured branch-aware code coverage in the local Python 3.14 environment.
- Public GitHub Actions passed the test, release-audit, and package-build jobs on
  Python 3.10 and 3.12, plus the independent Skill specification job.
- Official `skills-ref validate` against the bundled Skill directory.
- Live source preparation for the same DataClawEval paper through:
  - an existing local PDF;
  - arXiv ID `2607.28033`; and
  - direct public URL `https://export.arxiv.org/pdf/2607.28033`.
- All three live inputs produced SHA-256
  `038c793698ab91ec168f536621744d00a433ee4ef385f90986f0ca4484e13cfc`.
- A 16-page full-text `data-agent` analysis produced a self-contained HTML
  report and 72 JSONL learning records.
- Final example validation passed 14 named deterministic check groups with no errors
  or warnings.
- The HTML validator now requires a reading-progress indicator, captioned
  explanatory figure, compact experiment table, print styles, and no meter-style
  evidence score. Six DataClawEval key metrics remain source-anchored in the
  canonical analysis JSON but their citations are hidden from the visual strip.
- Summary tests require the paper-centered core to render before the separate
  analyst verdict, reject common review-style openings and formula notation,
  and enforce a 220-character hard limit for Chinese core summaries.
- Renderer regression tests cap five- or six-item desktop metric strips at three
  columns and require top-aligned narrative labels and prose.
- Renderer tests require CSS current-section timelines for the table of contents;
  this checks generated structure, not rendered-browser fidelity.
- Canonical Codex entry, Claude Code symlink entry, and generated standalone
  Skill directory all passed `skills-ref validate`.
- Deterministic release packaging produced 29 runtime files. Repeated builds
  matched byte-for-byte; the current ZIP SHA-256 is
  `56092176ba6a5ec2cb21bcc5282e6cb7258270a4713e99afcb5df364a6062f8e`.
- Release audit passed for 59 candidate repository files at this checkpoint.

## What these results do not establish

- No scientific-analysis accuracy, precision, recall, or stability was measured.
- The DataClawEval benchmark itself was not executed or reproduced.
- Trigger-routing eval prompts were specified but not benchmarked across fresh
  independent Agent sessions.
- Claude Code format discovery is validated, but the semantic workflow has not
  yet been forward-tested in an independent Claude Code session.
- Automated Product Design screenshot capture was blocked when the in-app
  browser rejected the local file URL. The owner subsequently approved the
  current desktop report; mobile and print visual review remains open.
- Evidence anchors pass structural checks; a human still needs to confirm that
  each anchor supports the nearby interpretation.

Use the current [DataClawEval report](../examples/data-claw/report.html) for
qualitative review. Do not turn the deterministic pass count into an accuracy
claim.
