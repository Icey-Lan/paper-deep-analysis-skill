# Report design-density review

Updated: 2026-08-14

## Why the first standalone renderer regressed

The first standalone build optimized for portability, escaping, offline use,
generic schemas, and explicit evidence boundaries. Those constraints were
correct, but the renderer was rebuilt as a generic wide card page instead of
extracting the Tracker report's editorial design system. The result preserved
safety while losing the visual behaviors that made the earlier report useful:

- a conclusion-led headline rather than the paper title as the dominant hero;
- a compact verdict and evidence-boundary strip near the top;
- paper-reported key metrics visible before the long analysis;
- an explicit method flow, evidence overview, and compact claim ledger;
- narrow reading width, sharp dividers, and differentiated section weights;
- report-language navigation instead of English chrome around Chinese content.

The visual reference was the existing Tracker DataClawEval screenshot at
`agent-paper-tracker-codex/output/playwright/deep-read-desktop.png`, supported by
the earlier Product Design audit and deterministic template. The in-app browser
security policy still blocks a fresh automated screenshot of local report
files, so this change does not claim completed desktop/mobile/print visual QA.

## First refactor and user correction

The first refactor restored density but added an evidence-status meter and a
claim-strength distribution. User review correctly identified that these
graphics were difficult to interpret because the qualitative labels had no
publicly documented calibration and could be mistaken for rigorous paper
scores. The review also found untranslated interface text, overly visible
metric citations, fragmented paragraph-level citations, missing Introduction
narrative and concepts, a fixed Data Agent perspective, small text, and too many
repeating boxes.

These findings separate into three categories:

- design: reading progress, typography, color, information density, and less
  repetitive framing;
- content: Introduction narrative, experiment table, multi-dimensional
  criticism, dynamic perspective, and concepts;
- evidence methodology: remove unexplained qualitative score graphics and keep
  evidence labels in canonical data rather than presenting them as measurements.

## Adopted design and content contract

The renderer now keeps the standalone safety model while restoring the earlier
editorial density:

1. `executive_summary.headline` supplies a short paper-centered `h1`; the paper
   title remains visible as source identity.
2. A CSS scroll-progress indicator gives the reader a page-position cue without
   adding JavaScript or a network dependency.
3. A three-column disclosure explains reading basis, judgment source, and model
   assistance in concrete Chinese wording for Chinese reports.
4. Evidence overview is one explicit sentence describing what the experiments
   support and what remains unverified.
5. `key_metrics` accepts at most six paper-reported quantities. Every item needs
   context and at least one evidence anchor.

## Second report-sample correction

The three-input review on 2026-08-14 exposed three remaining first-screen
problems: executive-summary copy had become a compressed specialist abstract,
six long metric values collided in one row, and the numbered narrative labels
sat slightly below the first line of body copy.

The reusable contract now treats the core conclusion as a two-sentence reading
hook for a curious AI explorer: familiar-language problem first, then the paper's
approach and clearest supported result. Chinese summaries target 90-160
characters, have a 220-character hard limit, and reject formula notation;
technical details remain available in Method, Evidence, metrics, and Concepts.
The metric renderer places five or six values in a three-column grid, while
smaller sets retain one row. Narrative labels and prose explicitly align to the
same top edge. These changes were regenerated across all three evaluation
reports and the public example; deterministic validation passed for each. A
fresh browser screenshot comparison is still not claimed.
6. Metric anchors remain in canonical JSON but do not appear in the first-glance
   strip; the strip shows only value and meaning.
7. The Introduction narrative explicitly covers context, prior gap, importance,
   solution, and findings before listing contributions.
8. The method flow is generated from validated workflow statements.
9. Evidence uses an experiment table plus prose on strengths, weaknesses, and
   reusability. Claims use numbered claim/support units. No evidence meter or
   claim-strength distribution is rendered.
10. Criticism covers six dimensions and groups citations after a complete set of
    points. Profile choice is dynamic and begins with applicability, integration
    difficulty, and a summary judgment.
11. Concepts include formal definition, plain-language explanation, importance,
    and grouped sources.
12. The report stays offline and contains no script, SVG, Mermaid, remote font,
    or model-authored markup.

## Third comparison: the executive summary and reading rhythm

The owner compared three DataClawEval reports. The original Hermes report had
the strongest core summary because it named both the expanded end-to-end task
and the experimental distinction between aggregate score, cross-engine ability,
stability, and tool cost. The first standalone report preserved the evaluation
object and graders but weakened the main finding. The next refactor accidentally
promoted the analyst's limitation judgment into the largest summary text.

The schema now prevents those jobs from collapsing:

- `core_conclusion` states the paper's gap or task, named approach or study
  object, and strongest supported result;
- `why_it_matters` explains reader relevance;
- `analyst_verdict` contains transfer judgment and limitations; and
- `evidence_summary` states the support boundary.

The representative report now uses the paper-centered core first. A validator
rejects common review-style openings such as "this is a valuable paper, but..."
and rejects a core conclusion duplicated from the analyst verdict. This is a
guardrail, not proof that the summary is scientifically correct.

The typography pass uses the local platform UI stack first, a restrained serif
display stack for research headings, a 49rem reading measure, consistent
section spacing, tabular figures, and equal metric columns separated by neutral
rules. Criticism and concepts now use numbered editorial units rather than
repeating multi-color top borders and boxed cards. The sticky table of contents
uses CSS view timelines to indicate the section crossing the reading zone; the
page remains self-contained and script-free. Browsers without scroll-driven CSS
animation retain a usable static table of contents.

## Deterministic acceptance checks

- one `main` and one `h1`;
- a CSS reading-progress element and print rule that hides it;
- at least one captioned explanatory figure;
- no `meter` element or unexplained qualitative evidence score;
- one compact experiment evidence table;
- narrative and concept sections reachable from navigation;
- current-section navigation styles and reduced-motion fallback are present;
- no external resources, active content, embedded SVG, unresolved fragments,
  placeholders, local absolute paths, or missing print CSS;
- schema and semantic validation for every key-metric anchor.

These checks establish output structure and provenance, not design quality or
scientific accuracy. The owner should reload the representative report and
review desktop, mobile, and print presentation before publication.
