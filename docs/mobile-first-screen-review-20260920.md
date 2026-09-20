# Mobile first-screen correction

Owner requirement: the hero, essential introduction, action pills, and Continue/down arrow must fit on the initial visible phone screen. At each viewport size every mobile hero must have the same vertical height. This supersedes PR342's insufficient section-containment acceptance; its completed Answers directory rows remain intact.

The shared image budget uses `clamp(100px, calc(100svh - 480px), 360px)`. Mobile introductions use compact readable spacing and 44px minimum controls. Complete scene images sit over a soft decorative surround made from the same artwork. Home retains its approved central portrait framing, with some panorama side scenery cropped. No image asset, full-size destination, or desktop presentation was replaced.

## Rendered acceptance

CUA browser review at scroll position zero covered every one of the 41 sitemap routes at 320x568, 375x667, 390x740, 412x775, 430x844, and 700x900: 246 page/viewport observations, including 240 openings (Search has no hero opening). All passed:

- Every visible opening action and Continue cue ended within `visualViewport.height`.
- Every opening action retained a minimum 44px touch height.
- All 39 hero frames had one shared height at each viewport, including Come Follow Me's pseudo-element and General Conference's image.
- No horizontal page overflow; scroll position remained zero.
- The minimum clearance beneath a Continue cue was 12px.

Measured shared heights were 100, 187.2, 260, 295.2, 360, and 360 CSS pixels respectively (subpixel rounding under 0.001px). The browser viewport represents available web content space, not the physical phone screen plus browser chrome.

Visual review included Home, Ask, Answers, Look Unto Me, Come Follow Me, and General Conference. Answers' hero opened its artwork study and closed with focus restored; the original full-size link was retained. Desktop checks at 1440x900 on Home, Answers, Come Follow Me, and General Conference found no horizontal overflow and no visible mobile cue or decorative surround.

Enlarged-text probes covered the longest opening templates; text and controls expand naturally beyond the initial viewport rather than being clipped or shrunk. Come Follow Me's Continue action reached the following study navigation by keyboard with its destination visible. First-screen fit is a normal-text portrait-viewport claim, not a promise that arbitrarily enlarged text or very short landscape screens can fit without scrolling. The enlarged-text probe also exposed pre-existing horizontal overflow elsewhere in several full pages; this release does not claim a whole-site enlarged-text audit.

Independent review approved the mobile implementation, desktop isolation, decorative accessibility, and exact stylesheet ledger update. This record is technical verification, not owner visual acceptance.
