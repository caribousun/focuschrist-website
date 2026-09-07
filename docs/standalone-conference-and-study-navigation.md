# Standalone General Conference and current-study navigation

Owner clarification, September 7, 2026: General Conference belongs on its own page like Come, Follow Me. Every topic pill in Answers must show the selected topic in the menu with the same gold text and underline. This supersedes the embedded-Answers location in the earlier General Conference production prompt.

## Implemented behavior

- `general-conference.html` contains the complete source-reviewed April 2026 collection, six topic paths, 37 message cards, filtering, personal study prompts, enduring voices, and connected study links.
- Its opening occupies the first screen and uses approved study artwork. Short viewports allow content to continue naturally without clipping.
- General Conference appears as the active desktop and hamburger menu destination. Existing conference bookmarks on Answers forward to the new page; deep section bookmarks keep their destination. Answers retains a usable fallback link without JavaScript.
- The sixteen existing Answers topic pills resolve to their actual article or section. The current topic appears after Art in the desktop menu while the Answers parent remains available. Phone headers show the current study label beside the site name, with the full navigation in the hamburger menu.
- Hash changes update section labels and restore the parent state when leaving a section. Stand Forever is distinguished from its containing Look Unto Me study. The duplicate General Conference pill is prevented.

## Preservation and release checks

Source identities and thumbnail bytes remain unchanged. Shared-script revision changes refresh navigation without changing other page content. Permanent tests cover the complete collection, standalone metadata, legacy routing, all sixteen actual pill destinations, repeated hash transitions, parent links, current-state attributes, and duplicate prevention. Source review and content-audit records are required before release.

Desktop and phone screenshots were inspected during implementation, including the longest topic label. The new conference opening was checked against the viewport boundary. Browser coverage is viewport emulation, not physical-device certification.
