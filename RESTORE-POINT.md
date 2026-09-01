# RESTORE POINT

September 1, 2026 — All-page Ask reliability release

- Production merge commit: `31c7ac9baf9ee9794b802d30c6cd66cff3bf31c8`
- Source policy: `2026-09-01.9`; cache version: `20260901-9`
- Main Ask, Pioneers, and Church History final-owner runtime suites passed.
- Independent adversarial verification passed before release.
- Live production acceptance passed for reviewed local answers, remote research, negative intent boundaries, sources, reset behavior, and restored controls.
- Owner regression passed: `What year did the handcarts begin?` returned 1856 with the official Handcart Companies source.
- Roll back to `8309d240f01d5fe8f628f1e9ab53451cad21f527` only if this release must be reverted.

Previous restore point:

April 3, 2026

- Added concurrency control to deploy-pages.yml
- Prevents deployment in progress errors
- Site verified working at focuschrist.com
