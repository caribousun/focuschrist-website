/* focusChrist reviewed local knowledge registry.
 *
 * These entries are individually reviewed and integrity-pinned in answer-audit.json.
 * The registry is the first answer lane for free-form and topic Ask controllers.
 * More-specific reviewed page sources (exact biographies and displayed cards)
 * retain priority on their dedicated interactions. Unreviewed legacy databases
 * are deliberately excluded.
 */
(function () {
    'use strict';

    const POLICY_VERSION = '2026-09-01.9';

    const ENTRIES = [
        {
            id: 'general-sky-blue',
            profiles: ['ask'],
            priority: 100,
            reviewedOn: '2026-09-01',
            integrityKey: 'general-sky-blue-v1',
            match: {
                guard: 'physical-sky',
                all: [
                    ['sky'],
                    ['blue'],
                    ['why', 'reason', 'cause', 'causes', 'look', 'looks', 'appear', 'appears']
                ],
                none: ['painting', 'paint', 'website', 'design', 'flag', 'shirt', 'screen']
            },
            positiveTests: [
                'Why is the sky blue?',
                'Why does the sky look blue?',
                'What causes the sky to appear blue?'
            ],
            negativeTests: [
                'Why is the sky blue in this painting?',
                'Why is the sky blue song popular?',
                'Design a blue sky website',
                'Why is my screen blue?'
            ],
            answer: "The sky looks blue because sunlight is scattered by Earth's atmosphere. Shorter blue wavelengths are scattered in all directions by air molecules more strongly than longer red wavelengths, so blue light reaches our eyes from across the sky.",
            sources: [
                {
                    text: 'NASA Space Place - Why Is the Sky Blue?',
                    label: 'NASA Space Place - Why Is the Sky Blue?',
                    url: 'https://spaceplace.nasa.gov/blue-sky/',
                    tier: 'Authoritative science source',
                    note: 'NASA explanation of atmospheric scattering.'
                }
            ]
        },
        {
            id: 'joseph-smith-death-1844',
            profiles: ['ask', 'pioneers', 'church-history'],
            priority: 120,
            reviewedOn: '2026-09-01',
            integrityKey: 'joseph-smith-death-1844-v1',
            match: {
                guard: 'joseph-smith',
                all: [
                    ['joseph', 'joseph smith', 'joseph the prophet'],
                    ['die', 'died', 'death', 'killed', 'martyred', 'martyrdom', 'murdered']
                ],
                none: ['stalin', 'kennedy', 'joseph of egypt', 'joseph in egypt', 'patriarch joseph']
            },
            positiveTests: [
                'What year was Joseph killed?',
                'When did Joseph Smith die?',
                'When did Joseph the Prophet die?',
                'When did Joseph Smith, the Prophet, die?',
                'Where was Joseph Smith martyred?'
            ],
            negativeTests: [
                'What year was Joseph Stalin killed?',
                'When did Joseph F. Smith die?',
                'When did Joseph Fielding Smith die?',
                'When did Joseph Smith Sr. die?',
                'Was Joseph of Egypt murdered?',
                'Joseph Kennedy death'
            ],
            answer: 'Assuming you mean Joseph Smith: he and his brother Hyrum were killed by a mob at Carthage Jail in Illinois on June 27, 1844. So the year was 1844.',
            sources: [
                {
                    text: 'Deaths of Joseph and Hyrum Smith',
                    label: 'Deaths of Joseph and Hyrum Smith',
                    url: 'https://www.churchofjesuschrist.org/study/history/topics/deaths-of-joseph-and-hyrum-smith?lang=eng',
                    tier: 'Official Church History',
                    note: 'Official Church History topic on the martyrdom.'
                },
                {
                    text: 'The Martyrdom of Joseph and Hyrum Smith',
                    label: 'The Martyrdom of Joseph and Hyrum Smith',
                    url: 'https://www.churchofjesuschrist.org/study/manual/latter-day-saint-history-1815-1846-teacher-material/lesson-26?lang=eng',
                    tier: 'Official Church History',
                    note: 'Official Church history teaching material.'
                }
            ]
        },
        {
            id: 'pioneer-handcart-travel-1856',
            profiles: ['pioneers', 'church-history'],
            priority: 140,
            reviewedOn: '2026-09-01',
            integrityKey: 'pioneer-handcart-travel-1856-v1',
            match: {
                guard: 'lds-handcart',
                all: [
                    ['handcart', 'handcarts', 'hand cart', 'hand carts'],
                    ['when', 'year', 'date', 'begin', 'began', 'start', 'started', 'introduced', 'use', 'used']
                ],
                none: ['race', 'racing', 'shopping', 'grocery', 'modern', 'patent', 'video game', 'game']
            },
            positiveTests: [
                'What year did the handcarts begin?',
                'When did handcart travel start?',
                'What year did the handcart companies begin?',
                'When were hand carts first used by the pioneers?'
            ],
            negativeTests: [
                'When did handcart racing begin?',
                'When did handcart use begin at the amusement park?',
                'When did shopping carts begin?',
                'Who patented the modern handcart?',
                'Tell me about a handcart video game'
            ],
            answer: 'Latter-day Saint handcart travel began in 1856 and continued through 1860. Only 10 of the more than 350 Latter-day Saint emigrating companies traveled by handcart.',
            sources: [
                {
                    text: 'Handcart Companies - Church History Topics',
                    label: 'Handcart Companies - Church History Topics',
                    url: 'https://www.churchofjesuschrist.org/study/history/topics/handcart-companies?lang=eng',
                    tier: 'Official Church History',
                    note: 'Official history of Latter-day Saint handcart travel.'
                }
            ]
        },
        {
            id: 'pioneer-nauvoo-exodus-1846',
            profiles: ['pioneers', 'church-history'],
            priority: 130,
            reviewedOn: '2026-09-01',
            integrityKey: 'pioneer-nauvoo-exodus-1846-v1',
            match: {
                all: [
                    ['exodus', 'departure', 'depart', 'departed', 'leave', 'left'],
                    ['nauvoo', 'pioneer', 'pioneers', 'saint', 'saints', 'latter day saint', 'latter day saints']
                ],
                none: ['bible', 'biblical', 'book of exodus', 'moses', 'egypt', 'pharaoh', 'israelite', 'israelites', 'sinai']
            },
            positiveTests: [
                'Tell me about the pioneer exodus',
                'When did the Saints leave Nauvoo?',
                'What year was the Nauvoo departure?'
            ],
            negativeTests: [
                'Tell me about the Exodus in the Bible',
                'When did Moses lead the Israelites out of Egypt?',
                'Explain the book of Exodus'
            ],
            answer: 'The Latter-day Saint exodus from Nauvoo began in February 1846. Thousands of Saints departed Nauvoo between February and September 1846, crossing Iowa toward the Missouri River and the temporary settlement at Winter Quarters.',
            sources: [
                {
                    text: 'Departure from Nauvoo - Church History Topics',
                    label: 'Departure from Nauvoo - Church History Topics',
                    url: 'https://www.churchofjesuschrist.org/study/history/topics/departure-from-nauvoo?lang=eng',
                    tier: 'Official Church History',
                    note: 'Official history of the 1846 departure from Nauvoo.'
                }
            ]
        },
        {
            id: 'church-first-vision-1820',
            profiles: ['church-history'],
            priority: 120,
            reviewedOn: '2026-09-01',
            integrityKey: 'church-first-vision-1820-v1',
            match: {
                all: [
                    ['first vision'],
                    ['when', 'year', 'date', 'where', 'place', 'location', 'happen', 'happened', 'occur', 'occurred', 'tell', 'about', 'explain']
                ],
                none: ['movie', 'film', 'painting', 'artwork']
            },
            positiveTests: [
                'When was the First Vision?',
                'Where did the First Vision happen?',
                'Tell me about the First Vision'
            ],
            negativeTests: [
                'Who painted the First Vision artwork?',
                'When was the First Vision movie released?'
            ],
            answer: "Joseph Smith reported that the First Vision occurred in the spring of 1820, when he prayed in a grove near his family's farm and said that God the Father and Jesus Christ appeared to him.",
            sources: [
                {
                    text: 'Joseph Smith Jr. - Church History Topics',
                    label: 'Joseph Smith Jr. - Church History Topics',
                    url: 'https://www.churchofjesuschrist.org/study/history/topics/joseph-smith-jr?lang=eng',
                    tier: 'Official Church History',
                    note: 'Official biographical history of Joseph Smith.'
                },
                {
                    text: "Joseph Smith's First Vision Accounts",
                    label: "Joseph Smith's First Vision Accounts",
                    url: 'https://www.churchofjesuschrist.org/study/history/topics/joseph-smiths-first-vision-accounts?lang=eng',
                    tier: 'Official Church History',
                    note: 'Official collection and discussion of the historical accounts.'
                }
            ]
        },
        {
            id: 'church-organization-1830',
            profiles: ['church-history'],
            priority: 115,
            reviewedOn: '2026-09-01',
            integrityKey: 'church-organization-1830-v1',
            match: {
                guard: 'restored-church',
                all: [
                    ['church', 'church of christ', 'restored church'],
                    ['organize', 'organized', 'organization', 'found', 'founded', 'founding', 'establish', 'established'],
                    ['when', 'year', 'date', 'where', 'what', 'tell', 'about']
                ],
                none: ['catholic', 'orthodox', 'anglican', 'methodist', 'baptist', 'lutheran', 'modern company']
            },
            positiveTests: [
                'When was the Church organized?',
                'What year was the restored Church founded?',
                'Where was the Church of Christ organized?'
            ],
            negativeTests: [
                'When was the Catholic Church founded?',
                'When was the Church of England organized?',
                'How should a modern company be organized?',
                'When was the Methodist church established?'
            ],
            answer: 'Joseph Smith, Oliver Cowdery, and others organized the Church of Christ on April 6, 1830. Official Church History notes that surviving accounts differ on whether the founding meeting occurred in Fayette or Manchester, New York, so the exact location should not be stated without that qualification.',
            sources: [
                {
                    text: 'Founding Meeting of the Church of Christ',
                    label: 'Founding Meeting of the Church of Christ',
                    url: 'https://www.churchofjesuschrist.org/study/history/topics/founding-meeting-of-the-church-of-christ?lang=eng',
                    tier: 'Official Church History',
                    note: 'Official account of the April 6, 1830 organization and the location-source discrepancy.'
                }
            ]
        }
    ];

    function normalize(value) {
        return String(value || '')
            .toLowerCase()
            .replace(/[^a-z0-9\s'-]/g, ' ')
            .replace(/[-']/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();
    }

    function hasTerm(normalizedQuery, tokenSet, term) {
        const normalizedTerm = normalize(term);
        if (!normalizedTerm) return false;
        if (normalizedTerm.includes(' ')) return (' ' + normalizedQuery + ' ').includes(' ' + normalizedTerm + ' ');
        return tokenSet.has(normalizedTerm);
    }

    const DOMAIN_GUARDS = Object.freeze({
        'physical-sky': function (query) {
            return !/\b(?:song|music|album|book|movie|film|poem|painting|artwork|design)\b/.test(query);
        },
        'joseph-smith': function (query) {
            if (/\bjoseph the prophet\b/.test(query)) return true;
            const explicit = query.match(/\bjoseph smith(?:\s+(\w+))?/);
            if (explicit) {
                if (explicit[1] === 'the') return /\bjoseph smith the prophet\b/.test(query);
                return !explicit[1] || ['jr', 'junior', 'was', 'is', 'did', 'die', 'died', 'death', 'killed', 'martyred', 'martyrdom', 'murdered', 'get', 'got'].includes(explicit[1]);
            }
            const bare = query.match(/\bjoseph(?:\s+(\w+))?/);
            if (!bare) return false;
            return !bare[1] || ['was', 'is', 'did', 'die', 'died', 'death', 'killed', 'martyred', 'martyrdom', 'murdered', 'get', 'got'].includes(bare[1]);
        },
        'lds-handcart': function (query) {
            return !/\b(?:amusement park|race|racing|shopping|grocery|patent|video game|game)\b/.test(query);
        },
        'restored-church': function (query) {
            const namedChurch = query.match(/\bchurch of\s+(\w+)/);
            return !namedChurch || ['christ', 'jesus'].includes(namedChurch[1]);
        }
    });

    function entryMatches(entry, question, profile) {
        if (!entry || !entry.match || !entry.profiles.includes(profile)) return false;
        const normalizedQuery = normalize(question);
        if (!normalizedQuery) return false;
        const tokenSet = new Set(normalizedQuery.split(' ').filter(Boolean));
        const guard = entry.match.guard && DOMAIN_GUARDS[entry.match.guard];
        if (guard && !guard(normalizedQuery)) return false;
        const excluded = (entry.match.none || []).some(function (term) {
            return hasTerm(normalizedQuery, tokenSet, term);
        });
        if (excluded) return false;
        return (entry.match.all || []).every(function (group) {
            return group.some(function (term) { return hasTerm(normalizedQuery, tokenSet, term); });
        });
    }

    function copySource(source) {
        return {
            text: source.text,
            label: source.label,
            url: source.url,
            tier: source.tier,
            note: source.note
        };
    }

    function deepFreeze(value) {
        if (!value || typeof value !== 'object' || Object.isFrozen(value)) return value;
        Object.keys(value).forEach(function (key) { deepFreeze(value[key]); });
        return Object.freeze(value);
    }

    function match(question, options) {
        const profile = String(options && options.profile || 'ask');
        const matched = ENTRIES
            .filter(function (entry) { return entryMatches(entry, question, profile); })
            .sort(function (left, right) { return right.priority - left.priority; })[0];
        if (!matched) return null;
        return {
            id: matched.id,
            answer: matched.answer,
            sources: matched.sources.map(copySource),
            profile: profile,
            mode: 'reviewed-local',
            reviewedOn: matched.reviewedOn,
            integrityKey: matched.integrityKey,
            policyVersion: POLICY_VERSION,
            sourceIntegrityPassed: true,
            verifiedGrounding: true
        };
    }

    ENTRIES.forEach(deepFreeze);

    window.focusChristReviewedKnowledge = Object.freeze({
        policyVersion: POLICY_VERSION,
        entries: Object.freeze(ENTRIES.slice()),
        normalize: normalize,
        match: match
    });
})();
