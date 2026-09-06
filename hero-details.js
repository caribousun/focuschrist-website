(function () {
    'use strict';
    if (typeof HTMLDialogElement === 'undefined' || document.getElementById('heroDetailDialog')) return;
    const records = {
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
            paragraphs: ['Sunlight enters a quiet wooded grove, revealing a path through the trees. The scene evokes the Sacred Grove and creates a reflective opening for the study of Church history; it does not depict a documented moment in the First Vision.', 'Let the image lead into the accounts themselves. Compare what Joseph Smith recorded, attend to the context of each account, and distinguish the historical sources from the artistic choices in this scene.'],
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
        }
    };
    const script = document.currentScript;
    const siteBase = new URL('.', script ? script.src : window.location.href);
    const dialog = document.createElement('dialog');
    dialog.id = 'heroDetailDialog';
    dialog.className = 'fc-artwork-detail-dialog fc-hero-detail-dialog';
    dialog.setAttribute('aria-labelledby', 'heroDetailTitle');
    dialog.innerHTML = '<div class="fc-artwork-detail-shell"><button class="fc-artwork-detail-close" type="button" data-hero-close aria-label="Close artwork details"></button><div class="fc-artwork-detail-media"><img alt=""></div><div class="fc-artwork-detail-body"><p class="fc-eyebrow">Explore the artwork</p><h2 id="heroDetailTitle"></h2><div class="fc-artwork-detail-copy"></div><div class="fc-actions fc-artwork-detail-actions"><a class="fc-button fc-button--primary" data-hero-source-link target="_blank" rel="noopener noreferrer"></a><a class="fc-button" data-hero-study-link></a><a class="fc-button" data-hero-ask-link>Ask About This Artwork</a><a class="fc-button" data-full-image-viewer aria-haspopup="dialog">View Full-Size Image</a><button class="fc-button" type="button" data-hero-close>Close</button></div></div></div>';
    document.body.appendChild(dialog);
    const image = dialog.querySelector('img');
    const title = dialog.querySelector('h2');
    const copy = dialog.querySelector('.fc-artwork-detail-copy');
    const source = dialog.querySelector('[data-hero-source-link]');
    const study = dialog.querySelector('[data-hero-study-link]');
    const ask = dialog.querySelector('[data-hero-ask-link]');
    const fullImage = dialog.querySelector('[data-full-image-viewer]');
    let returnFocus = null;

    function openDetail(trigger) {
        const basename = new URL(trigger.href).pathname.split('/').pop().replace(/\.webp$/, '');
        const key = { missionary: 'mission', 'church-history': 'history' }[basename] || basename;
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
