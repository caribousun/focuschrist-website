# Legacy answer repairs successor registration

This directory registers one exact change set: the legacy answer
repairs in `ask.html` and `pioneers.html`, built as PR #516 on branch
`feature/legacy-answer-repairs-2026-10-24` (Hannah's full coverage
pass flagged 92 answers across the reviewed bank and the two legacy
qaDatabase stores; the bank repairs ride the dataset lane, and this
layer registers the legacy-store repairs PR #516 carries: 76 repaired
answer strings in ask.html, including the `pioneer-hospitality`
source-slug correction inside the pioneer hotels entry's sources, and
13 repaired answer strings in pioneers.html, each replacement
carrying the fuller gate of Hannah's pass, Jeff's exact-text
concurrence, and Merlin's concurrence, with Newton's source
corrections folded in at the final content head).

- ask.html: predecessor SHA-256
  `4881b5a20ed045b1d45dd1c393d3204c56cf46692d7fa4837e5257346aa4e7a9`,
  candidate SHA-256
  `0d9a5f1ba3a6bf815084ef3df330b25b771332dfa837dd2f21e74b133a9cfc90`.
  47 spans in candidate-byte coordinates, together covering exactly
  the 76 changed lines, all inside the qaDatabase store (spans are
  described by the first entry key of each span's lines):
  - [50548, 59738): 5 lines from 'faith and trials' (8161 bytes
    replaced with 9190 bytes).
  - [60817, 63844): 2 lines from 'men are that they might have joy'
    (2167 replaced with 3027).
  - [66702, 67510): 'is it true' (575 replaced with 808).
  - [98597, 99506): 'holy ghost as guide' (567 replaced with 909).
  - [102190, 104381): 'obedience unlocks revelation' (1840 replaced
    with 2191).
  - [104382, 105023): 'spirit upon the face of the earth' (592
    replaced with 641).
  - [113279, 114606): 'atonement presence of god' (1032 replaced with
    1327).
  - [115679, 121208): 4 lines from 'atonement daily walk' (4189
    replaced with 5529).
  - [122347, 124471): 'atonement hope' (1586 replaced with 2124).
  - [127655, 128851): 'atonement mosiah' (920 replaced with 1196).
  - [137731, 140049): 'become like savior' (1792 replaced with 2318).
  - [151180, 152435): 'law of consecration' (594 replaced with 1255).
  - [154199, 155730): 'children who die' (559 replaced with 1531).
  - [166126, 167516): 'holy ghost gift that stays' (1332 replaced
    with 1390).
  - [179051, 181698): 2 lines from 'baptism for the dead' (2057
    replaced with 2647).
  - [182765, 184087): 'agency' (1045 replaced with 1322).
  - [192548, 193762): 'how to hear revelation' (1366 replaced with
    1214).
  - [229264, 230348): 'priesthood' (508 replaced with 1084).
  - [235378, 237540): 2 lines from 'eliza r snow' (1927 replaced with
    2162).
  - [238622, 239719): 'pioneer quail miracle' (998 replaced with
    1097).
  - [246777, 247681): 'perpetual emigrating fund' (808 replaced with
    904).
  - [251642, 253976): 2 lines from 'willie handcart company' (2027
    replaced with 2334).
  - [255008, 255984): 'british converts pioneer' (1023 replaced with
    976).
  - [257060, 258118): 'pioneer handcart companies' (999 replaced with
    1058).
  - [274832, 275694): 'pioneer courage' (859 replaced with 862).
  - [287421, 288411): 'pioneer names' (855 replaced with 990).
  - [291973, 293214): 'pioneer temples' (918 replaced with 1241).
  - [295026, 296132): 'pioneer photography' (964 replaced with 1106).
  - [300501, 301171): 'pioneer horses' (808 replaced with 670).
  - [313660, 314435): 'pioneer rivers' (768 replaced with 775).
  - [341847, 342551): 'pioneer soap' (488 replaced with 704).
  - [354856, 355677): 'pioneer trade' (508 replaced with 821).
  - [357698, 362150): 6 lines from 'pioneer mining' (2999 replaced
    with 4452).
  - [363153, 365688): 3 lines from 'pioneer forts' (1565 replaced
    with 2535).
  - [366785, 367641): 'pioneer telegraph' (540 replaced with 856).
  - [368162, 370479): 3 lines from 'pioneer newspapers' (1529
    replaced with 2317).
  - [374188, 376683): 3 lines from 'pioneer courts' (1449 replaced
    with 2495).
  - [378160, 380417): 3 lines from 'pioneer blacksmiths' (1476
    replaced with 2257).
  - [380925, 383253): 3 lines from 'pioneer musicians' (1468 replaced
    with 2328).
  - [385869, 386667): 'pioneer funerals' (498 replaced with 798).
  - [389644, 390983): 'infant baptism' (827 replaced with 1339).
  - [392820, 394118): 'eternal progression' (1060 replaced with 1298).
  - [395901, 396955): 'chastity' (928 replaced with 1054).
  - [397824, 399153): 'tithing' (913 replaced with 1329).
  - [401263, 402294): 'son of man' (977 replaced with 1031).
  - [403332, 404483): 'translation' (962 replaced with 1151).
  - [405475, 413991): 4 lines from 'bible prophecy mormon' (6710
    replaced with 8516).
- pioneers.html: predecessor SHA-256
  `b2b988d240a7d54b60b2d2701fde26f54fa6ca1b63261b3d7f7f9e89377a3bf5`,
  candidate SHA-256
  `0674855075616de71f8b89b8b6e3b0145a48e80cc7e7f1b8b7a64874b77fa05d`.
  11 spans in candidate-byte coordinates, together covering exactly
  the 13 changed lines, all inside the qaDatabase store:
  - [28637, 29445): 'is it true' (573 replaced with 808).
  - [77484, 80131): 2 lines from 'baptism for the dead' (2057
    replaced with 2647).
  - [81198, 82520): 'agency' (1045 replaced with 1322).
  - [90921, 92133): 'how to hear revelation' (1354 replaced with
    1212).
  - [125000, 126080): 'priesthood' (504 replaced with 1080).
  - [131070, 133224): 2 lines from 'eliza r snow' (1919 replaced with
    2154).
  - [134288, 135383): 'pioneer quail miracle' (996 replaced with
    1095).
  - [141350, 142689): 'infant baptism' (827 replaced with 1339).
  - [144526, 145822): 'eternal progression' (1058 replaced with 1296).
  - [147603, 148653): 'chastity' (924 replaced with 1050).
  - [149520, 150848): 'tithing' (912 replaced with 1328).

The ask.html predecessor hash is exactly the after hash the citation
rendering successor layer (docs/citation-rendering-successor/
manifest.json) pins for ask.html, and the pioneers.html predecessor
hash is exactly the after hash the answer-bank successor layer
(docs/answer-bank-successor/manifest.json) pins for pioneers.html;
this layer strips back to those states, the citation layer then
strips ask.html back to the answer-bank after state
(`735ccd0d56d7931a651ec8c06759cc849e7895fa55311f8d9d7d6bb36b419612`),
the answer-bank layer strips both pages back to the states the
continue-motion predecessor map (docs/continue-motion/
predecessors.json) pins as current for them (ask.html
`4a5f73ee35fb5cd8d1a9d30109f7daf9f85f7e3913fb5e3cc012a996d6058db3`,
pioneers.html
`57fe21dc3a92dde1b5c51cddcf872cabe62d1e88a7ec259fc135afaa80cb8b81`),
and the motion chain then reconstructs the historical predecessors
(ask.html
`bbeeb8c6e40d4b55a7949ba7544200796457df1ad975fbd2bdb9b75f9d8c8a04`,
pioneers.html
`b2ed6c9a12d25600262997235fa9971972dddd93f0ef26cad852f7ab66ffc0e0`).
`manifest.json` is pinned in `tools/legacy_answer_repairs_successor.py`
as `SOURCE_SHA`. That pin records the exact candidate spans only. It
is not review approval. No answer-bank or citation manifest, module,
or review record, no display-gate layer, no predecessor map, MAP_SHA,
or motion review record is changed by this layer. Because the
citation layer's check reads ask.html raw, the continue-motion
binding validates that layer against the legacy-restored projection
of ask.html (a temporary view) rather than the raw final bytes, and
the answer-bank layer against the legacy-then-citation-restored
projection of both pages, without altering either layer itself.

## Review model

The repairs in PR #516 were independently reviewed by Jeff in
J-2026-10-25-081 (CONCUR WITH CONDITIONS on the repaired content:
C1 requires this registration delta on the same branch, C2 requires
green CI at the registered head before any merge; the registry
figures were corrected from the manifests in J-2026-10-25-082), and
Newton's source corrections to the repaired texts were reviewed in
J-2026-10-25-084 and J-2026-10-25-085 and folded into the final
content head this registration pins. The registration itself is
re-reviewed by Jeff on the exact head carrying it; that re-review is
delivered on the channel and gates the merge, and no finished in-tree
review record is claimed in this directory. The module's check
verifies the registration's exact bytes, spans, and round trip only.
