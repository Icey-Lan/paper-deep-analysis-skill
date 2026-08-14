# Evidence guide

An evidence anchor locates support in the source. Use the PDF page index shown by
the extractor (`page` starts at 1), plus section/table/figure when known.

Good anchor:

```json
{
  "page": 7,
  "section": "4.2 Main results",
  "figure": null,
  "table": "Table 2",
  "note": "Comparison against the strongest reported baseline"
}
```

Do not cite “the paper,” the abstract, or a bibliography entry as evidence for a
specific result without a page or section. A source can be genuinely ambiguous;
record that in `note` rather than manufacturing precision.

## Evidence strength

- `strong`: direct result with suitable comparison and enough detail to inspect;
- `moderate`: relevant evidence with a meaningful limitation;
- `weak`: indirect, incomplete, anecdotal, or under-specified evidence;
- `not_reported`: the paper provides no supporting evidence found during review.

This describes support in the paper, not whether the claim is universally true.
Keep these labels in canonical data for validation and downstream learning. Do
not convert them into visual bar lengths, percentages, radar charts, or an
overall paper score unless the user supplies a separate, documented scoring
rubric. In the human report, explain the concrete evidence and its limits in
prose.

## Attribution

- `paper_claim` must be a faithful paraphrase of an author claim or result.
- `analyst_inference` must make the reasoning step visible and avoid author voice.
- `derived_lesson` must state conditions and limits; it is not a hidden claim that
  the authors proved the lesson.

Avoid long quotations. Evidence snippets, if used, should be necessary, short,
and attributed.
