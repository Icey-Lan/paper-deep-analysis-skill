# Failure catalog

Failures are expected states. Do not create partial public artifacts after a
blocking failure. Record the code, safe message, recovery, and whether any
source material was retained locally.

| Code | Meaning | Safe recovery |
|---|---|---|
| `input.not_found` | Local path does not exist or input type is unknown | Correct the input or provide a PDF/URL/arXiv ID |
| `input.not_pdf` | Local file or response is not a valid PDF | Provide the intended PDF |
| `input.encrypted` | PDF needs a password | Provide an authorized decrypted copy |
| `input.ocr_required` | Too little text was extracted | Run authorized OCR separately, then retry |
| `limit.bytes` | Download or local file is too large | Review the limit; raise it only with explicit approval |
| `limit.pages` | PDF has too many pages | Narrow the source or approve a reviewed limit change |
| `limit.text` | Extracted text exceeds the bound | Narrow the source or approve a reviewed limit change |
| `network.scheme` | URL is not HTTPS | Use HTTPS or an authorized local PDF |
| `network.private` | Host resolves to a non-public address | Do not fetch; provide a local PDF |
| `network.credentials` | URL embeds credentials | Remove credentials and use a public link/local PDF |
| `network.redirect` | Redirect is missing, excessive, or unsafe | Provide a final public PDF URL |
| `network.http_status` | Source returned an error | Check access without bypassing login/paywall |
| `landing.no_pdf` | No explicit public PDF link was found | Provide the direct PDF URL or local PDF |
| `landing.ambiguous` | Multiple PDF links are plausible | Choose the intended PDF URL |
| `schema.analysis` | Canonical JSON is invalid | Fix `analysis.json`; never patch generated HTML |
| `evidence.missing` | A material statement has no anchor | Re-read and add evidence or remove/calibrate the statement |
| `identity.mismatch` | Analysis/run hash or stable ID differs from source | Stop and resolve the source mix-up |
| `artifact.html` | HTML is active, external, malformed, or leaks local data | Fix renderer/data and regenerate |
| `artifact.dataset` | JSONL is invalid, duplicated, or leaks local data | Fix canonical analysis/exporter and regenerate |
| `review.visual_pending` | Browser/mobile/print visual review was not completed | Keep release blocked until a human or compliant browser reviews it |
