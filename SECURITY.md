# Security policy

## Supported version

Only the latest release on the default branch receives security fixes. The
current `0.1.0` build is a pre-release and has not received an independent
security audit.

## Reporting

Open a GitHub security advisory for suspected vulnerabilities. Do not attach
private papers, credentials, signed URLs, cookies, extracted full text, or
customer data. Use a minimal synthetic PDF and redact local paths.

## Scope reminders

The downloader blocks common SSRF targets and validates redirects, but it is not
a network sandbox. The Skill never needs browser cookies or authentication.
Run untrusted inputs with appropriate operating-system and network isolation.
