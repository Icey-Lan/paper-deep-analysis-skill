# Quality and validation

Quality is treated as a set of observable checks, not a single score.

## Required gates

- input identity and SHA-256 are recorded;
- the PDF is valid, readable, within configured limits, and text-bearing;
- every material claim has at least one page or section evidence anchor;
- every displayed key metric has context and at least one evidence anchor;
- each statement is labeled as `paper_claim`, `analyst_inference`, or
  `derived_lesson`;
- uncertainty, missing evidence, and extraction limits are visible;
- JSON and JSONL conform to bundled schemas;
- generated HTML contains one `main`, one `h1`, a skip link, print styles, no
  external scripts, and no unescaped model-authored markup;
- generated HTML contains a reading-progress indicator, captioned method flow,
  CSS current-section navigation, a paper-centered core conclusion separated
  from the analyst verdict, experiment evidence table, Introduction narrative,
  dynamic profile summary, and concepts;
- generated HTML contains no evidence meter, claim-strength distribution, or
  qualitative status converted into a pseudo-quantitative graphic;
- public artifacts do not contain the source PDF, full extracted text, local
  absolute paths, credentials, or cookies;
- run provenance names the host and model honestly and does not invent metrics.
- Codex and Claude Code project entries resolve to the same canonical Skill;
- the standalone release archive contains only allowlisted runtime file types,
  includes the license, and matches its generated checksum manifest.

## Human review

Automated validation cannot establish that the analysis is scientifically
correct or useful. Before publication, a reviewer should check:

1. whether the report captures the paper's actual contribution;
2. whether the prominent core conclusion states the paper's problem, approach,
   and strongest finding rather than the reviewer's evaluation;
3. whether evidence anchors support the nearby interpretation;
4. whether counter-evidence and limitations are fairly represented;
5. whether actionable lessons go beyond paraphrasing the abstract;
6. whether the HTML remains readable on desktop, mobile, and print/PDF.

## Known limitations in v0.1

- pypdf reading order can be wrong for multi-column or unusual layouts.
- OCR is not bundled; image-only papers stop with an actionable failure.
- equation, table, and figure understanding depends on the host Agent's visual
  capabilities and explicit inspection.
- landing-page PDF discovery is intentionally conservative.
- schema validity does not prove factual validity.
