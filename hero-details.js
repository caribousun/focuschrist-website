(function () {
    'use strict';
    if (typeof HTMLDialogElement === 'undefined' || document.getElementById('heroDetailDialog')) return;
    const records = {
        'birth-of-christ': {
            title: 'Mary lays her newborn Son in a manger',
            paragraphs: ['Mary lays her swaddled newborn in a manger. This tender moment turns our attention to the birth of Jesus Christ in Bethlehem.', 'Read Luke 2:6–7, then follow the scriptural promises and witnesses surrounding His birth. The setting is an artistic interpretation of the account.'],
            source: 'https://www.churchofjesuschrist.org/study/scriptures/nt/luke/2?lang=eng&id=p6-p7#p6', sourceLabel: 'Read Luke 2:6–7', study: 'birth-of-christ.html#promised-son', studyLabel: 'Begin the Birth of Christ Study'
        },
        atonement: {
            title: 'In Gethsemane',
            paragraphs: ['Beneath the olive branches, Jesus kneels beside a rock with His hands clasped in prayer. His bowed head draws us into a quiet moment of reverence.', 'Read His prayer to the Father in Luke 22, then follow the study of His Atonement, Resurrection, and redeeming love. This scene is a devotional artistic interpretation.'],
            source: 'https://www.churchofjesuschrist.org/study/scriptures/nt/luke/22?lang=eng&id=p39-p46#p39', sourceLabel: 'Read Luke 22:39–46', study: 'atonement.html#before-the-world', studyLabel: 'Begin the Atonement Study'
        },
        'joseph-likeness': {
            title: 'The Face Behind the History',
            paragraphs: ['Light brown hair, a white neckcloth and a dark coat frame the Joseph Smith portrait adopted by focusChrist. This artistic likeness guides the face used in the new scenes on this page.', 'Explore the historical death masks and the creative choices behind our portrait. The adopted image offers a consistent artistic interpretation rather than an authenticated historical photograph.'],
            source: 'https://churchhistorylibrary.churchofjesuschrist.org/joseph-and-hyrum-death-masks?lang=eng', sourceLabel: 'Explore the Historical Death Masks', study: 'joseph-smith-likeness.html#our-portrait', studyLabel: 'How We Developed the Portrait'
        },
        'bom-evidences': {
            title: 'Listen, Learn, and Come unto Christ',
            paragraphs: ['Jesus Christ turns toward a woman while others listen nearby. The shared gaze places patient attention at the heart of this imagined gathering.', 'Let the warmth of the encounter invite you into the record itself: read the Savior’s words, bring sincere questions, and consider how your study can lead to a closer relationship with Him.'],
            source: 'https://www.churchofjesuschrist.org/study/scriptures/bofm/3-ne/11?lang=eng', sourceLabel: 'Read 3 Nephi 11', study: 'book-of-mormon-evidences.html#come-to-christ', studyLabel: 'Explore the Witness of Christ'
        },
        home: {
            title: 'A Welcoming Savior',
            paragraphs: ["This devotional portrait places Christ's warm expression against golden light. The close composition invites a personal moment of reflection on His compassion and welcome.", 'Consider what helps you turn toward Jesus Christ in daily life. Continue with the study of His life and mission, using scripture to deepen the reflection suggested by the artwork.'],
            source: 'https://www.churchofjesuschrist.org/study/manual/gospel-topics/jesus-christ-study-guide?lang=eng', sourceLabel: 'Study Jesus Christ', study: 'art-study/the-living-christ.html', studyLabel: 'Study the Living Christ'
        },
        ask: {
            title: 'An Invitation to Ask and Listen',
            paragraphs: ['Christ sits among attentive listeners above a sunlit lake, extending an open hand. This imagined teaching scene gives visual form to an invitation to bring sincere questions and make room to listen.', 'Notice the space between speaking and receiving an answer. As you study Matthew 7:7, consider one question you would like to explore through prayer, scripture, and patient reflection.'],
            source: 'https://www.churchofjesuschrist.org/study/scriptures/nt/matt/7.7?lang=eng', sourceLabel: 'Read Matthew 7:7', study: 'answers/prayer-and-personal-revelation.html', studyLabel: 'Explore Prayer and Personal Revelation'
        },
        answers: {
            title: 'Make Room for Study',
            paragraphs: ['Open scriptures, a notebook, and a quiet conversation overlook a lake at sunset. Together, these details suggest that seeking understanding can include careful reading, recording questions, and listening to another person.', 'The scene offers a place to pause without requiring every question to be settled at once. Read James 1 alongside your own questions, then explore how prayer and thoughtful study can work together.'],
            source: 'https://www.churchofjesuschrist.org/study/scriptures/nt/james/1?lang=eng', sourceLabel: 'Read James 1', study: 'answers/prayer-and-personal-revelation.html', studyLabel: 'Explore Prayer and Personal Revelation'
        },
        art: {
            title: 'Remember Him Through Art',
            paragraphs: ['Brushes, sketches, and a landscape painting fill a sunlit studio. A framed image of Christ and a temple beyond the window connect artistic attention with worship, beauty, and remembrance.', 'The imagined setting invites you to notice which details turn your thoughts toward the Savior. Continue from that impression into The Living Christ, allowing its testimony to guide your study beyond the image.'],
            source: 'https://www.churchofjesuschrist.org/study/scriptures/the-living-christ-the-testimony-of-the-apostles/the-living-christ-the-testimony-of-the-apostles?lang=eng', sourceLabel: 'Read The Living Christ', study: 'art-study/the-living-christ.html', studyLabel: 'Explore the Living Christ Artwork'
        },
        mission: {
            title: 'His Work Throughout the World',
            paragraphs: ['Christ stands at the center of a symbolic gathering of modern missionaries and neighbors. Teaching, listening, cleanup, and food distribution appear beneath a subtle world map, bringing several forms of service into one composition.', "The scene connects an invitation to know Christ with attentive care for people. Read the Savior's commission in Matthew 28, then consider how to share faith with respect for another person's questions, circumstances, and choices."],
            source: 'https://www.churchofjesuschrist.org/study/scriptures/nt/matt/28?lang=eng', sourceLabel: 'Read Matthew 28', study: 'answers/jesus-christ-latter-day-saint-beliefs.html', studyLabel: 'Explore Faith in Jesus Christ'
        },
        history: {
            title: 'Light in the Grove',
            paragraphs: ['Sunlight enters a quiet wooded grove and reveals a path through the trees, creating a reflective opening for the study of the Sacred Grove and the First Vision.', 'Let the light, stillness and open path lead into the accounts themselves. Compare what Joseph Smith recorded and attend carefully to the context of each account.'],
            source: 'https://www.churchofjesuschrist.org/study/manual/gospel-topics-essays/first-vision-accounts?lang=eng', sourceLabel: 'Read First Vision Accounts', study: 'answers/who-was-joseph-smith.html', studyLabel: 'Study Joseph Smith and the Restoration'
        },
        pioneers: {
            title: 'Faith Across the Journey',
            paragraphs: ['A family moves a handcart across open country while covered wagons continue toward distant mountains. This interpretive scene draws attention to shared effort, family ties, and the uncertainty of a long journey.', 'The figures represent a broad pioneer experience rather than an identified family or company. Continue into historical sources and individual accounts, where names, dates, hardships, and choices give the people of the migration their own voices.'],
            source: 'https://www.churchofjesuschrist.org/study/church-history?lang=eng', sourceLabel: 'Explore Church History Sources', study: 'church-history.html', studyLabel: 'Continue Studying Church History'
        },
        watch: {
            title: 'Hear Him and Continue Learning',
            paragraphs: ['Christ welcomes listeners beside the water, while an open tomb appears at the edge of the scene. This symbolic composition brings together His teaching and the hope of His Resurrection rather than portraying one recorded event.', 'A moving image can begin reflection that continues after viewing. Read John 20 and consider what its resurrection witnesses actually report, then explore how faith in the living Christ shapes discipleship.'],
            source: 'https://www.churchofjesuschrist.org/study/scriptures/nt/john/20?lang=eng', sourceLabel: 'Read John 20', study: 'answers/jesus-christ-latter-day-saint-beliefs.html', studyLabel: "Explore the Savior's Life and Mission"
        },
        about: {
            title: 'A Place to Study Together',
            paragraphs: ['Open scriptures and a notebook overlook a gathering place where people approach one another beneath the trees. The warm light and distant temple suggest a setting for study, conversation, and belonging.', "This imagined community reflects focusChrist's invitation to learn about Jesus Christ with care for the people who bring their questions. Begin with His life and teachings, then choose a study that speaks to your present needs."],
            source: 'https://www.churchofjesuschrist.org/study/manual/gospel-topics/jesus-christ-study-guide?lang=eng', sourceLabel: 'Study Jesus Christ', study: 'answers/jesus-christ-latter-day-saint-beliefs.html', studyLabel: 'Explore Faith in Jesus Christ'
        },
        'living-christ-art': {
            title: 'The Living Christ',
            paragraphs: ['A radiant portrait centers the smiling face of Jesus Christ against a field of golden light. The brightness gathering around Him gives visual form to Christian hope in a Savior who rose from the tomb and lives.', 'Let the image lead into the witnesses of John 20: Mary hears Jesus call her by name, the disciples see His wounds, and Thomas receives an invitation to believe.'],
            source: 'https://www.churchofjesuschrist.org/study/scriptures/nt/john/20?lang=eng', sourceLabel: 'Read John 20', study: 'art-study/the-living-christ.html#scripture-study', studyLabel: 'Begin the Scripture Study'
        },
        'good-shepherd-art': {
            title: 'The Good Shepherd',
            paragraphs: ['Jesus stands in the warmth of a busy village street, His open expression drawing attention to nearness, recognition, and welcome. The everyday setting brings the shepherd image into the places where people live and work.', 'In John 10, Christ describes the good shepherd as one who knows His sheep, calls them, remains with them in danger, and willingly gives His life for them.'],
            source: 'https://www.churchofjesuschrist.org/study/scriptures/nt/john/10?lang=eng', sourceLabel: 'Read John 10', study: 'art-study/the-good-shepherd.html#scripture-study', studyLabel: 'Begin the Scripture Study'
        },
        'little-children-art': {
            title: 'Suffer the Little Children',
            paragraphs: ['Jesus sits at the center of a circle of children in an olive grove. Their closeness, varied expressions, and His welcoming gesture emphasize that each child has a place near Him.', 'Mark 10 records that Jesus corrected those who tried to turn children away, then took the children in His arms and blessed them. Read the account with attention to both the barrier and His welcome.'],
            source: 'https://www.churchofjesuschrist.org/study/scriptures/nt/mark/10?lang=eng&id=p13-p16#p13', sourceLabel: 'Read Mark 10:13–16', study: 'art-study/suffer-the-little-children.html#scripture-study', studyLabel: 'Begin the Scripture Study'
        },
        'be-still-art': {
            title: 'Be Still',
            paragraphs: ['Christ walks beside a burdened man through a crowded modern street, placing a steadying hand on his shoulder. The surrounding movement makes their quiet companionship the center of the scene.', 'Psalm 46 speaks of God as refuge and strength amid upheaval before giving the invitation to be still and know Him. The image invites reflection on Christ’s presence without pretending that hardship or responsibility disappears.'],
            source: 'https://www.churchofjesuschrist.org/study/scriptures/ot/ps/46?lang=eng', sourceLabel: 'Read Psalm 46', study: 'art-study/be-still.html#psalm-context', studyLabel: 'Begin the Scripture Study'
        }
    };
    // Each topic keeps its own artwork context and return to the study.
    Object.assign(records, {
    "topic-christian": {
        "title": "A neighbor receives a meal",
        "paragraphs": [
            "A young woman hands a covered meal to an older man in a community kitchen.",
            "Their shared attention gives an ordinary act of care its warmth. In John 13:34–35, Jesus teaches His disciples to love one another. This modern scene invites reflection on following Him through service."
        ],
        "source": "https://www.churchofjesuschrist.org/study/scriptures/nt/john/13?lang=eng",
        "sourceLabel": "Read John 13:34–35",
        "study": "answers/are-latter-day-saints-christian.html#scripture-study",
        "studyLabel": "Study Christian discipleship"
    },
    "topic-aaronic": {
    "title": "Prepare to serve at the sacrament table",
    "paragraphs": ["Two young men attend to the bread and white cloth at a chapel’s sacrament table. This imagined contemporary scene connects priesthood study with careful, reverent service. Read John the Baptist’s words, then consider how preparation can help us remember Jesus Christ."],
    "source": "https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/13?lang=eng",
    "sourceLabel": "Read Doctrine and Covenants 13",
    "study": "answers/aaronic-priesthood-restoration.html#begin-study",
    "studyLabel": "Open the Aaronic Priesthood study"
},
    "topic-melchizedek": {
    "title": "A blessing offered with care",
    "paragraphs": ["Two men bow their heads as they offer a priesthood blessing to a seated man. This imagined contemporary scene invites reflection on service offered with humility and care. Follow the historical witnesses in this study and consider how the Lord’s counsel shapes the exercise of authority."],
    "source": "https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/128?lang=eng",
    "sourceLabel": "Read Doctrine and Covenants 128",
    "study": "answers/melchizedek-priesthood-restoration.html#begin-study",
    "studyLabel": "Open the Melchizedek Priesthood study"
},
    "topic-bible-bom": {
        "title": "Two witnesses in one study",
        "paragraphs": [
            "A reader follows a passage with her finger while two open scripture volumes rest before her.",
            "The quiet comparison invites careful reading of the Bible and the Book of Mormon. Read 2 Nephi 29:8, then consider how each record bears witness of Jesus Christ. This is an imagined modern study scene."
        ],
        "source": "https://www.churchofjesuschrist.org/study/scriptures/bofm/2-ne/29?lang=eng",
        "sourceLabel": "Read 2 Nephi 29:8",
        "study": "answers/bible-and-book-of-mormon-together.html#scripture-study",
        "studyLabel": "Compare the two witnesses"
    },
    "topic-child-loss": {
        "title": "Someone stays beside you",
        "paragraphs": [
            "A woman holds a small knitted cap while a friend stays close beside her.",
            "The cap and patient company give room to sorrow without asking it to end. Moroni 8 teaches of Christ’s mercy toward little children; this imagined moment of support does not explain the cause of any family’s loss."
        ],
        "source": "https://www.churchofjesuschrist.org/study/scriptures/bofm/moro/8?lang=eng",
        "sourceLabel": "Read Moroni 8",
        "study": "answers/death-of-a-child.html#scripture-study",
        "studyLabel": "Continue the gentle study"
    },
    "topic-divorce": {
        "title": "Help with the next step",
        "paragraphs": [
            "A woman receives groceries at her new doorway while a friend meets her eyes.",
            "A small act of practical help can ease a difficult day. Mosiah 18:8–9 teaches a willingness to bear burdens and mourn with others. The scene is a modern reflection on support through change."
        ],
        "source": "https://www.churchofjesuschrist.org/study/scriptures/bofm/mosiah/18?lang=eng",
        "sourceLabel": "Read Mosiah 18:8–9",
        "study": "answers/divorce-and-faith.html#scripture-study",
        "studyLabel": "Study support through change"
    },
    "topic-trials": {
        "title": "A steady hand on a difficult path",
        "paragraphs": [
            "Jesus steadies a weary man on a rain-soaked path and listens as their eyes meet.",
            "The rough ground gives this devotional scene a sense of effort and companionship. Read Christ’s invitation in Matthew 11:28–30, then consider the spiritual and practical help available during a trial. The scene is symbolic rather than a recorded event."
        ],
        "source": "https://www.churchofjesuschrist.org/study/scriptures/nt/matt/11?lang=eng",
        "sourceLabel": "Read Matthew 11:28–30",
        "study": "answers/faith-in-jesus-christ-during-trials.html#scripture-study",
        "studyLabel": "Study faith during trials"
    },
    "topic-father": {
        "title": "Jesus teaches of His Father",
        "paragraphs": [
            "Jesus turns toward Philip in a lamplit room, speaking with an open hand.",
            "In John 14:8–10, Philip asks about the Father, and Jesus explains His relationship with Him. Read their exchange in context. The faces, clothing, and room are an artistic interpretation of the account."
        ],
        "source": "https://www.churchofjesuschrist.org/study/scriptures/nt/john/14?lang=eng",
        "sourceLabel": "Read John 14:8–10",
        "study": "answers/god-our-heavenly-father.html#pray-to-the-father",
        "studyLabel": "Study Christ’s teaching of the Father"
    },
    "topic-grief": {
        "title": "Compassion at Nain",
        "paragraphs": [
            "Jesus meets a grieving widow outside the town while mourners wait nearby.",
            "Luke 7:11–15 records His compassion for the widow of Nain before He restores her son to life. This interpretation pauses with His attention to her sorrow; the town, clothing, and faces are artistic choices."
        ],
        "source": "https://www.churchofjesuschrist.org/study/scriptures/nt/luke/7?lang=eng",
        "sourceLabel": "Read Luke 7:11–15",
        "study": "answers/grief-and-faith.html#comfort-in-grief",
        "studyLabel": "Begin with compassion"
    },
    "topic-jesus": {
        "title": "Living water at the well",
        "paragraphs": [
            "Jesus and a woman speak beside a stone well, with her water jar close at hand.",
            "John 4:7–26 records the Savior’s conversation with a Samaritan woman about living water and worship. Follow their words beyond this imagined moment; the setting, faces, and clothing are artistic interpretations."
        ],
        "source": "https://www.churchofjesuschrist.org/study/scriptures/nt/john/4?lang=eng",
        "sourceLabel": "Read John 4:7–26",
        "study": "answers/jesus-christ-latter-day-saint-beliefs.html#scripture-study",
        "studyLabel": "Study the Savior’s life and teachings"
    },
    "topic-look-unto": {
        "title": "Look to Him while the way unfolds",
        "paragraphs": [
            "Jesus stands along an olive-lined path with a hand over His heart and a calm, attentive expression.",
            "This devotional scene invites a pause with Doctrine and Covenants 6:36. Read the verse with its surrounding counsel, then consider what turning toward Christ might mean in an ordinary decision. It does not portray the historical setting of the revelation."
        ],
        "source": "https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/6?lang=eng&id=p36#p36",
        "sourceLabel": "Read Doctrine and Covenants 6:36",
        "study": "answers/look-unto-me-doctrine-and-covenants-6-36.html#passage",
        "studyLabel": "Read the passage in context"
    },
    "topic-restoration": {
        "title": "A congregation cares for one another",
        "paragraphs": [
            "Two volunteers prepare a box of food together, attending to the work before them.",
            "Their shared task offers a modern reflection on covenant care. Mosiah 18:8–10 describes a people willing to bear burdens and serve God. Continue into the study of Christ’s Church, its teachings, and its claims."
        ],
        "source": "https://www.churchofjesuschrist.org/study/scriptures/bofm/mosiah/18?lang=eng",
        "sourceLabel": "Read Mosiah 18:21",
        "study": "answers/restored-church-of-jesus-christ.html#covenant-life",
        "studyLabel": "Study covenant life together"
    },
    "topic-settle-heart": {
        "title": "Walk with Him",
        "paragraphs": [
                "Jesus and a disciple walk beside one another, their eyes meeting as they talk. The quiet exchange invites us to consider what it means to follow Him.",
                "This is a devotional interpretation of discipleship, not a reconstruction of a named encounter. Read the invitation to follow Jesus in Luke 9:23, then explore the message and scripture studies."
        ],
        "source": "https://www.churchofjesuschrist.org/study/scriptures/nt/luke/9?lang=eng&id=p23#p23",
        "sourceLabel": "Read Luke 9:23",
        "study": "answers/settle-this-in-your-hearts.html#the-invitation",
        "studyLabel": "Begin the Settle Your Heart study"
},
    "topic-stand-forever": {
        "title": "Build on the rock",
        "paragraphs": [
            "A reader stands on solid rock with a closed scripture book as the clouds begin to clear.",
            "The landscape offers a modern visual reflection on Helaman 5:12 and the invitation to build on Jesus Christ. Let the image lead into the questions and original sources explored in Stand Forever."
        ],
        "source": "https://www.churchofjesuschrist.org/study/scriptures/bofm/hel/5?lang=eng",
        "sourceLabel": "Read Helaman 5:12",
        "study": "answers/stand-forever.html#stand-forever",
        "studyLabel": "Explore the foundational questions"
    },
    "topic-life-after-death": {
        "title": "A living Savior on the shore",
        "paragraphs": [
            "The risen Jesus stands on the shore at dawn, looking toward the fishermen on the water.",
            "John 21:4–14 records His appearance by the Sea of Tiberias and the meal He shares with His disciples. The shoreline, boat, and faces are artistic interpretations. Read the account as one witness of the Savior’s life after death."
        ],
        "source": "https://www.churchofjesuschrist.org/study/scriptures/nt/john/21?lang=eng",
        "sourceLabel": "Read John 21:4–14",
        "study": "answers/what-happens-after-death.html#resurrection",
        "studyLabel": "Study the Resurrection witnesses"
    },
    "topic-marriage": {
        "title": "Care through the years",
        "paragraphs": [
            "An older couple share a small moment of care beneath a flowering tree.",
            "Their attentive faces invite reflection on love practiced through the years. Continue into the teaching about eternal marriage in Doctrine and Covenants 132:19, keeping the scripture’s covenant context distinct from this imagined modern scene."
        ],
        "source": "https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/132?lang=eng",
        "sourceLabel": "Read Doctrine and Covenants 132:19",
        "study": "answers/what-is-eternal-marriage.html#meaning",
        "studyLabel": "Study the meaning of eternal marriage"
    },
    "topic-book-of-mormon": {
        "title": "Begin with the record",
        "paragraphs": [
            "A traveler reads the Book of Mormon while daylight enters the train window.",
            "An ordinary journey becomes time to consider the record. Read Moroni 10:3–5, then follow its invitation to remember, ponder, and ask God. This is an imagined contemporary reading scene."
        ],
        "source": "https://www.churchofjesuschrist.org/study/scriptures/bofm/moro/10?lang=eng",
        "sourceLabel": "Read Moroni 10:3–5",
        "study": "answers/what-is-the-book-of-mormon.html#scripture-study",
        "studyLabel": "Begin studying the Book of Mormon"
    },
    "topic-joseph": {
        "title": "Joseph and the published record",
        "paragraphs": [
            "Joseph Smith holds a small bound book outside an early printing shop.",
            "This interpretation places him near the publication of the Book of Mormon in 1830, when he was twenty-four. The pose and surroundings are imagined. Continue with Joseph Smith—History and the linked historical sources to examine his own account and the record around it."
        ],
        "source": "https://www.churchofjesuschrist.org/study/scriptures/pgp/js-h/1?lang=eng",
        "sourceLabel": "Read Joseph Smith—History",
        "study": "answers/who-was-joseph-smith.html#scripture-study",
        "studyLabel": "Study Joseph Smith and the record"
    },
    "topic-families": {
        "title": "Love in the work of a day",
        "paragraphs": [
            "Three generations gather around the kitchen counter to work the dough together.",
            "Their shared attention gives a familiar household task a sense of care and belonging. Mosiah 4:14–15 teaches parents to help children love and serve one another. This imagined family moment invites reflection on patient daily teaching."
        ],
        "source": "https://www.churchofjesuschrist.org/study/scriptures/bofm/mosiah/4?lang=eng",
        "sourceLabel": "Read Mosiah 4:14–15",
        "study": "answers/why-families-are-important.html#scripture-study",
        "studyLabel": "Study love and family responsibility"
    },
    "topic-temples": {
        "title": "Remembering the generations",
        "paragraphs": [
            "An older woman and a younger man study a family photograph together.",
            "Remembering a person can begin with a name, a picture, and a story. Doctrine and Covenants 128:18 connects generations in the work of salvation. This modern interpretation leads into study of family history and temple service."
        ],
        "source": "https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/128?lang=eng",
        "sourceLabel": "Read Doctrine and Covenants 128:18",
        "study": "answers/why-latter-day-saints-build-temples.html#scripture-study",
        "studyLabel": "Study temples and generations"
    },
    "topic-living-christ": {
        "title": "He lives and ministers",
        "paragraphs": [
            "The risen Savior meets your gaze with a warm smile, one hand resting over His heart.",
            "This devotional portrait invites a quiet moment with Jesus Christ. The Living Christ bears apostolic testimony of His Resurrection, continuing ministry, and promised return; the garden, gesture, and expression are artistic interpretation."
        ],
        "source": "https://www.churchofjesuschrist.org/study/scriptures/the-living-christ-the-testimony-of-the-apostles/the-living-christ-the-testimony-of-the-apostles?lang=eng",
        "sourceLabel": "Read The Living Christ",
        "study": "art-study/the-living-christ.html#scripture-study",
        "studyLabel": "Read the Resurrection witnesses"
    },
    "topic-prayer": {
        "title": "He went out to pray",
        "paragraphs": [
            "Jesus pauses alone in prayer beneath the night sky.",
            "Luke 6:12 records that He went into a mountain and continued all night in prayer to God. The landscape and moment shown here are artistic interpretations. Read the account, then explore prayer and personal revelation with its context in view."
        ],
        "source": "https://www.churchofjesuschrist.org/study/scriptures/nt/luke/6?lang=eng&id=p12#p12",
        "sourceLabel": "Read Luke 6:12",
        "study": "answers/prayer-and-personal-revelation.html#scripture-study",
        "studyLabel": "Study prayer and personal revelation"
    }
});
    const script = document.currentScript;
    const siteBase = new URL('.', script ? script.src : window.location.href);
    const dialog = document.createElement('dialog');
    dialog.id = 'heroDetailDialog';
    dialog.className = 'fc-artwork-detail-dialog fc-hero-detail-dialog';
    dialog.setAttribute('aria-labelledby', 'heroDetailTitle');
    dialog.innerHTML = '<div class="fc-artwork-detail-shell"><button class="fc-artwork-detail-close" type="button" data-hero-close aria-label="Close artwork details"></button><div class="fc-artwork-detail-media"><img alt=""></div><div class="fc-artwork-detail-body"><p class="fc-eyebrow">Explore the artwork</p><h2 id="heroDetailTitle"></h2><div class="fc-artwork-detail-copy" tabindex="0" role="region" aria-label="Artwork reflection"></div><div class="fc-actions fc-artwork-detail-actions"><a class="fc-button fc-button--primary" data-hero-source-link target="_blank" rel="noopener noreferrer"></a><a class="fc-button" data-hero-study-link></a><a class="fc-button" data-hero-ask-link>Ask About This Artwork</a><a class="fc-button" data-full-image-viewer aria-haspopup="dialog">View Full-Size Image</a><button class="fc-button" type="button" data-hero-close>Close</button></div></div></div>';
    document.body.appendChild(dialog);
    const image = dialog.querySelector('img');
    const title = dialog.querySelector('h2');
    const copy = dialog.querySelector('.fc-artwork-detail-copy');
    const source = dialog.querySelector('[data-hero-source-link]');
    const study = dialog.querySelector('[data-hero-study-link]');
    const ask = dialog.querySelector('[data-hero-ask-link]');
    const fullImage = dialog.querySelector('[data-full-image-viewer]');
    let returnFocus = null;

    function getRecordKey(trigger) {
        if (trigger.dataset.heroRecord && records[trigger.dataset.heroRecord]) return trigger.dataset.heroRecord;
        if (trigger.classList.contains('fc-home-hero') || trigger.classList.contains('fc-answer-detail-hero')) return 'home';
        const basename = new URL(trigger.href).pathname.split('/').pop().replace(/\.(?:webp|png|jpe?g|avif)$/i, '');
        return { missionary: 'mission', 'church-history': 'history' }[basename] || basename;
    }

    function openDetail(trigger) {
        const key = getRecordKey(trigger);
        const record = records[key];
        if (!record) return false;
        image.src = trigger.href;
        image.alt = trigger.dataset.fullImageAlt || record.title;
        title.textContent = record.title;
        copy.replaceChildren();
        record.paragraphs.forEach(function (text) {
            const paragraph = document.createElement('p');
            paragraph.textContent = text;
            copy.appendChild(paragraph);
        });
        source.href = record.source;
        source.textContent = record.sourceLabel;
        study.href = new URL(record.study, siteBase).href;
        study.textContent = record.studyLabel;
        if (key === 'home' && /\/(answers|art-study)\//.test(window.location.pathname)) {
            const related = Array.from(document.querySelectorAll('[data-connected-study] .fc-study-grid a[href], .fc-study-grid a[href]')).find(function (link) {
                const url = new URL(link.href);
                return url.origin === window.location.origin && url.pathname !== window.location.pathname && /\.html$/.test(url.pathname);
            });
            if (related) {
                study.href = related.href;
                study.textContent = related.textContent.trim() || 'Continue Related Study';
            }
        }
        const askUrl = new URL(trigger.dataset.heroAsk || 'ask.html', siteBase);
        askUrl.searchParams.set('art', record.title);
        if (!askUrl.searchParams.has('topic')) askUrl.searchParams.set('topic', record.title);
        if (!askUrl.searchParams.has('return')) askUrl.searchParams.set('return', window.location.pathname + '?hero=1');
        if (key === 'home' && /\/(answers|art-study)\//.test(window.location.pathname)) {
            const heading = document.querySelector('h1');
            if (heading) askUrl.searchParams.set('topic', heading.textContent.trim());
        }
        askUrl.hash = 'ask-question';
        ask.href = askUrl.href;
        fullImage.href = trigger.href;
        fullImage.dataset.fullImageAlt = image.alt;
        returnFocus = trigger;
        document.body.classList.add('fc-dialog-open');
        if (!dialog.open) dialog.showModal();
        dialog.scrollTop = 0;
        copy.scrollTop = 0;
        dialog.querySelector('[data-hero-close]').focus({ preventScroll: true });
        return true;
    }

    document.querySelectorAll('a[data-hero-viewer]').forEach(function (trigger) {
        trigger.addEventListener('click', function (event) {
            if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
            if (openDetail(trigger)) event.preventDefault();
        });
    });
    dialog.querySelectorAll('[data-hero-close]').forEach(function (button) {
        button.addEventListener('click', function () { dialog.close(); });
    });
    dialog.addEventListener('click', function (event) { if (event.target === dialog) dialog.close(); });
    dialog.addEventListener('close', function () {
        if (!document.querySelector('dialog.fc-artwork-detail-dialog[open], dialog.fc-missionary-detail-dialog[open]')) document.body.classList.remove('fc-dialog-open');
        image.removeAttribute('src');
        if (returnFocus) returnFocus.focus({ preventScroll: true });
        returnFocus = null;
    });
    if (new URLSearchParams(window.location.search).get('hero') === '1') {
        const trigger = document.querySelector('a[data-hero-viewer]');
        if (trigger) openDetail(trigger);
    }
}());
