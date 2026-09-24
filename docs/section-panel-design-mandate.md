# Shared section-panel surface

Wyatt directed that section panels throughout the website follow the approved Home cards **Ask. Seek. Study.**, **Learn by Topic**, and **See and Remember**: the green-to-teal gradient, visible border, and narrow gold-accented left edge. This applies to existing text, related-study, resource, invitation, and reflection panels. Future panels must use this shared treatment rather than introduce flat dark surfaces.

The reference is `index.html .fc-home-purpose-paths .fc-card` in `site-system.css`. Its existing pixels and geometry remain unchanged. New shared tokens `--fc-panel-fill`, `--fc-panel-border`, `--fc-panel-shadow`, and `--fc-panel-hover-fill` reuse the Home palette. The accent is a background layer, and the outline can be inset, so no new positioned wrapper or dimension is required.

Apply the surface to a named panel component. Do not apply it indiscriminately to every `section`, article, reading paragraph, image, hero, dialog, button, pill, or grid wrapper. An image-and-reading composition is not automatically a panel: preserve the plain reading canvas and artwork framing. Keep existing padding, responsive layout, focus outlines, and natural height. Page-specific typography remains separate; descriptive text uses readable muted cream and headings use cream where the corresponding component owns those colors.

`section-panel-surfaces.json` identifies shared selectors, coordinated component owners, and explicit exclusions. `section-panel-inventory.json` records every current canonical-page consumer and every discovered panel-like class, plus runtime selector evidence. `tools/section_panel_surface_qa.py` rejects unclassified panel classes, inventory drift, missing shared stylesheets, and geometry changes inside the surface appendix. It is structural evidence, not a substitute for rendered desktop, phone, enlarged-text, hover, and focus review.

Do not infer aesthetic approval from this implementation or a technical pass. The original Home reference is approved; the expanded application still requires direct visual review.

The Mission work-card row has one separately scoped layout correction: `body.fc-site .fc-missionary-work-grid` uses an 18px gap and removes the obsolete enclosing strip border/background. Its original four-column desktop, two-column tablet and one-column phone rules remain in `missionary.css`. This prevents the new rounded panels from touching; it does not authorize changing other panel geometry.

## Named study controls

Scripture/source chips use distinct teal fill, light borders, cream text and 44px targets. Named Pioneer, Watch, Book of Mormon and Atonement navigation use that surface while retaining labels and destinations. Watch rows grow to fill their available width; numbered badges cannot shrink or wrap. Prose links, approved Home/History pills and explicit primary actions are excluded. Coverage and negative fixtures are recorded in study-link-controls.json, study-link-control-inventory.json and tools/study_link_controls_qa.js.
