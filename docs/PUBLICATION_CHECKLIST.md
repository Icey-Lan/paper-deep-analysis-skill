# Publication checklist

- [x] All tests pass in an isolated local Python environment (43 tests on
      Python 3.14; CI matrices for 3.10/3.12 are configured but not yet run on
      GitHub).
- [x] Skill frontmatter passes the official `skills-ref validate` command.
- [x] Live local-PDF, public-PDF-URL, and arXiv-ID samples are recorded honestly;
      all three resolved to the same DataClawEval SHA-256 in local runs.
- [x] Failure cases include scanned PDF, malformed PDF, blocked private URL,
      oversized source, schema error, and unsupported landing page.
- [ ] HTML is visually reviewed at desktop and mobile widths and in print mode.
- [x] Example artifacts contain no absolute paths, secrets, cookies, full text,
      or unlicensed paper assets.
- [x] Dependency licenses and notices are reviewed; AGPL PyMuPDF was replaced
      with BSD-licensed pypdf.
- [ ] README screenshots match the current renderer.
- [x] Known limitations and AI-assistance disclosure are visible.
- [ ] Repository history contains no ignored PDF or extracted full text (verify
      again after the first local commit).
- [ ] Human owner confirms repository name, attribution, and GitHub remote before
      any push.
