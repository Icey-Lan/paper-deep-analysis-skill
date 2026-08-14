# Publication checklist

- [x] All tests pass in an isolated local Python environment (60 tests on
      Python 3.14) and in public GitHub Actions on Python 3.10 and 3.12.
- [x] Skill frontmatter passes the official `skills-ref validate` command.
- [x] Codex and Claude Code project entries resolve to one canonical Skill and
      both pass `skills-ref validate`.
- [x] The deterministic runtime-only ZIP contains no tests, caches, local work
      data, paper PDF, or extracted full text; manifest and archive hashes match.
- [x] Live local-PDF, public-PDF-URL, and arXiv-ID samples are recorded honestly;
      all three resolved to the same DataClawEval SHA-256 in local runs.
- [x] Failure cases include scanned PDF, malformed PDF, blocked private URL,
      oversized source, schema error, and unsupported landing page.
- [x] Current desktop HTML was reviewed positively by the owner.
- [ ] Mobile-width and print-mode visual review is still pending.
- [x] Example artifacts contain no absolute paths, secrets, cookies, full text,
      or unlicensed paper assets.
- [x] Dependency licenses and notices are reviewed; AGPL PyMuPDF was replaced
      with BSD-licensed pypdf.
- [x] README contains no stale renderer screenshot.
- [x] Known limitations and AI-assistance disclosure are visible.
- [x] Local repository history contains no PDF, `pages.jsonl`, `source.pdf`,
      `.env`, detected secret, or user-specific absolute path after checkpoint
      commit `6cce3f1`.
- [x] Human owner confirmed the repository name, attribution, and public GitHub
      remote `Icey-Lan/paper-deep-analysis-skill` before the first push.
