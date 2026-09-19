# Alphabetical topic selectors

Wyatt requested alphabetical topic pills on 2026-09-19. Sort topic choices by their visible label, left to right then top to bottom, in source/keyboard order.

Applies to Answers, Church History, Pioneer topics, the six Ask topic-option groups, and Watch theme choices. Keep the separate Tell My Story action after Pioneer topics. Preserve numbered/chronological reading journeys, primary navigation, scripture references and mixed action groups.

This release reorders 10 groups (115 topic choices), preserving every original label, destination, handler and selected state. Independent review compared exact element multisets and proved all other HTML content unchanged before the Answers script cache-version update. The content-audit update records the new reading order only; no doctrine or source wording changed. Existing heroes, art and layouts are preserved.

`tools/topic_pill_order_qa.py` is included in Site QA. The navigation runtime test also covers alphabetical fallback insertion of General Conference. Static site, internal-link/fragment, search-index freshness, media voice, content-audit and Pioneer interaction checks passed. Browser checks verified alphabetical DOM order across all five pages at desktop and narrow widths; keyboard order, history anchors, Ask expansion and Watch theme switching were exercised. Public deployment verification is recorded separately in the project state.

Rollback: revert this scoped release. No scheduler, provider, artwork or AI configuration changes apply.
