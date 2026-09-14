# Section spacing review, 14 September 2026

Owner request: reduce the empty bands between History navigation, Joseph's
portrait link, the Evidences link and source note; inspect every public page for
the same issue without squeezing content or changing the site's presentation.

The cause was accumulated edge padding. History's compact sections contributed
56px on each side at desktop, while ordinary sections contributed 82px. The
visible card gaps were therefore 112px or 138px. Evidences navigation similarly
combined 82px of section padding with the reading article's 40px margin.

The shared body rules now use 16–24px per section edge, producing 32–48px between
ordinary sections. Resource cards retain their internal padding and use
32–48px external spacing, with half-gap margins next to padded sections. Ask's
body transitions and the Art featured section use the same spacing tokens.
Pioneer sections are checked after the shared script creates their main wrapper.
The old section token remains unchanged because other presentation regions use it.

Validation: 37 public pages at 390×844 and 1280×900, 74 settled browser cases,
584 visible section observations, no horizontal overflow. The compared hero and
opening rectangles did not change. The History gaps measure 32px and 48px;
Evidences navigation-to-reading uses the same total. Card interiors, typography,
artwork, source text, opening height and Continue controls are unchanged.
All 102 existing local workflow checks pass. Independent diff review found no
blocking issue. Release workflow and published-browser evidence are recorded in
the canonical Current State and release receipt after deployment.

Custom bordered chapters on the likeness page and the Come, Follow Me and
Conference layouts retain their deliberate separation. Topic-study sections
already use compact margins; only their oversized ordinary section wrapper and
resource-card margins need the shared correction. Uniformity means comparable
visible breathing room, not identical padding inside every kind of component.

For future visual review, measure the visible gap across both neighboring
wrappers, including padding, margins and inner containers. Check all page
families, not only the page receiving a new callout. Wait for the freshly
navigated document's styles and layout to settle before accepting measurements;
an immediate post-navigation sample can report the previous style state. Check
section anchors, expanded evidence, readable card interiors, protected opening
geometry and actual screenshots alongside the geometry report.
