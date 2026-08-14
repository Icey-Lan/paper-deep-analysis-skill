# Evaluation results

Updated: 2026-08-14

## What was actually run

- 43 local automated tests after the public-URL identity fix.
- 82% measured branch-aware code coverage in the local Python 3.14 environment.
- Official `skills-ref validate` against the bundled Skill directory.
- Live source preparation for the same DataClawEval paper through:
  - an existing local PDF;
  - arXiv ID `2607.28033`; and
  - direct public URL `https://export.arxiv.org/pdf/2607.28033`.
- All three live inputs produced SHA-256
  `038c793698ab91ec168f536621744d00a433ee4ef385f90986f0ca4484e13cfc`.
- A 16-page full-text `data-agent` analysis produced a self-contained HTML
  report and 56 JSONL learning records.
- Final example validation passed 14 named deterministic checks with no errors
  or warnings.
- Release audit passed for 55 candidate repository files at that checkpoint.

## What these results do not establish

- No scientific-analysis accuracy, precision, recall, or stability was measured.
- The DataClawEval benchmark itself was not executed or reproduced.
- Trigger-routing eval prompts were specified but not benchmarked across fresh
  independent Agent sessions.
- GitHub Actions has not run because no remote has been created or pushed.
- Product Design screenshot audit was blocked when the in-app browser rejected
  the local file URL. Desktop, mobile, and print visual review remains open.
- Evidence anchors pass structural checks; a human still needs to confirm that
  each anchor supports the nearby interpretation.

Use [eval-review.html](../eval-review.html) to inspect the live example and
record qualitative feedback. Do not turn the deterministic pass count into an
accuracy claim.
