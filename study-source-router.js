/* focusChrist verified study-source router.
 * Adds dependable source pathways without inventing URLs.
 * Priority: official Church resources first; BYU resources are secondary only outside
 * the dedicated Church History source contract.
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

    const HISTORY = {
        hub: ['Official Church History', 'https://www.churchofjesuschrist.org/study/church-history?lang=eng'],
        saints: ['Saints', 'https://www.churchofjesuschrist.org/study/church-history/saints?lang=eng'],
        saints1: ['Saints, Volume 1: The Standard of Truth, 1815-1846', 'https://www.churchofjesuschrist.org/study/history/saints-v1?lang=eng'],
        saints2: ['Saints, Volume 2: No Unhallowed Hand, 1846-1893', 'https://www.churchofjesuschrist.org/study/history/saints-v2?lang=eng'],
        saints3: ['Saints, Volume 3: Boldly, Nobly, and Independent, 1893-1955', 'https://www.churchofjesuschrist.org/study/history/saints-v3?lang=eng'],
        saints4: ['Saints, Volume 4: Sounded in Every Ear, 1955-2020', 'https://www.churchofjesuschrist.org/study/history/saints-v4?lang=eng'],
        topics: ['Church History Topics', 'https://www.churchofjesuschrist.org/study/history/topics?lang=eng'],
        firstVision: ['Joseph Smith’s First Vision Accounts', 'https://www.churchofjesuschrist.org/study/history/topics/joseph-smiths-first-vision-accounts?lang=eng'],
        firstVisionCollection: ['First Vision', 'https://www.churchofjesuschrist.org/study/manual/first-vision-accounts?lang=eng'],
        bomTranslation: ['Book of Mormon Translation', 'https://www.churchofjesuschrist.org/study/history/topics/book-of-mormon-translation?lang=eng'],
        seerStones: ['Seer Stones', 'https://www.churchofjesuschrist.org/study/history/topics/seer-stones?lang=eng'],
        kirtlandSafety: ['The Kirtland Safety Society', 'https://www.churchofjesuschrist.org/study/history/topics/kirtland-safety-society?lang=eng'],
        mountainMeadows: ['Mountain Meadows Massacre', 'https://www.churchofjesuschrist.org/study/history/topics/mountain-meadows-massacre?lang=eng'],
        aaronic: ['Restoration of the Aaronic Priesthood', 'https://www.churchofjesuschrist.org/study/history/topics/restoration-of-the-aaronic-priesthood?lang=eng'],
        melchizedek: ['Restoration of the Melchizedek Priesthood', 'https://www.churchofjesuschrist.org/study/history/topics/restoration-of-the-melchizedek-priesthood?lang=eng'],
        pluralMarriage: ['Joseph Smith and Plural Marriage', 'https://www.churchofjesuschrist.org/study/history/topics/joseph-smith-and-plural-marriage?lang=eng'],
        handcarts: ['Handcart Companies', 'https://www.churchofjesuschrist.org/study/history/topics/handcart-companies?lang=eng'],
        wordOfWisdom: ['Word of Wisdom (D&C 89)', 'https://www.churchofjesuschrist.org/study/history/topics/word-of-wisdom-dc-89?lang=eng'],
        women: ['Women’s History', 'https://www.churchofjesuschrist.org/study/church-history/womens-history?lang=eng'],
        jspPodcasts: ['Joseph Smith Papers Podcasts', 'https://www.churchofjesuschrist.org/study/manual/joseph-smith-papers-podcasts?lang=eng'],
        essays: ['Gospel Topics Essays', 'https://www.churchofjesuschrist.org/study/manual/gospel-topics-essays?lang=eng'],
        answers: ['Answers to Church History Questions', 'https://www.churchofjesuschrist.org/study/video/answers-to-church-history-questions?lang=eng'],
        global: ['Global Histories', 'https://www.churchofjesuschrist.org/study/history/global-histories?lang=eng']
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
        'church history','history of the church','historical','joseph smith','oliver cowdery','emma smith','brigham young','first vision',
        'restoration','pioneer','plural marriage','polygamy','race and priesthood','book of abraham','mountain meadows','nauvoo','kirtland',
        'missouri','handcart','willie','martin','martyrdom','priesthood restoration','seer stone','gold plates','saints volume','saints book',
        'manifesto','mormon battalion','winter quarters','liberty jail','kirtland safety society','extermination order','global histories'
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

    function pathEnds(name) {
        return window.location.pathname.toLowerCase().endsWith('/' + name);
    }

    function isPioneerPage() { return pathEnds('pioneers.html'); }
    function isChurchHistoryPage() { return pathEnds('church-history.html'); }

    function isFaithQuestion(question) {
        const sharedScriptureDependency = window.focusChristSourceIntegrity
            && typeof window.focusChristSourceIntegrity.isScriptureDependent === 'function'
            && window.focusChristSourceIntegrity.isScriptureDependent(question);
        return isPioneerPage() || isChurchHistoryPage() || sharedScriptureDependency || containsAny(question, FAITH_TERMS);
    }

    function isChurchHistoryQuestion(question) {
        if (isChurchHistoryPage() || isPioneerPage()) return true;
        const q = normalize(question);
        if (containsAny(q, HISTORY_TERMS)) return true;
        return q.includes('history') && containsAny(q, FAITH_TERMS);
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

    function historyEraSources(q, results) {
        const years = (q.match(/\b(18\d{2}|19\d{2}|20(?:0\d|1\d|20))\b/g) || []).map(Number);
        years.forEach(function (year) {
            if (year >= 1815 && year <= 1846) results.push(source(HISTORY.saints1, 'Official Church History', 'Narrative history for 1815-1846.'));
            else if (year >= 1846 && year <= 1893) results.push(source(HISTORY.saints2, 'Official Church History', 'Narrative history for 1846-1893.'));
            else if (year >= 1893 && year <= 1955) results.push(source(HISTORY.saints3, 'Official Church History', 'Narrative history for 1893-1955.'));
            else if (year >= 1955 && year <= 2020) results.push(source(HISTORY.saints4, 'Official Church History', 'Narrative history for 1955-2020.'));
        });
    }

    function sourcesForHistoryQuestion(question) {
        const q = normalize(question);
        const results = [];

        if (q.includes('first vision')) {
            results.push(source(HISTORY.firstVision, 'Official Church History', 'Church History Topic on the historical First Vision accounts.'));
            results.push(source(HISTORY.firstVisionCollection, 'Official Church History', 'Dedicated First Vision study collection.'));
        }
        if (q.includes('book of mormon') && (q.includes('translat') || q.includes('seer') || q.includes('stone'))) {
            results.push(source(HISTORY.bomTranslation, 'Official Church History', 'Church History Topic on Book of Mormon translation.'));
        }
        if (q.includes('seer stone') || q.includes('seer stones')) {
            results.push(source(HISTORY.seerStones, 'Official Church History', 'Church History Topic on seer stones.'));
        }
        if (q.includes('kirtland safety') || q.includes('kirtland bank') || (q.includes('kirtland') && q.includes('bank'))) {
            results.push(source(HISTORY.kirtlandSafety, 'Official Church History', 'Church History Topic on the Kirtland Safety Society.'));
        }
        if (q.includes('mountain meadows')) {
            results.push(source(HISTORY.mountainMeadows, 'Official Church History', 'Church History Topic on the Mountain Meadows Massacre.'));
            results.push(source(HISTORY.answers, 'Official Church History', 'Church-produced answers to frequently asked history questions.'));
        }
        if (q.includes('aaronic') || q.includes('john the baptist')) {
            results.push(source(HISTORY.aaronic, 'Official Church History', 'Church History Topic on restoration of the Aaronic Priesthood.'));
        }
        if (q.includes('melchizedek') || q.includes('peter james and john')) {
            results.push(source(HISTORY.melchizedek, 'Official Church History', 'Church History Topic on restoration of the Melchizedek Priesthood.'));
        }
        if (q.includes('priesthood restoration') || (q.includes('restoration') && q.includes('priesthood'))) {
            results.push(source(HISTORY.aaronic, 'Official Church History', 'Aaronic Priesthood restoration.'));
            results.push(source(HISTORY.melchizedek, 'Official Church History', 'Melchizedek Priesthood restoration.'));
        }
        if (q.includes('plural marriage') || q.includes('polygamy')) {
            results.push(source(HISTORY.pluralMarriage, 'Official Church History', 'Church History Topic on Joseph Smith and plural marriage.'));
            results.push(source(HISTORY.essays, 'Official Church', 'Official essays for additional historical and doctrinal context.'));
            results.push(source(HISTORY.answers, 'Official Church History', 'Church-produced answers to frequently asked history questions.'));
        }
        if (q.includes('handcart') || q.includes('willie') || q.includes('martin')) {
            results.push(source(HISTORY.handcarts, 'Official Church History', 'Church History Topic on handcart companies.'));
            results.push(source(HISTORY.saints2, 'Official Church History', 'The pioneer era in Saints, Volume 2.'));
        }
        if (q.includes('word of wisdom')) {
            results.push(source(HISTORY.wordOfWisdom, 'Official Church History', 'Church History Topic on the historical development of Word of Wisdom observance.'));
        }
        if (q.includes('women') || q.includes('relief society') || q.includes('eliza r. snow') || q.includes('emmeline')) {
            results.push(source(HISTORY.women, 'Official Church History', 'Official women’s history collection.'));
        }
        if (q.includes('joseph smith') || q.includes('emma smith') || q.includes('oliver cowdery')) {
            results.push(source(HISTORY.saints1, 'Official Church History', 'Narrative history of the early Restoration era.'));
            results.push(source(HISTORY.jspPodcasts, 'Official Church History', 'Church-hosted Joseph Smith Papers podcast series.'));
        }
        if (q.includes('nauvoo') || q.includes('martyrdom') || q.includes('liberty jail') || q.includes('missouri')) {
            results.push(source(HISTORY.saints1, 'Official Church History', 'Narrative history through the Nauvoo era and 1846.'));
        }
        if (q.includes('pioneer') || q.includes('brigham young') || q.includes('winter quarters') || q.includes('mormon battalion')) {
            results.push(source(HISTORY.saints2, 'Official Church History', 'Narrative history of the pioneer and settlement era.'));
        }
        if (q.includes('global') || q.includes('worldwide') || q.includes('country') || q.includes('africa') || q.includes('asia') || q.includes('europe') || q.includes('latin america') || q.includes('mexico') || q.includes('pacific')) {
            results.push(source(HISTORY.global, 'Official Church History', 'Country and regional histories from the Church History Department.'));
        }
        if (q.includes('twentieth century') || q.includes('20th century') || q.includes('world war') || q.includes('modernization')) {
            results.push(source(HISTORY.saints3, 'Official Church History', 'Narrative history for 1893-1955.'));
            results.push(source(HISTORY.saints4, 'Official Church History', 'Narrative history for 1955-2020.'));
        }
        if (q.includes('modern church') || q.includes('recent history') || q.includes('globalization')) {
            results.push(source(HISTORY.saints4, 'Official Church History', 'Narrative history for 1955-2020.'));
            results.push(source(HISTORY.global, 'Official Church History', 'Global and regional Church histories.'));
        }

        historyEraSources(q, results);

        results.push(source(HISTORY.topics, 'Official Church History', 'A-Z historical topic index for people, events, places, practices, and developments.'));
        results.push(source(HISTORY.saints, 'Official Church History', 'Current four-volume narrative history plus Saints study resources.'));
        results.push(source(HISTORY.hub, 'Official Church History', 'Primary Church History resource hub.'));
        results.push({
            label: 'Search official Church sources for this history question',
            url: churchSearchUrl(question),
            tier: 'Official Church search',
            note: 'Searches Church-owned resources using the wording of the question.'
        });

        return uniqueSources(results).slice(0, 6);
    }

    function historyPromptContext(question) {
        const sources = sourcesForHistoryQuestion(question);
        return [
            'CHURCH HISTORY PAGE SOURCE CONTRACT:',
            '- This is specifically a Latter-day Saint Church history question.',
            '- The governing source family is the official Church History collection at ChurchofJesusChrist.org and the current four-volume Saints narrative history.',
            '- Treat the verified official source routes listed below as higher authority than model memory.',
            '- Do not use external commentary, social media, unsourced apologetics, criticism, or general model memory to override the official source family.',
            '- Do not invent quotations, dates, motives, participants, document contents, miracle claims, statistics, or historical certainty.',
            '- If a requested detail is not reliably established by the official source family available to you, say that the detail should be verified in the linked official source rather than guessing.',
            '- Distinguish documented events from later recollection, tradition, interpretation, and disputed claims when that distinction matters.',
            '- For sensitive or contested subjects, describe the Church’s historical account accurately without pretending it settles claims the official sources do not establish.',
            '- Keep the answer useful and direct; the visitor will receive the official links after the answer.',
            '',
            'OFFICIAL STUDY ROUTES (LINKS ONLY; NOT CLAIM VERIFICATION):',
            sources.map(function (item) { return '- ' + item.label + ': ' + item.url; }).join('\n')
        ].join('\n');
    }

    function sourcesForQuestion(question) {
        if (!isFaithQuestion(question)) return [];
        const sharedScriptureDependency = window.focusChristSourceIntegrity
            && typeof window.focusChristSourceIntegrity.isScriptureDependent === 'function'
            && window.focusChristSourceIntegrity.isScriptureDependent(question);
        if (isChurchHistoryQuestion(question) && !sharedScriptureDependency) return sourcesForHistoryQuestion(question);

        const q = normalize(question);
        const results = [];
        results.push({
            label: 'Search official Church sources for this question',
            url: churchSearchUrl(question),
            tier: 'Official Church search',
            note: 'Searches Church-owned domains using the wording of your question.'
        });
        results.push(source(OFFICIAL.topics, 'Official Church', 'Broad doctrine, practice, history, and question-based study.'));

        if (sharedScriptureDependency || containsAny(q, SCRIPTURE_TERMS)) {
            results.push(source(OFFICIAL.scriptures, 'Official Church', 'Read the standard works in Gospel Library.'));
            results.push(source(BYU.citation, 'BYU educational', 'See where scripture passages are cited in General Conference and other materials.'));
        }
        if (q.includes('book of mormon')) results.push(source(OFFICIAL.bomVideos, 'Official Church media', 'Book of Mormon scenes for learning, teaching, and sharing.'));
        if (q.includes('bible') || q.includes('new testament') || q.includes('jesus') || q.includes('christ')) results.push(source(OFFICIAL.bibleVideos, 'Official Church media', 'New Testament scenes from the life and teachings of Jesus Christ.'));
        if (q.includes('conference') || q.includes('prophet') || q.includes('apostle') || q.includes('general authority')) results.push(source(OFFICIAL.conference, 'Official Church', 'Current and historical General Conference messages.'));
        if (q.includes('video') || q.includes('art') || q.includes('picture') || q.includes('image')) results.push(source(OFFICIAL.media, 'Official Church media', 'Official gospel video and image collections.'));

        return uniqueSources(results).slice(0, 5);
    }

    function ensureStyles() {
        if (document.getElementById('focuschrist-source-router-styles')) return;
        const style = document.createElement('style');
        style.id = 'focuschrist-source-router-styles';
        style.textContent = `
            .fc-source-paths{margin-top:16px;padding:14px 15px;border:1px solid rgba(224,170,62,.25);border-radius:12px;background:rgba(224,170,62,.045)}
            .fc-source-paths-title{margin:0 0 9px;color:#f0c36a;font-size:.76rem;font-weight:700;letter-spacing:1.6px;text-transform:uppercase}
            .fc-source-paths-list{display:grid;gap:8px}
            .fc-source-path{display:block;padding:9px 10px;border-radius:9px;background:rgba(134,175,200,.035);text-decoration:none!important}
            .fc-source-path:hover,.fc-source-path:focus-visible{background:rgba(134,175,200,.11);outline:1px solid rgba(240,195,106,.38)}
            .fc-source-path strong{display:block;color:#f0c36a;font-size:.9rem;line-height:1.35}
            .fc-source-path span{display:block;margin-top:2px;color:#92a6a8;font-size:.73rem;line-height:1.45}
            .fc-source-path-tier{color:#9eaa83!important;font-size:.68rem!important;text-transform:uppercase;letter-spacing:.8px}
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
        panel.setAttribute('aria-label', 'Official study routes');

        const title = document.createElement('div');
        title.className = 'fc-source-paths-title';
        const scriptureQuestion = window.focusChristSourceIntegrity
            && typeof window.focusChristSourceIntegrity.isScriptureDependent === 'function'
            && window.focusChristSourceIntegrity.isScriptureDependent(question);
        title.textContent = isChurchHistoryQuestion(question) && !scriptureQuestion
            ? 'Official Church History paths'
            : 'Official study paths';
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
        if (document.querySelector('script[data-focuschrist-study-intelligence-v3]') || document.querySelector('script[src*="study-intelligence-v3.js"]')) return;
        const script = document.createElement('script');
        script.src = 'study-intelligence-v3.js?v=20260831-5';
        script.defer = true;
        script.setAttribute('data-focuschrist-study-intelligence-v3', 'true');
        script.addEventListener('error', function () { console.error('focusChrist Study Intelligence v3 failed to load.'); }, { once: true });
        document.body.appendChild(script);
    }

    window.focusChristSourceRouter = {
        isFaithQuestion: isFaithQuestion,
        isChurchHistoryQuestion: isChurchHistoryQuestion,
        churchSearchUrl: churchSearchUrl,
        sourcesForQuestion: sourcesForQuestion,
        sourcesForHistoryQuestion: sourcesForHistoryQuestion,
        historyPromptContext: historyPromptContext
    };

    function init() {
        ensureStyles();
        initAnswerObserver();
        loadGroundedIntelligence();
        document.documentElement.setAttribute('data-focuschrist-source-router-ready', 'true');
        document.documentElement.setAttribute('data-focuschrist-history-source-index', 'official-church-history-v1');
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
    else init();
})();
