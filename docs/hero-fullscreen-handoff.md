# Site-wide hero full-screen action

The owner requested a clear way to view every page hero uncropped at full size and delegated the choice between image click and a pill. Every image-first page now has a lower-right View full-screen image pill, using the existing same-page dialog. All26 pages are enrolled, including the twelve answer studies, four art studies and404 page.

Each control links to its actual hero asset. The Mission link retains its approved image cache key; Ask retains its approved-red key; nested pages use their actual shared Home hero with correct relative paths. Pioneers preserves its existing whole-hero anchor and adds a visible span pill without nesting anchors. Existing full-image-viewer.js handles close, Escape, background click, scroll lock and focus return. New pages load that same script and stylesheet exactly once.

Hero assets, dimensions, cropping, layout and main introduction typography are unchanged. Pill styling is absolutely positioned, uses the existing pill class and palette, and retains a44px minimum touch target. No new animation or image generation is involved.

The source-content ledger update is limited to the reviewed control label and accessible label. Historical, scriptural, doctrinal and study text is unchanged. Independent review and live interaction verification are required for release closure in Focus Current State and Run Log.
