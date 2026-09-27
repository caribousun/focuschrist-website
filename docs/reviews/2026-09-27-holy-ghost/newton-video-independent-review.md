# Independent video integration review

Reviewed holy-ghost-video.js, CSS, page markup and three DOM regressions. Accepted for candidate integration: exact selected video, no player request or autoplay on initial page load, accessible native preview and close controls, live loading/error status, fixed 15-second readiness timeout, disposal on close/error, stale callback generation checks, and permanent YouTube fallback. The component remains page-scoped.

QA now checks the exact preview/asset/source identity and dependency versions; wrong-video mutation is rejected. Existing art, scripture, chapter and Ask-return guards remain active. Workflow registers the three video tests using its existing jsdom installation.

DOM tests mock the provider and do not demonstrate real network playback, current embedding permission or owner aesthetic approval. Parent owns real-browser verification. A stalled provider API load can remain pending while the visible timeout offers the external fallback; that does not trap navigation or remove the fallback.

See newton-video-final-qa.json for command results. No publication or paid provider calls performed.
