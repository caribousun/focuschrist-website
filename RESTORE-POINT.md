# RESTORE POINT

September 1, 2026 — Final all-page Ask conversation and live-cache release

- Verified Ask runtime / production-gate merge commit: `baaa15a24e5b35101bde8a5046b86295310b50bb`
- Feature repair merge: `f58b232ed9386361285fafd44e5fea8390fe1868`
- Source policy: `2026-09-01.15`; cache version: `20260901-15`
- PR #56 feature CI `33474211249` and PR #57 live-gate CI `33475167356`: success
- Post-feature Site QA `33474356949`, Worker `33474356964`, and Pages `33474356962`: success
- Current Pages run `33475248240` and Site QA/live production run `33475248219`: success
- Live production gate verified 15 exact assets / 15 canonical cache keys after a stability interval and passed Lincoln, Joseph Smith, Handcart Companies, plural marriage, Jesus Christ, chaining, reset, and competing-identity contracts.
- Independent adversarial verification passed for both the feature repair and the permanent production gate.
- Feature rollback boundary: `a51ff33ca805eb5122a0b35ff421b3277c37668a` is the pre-.15 production commit. Use only through a deliberate reviewed rollback.
- Gate-only rollback boundary: `f58b232ed9386361285fafd44e5fea8390fe1868` preserves the .15 feature repair without the post-deploy gate.

Previous restore point:

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
