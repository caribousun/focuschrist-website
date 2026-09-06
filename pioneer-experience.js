/* focusChrist Pioneer conversation experience.
 * Page-specific historical context hardening for Journey, Trail, Pioneer Topics,
 * Tell My Story, and free-form pioneer questions.
 */
(function () {
    'use strict';

    const PROXY_URL = 'https://focuschrist-groq-proxy.caribousun.workers.dev';
    const MODEL = 'groq/compound';
    const PIONEER_POLICY_VERSION = '2026-09-03.16';
    let pioneerRequestSerial = 0;

    const PIONEER_TOPIC_ANSWERS = Object.freeze({
        'Exodus from Nauvoo': {
            answer: 'The Latter-day Saint exodus from Nauvoo began in February 1846 after mounting hostility made it unsafe for Church members to remain. Thousands crossed the Mississippi River and traveled slowly across Iowa. The difficult journey led Church leaders to establish way stations and, eventually, Winter Quarters near the Missouri River. The exodus was more than a single wagon departure: it was an organized migration that continued as later companies followed the first Saints west.',
            sources: [['Departure from Nauvoo', 'https://www.churchofjesuschrist.org/study/history/topics/departure-from-nauvoo?lang=eng']]
        },
        'Winter Quarters': {
            answer: 'Winter Quarters was a temporary Latter-day Saint settlement beside the Missouri River, established in 1846 after the difficult crossing of Iowa. Mud and sickness had slowed the migration, and families built cabins and dugouts, endured disease and shortages, and prepared companies and supplies for the journey west. It also became an important place of Church organization before Brigham Young and the vanguard company departed for the Salt Lake Valley in 1847.',
            sources: [['Winter Quarters', 'https://www.churchofjesuschrist.org/study/history/topics/winter-quarters?lang=eng']]
        },
        'Handcart Companies': {
            answer: 'From 1856 through 1860, 10 Latter-day Saint emigrating companies crossed the plains with handcarts. The plan offered people who could not afford wagon travel a less expensive way to gather to Utah. Most companies completed the journey without extraordinary loss, but the late-departing Willie and Martin companies were trapped by severe storms in 1856. Their suffering and the rescue sent from Utah are central parts of the handcart story.',
            sources: [['Handcart Companies', 'https://www.churchofjesuschrist.org/study/history/topics/handcart-companies?lang=eng']]
        },
        'Brigham Young': {
            answer: 'Brigham Young became President of the Quorum of the Twelve Apostles after Joseph Smith\'s death and directed preparations for the Saints\' westward migration. He led the 1847 vanguard company to the Salt Lake Valley and later served as the second President of the Church and the first governor of Utah Territory. His pioneer-era leadership included organizing migration, settlements, missionary work, temples, and the gathering of converts from many nations.',
            sources: [['Brigham Young', 'https://www.churchofjesuschrist.org/study/history/topics/brigham-young?lang=eng']]
        },
        'Salt Lake Valley': {
            answer: 'The 1847 vanguard company entered the Salt Lake Valley in July, with Brigham Young arriving on July 24. The pioneers immediately began planting, diverting water for irrigation, surveying a city, and building a settlement. The valley was not empty land: Native peoples had long used the wider region, and later settlement brought complicated and often strained relationships over land and resources.',
            sources: [['Salt Lake Valley', 'https://www.churchofjesuschrist.org/study/history/topics/salt-lake-valley?lang=eng'], ['Pioneer Settlements', 'https://www.churchofjesuschrist.org/study/history/topics/pioneer-settlements?lang=eng']]
        },
        'Pioneer Life': {
            answer: 'Pioneer life required constant work. On the trail, families walked, cared for animals, repaired wagons or handcarts, gathered fuel and water, cooked, washed, and made camp each day. In new settlements they built shelter, planted crops, dug irrigation ditches, established schools and worship services, and relied on neighbors when food, labor, or medical help was scarce. Experiences varied greatly by company, year, wealth, health, age, and location.',
            sources: [['Pioneer Trek', 'https://www.churchofjesuschrist.org/study/history/topics/pioneer-trek?lang=eng'], ['Pioneer Settlements', 'https://www.churchofjesuschrist.org/study/history/topics/pioneer-settlements?lang=eng']]
        },
        'Women Pioneers': {
            answer: 'Women were essential participants in the pioneer migration and settlement. They drove teams, pulled handcarts, prepared food, cared for children and the sick, gave birth on the trail, earned income, preserved family records, and helped establish religious and community life. Their journals and life histories show courage and faith, but also grief, exhaustion, disagreement, leadership, and individual agency rather than one single pioneer experience.',
            sources: [['Latter-day Saint Women\'s History', 'https://www.churchofjesuschrist.org/study/church-history/womens-history?lang=eng'], ['Church History Biographical Database', 'https://history.churchofjesuschrist.org/chd/landing?lang=eng']]
        },
        'Pioneer Faith': {
            answer: 'Many Latter-day Saint pioneers understood gathering as a covenant commitment to Jesus Christ. Prayer, worship, scripture, temple covenants, hymns, and mutual service helped them interpret sacrifice and endure uncertainty. Their records also preserve fear, sorrow, frustration, and questions. Pioneer faith is therefore best understood through their own journals and histories, not as a claim that every traveler felt or experienced the journey in the same way.',
            sources: [['Pioneer Trek', 'https://www.churchofjesuschrist.org/study/history/topics/pioneer-trek?lang=eng'], ['Hymns of the Trail', 'https://history.churchofjesuschrist.org/content/museum/museum-treasures-hymns-of-the-trail?lang=eng']]
        },
        'Pioneer Miracles': {
            answer: 'Pioneer accounts sometimes describe rescues, providential timing, unexpected food, healing, or strength beyond what participants believed they possessed. One well-known example is the fight to save the 1848 crops from crickets, later remembered in connection with arriving gulls. Official Church history also cautions that this story developed in the retelling. The most responsible study preserves both the pioneers\' faith-filled interpretation and what the surviving historical evidence can establish.',
            sources: [['Crickets and Seagulls', 'https://www.churchofjesuschrist.org/study/history/topics/crickets-and-seagulls?lang=eng'], ['Handcart Companies', 'https://www.churchofjesuschrist.org/study/history/topics/handcart-companies?lang=eng']]
        },
        'Pioneer Legacy': {
            answer: 'The pioneer legacy includes faith, migration, rescue, family sacrifice, temple building, and the creation of communities across the West. It also includes difficult history: settlement affected Native peoples, strained land and water relationships, and produced conflict as well as cooperation. Remembering the pioneers honestly means honoring courage and service while listening to individual records and acknowledging the consequences and complexities of settlement.',
            sources: [['Pioneer Settlements', 'https://www.churchofjesuschrist.org/study/history/topics/pioneer-settlements?lang=eng'], ['Pioneer Trek', 'https://www.churchofjesuschrist.org/study/history/topics/pioneer-trek?lang=eng']]
        },
        'Martin Handcart Company': {
            answer: 'Edward Martin led the fifth handcart company of 1856. Because the company left late, its members encountered deep snow, bitter cold, hunger, exhaustion, and death in present-day Wyoming. Rescuers from Utah brought food, wagons, clothing, and assistance, and the surviving company members reached Salt Lake City on November 30. Their story should be remembered both for extraordinary faith and rescue and for the grave consequences of late departure and inadequate provisions.',
            sources: [['Handcart Companies', 'https://www.churchofjesuschrist.org/study/history/topics/handcart-companies?lang=eng'], ['Go and Bring Them In', 'https://www.churchofjesuschrist.org/study/ensign/2006/12/go-and-bring-them-in?lang=eng']]
        },
        'Willie Handcart Company': {
            answer: 'James G. Willie led the fourth handcart company of 1856. The company departed late and was caught by severe autumn snow and cold in present-day Wyoming. Food had become critically scarce before rescuers from Utah reached the travelers. Survivors arrived in Salt Lake City on November 9. The Willie company\'s history joins devotion and endurance with an important warning about timing, preparation, and the human cost of the disaster.',
            sources: [['Handcart Companies', 'https://www.churchofjesuschrist.org/study/history/topics/handcart-companies?lang=eng'], ['Five Things about the Handcart Rescue', 'https://www.churchofjesuschrist.org/learn/history/sites/wyoming/discover/five-things-you-might-not-know-about-the-handcart-rescue?lang=eng']]
        },
        'Pioneer Daily Life': {
            answer: 'A typical travel day began early with prayer, breakfast, packing, and preparing animals or handcarts. Companies traveled as weather, water, terrain, health, and livestock allowed, then formed camp, cooked, repaired equipment, cared for the sick, guarded animals, and recorded the day. Sundays were often set apart for worship and rest. Daily routines differed between wagon and handcart companies and changed again once families began building permanent settlements.',
            sources: [['Pioneer Trek', 'https://www.churchofjesuschrist.org/study/history/topics/pioneer-trek?lang=eng'], ['1847 Trek Daily Summaries', 'https://newsroom.churchofjesuschrist.org/article/how-brigham-young-first-arrived-in-the-salt-lake-valley']]
        },
        'Pioneer Children': {
            answer: 'Children walked or rode according to their age, health, and available space. Many helped gather fuel, fetch water, herd livestock, care for younger children, prepare camp, or pull a handcart. They also played, sang, learned, and formed friendships. Journals and family histories record both adventure and severe hardship, including illness, hunger, bereavement, and deaths. Their experiences are best studied as individual lives rather than as one simplified pioneer-child story.',
            sources: [['Church History Biographical Database', 'https://history.churchofjesuschrist.org/chd/landing?lang=eng'], ['Pioneer Trek', 'https://www.churchofjesuschrist.org/study/history/topics/pioneer-trek?lang=eng']]
        },
        'Pioneer Food': {
            answer: 'Pioneer food depended on the company, season, resources, and stage of the journey. Travelers commonly carried durable staples such as flour or meal, bacon, beans, rice, dried fruit, sugar, and salt, while milk, butter, fresh meat, or gathered food varied with circumstances. Meals were cooked over fires, and safe water and fuel could be difficult to find. Rations became dangerously small in some late companies, especially during the 1856 handcart disaster.',
            sources: [['Pioneer Trek', 'https://www.churchofjesuschrist.org/study/history/topics/pioneer-trek?lang=eng'], ['Handcart Companies', 'https://www.churchofjesuschrist.org/study/history/topics/handcart-companies?lang=eng']]
        },
        'Pioneer Clothing': {
            answer: 'Pioneers generally wore ordinary mid-19th-century clothing adapted as well as possible for months of travel and outdoor labor. Layered wool and cotton garments, hats or bonnets, aprons, coats, stockings, boots, and sturdy shoes offered protection, but clothing wore out and had to be patched repeatedly. What a person owned depended on age, means, occupation, origin, and available packing space, so no single costume represents every Latter-day Saint pioneer.',
            sources: [['Church History Biographical Database', 'https://history.churchofjesuschrist.org/chd/landing?lang=eng'], ['Pioneer Trek', 'https://www.churchofjesuschrist.org/study/history/topics/pioneer-trek?lang=eng']]
        },
        'Pioneer Trails': {
            answer: 'The Latter-day Saint pioneer route began at Nauvoo, crossed Iowa to the Missouri River settlements, and then followed established overland corridors through present-day Nebraska and Wyoming before turning toward the Salt Lake Valley. Travelers passed landmarks such as Chimney Rock, Fort Laramie, Independence Rock, the Sweetwater River, South Pass, Fort Bridger, and Emigration Canyon. Routes and outfitting points changed over time, especially for later handcart companies.',
            sources: [['Pioneer Trek', 'https://www.churchofjesuschrist.org/study/history/topics/pioneer-trek?lang=eng'], ['Mormon Handcart Trail', 'https://history.churchofjesuschrist.org/article/interactive-map-mormon-handcart-trail?lang=eng']]
        }
    });

    function reviewedTopicAnswer(topic) {
        const entry = PIONEER_TOPIC_ANSWERS[String(topic || '').trim()];
        if (!entry) return null;
        return {
            id: 'pioneer-topic-' + String(topic).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''),
            answer: entry.answer,
            sources: entry.sources.map(function (source) {
                return { text: source[0], label: source[0], url: source[1], tier: 'Official Church History' };
            }),
            mode: 'reviewed-local-pioneer-topic',
            sourceIntegrityPassed: true,
            verifiedGrounding: true
        };
    }

    const PIONEER_PAGE_CONTEXT = [
        'PIONEER PAGE HARD CONTEXT:',
        '- This page is about 19th-century Latter-day Saint pioneer and related Church history.',
        '- UI-generated prompts from The Journey, The Trail, Willie & Martin Companies, and Pioneer Topics MUST be interpreted in Latter-day Saint pioneer context.',
        '- Ambiguous historical words on this page default to pioneer meaning unless the visitor explicitly asks for a different meaning.',
        '- In particular, "Exodus from Nauvoo" means the 1846 departure and westward migration of Latter-day Saints from Nauvoo, Illinois, across Iowa toward the Missouri River/Winter Quarters. It does NOT mean the biblical Book of Exodus.',
        '- Official Church history records that the first wagons left Nauvoo on February 4, 1846; thousands departed between February and September 1846; the difficult Iowa crossing led to the establishment of Winter Quarters; and the 1847 pioneer company later continued west toward the Salt Lake Valley.',
        '- Terms such as Nauvoo, Winter Quarters, Mormon Battalion, Mormon Trail, handcart company, Willie Company, Martin Company, rescue, Sweetwater, Martins Cove, Brigham Young, Salt Lake Valley, and pioneer exodus belong to this historical frame unless the visitor clearly says otherwise.'
    ].join('\n');

    const EXPLICIT_NON_PIONEER_RE = /\b(?:bible|biblical|old testament|book of exodus|moses|egypt|egyptian|israelites|ancient israel|sinai|pharaoh)\b/i;

    function chatBox() { return document.getElementById('chatBox'); }
    function userInput() { return document.getElementById('userInput'); }
    function sendButton() { return document.getElementById('sendBtn'); }
    function composerLabel() { return document.getElementById('pioneerComposerLabel'); }

    function resolvePioneerContext(question) {
        const registry = window.focusChristReviewedKnowledge;
        if (!registry || typeof registry.resolveFollowup !== 'function') {
            return { query: question, resolved: false, entryId: null, contextQuestion: null };
        }
        return registry.resolveFollowup(question, { profile: 'pioneers', history: recentHistory() });
    }

    function reviewedPioneerKnowledge(question, suppliedResolution) {
        const registry = window.focusChristReviewedKnowledge;
        if (!registry || typeof registry.match !== 'function') return null;
        const resolution = suppliedResolution || (typeof registry.resolveFollowup === 'function'
            ? registry.resolveFollowup(question, { profile: 'pioneers', history: recentHistory() })
            : { query: question, resolved: false, entryId: null });
        if (resolution.genericContext === true) return null;
        const reviewed = registry.match(resolution.query, {
            profile: 'pioneers',
            contextVariant: resolution.contextVariant
        });
        if (!reviewed) return null;
        return Object.assign({}, reviewed, {
            contextResolved: resolution.resolved === true,
            contextEntryId: resolution.entryId || null,
            contextQuestion: resolution.contextQuestion || null
        });
    }

    function appendTextParagraph(parent, text) {
        const p = document.createElement('p');
        p.textContent = text;
        parent.appendChild(p);
    }

    function safeSourceHref(value) {
        try {
            const url = new URL(value, window.location.href);
            if (url.protocol === 'http:' || url.protocol === 'https:' || url.origin === window.location.origin) return url.href;
        } catch (_error) {}
        return '#';
    }

    window.addMessage = function (text, isUser, sources = [], extraBtn = null) {
        const box = chatBox();
        if (!box) return null;

        const message = document.createElement('div');
        message.className = 'message ' + (isUser ? 'user-message' : 'bot-message');

        let rawText = String(text || '');
        if (!rawText.includes('\n') && rawText.length > 100) rawText = rawText.replace(/([.!?])\s+/g, '$1\n');
        const paragraphs = rawText.split('\n').map(function (item) { return item.trim(); }).filter(Boolean);

        if (isUser) {
            const p = document.createElement('p');
            const strong = document.createElement('strong');
            strong.textContent = 'You asked: ';
            p.appendChild(strong);
            p.appendChild(document.createTextNode(paragraphs[0] || rawText));
            message.appendChild(p);
        } else {
            (paragraphs.length ? paragraphs : [rawText]).forEach(function (paragraph) { appendTextParagraph(message, paragraph); });
        }

        if (!isUser && Array.isArray(sources) && sources.length) {
            const sourceWrap = document.createElement('div');
            sourceWrap.className = 'sources';
            const title = document.createElement('div');
            title.className = 'sources-title';
            title.textContent = 'Sources';
            sourceWrap.appendChild(title);
            sources.forEach(function (source) {
                const link = document.createElement('a');
                link.className = 'source-link';
                link.href = safeSourceHref(source.url || '#');
                link.target = '_blank';
                link.rel = 'noopener noreferrer';
                link.textContent = source.text || 'Source';
                sourceWrap.appendChild(link);
            });
            message.appendChild(sourceWrap);
        }

        if (!isUser && extraBtn && extraBtn.text) {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'pioneer-extra-action';
            button.textContent = extraBtn.text;
            if (extraBtn.action === 'askTellMyStory()' && typeof window.askTellMyStory === 'function') {
                button.addEventListener('click', function () { window.askTellMyStory(); });
            }
            message.appendChild(button);
        }

        box.appendChild(message);
        return message;
    };

    function recentHistory() {
        if (typeof conversationHistory === 'undefined' || !Array.isArray(conversationHistory)) return [];
        return conversationHistory.slice(-10).filter(function (item) {
            return item && (item.role === 'user' || item.role === 'assistant') && item.content;
        });
    }

    function rememberExchange(question, answer, contextReceipt) {
        if (typeof conversationHistory === 'undefined' || !Array.isArray(conversationHistory)) return;
        const userTurn = { role: 'user', content: question };
        if (contextReceipt && (contextReceipt.contextEntryId || contextReceipt.entryId)) {
            userTurn.contextEntryId = contextReceipt.contextEntryId || contextReceipt.entryId;
        }
        if (contextReceipt && contextReceipt.contextQuestion) userTurn.contextQuestion = contextReceipt.contextQuestion;
        conversationHistory.push(userTurn);
        conversationHistory.push({ role: 'assistant', content: String(answer || '') });
        while (conversationHistory.length > 20) conversationHistory.shift();
        try { sessionStorage.setItem('focuschrist_history', JSON.stringify(conversationHistory)); } catch (_error) {}
    }

    function normalizeDisplayText(text) {
        return String(text || '')
            .replace(/[\u00A0\u2007\u202F]/g, ' ')
            .replace(/[\u2010\u2011\u2012\u2013\u2014\u2212]/g, '-')
            .replace(/[\u2018\u2019]/g, "'")
            .replace(/[\u201C\u201D]/g, '"')
            .replace(/\u2026/g, '...')
            .replace(/[ \t]+\n/g, '\n')
            .replace(/[ \t]{2,}/g, ' ')
            .replace(/\n{3,}/g, '\n\n')
            .trim();
    }

    function buildSystemPrompt(question, pageReference) {
        const explicitOtherContext = EXPLICIT_NON_PIONEER_RE.test(question);
        return [
            'You are the historical study assistant on the focusChrist Pioneers page.',
            PIONEER_PAGE_CONTEXT,
            '',
            explicitOtherContext
                ? 'The visitor has explicitly signaled a biblical or non-pioneer context. Answer that explicit request directly, while not confusing it with the Pioneer-page default.'
                : 'No explicit non-pioneer context was requested. Stay inside the Latter-day Saint pioneer/history frame.',
            '',
            'HISTORICAL DISCIPLINE:',
            '- Answer the exact historical topic first.',
            '- Never switch an ambiguous Pioneer-page label to an unrelated biblical, general-history, or modern topic merely because a keyword overlaps.',
            '- Distinguish well-established fact from recollection, tradition, inference, disputed interpretation, or devotional retelling.',
            '- Never invent dates, people, quotations, journal language, miracles, statistics, source titles, URLs, or certainty.',
            '- If a precise detail is not grounded by the page context supplied here and you are not confident, state that limitation briefly instead of guessing.',
            '- Do not romanticize suffering. Do not manufacture providential claims or miracles.',
            '- Do not portray focusChrist as an official Church website.',
            '- Do not invent source URLs. The page provides verified source-routing separately.',
            '',
            'FAITH AND TONE:',
            '- Explain faith when it is genuinely part of the historical record or the visitor asks about it.',
            '- Do not append a canned testimony, blessing, or forced devotional closing.',
            '- Give a complete, useful answer unless the visitor explicitly asks for brevity. Never answer a sincere question with only one or two words.',
            '- For a simple fact, state the answer directly and add the context needed to understand it. For a nuanced topic, normally use two to five short paragraphs.',
            '- Be respectful, readable, and historically focused.',
            '- Use plain text, short paragraphs, and simple hyphen bullets only when useful.',
            '- End with a complete sentence.',
            pageReference ? '\nPAGE-SUPPLIED CONTEXT FOR THIS INTERACTION:\n' + pageReference : ''
        ].filter(Boolean).join('\n');
    }

    async function requestPioneerAI(question, pageReference, disclosureKey) {
        const messages = [{ role: 'system', content: buildSystemPrompt(question, pageReference || '') }];
        if (!disclosureKey) recentHistory().forEach(function (item) { messages.push({ role: item.role, content: String(item.content) }); });
        messages.push({ role: 'user', content: question });

        const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
        const timer = controller ? window.setTimeout(function () { controller.abort(); }, 75000) : null;
        try {
            const response = await fetch(PROXY_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: MODEL,
                    messages: messages,
                    focuschrist_page: 'pioneers',
                    focuschrist_pioneer_topic: disclosureKey || undefined,
                    focuschrist_profile: 'pioneer-study',
                    temperature: 0.2,
                    max_tokens: 1200
                }),
                signal: controller ? controller.signal : undefined
            });
            if (!response.ok) throw new Error('Pioneer study service returned ' + response.status);
            const data = await response.json();
            const raw = data && data.choices && data.choices[0] && data.choices[0].message ? data.choices[0].message.content : '';
            const sources = Array.isArray(data.focuschrist_sources) ? data.focuschrist_sources : [];
            const serverVerified = data.focuschrist_source_integrity_verified === true;
            let answer = normalizeDisplayText(raw);
            if (!answer) throw new Error('Empty Pioneer study response');
            const integrity = window.focusChristSourceIntegrity && typeof window.focusChristSourceIntegrity.guardGeneratedAnswer === 'function'
                ? window.focusChristSourceIntegrity.guardGeneratedAnswer(answer, {
                    trustedReferenceText: sources.map(function (source) { return (source.text || '') + ' ' + (source.url || ''); }).join('\n'),
                    requireTrustedScripture: true,
                    sourceDependent: true,
                    serverVerified: serverVerified
                })
                : { ok: false, answer: 'I cannot verify the source claim well enough to present it as authoritative.' };
            answer = integrity.answer;
            return {
                answer: answer,
                sources: integrity.ok ? sources : [],
                pioneerContext: true,
                sourceIntegrityPassed: integrity.ok && serverVerified,
                sourceIntegrityStatus: serverVerified ? String(data.focuschrist_gateway_mode || 'retrieval-researched-and-verified') : String(data.focuschrist_gateway_mode || 'verification-unavailable'),
                sourcePolicyVersion: String(data.focuschrist_source_policy || '')
            };
        } finally {
            if (timer) window.clearTimeout(timer);
        }
    }

    window.focusChristPioneerAskAI = requestPioneerAI;

    function setConversationMode(active) {
        const label = composerLabel();
        const input = userInput();
        if (label) label.textContent = active ? 'Continue the conversation' : 'Ask a pioneer question';
        if (input) input.placeholder = active ? 'Ask a follow-up question...' : 'Ask a sincere pioneer question...';
        document.body.classList.toggle('pioneer-conversation-active', !!active);
    }

    function preferredScrollBehavior() {
        return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
    }

    function fixedHeaderOffset() {
        const header = document.querySelector('.nav[data-focuschrist-header="standard"]');
        if (!header) return 20;
        const style = window.getComputedStyle(header);
        if (style.position !== 'fixed') return 20;
        return Math.ceil(header.getBoundingClientRect().height) + 24;
    }

    function scrollPageToElement(element) {
        if (!element) return;
        const top = element.getBoundingClientRect().top + window.scrollY - fixedHeaderOffset();
        window.scrollTo({ top: Math.max(0, top), behavior: preferredScrollBehavior() });
    }

    function ensurePioneerEntryStyles() {
        if (document.getElementById('pioneer-entry-styles')) return;
        const style = document.createElement('style');
        style.id = 'pioneer-entry-styles';
        style.textContent = `
            html[data-focuschrist-pioneer-entry-active] body.fc-site .qa-container {
                border-color: rgba(240,195,106,.68);
                box-shadow: var(--fc-shadow), 0 0 0 3px rgba(240,195,106,.10);
            }
        `;
        document.head.appendChild(style);
    }

    function focusPioneerComposer(updateHash) {
        const section = document.querySelector('.qa-section');
        const container = document.querySelector('.qa-container');
        const input = userInput();
        if (!section || !container || !input) return;

        section.id = 'ask-pioneers';
        document.documentElement.setAttribute('data-focuschrist-pioneer-entry-active', 'true');
        scrollPageToElement(container);

        window.setTimeout(function () {
            try { input.focus({ preventScroll: true }); } catch (_error) { input.focus(); }
        }, 260);

        if (updateHash && window.history && typeof window.history.replaceState === 'function') {
            window.history.replaceState(null, '', '#ask-pioneers');
        }
    }

    function initTopPioneerAskEntry() {
        const section = document.querySelector('.qa-section');
        const intro = document.querySelector('.fc-page-intro .fc-container--standard');
        const input = userInput();
        if (!section || !intro || !input) return;

        ensurePioneerEntryStyles();
        section.id = 'ask-pioneers';

        if (!intro.querySelector('[data-focuschrist-top-pioneer-ask-cta]')) {
            const actions = document.createElement('div');
            actions.className = 'fc-actions fc-actions--center';
            actions.setAttribute('data-focuschrist-top-pioneer-ask-cta', 'true');

            const link = document.createElement('a');
            link.className = 'fc-button fc-button--primary';
            link.href = '#ask-pioneers';
            link.textContent = 'Ask a Pioneer Question';
            link.addEventListener('click', function (event) {
                event.preventDefault();
                focusPioneerComposer(true);
            });
            actions.appendChild(link);
            intro.appendChild(actions);
        }

        input.addEventListener('focus', function () {
            document.documentElement.setAttribute('data-focuschrist-pioneer-entry-active', 'true');
        });

        window.addEventListener('hashchange', function () {
            if (window.location.hash === '#ask-pioneers') focusPioneerComposer(false);
        });

        if (window.location.hash === '#ask-pioneers') {
            window.setTimeout(function () { focusPioneerComposer(false); }, 90);
        }
    }

    function removeWelcome() {
        const box = chatBox();
        if (!box) return;
        const welcome = box.querySelector('.welcome');
        if (welcome) welcome.remove();
    }

    function showLoading(container) {
        const box = container || chatBox();
        if (!box) return null;
        const loading = document.createElement('div');
        loading.className = 'loading';
        loading.setAttribute('role', 'status');
        loading.textContent = 'Searching pioneer history and study sources...';
        box.appendChild(loading);
        if (box === chatBox()) box.scrollTop = box.scrollHeight;
        return loading;
    }

    function positionAnswer(answerElement) {
        const box = chatBox();
        if (!box || !answerElement) return;
        const internalTop = Math.max(0, answerElement.offsetTop - box.offsetTop - 12);
        box.scrollTo({ top: internalTop, behavior: 'smooth' });
        const header = document.querySelector('.nav[data-focuschrist-header="standard"]');
        const headerHeight = header && getComputedStyle(header).position === 'fixed' ? header.getBoundingClientRect().height : 0;
        const safeTop = headerHeight + 18;
        const rect = box.getBoundingClientRect();
        if (rect.top < safeTop || rect.top > window.innerHeight * 0.72) {
            window.scrollTo({ top: window.scrollY + rect.top - safeTop, behavior: 'smooth' });
        }
    }

    function pioneerRecordContext(choice) {
        const name = String(choice && choice.name || '').trim();
        return [
            'SELECTED PERSON FROM THE TELL MY STORY, TOO INDEX:',
            'Selected name: ' + name,
            'Retrieve this exact person’s complete entry from the server-owned Tell My Story, Too text, including continuation pages.',
            'Summarize that entry accurately without inventing details or reproducing long passages.',
            'Use official Church history records to corroborate identity and core chronology when available, while preserving attribution for family recollections and source traditions in the book.'
        ].join('\n');
    }

    function cleanLocalPioneerStory(choice) {
        const name = String(choice && choice.name || '').trim();
        let story = String(choice && (choice.fullStory || choice.story) || '').trim();
        if (!name || !story) return '';
        const escapedName = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const continuationHeader = new RegExp('^\\s*\\(' + escapedName + '\\s*-\\s*Page\\s+\\d+\\)\\s*$', 'gim');
        story = story
            .replace(/--- PAGE \d+ ---/g, '')
            .replace(/This biographical sketch comes from[\s\S]*?non-commercial purposes\./gi, '')
            .replace(continuationHeader, '')
            .replace(/^\s*\d+\s*$/gm, '')
            .replace(/\n{3,}/g, '\n\n')
            .trim();
        return story ? 'From Tell My Story, Too:\n\n' + story : '';
    }

    function showLocalPioneerStory(choice, originalQuestion) {
        const localStory = cleanLocalPioneerStory(choice);
        if (!localStory) return null;
        const selectedName = String(choice.name || '').trim();
        const question = originalQuestion && String(originalQuestion).trim()
            ? String(originalQuestion).trim() + ' — Selected: ' + selectedName
            : 'Selected: ' + selectedName;
        window.currentPioneerSelection = {
            name: selectedName,
            fullStory: String(choice.fullStory || choice.story || '')
        };
        document.documentElement.setAttribute('data-focuschrist-pioneer-answer-mode', 'reviewed-local-book-entry');
        const answer = window.addMessage(localStory, false, [{
            text: 'Tell My Story, Too — ' + selectedName,
            url: 'tell-my-story-too.txt'
        }]);
        rememberExchange(question, localStory.slice(0, 6000));
        setConversationMode(true);
        positionAnswer(answer);
        return answer;
    }

    async function answerSelectedPioneer(choice, originalQuestion, ownerRequestId) {
        if (!choice || !choice.name) return;
        const requestId = ownerRequestId || ++pioneerRequestSerial;
        window.storyChoices = null;
        const selectedName = String(choice.name).trim();
        window.addMessage('Selected: ' + selectedName, true);
        const localAnswer = showLocalPioneerStory(choice, originalQuestion);
        if (localAnswer) return;
        const loading = showLoading();
        try {
            const question = originalQuestion && String(originalQuestion).trim()
                ? String(originalQuestion).trim() + '\n\nSelected pioneer: ' + selectedName
                : 'Tell me about the Latter-day Saint pioneer ' + selectedName + '.';
            const response = await requestPioneerAI(question, pioneerRecordContext(choice));
            if (requestId !== pioneerRequestSerial) return;
            if (loading && loading.isConnected) loading.remove();
            rememberExchange(question, response.answer);
            const answer = window.addMessage(response.answer, false, response.sources || []);
            setConversationMode(true);
            positionAnswer(answer);
        } catch (error) {
            if (requestId !== pioneerRequestSerial) return;
            console.error('Selected pioneer research error:', error);
            if (loading && loading.isConnected) loading.remove();
            const answer = window.addMessage('I could not verify that pioneer record just now. Please try again or open the Church History Biographical Database.', false, [{
                text: 'Church History Biographical Database',
                url: 'https://history.churchofjesuschrist.org/chd/landing'
            }]);
            positionAnswer(answer);
        }
    }

    function renderPioneerChoices(match, originalQuestion) {
        const choices = Array.isArray(match && match.choices) ? match.choices : [];
        const answer = window.addMessage('I found more than one matching pioneer. Choose a person below so I use the correct record.', false);
        if (!answer || !choices.length) return answer;
        const group = document.createElement('div');
        group.className = 'pioneer-choice-list';
        group.setAttribute('role', 'group');
        group.setAttribute('aria-label', 'Choose a pioneer');
        choices.forEach(function (choice, index) {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'pioneer-choice';
            button.textContent = String(choice.name || ('Pioneer ' + (index + 1)));
            button.addEventListener('click', function () {
                group.querySelectorAll('button').forEach(function (item) { item.disabled = true; });
                answerSelectedPioneer(choice, originalQuestion);
            });
            group.appendChild(button);
        });
        answer.appendChild(group);
        window.storyChoices = choices;
        return answer;
    }

    window.selectPioneerStory = function (index) {
        const choices = Array.isArray(window.storyChoices) ? window.storyChoices : [];
        const choice = choices[Number(index)];
        if (choice) answerSelectedPioneer(choice, '');
    };
    window.focusChristAnswerSelectedPioneer = answerSelectedPioneer;

    function controlPageReference(control, kind, mappedTopic) {
        if (!control) return kind + ': ' + mappedTopic;
        const date = control.querySelector('.timeline-date, .map-date');
        const title = control.querySelector('.timeline-title, .map-content h4, .map-content h3');
        const desc = control.querySelector('.timeline-desc, .map-content p');
        return [
            kind + ': ' + mappedTopic,
            date && date.textContent.trim() ? 'Displayed date: ' + date.textContent.trim() : '',
            title && title.textContent.trim() ? 'Displayed title: ' + title.textContent.trim() : '',
            desc && desc.textContent.trim() ? 'Displayed description: ' + desc.textContent.trim() : ''
        ].filter(Boolean).join('\n');
    }

    function renderDisclosureAnswer(container, answer, sources) {
        container.innerHTML = '';
        String(answer || '').split('\n').map(function (part) { return part.trim(); }).filter(Boolean).forEach(function (part) {
            const p = document.createElement('p');
            p.textContent = part;
            container.appendChild(p);
        });
        (Array.isArray(sources) ? sources : []).forEach(function (source) {
            let url;
            try { url = new URL(source.url); } catch (_error) { return; }
            if (url.protocol !== 'https:' || !(url.hostname === 'churchofjesuschrist.org' || url.hostname.endsWith('.churchofjesuschrist.org'))) return;
            const paragraph = document.createElement('p');
            const link = document.createElement('a');
            link.href = url.href;
            link.textContent = 'Read the source: ' + String(source.text || 'Official Church history');
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            paragraph.appendChild(link);
            container.appendChild(paragraph);
        });
        const collapse = document.createElement('button');
        collapse.type = 'button';
        collapse.className = 'pioneer-collapse-action';
        collapse.textContent = 'Collapse';
        collapse.addEventListener('click', function (event) {
            event.stopPropagation();
            container.style.display = 'none';
            const control = container.closest('[data-focus-expand]');
            if (control) {
                control.classList.remove('expanded');
                control.setAttribute('aria-expanded', 'false');
            }
        });
        container.appendChild(collapse);
    }

    async function researchDisclosure(control, aiResponse, mappedTopic, kind) {
        if (aiResponse.dataset.focuschristResearchState === 'pending') return;
        aiResponse.dataset.focuschristResearchState = 'pending';
        control.setAttribute('data-focuschrist-disclosure-mode', 'loading');
        aiResponse.setAttribute('aria-busy', 'true');
        renderDisclosureAnswer(aiResponse, 'Researching this topic. The detailed answer will appear here.');
        try {
            const pageReference = controlPageReference(control, kind, mappedTopic);
            const heading = control.querySelector('.timeline-title, .map-content h4, .map-content h3');
            const subject = heading ? heading.textContent.trim() : mappedTopic;
            const query = 'Explain this Latter-day Saint pioneer history topic: ' + subject;
            const result = await requestPioneerAI(query, pageReference, control.getAttribute('data-topic'));
            if (!result || !result.sourceIntegrityPassed || !result.answer) {
                throw new Error('The detailed topic answer could not be verified');
            }
            renderDisclosureAnswer(aiResponse, result.answer, result.sources);
            aiResponse.dataset.focuschristResearchState = 'complete';
            aiResponse.dataset.focuschristLoaded = 'verified-research';
            control.setAttribute('data-focuschrist-disclosure-mode', 'verified-research');
        } catch (error) {
            console.error('Pioneer disclosure error:', error);
            aiResponse.dataset.focuschristResearchState = 'error';
            control.setAttribute('data-focuschrist-disclosure-mode', 'research-unavailable');
            renderDisclosureAnswer(aiResponse, 'A detailed answer could not be verified right now. You can try again or continue with the historical sources linked on this page.');
            const retry = document.createElement('button');
            retry.type = 'button';
            retry.className = 'pioneer-collapse-action';
            retry.textContent = 'Try again';
            retry.addEventListener('click', function (event) {
                event.stopPropagation();
                return researchDisclosure(control, aiResponse, mappedTopic, kind);
            });
            aiResponse.appendChild(retry);
        } finally {
            aiResponse.setAttribute('aria-busy', 'false');
        }
    }

    async function runDisclosure(control, mappedTopic, kind) {
        const aiResponse = control ? control.querySelector('.ai-response') : null;
        if (!control || !aiResponse) return;

        document.querySelectorAll('[data-focus-expand].expanded').forEach(function (item) {
            if (item !== control) {
                item.classList.remove('expanded');
                item.setAttribute('aria-expanded', 'false');
                const response = item.querySelector('.ai-response');
                if (response) response.style.display = 'none';
            }
        });

        const isExpanding = !control.classList.contains('expanded');
        control.classList.toggle('expanded', isExpanding);
        control.setAttribute('aria-expanded', isExpanding ? 'true' : 'false');
        if (!isExpanding) {
            aiResponse.style.display = 'none';
            return;
        }

        aiResponse.style.display = 'block';
        // A collapse only hides the panel. Preserve its answer or pending request.
        if (aiResponse.dataset.focuschristResearchState) return;
        await researchDisclosure(control, aiResponse, mappedTopic, kind);
    }
    window.focusChristRunPioneerDisclosure = runDisclosure;

    function disclosureTopic(control) {
        const key = control ? String(control.getAttribute('data-topic') || '') : '';
        const mode = control ? String(control.getAttribute('data-focus-expand') || '') : '';
        if (mode === 'trail') {
            const mapped = typeof trailTopicMap !== 'undefined' && trailTopicMap[key] ? trailTopicMap[key] : key;
            return { mapped: mapped || 'Pioneer trail', kind: 'Trail' };
        }
        const mapped = typeof topicMap !== 'undefined' && topicMap[key] ? topicMap[key] : key;
        const isHandcart = /^(?:willie|martin)-/i.test(key);
        return { mapped: mapped || 'Pioneer journey', kind: isHandcart ? 'Willie & Martin Companies' : 'Journey' };
    }

    function ownDisclosureEvent(event) {
        if (!event || !event.target || typeof event.target.closest !== 'function') return;
        const control = event.target.closest('[data-focus-expand]');
        if (!control) return;
        if (event.target.closest('.ai-response')) return;
        if (event.type === 'keydown' && event.key !== 'Enter' && event.key !== ' ') return;

        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();

        const topic = disclosureTopic(control);
        runDisclosure(control, topic.mapped, topic.kind);
    }

    function installDisclosureOwnership() {
        document.addEventListener('click', ownDisclosureEvent, true);
        document.addEventListener('keydown', ownDisclosureEvent, true);
        document.documentElement.setAttribute('data-focuschrist-pioneer-disclosure-controller', 'hardened');
    }

    window.expandTimelineItem = function (element, topic) {
        const mapped = typeof topicMap !== 'undefined' && topicMap[topic] ? topicMap[topic] : String(topic || 'Pioneer journey');
        const kind = /^(?:willie|martin)-/i.test(String(topic || '')) ? 'Willie & Martin Companies' : 'Journey';
        runDisclosure(element, mapped, kind);
    };

    window.expandTrailPoint = function (element, locationKey) {
        const mapped = typeof trailTopicMap !== 'undefined' && trailTopicMap[locationKey] ? trailTopicMap[locationKey] : String(locationKey || 'Pioneer trail');
        runDisclosure(element, mapped, 'Trail');
    };

    window.sendMessage = async function () {
        const input = userInput();
        const button = sendButton();
        if (!input || !button) return;
        const question = input.value.trim();
        if (!question) return;
        const safety = window.focusChristQuestionSafety && typeof window.focusChristQuestionSafety.evaluate === 'function'
            ? window.focusChristQuestionSafety.evaluate(question)
            : { allowed: !(typeof window.containsInappropriate === 'function' && window.containsInappropriate(question)), response: '' };
        if (!safety.allowed) {
            input.value = '';
            const answer = window.addMessage(safety.response || 'Please rephrase the question respectfully.', false);
            setConversationMode(true);
            positionAnswer(answer);
            try { input.focus({ preventScroll: true }); } catch (_error) { input.focus(); }
            return;
        }
        const requestId = ++pioneerRequestSerial;

        removeWelcome();
        window.addMessage(question, true);
        input.value = '';
        button.disabled = true;
        input.disabled = true;
        let loading = null;

        try {
            const contextResolution = resolvePioneerContext(question);
            const reviewed = reviewedPioneerKnowledge(question, contextResolution);
            if (reviewed) {
                const answer = window.addMessage(reviewed.answer, false, reviewed.sources || []);
                rememberExchange(question, reviewed.answer, reviewed);
                setConversationMode(true);
                positionAnswer(answer);
                return;
            }

            loading = showLoading();

            let pageReference = '';
            if (typeof searchTellMyStory === 'function') {
                const storyMatch = await searchTellMyStory(question);
                if (requestId !== pioneerRequestSerial) return;
                if (storyMatch && storyMatch[0] && storyMatch[0].full === false && storyMatch[0].choices) {
                    if (loading) loading.remove();
                    const answer = renderPioneerChoices(storyMatch[0], question);
                    setConversationMode(true);
                    positionAnswer(answer);
                    return;
                }
                if (storyMatch && storyMatch[0] && storyMatch[0].full === true) {
                    if (loading && loading.isConnected) loading.remove();
                    await answerSelectedPioneer(storyMatch[0], question, requestId);
                    return;
                }
                if (Array.isArray(storyMatch) && storyMatch.length && typeof storyMatch[0] === 'string') {
                    pageReference = 'Relevant excerpts located in the page Tell My Story collection:\n' + storyMatch.join('\n\n');
                }
            }

            const response = await requestPioneerAI(contextResolution.query || question, pageReference);
            if (requestId !== pioneerRequestSerial) return;
            if (loading && loading.isConnected) loading.remove();
            rememberExchange(question, response.answer, contextResolution);
            const answer = window.addMessage(response.answer, false, response.sources || []);
            setConversationMode(true);
            positionAnswer(answer);
        } catch (error) {
            if (requestId !== pioneerRequestSerial) return;
            console.error('Pioneer conversation error:', error);
            if (loading && loading.isConnected) loading.remove();
            const answer = window.addMessage('I could not complete that pioneer-history answer just now. Please try again or continue with the verified Church history resources.', false);
            setConversationMode(true);
            positionAnswer(answer);
        } finally {
            if (requestId !== pioneerRequestSerial) return;
            button.disabled = false;
            input.disabled = false;
            try { input.focus({ preventScroll: true }); } catch (_error) { input.focus(); }
        }
    };

    window.askTellMyStory = async function () {
        const text = typeof loadTellMyStory === 'function' ? await loadTellMyStory() : '';
        if (!text) {
            window.addMessage('I could not load the pioneer index just now. Please try again.', false);
            return;
        }
        const lines = String(text).split('\n');
        const starts = [];
        for (let index = 0; index < lines.length; index += 1) {
            const name = lines[index].trim();
            if (!/^[A-Z][A-Z\s]{3,}$/.test(name) || name.includes('PAGE') || name.includes('TELL MY')) continue;
            const nearby = lines.slice(index, index + 5).join(' ').toLowerCase();
            if (!(nearby.includes('company') || nearby.includes('handcart') || nearby.includes('born'))) continue;
            starts.push({ name: name, index: index });
        }
        const candidates = starts.map(function (entry, index) {
            const nextEntry = starts[index + 1];
            const end = nextEntry ? nextEntry.index : lines.length;
            return { name: entry.name, fullStory: lines.slice(entry.index, end).join('\n').trim() };
        });
        if (!candidates.length) {
            window.addMessage('I could not identify a pioneer record in the index just now.', false);
            return;
        }
        const selected = candidates[Math.floor(Math.random() * candidates.length)];
        await answerSelectedPioneer(selected, 'Tell me one verified pioneer story.');
    };

    window.askTopic = async function (topic) {
        const box = chatBox();
        if (!box) return;
        const requestId = ++pioneerRequestSerial;
        box.innerHTML = '';
        window.addMessage(topic, true);
        const reviewed = reviewedTopicAnswer(topic) || reviewedPioneerKnowledge(topic);
        if (reviewed) {
            const answer = window.addMessage(reviewed.answer, false, reviewed.sources || []);
            rememberExchange(topic, reviewed.answer, reviewed);
            setConversationMode(true);
            positionAnswer(answer);
            return;
        }
        const loading = showLoading();
        try {
            const query = 'Latter-day Saint pioneer history - Pioneer Topic: ' + topic;
            const response = await requestPioneerAI(query, 'Pioneer Topic button selected: ' + topic);
            if (requestId !== pioneerRequestSerial) return;
            if (loading && loading.isConnected) loading.remove();
            rememberExchange(topic, response.answer);
            const answer = window.addMessage(response.answer, false, response.sources || []);
            setConversationMode(true);
            positionAnswer(answer);
        } catch (error) {
            if (requestId !== pioneerRequestSerial) return;
            console.error('Pioneer topic error:', error);
            if (loading && loading.isConnected) loading.remove();
            window.addMessage('I could not complete that pioneer-history topic just now. Please try again.', false);
        }
    };

    window.clearChat = function () {
        pioneerRequestSerial += 1;
        if (typeof conversationHistory !== 'undefined' && Array.isArray(conversationHistory)) conversationHistory.length = 0;
        try { sessionStorage.removeItem('focuschrist_history'); } catch (_error) {}
        const box = chatBox();
        if (box) {
            box.innerHTML = '';
            const welcome = document.createElement('div');
            welcome.className = 'welcome';
            const h3 = document.createElement('h3');
            h3.textContent = 'Ask About Pioneers';
            const p = document.createElement('p');
            p.textContent = 'Ask a sincere question about Latter-day Saint pioneers and their history, or choose a topic below.';
            welcome.appendChild(h3);
            welcome.appendChild(p);
            box.appendChild(welcome);
        }
        const input = userInput();
        const button = sendButton();
        if (input) {
            input.value = '';
            input.disabled = false;
        }
        if (button) {
            button.disabled = false;
            button.textContent = 'Ask';
        }
        setConversationMode(false);
        if (input) {
            try { input.focus({ preventScroll: true }); } catch (_error) { input.focus(); }
        }
    };

    installDisclosureOwnership();

    document.addEventListener('DOMContentLoaded', function () {
        const inputArea = document.querySelector('.qa-container .input-area');
        if (inputArea && !document.getElementById('pioneerComposerLabel')) {
            const label = document.createElement('div');
            label.id = 'pioneerComposerLabel';
            label.className = 'pioneer-composer-label';
            label.textContent = 'Ask a pioneer question';
            inputArea.parentNode.insertBefore(label, inputArea);
        }
        const box = chatBox();
        if (box) {
            box.setAttribute('aria-live', 'polite');
            box.setAttribute('aria-label', 'Pioneer study conversation');
        }
        document.querySelectorAll('.category-btn').forEach(function (link) {
            link.addEventListener('click', function (event) { event.preventDefault(); });
        });
        initTopPioneerAskEntry();
        const warmTellMyStory = function () {
            if (typeof loadTellMyStory === 'function') loadTellMyStory();
        };
        if (typeof window.requestIdleCallback === 'function') window.requestIdleCallback(warmTellMyStory);
        else window.setTimeout(warmTellMyStory, 250);
        setConversationMode(false);
        document.documentElement.setAttribute('data-focuschrist-pioneer-policy', PIONEER_POLICY_VERSION);
    });
})();
