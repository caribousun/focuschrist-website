/* focusChrist verified study-source router.
 * Adds dependable source pathways for faith/history questions without inventing URLs.
 * Priority: official Church resources first; BYU resources are clearly secondary.
 */
(function () {
    'use strict';

    const OFFICIAL = {
        topics: ['Topics & Questions', 'https://www.churchofjesuschrist.org/study/manual/gospel-topics?lang=eng'],
        essays: ['Gospel Topics Essays', 'https://www.churchofjesuschrist.org/study/manual/gospel-topics/essays?lang=eng'],
        scriptures: ['Scriptures', 'https://www.churchofjesuschrist.org/study/scriptures?lang=eng'],
        conference: ['General Conference', 'https://www.churchofjesuschrist.org/study/general-conference?lang=eng'],
        media: ['Gospel Video & Image Resources', 'https://www.churchofjesuschrist.org/study/videos-and-images?lang=eng'],
        bibleVideos: ['Bible Videos', 'https://www.churchofjesuschrist.org/study/videos-and-images/bible-videos?lang=eng'],
        bomVideos: ['Book of Mormon Videos', 'https://www.churchofjesuschrist.org/study/videos-and-images/book-of-mormon-videos?lang=eng']
    };

    const BYU = {
        rsc: ['BYU Religious Studies Center', 'https://rsc.byu.edu/'],
        rscSearch: ['BYU RSC Search', 'https://rsc.byu.edu/search'],
        citation: ['BYU Scripture Citation Index', 'https://scriptures.byu.edu/']
    };

    const FAITH_TERMS = [
        'jesus','christ','savior','redeemer','god','heavenly father','holy ghost','spirit','gospel','faith','repentance',
        'baptism','confirmation','sacrament','atonement','resurrection','prayer','revelation','scripture','bible','book of mormon',
        'doctrine and covenants','pearl of great price','church','latter-day','latter day','lds','mormon','temple','endowment',
        'sealing','garment','garments','covenant','priesthood','aaronic','melchizedek','prophet','apostle','general conference',
        'joseph smith','oliver cowdery','emma smith','brigham young','first vision','restoration','pioneer','tithing','word of wisdom',
        'plan of salvation','spirit world','premortal','premortality','celestial','terrestrial','telestial','exaltation','salvation',
        'eternal family','family history','familysearch','plural marriage','polygamy','book of abraham','race and priesthood','dna',
        'commandment','sin','forgiveness','grace','ordinance','missionary','missionaries','bishop','ward','stake','relief society',
        'quorum','elder','seventy','patriarch','patriarchal blessing','ministering','calling','callings','zion','nauvoo','kirtland'
    ];

    const HISTORY_TERMS = [
        'history','historical','joseph smith','oliver cowdery','emma smith','brigham young','first vision','restoration','pioneer',
        'plural marriage','polygamy','race and priesthood','book of abraham','dna','mountain meadows','nauvoo','kirtland','missouri',
        'handcart','martyrdom','priesthood restoration'
    ];

    const SCRIPTURE_TERMS = [
        'scripture','verse','chapter','bible','book of mormon','doctrine and covenants','d&c','pearl of great price',
        'genesis','exodus','psalm','isaiah','matthew','mark','luke','john','acts','romans','corinthians','revelation',
        'nephi','jacob','enos','mosiah','alma','helaman','3 nephi','mormon','ether','moroni'
    ];

    function normalize(text) {
        return String(text || '').toLowerCase().replace(/\s+/g, ' ').trim();
    }

    function containsAny(text, terms) {
        const value = normalize(text);
        return terms.some(function (term) { return value.includes(term); });
    }

    function isPioneerPage() {
        return window.location.pathname.toLowerCase().endsWith('/pioneers.html');
    }

    function isFaithQuestion(question) {
        return isPioneerPage() || containsAny(question, FAITH_TERMS);
    }

    function churchSearchUrl(question) {
        return 'https://www.churchofjesuschrist.org/search?lang=eng&query=' + encodeURIComponent(String(question || '').trim());
    }

    function uniqueSources(items) {
        const seen = new Set();
        return items.filter(function (item) {
            if (!item || !item.url || seen.has(item.url)) return false;
            seen.add(item.url);
            return true;
        });
    }

    function source(labelUrl, tier, note) {
        return { label: labelUrl[0], url: labelUrl[1], tier: tier, note: note || '' };
    }

    function sourcesForQuestion(question) {
        if (!isFaithQuestion(question)) return [];
        const q = normalize(question);
        const results = [];

        results.push({
            label: 'Search official Church sources for this question',
            url: churchSearchUrl(question),
            tier: 'Official Church search',
            note: 'Searches Church-owned domains using the wording of your question.'
        });
        results.push(source(OFFICIAL.topics, 'Official Church', 'Broad doctrine, practice, history, and question-based study.'));

        if (containsAny(q, HISTORY_TERMS)) {
            results.push(source(OFFICIAL.essays, 'Official Church', 'In-depth essays for complex historical and doctrinal topics.'));
            results.push(source(BYU.rscSearch, 'BYU educational', 'Secondary scholarly context; not an official doctrinal source.'));
        }

        if (containsAny(q, SCRIPTURE_TERMS)) {
            results.push(source(OFFICIAL.scriptures, 'Official Church', 'Read the standard works in Gospel Library.'));
            results.push(source(BYU.citation, 'BYU educational', 'See where scripture passages are cited in General Conference and other materials.'));
        }

        if (q.includes('book of mormon')) {
            results.push(source(OFFICIAL.bomVideos, 'Official Church media', 'Book of Mormon scenes for learning, teaching, and sharing.'));
        }

        if (q.includes('bible') || q.includes('new testament') || q.includes('jesus') || q.includes('christ')) {
            results.push(source(OFFICIAL.bibleVideos, 'Official Church media', 'New Testament scenes from the life and teachings of Jesus Christ.'));
        }

        if (q.includes('conference') || q.includes('prophet') || q.includes('apostle') || q.includes('general authority')) {
            results.push(source(OFFICIAL.conference, 'Official Church', 'Current and historical General Conference messages.'));
        }

        if (q.includes('video') || q.includes('art') || q.includes('picture') || q.includes('image')) {
            results.push(source(OFFICIAL.media, 'Official Church media', 'Official gospel video and image collections.'));
        }

        return uniqueSources(results).slice(0, 5);
    }

    function ensureStyles() {
        if (document.getElementById('focuschrist-source-router-styles')) return;
        const style = document.createElement('style');
        style.id = 'focuschrist-source-router-styles';
        style.textContent = `
            .fc-source-paths{margin-top:16px;padding:14px 15px;border:1px solid rgba(211,170,98,.25);border-radius:12px;background:rgba(211,170,98,.045)}
            .fc-source-paths-title{margin:0 0 9px;color:#d3aa62;font-size:.76rem;font-weight:700;letter-spacing:1.6px;text-transform:uppercase}
            .fc-source-paths-list{display:grid;gap:8px}
            .fc-source-path{display:block;padding:9px 10px;border-radius:9px;background:rgba(255,255,255,.025);text-decoration:none!important}
            .fc-source-path:hover,.fc-source-path:focus-visible{background:rgba(211,170,98,.09);outline:1px solid rgba(240,204,130,.38)}
            .fc-source-path strong{display:block;color:#f0cc82;font-size:.9rem;line-height:1.35}
            .fc-source-path span{display:block;margin-top:2px;color:#a9937e;font-size:.73rem;line-height:1.45}
            .fc-source-path-tier{color:#c39757!important;font-size:.68rem!important;text-transform:uppercase;letter-spacing:.8px}
        `;
        document.head.appendChild(style);
    }

    function latestQuestion(chatBox) {
        const messages = chatBox ? chatBox.querySelectorAll('.user-message') : [];
        return messages.length ? (messages[messages.length - 1].textContent || '').trim() : '';
    }

    function appendSourcePaths(answer, question) {
        if (!answer || answer.querySelector('.fc-source-paths')) return;
        const sources = sourcesForQuestion(question);
        if (!sources.length) return;

        const panel = document.createElement('aside');
        panel.className = 'fc-source-paths';
        panel.setAttribute('data-focuschrist-source-paths', 'true');
        panel.setAttribute('aria-label', 'Verified study sources');

        const title = document.createElement('div');
        title.className = 'fc-source-paths-title';
        title.textContent = 'Verified study paths';
        panel.appendChild(title);

        const list = document.createElement('div');
        list.className = 'fc-source-paths-list';
        sources.forEach(function (item) {
            const link = document.createElement('a');
            link.className = 'fc-source-path';
            link.href = item.url;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';

            const strong = document.createElement('strong');
            strong.textContent = item.label;
            link.appendChild(strong);

            const tier = document.createElement('span');
            tier.className = 'fc-source-path-tier';
            tier.textContent = item.tier;
            link.appendChild(tier);

            if (item.note) {
                const note = document.createElement('span');
                note.textContent = item.note;
                link.appendChild(note);
            }
            list.appendChild(link);
        });
        panel.appendChild(list);
        answer.appendChild(panel);
    }

    function enhanceLatest(chatBox) {
        if (!chatBox) return;
        const answers = chatBox.querySelectorAll('.bot-message');
        if (!answers.length) return;
        appendSourcePaths(answers[answers.length - 1], latestQuestion(chatBox));
    }

    function initAnswerObserver() {
        const chatBox = document.getElementById('chatBox');
        if (!chatBox || typeof MutationObserver === 'undefined') return;
        enhanceLatest(chatBox);
        const observer = new MutationObserver(function () {
            window.setTimeout(function () { enhanceLatest(chatBox); }, 40);
        });
        observer.observe(chatBox, { childList: true, subtree: true });
    }

    function loadGroundedIntelligence() {
        if (document.querySelector('script[data-focuschrist-study-intelligence-v3]')) return;
        const script = document.createElement('script');
        script.src = 'study-intelligence-v3.js?v=20260830-3';
        script.defer = true;
        script.setAttribute('data-focuschrist-study-intelligence-v3', 'true');
        script.addEventListener('error', function () {
            console.error('focusChrist Study Intelligence v3 failed to load.');
        }, { once: true });
        document.body.appendChild(script);
    }

    window.focusChristSourceRouter = {
        isFaithQuestion: isFaithQuestion,
        churchSearchUrl: churchSearchUrl,
        sourcesForQuestion: sourcesForQuestion
    };

    function init() {
        ensureStyles();
        initAnswerObserver();
        loadGroundedIntelligence();
        document.documentElement.setAttribute('data-focuschrist-source-router-ready', 'true');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init, { once: true });
    } else {
        init();
    }
})();