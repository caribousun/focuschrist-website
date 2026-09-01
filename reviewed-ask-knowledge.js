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

    const POLICY_VERSION = '2026-09-01.10';

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
            id: 'ask-jesus-christ-central',
            profiles: ['ask'],
            priority: 180,
            reviewedOn: '2026-09-01',
            integrityKey: 'ask-jesus-christ-central-v1',
            match: {
                exact: [
                    'Who is Jesus Christ, and why is He central to Latter-day Saint belief?',
                    'Who is Jesus Christ?',
                    'Why is Jesus Christ central to Latter-day Saint belief?'
                ],
                all: [
                    ['jesus', 'jesus christ', 'christ'],
                    ['who', 'central', 'important', 'belief', 'believe']
                ],
                none: ['jesus christ superstar', 'actor', 'film', 'movie', 'paint', 'painted', 'painting']
            },
            positiveTests: [
                'Who is Jesus Christ, and why is He central to Latter-day Saint belief?',
                'Who is Jesus Christ?',
                'Why is Christ central to Latter-day Saint belief?'
            ],
            negativeTests: [
                'Who played Jesus Christ in that movie?',
                'Who painted this image of Jesus Christ?'
            ],
            answer: 'Latter-day Saints worship Jesus Christ as the divine Son of God and the Savior and Redeemer of the world. They believe He was chosen before mortality to carry out the Father\'s plan, lived a perfect mortal life, atoned for humanity\'s sins and suffering, died on the cross, and rose bodily from the dead.\n\nHe is central because every part of salvation depends on Him. His Resurrection makes resurrection possible for everyone, and His grace makes repentance, forgiveness, spiritual healing, and eternal life possible. Latter-day Saint teachings about scripture, priesthood, prophets, temples, ordinances, covenants, and discipleship are intended to lead people to Jesus Christ, not replace Him.',
            sources: [
                {
                    text: 'Jesus Christ - Gospel Study Guide',
                    label: 'Jesus Christ - Gospel Study Guide',
                    url: 'https://www.churchofjesuschrist.org/study/manual/gospel-topics/jesus-christ-study-guide?lang=eng',
                    tier: 'Official Church teaching',
                    note: 'Official overview of Jesus Christ as Savior and Redeemer.'
                },
                {
                    text: 'The Living Christ: The Testimony of the Apostles',
                    label: 'The Living Christ: The Testimony of the Apostles',
                    url: 'https://www.churchofjesuschrist.org/study/scriptures/the-living-christ-the-testimony-of-the-apostles/the-living-christ-the-testimony-of-the-apostles?lang=eng',
                    tier: 'Official apostolic testimony',
                    note: 'Official apostolic testimony of the life and mission of Jesus Christ.'
                }
            ]
        },
        {
            id: 'ask-prayer-personal-revelation',
            profiles: ['ask'],
            priority: 175,
            reviewedOn: '2026-09-01',
            integrityKey: 'ask-prayer-personal-revelation-v1',
            match: {
                exact: [
                    'How can I recognize answers to prayer and personal revelation?',
                    'How can I recognize answers to prayer?',
                    'How do I recognize personal revelation?'
                ],
                all: [
                    ['prayer', 'pray', 'personal revelation', 'revelation'],
                    ['answer', 'answers', 'recognize', 'discern', 'guidance', 'know']
                ],
                none: ['survey', 'quiz', 'exam', 'trivia']
            },
            positiveTests: [
                'How can I recognize answers to prayer and personal revelation?',
                'How can I recognize answers to prayer?',
                'How do I discern personal revelation?'
            ],
            negativeTests: [
                'How do I recognize answers on a school exam?',
                'How should I analyze survey answers about prayer?'
            ],
            answer: 'Latter-day Saints believe Heavenly Father hears sincere prayer and can guide individuals through the Holy Ghost. An answer may come as peace, warning, clearer understanding, remembered truth, a quiet recurring impression, or gradual direction rather than a dramatic sign. A person can prepare by praying sincerely, studying the question, searching scripture, making a thoughtful decision, and remaining willing to accept correction.\n\nNot every feeling is revelation. A trustworthy impression will be consistent with God\'s commandments and the teachings of Jesus Christ, will respect other people\'s agency, and will stay within the responsibilities God has given you. Time, repeated impressions, scripture, wise counsel, and the spiritual and practical fruits of a choice can help test it. If no answer comes immediately, faithful waiting and responsible action may be part of the answer.',
            sources: [
                {
                    text: 'Prayer - Gospel Study Guide',
                    label: 'Prayer - Gospel Study Guide',
                    url: 'https://www.churchofjesuschrist.org/study/manual/gospel-topics/prayer-study-guide?lang=eng',
                    tier: 'Official Church teaching',
                    note: 'Official study guide on prayer and receiving answers.'
                },
                {
                    text: 'Revelation - Gospel Study Guide',
                    label: 'Revelation - Gospel Study Guide',
                    url: 'https://www.churchofjesuschrist.org/study/manual/gospel-topics/revelation-study-guide?lang=eng',
                    tier: 'Official Church teaching',
                    note: 'Official study guide on revelation and personal guidance.'
                }
            ]
        },
        {
            id: 'ask-why-build-temples',
            profiles: ['ask'],
            priority: 175,
            reviewedOn: '2026-09-01',
            integrityKey: 'ask-why-build-temples-v1',
            match: {
                exact: [
                    'Why do Latter-day Saints build temples?',
                    'Why does the Church build temples?',
                    'What is the purpose of Latter-day Saint temples?'
                ],
                all: [
                    ['temple', 'temples'],
                    ['why', 'build', 'purpose', 'used', 'worship']
                ],
                none: ['solomon', 'herod', 'ancient greek', 'hindu', 'buddhist']
            },
            positiveTests: [
                'Why do Latter-day Saints build temples?',
                'Why does the Church build temples?',
                'What is the purpose of LDS temples?'
            ],
            negativeTests: [
                'Why did Solomon build the temple?',
                'How were ancient Greek temples used?'
            ],
            answer: 'Latter-day Saints build temples because they believe God commands His people to create sacred houses of worship where they can learn of Jesus Christ, make covenants with God, and receive ordinances not performed in ordinary Sunday meetinghouses. Temple worship includes the endowment, which teaches God\'s plan and includes covenants of discipleship, and sealings, which unite husbands and wives and connect children to parents with promises that can continue beyond death.\n\nTemples are also used for proxy ordinances on behalf of people who have died. Latter-day Saints believe those ordinances are offered without removing the deceased person\'s agency. In this belief, every temple practice is meant to point worshippers toward the Atonement of Jesus Christ and prepare them to return to God.',
            sources: [
                {
                    text: 'Why Latter-day Saints Build Temples',
                    label: 'Why Latter-day Saints Build Temples',
                    url: 'https://www.churchofjesuschrist.org/temples/why-latter-day-saints-build-temples?lang=eng',
                    tier: 'Official Church teaching',
                    note: 'Official explanation of the purpose of Latter-day Saint temples.'
                },
                {
                    text: 'Temples - Topics and Questions',
                    label: 'Temples - Topics and Questions',
                    url: 'https://www.churchofjesuschrist.org/study/manual/gospel-topics/temples?lang=eng',
                    tier: 'Official Church teaching',
                    note: 'Official overview of temple worship, covenants, and ordinances.'
                }
            ]
        },
        {
            id: 'ask-after-death',
            profiles: ['ask'],
            priority: 175,
            reviewedOn: '2026-09-01',
            integrityKey: 'ask-after-death-v1',
            match: {
                exact: [
                    'What do Latter-day Saints believe happens after death?',
                    'What happens after death?',
                    'What does the Church teach about life after death?'
                ],
                all: [
                    ['after death', 'life after death', 'spirit world'],
                    ['what', 'happen', 'happens', 'believe', 'teach']
                ],
                none: ['movie', 'novel', 'video game', 'song']
            },
            positiveTests: [
                'What do Latter-day Saints believe happens after death?',
                'What happens after death?',
                'What does the Church teach about life after death?'
            ],
            negativeTests: [
                'What happens after the death scene in that movie?',
                'Is After Death the name of a novel?'
            ],
            answer: 'Latter-day Saints believe physical death temporarily separates the spirit from the body; it does not end personal existence. The spirit continues in a postmortal spirit world while awaiting resurrection. Church teaching describes that world as a place of peace for the righteous and also a place where the gospel can be taught to those who did not receive a full opportunity in mortality.\n\nBecause Jesus Christ rose from the dead, every person will be resurrected, with body and spirit reunited immortally. After resurrection comes judgment by a perfectly just and merciful God. Latter-day Saints therefore see death as a real and painful separation, but not a permanent one: resurrection is universal through Christ, and eternal life with God is made possible through His grace and the faithful response of each person.',
            sources: [
                {
                    text: 'Plan of Salvation - Gospel Study Guide',
                    label: 'Plan of Salvation - Gospel Study Guide',
                    url: 'https://www.churchofjesuschrist.org/study/manual/gospel-topics/plan-of-salvation-study-guide?lang=eng',
                    tier: 'Official Church teaching',
                    note: 'Official overview of premortality, mortality, the spirit world, resurrection, and judgment.'
                },
                {
                    text: 'Spirit World - Gospel Study Guide',
                    label: 'Spirit World - Gospel Study Guide',
                    url: 'https://www.churchofjesuschrist.org/study/manual/gospel-topics/spirit-world-study-guide?lang=eng',
                    tier: 'Official Church teaching',
                    note: 'Official explanation of the postmortal spirit world.'
                }
            ]
        },
        {
            id: 'ask-bible-book-of-mormon-together',
            profiles: ['ask'],
            priority: 175,
            reviewedOn: '2026-09-01',
            integrityKey: 'ask-bible-book-of-mormon-together-v1',
            match: {
                exact: [
                    'How do the Bible and the Book of Mormon work together?',
                    'How do Latter-day Saints use the Bible and Book of Mormon together?',
                    'Does the Book of Mormon replace the Bible?'
                ],
                all: [
                    ['bible'],
                    ['book of mormon'],
                    ['together', 'relate', 'relationship', 'replace', 'compare', 'both']
                ],
                none: ['movie adaptation', 'bookstore', 'auction']
            },
            positiveTests: [
                'How do the Bible and the Book of Mormon work together?',
                'How do Latter-day Saints use the Bible and Book of Mormon together?',
                'Does the Book of Mormon replace the Bible?'
            ],
            negativeTests: [
                'Where can I buy a Bible at a bookstore?',
                'Is there a movie adaptation of the Book of Mormon musical?'
            ],
            answer: 'Latter-day Saints accept both the Bible and the Book of Mormon as scripture and read them as distinct witnesses of Jesus Christ. The Bible preserves God\'s covenant dealings with Israel, the mortal ministry, Crucifixion, and Resurrection of Jesus, and the teachings of His early Apostles. The Book of Mormon describes another people and setting, teaches of Christ before His birth, and includes an account of the resurrected Savior ministering in the ancient Americas.\n\nThe Book of Mormon does not replace the Bible. The two records reinforce teachings such as faith in Christ, repentance, baptism, the Holy Ghost, resurrection, judgment, charity, prayer, and covenant discipleship. Their different voices and histories matter: Latter-day Saints see agreement between separate scriptural witnesses as a way to deepen and corroborate testimony of the same Savior.',
            sources: [
                {
                    text: 'How the Bible and the Book of Mormon Work Together',
                    label: 'How the Bible and the Book of Mormon Work Together',
                    url: 'https://www.churchofjesuschrist.org/comeuntochrist/believe/book-of-mormon/how-the-bible-and-the-book-of-mormon-work-together',
                    tier: 'Official Church explanation',
                    note: 'Official explanation of the relationship between the two scriptural records.'
                },
                {
                    text: 'The Book of Mormon: Another Testament of Jesus Christ',
                    label: 'The Book of Mormon: Another Testament of Jesus Christ',
                    url: 'https://www.churchofjesuschrist.org/comeuntochrist/believe/book-of-mormon/another-testament-of-jesus-christ',
                    tier: 'Official Church explanation',
                    note: 'Official introduction to the Book of Mormon as another witness of Jesus Christ.'
                }
            ]
        },
        {
            id: 'ask-faith-during-trials',
            profiles: ['ask'],
            priority: 175,
            reviewedOn: '2026-09-01',
            integrityKey: 'ask-faith-during-trials-v1',
            match: {
                exact: [
                    'How can faith in Jesus Christ help during difficult times?',
                    'How can faith help during difficult times?',
                    'How can Jesus Christ help me through trials?'
                ],
                all: [
                    ['faith', 'jesus', 'jesus christ', 'christ'],
                    ['trial', 'trials', 'difficult', 'hard time', 'hard times', 'adversity', 'suffering', 'grief']
                ],
                none: ['court trial', 'clinical trial', 'free trial', 'software trial']
            },
            positiveTests: [
                'How can faith in Jesus Christ help during difficult times?',
                'How can faith help during hard times?',
                'How can Christ help me through trials?'
            ],
            negativeTests: [
                'How can I register for a clinical trial?',
                'When does the free software trial end?'
            ],
            answer: 'Faith in Jesus Christ does not guarantee that every trial will disappear. It means trusting His power, wisdom, and love enough to keep turning toward Him while also taking responsible action. A faithful person may still grieve, fear, question, seek counseling, ask for practical help, or feel exhausted. Latter-day Saint scripture teaches that Christ understands mortal pain personally and can give strength, comfort, wisdom, forgiveness, and power to change.\n\nFaith can also restore direction. Instead of asking only why suffering happened, a disciple can ask what faithful step is possible now, what support is needed, what should change, and whom they can help. Christian hope ultimately rests in Christ\'s Resurrection: suffering and death are real, but they are not the final word, and God can heal and make right what mortality leaves unfinished.',
            sources: [
                {
                    text: 'Faith in Jesus Christ - Gospel Study Guide',
                    label: 'Faith in Jesus Christ - Gospel Study Guide',
                    url: 'https://www.churchofjesuschrist.org/study/manual/gospel-topics/faith-in-jesus-christ-study-guide?lang=eng',
                    tier: 'Official Church teaching',
                    note: 'Official study guide on trusting and following Jesus Christ.'
                },
                {
                    text: 'Adversity - Topics and Questions',
                    label: 'Adversity - Topics and Questions',
                    url: 'https://www.churchofjesuschrist.org/study/manual/gospel-topics/adversity?lang=eng',
                    tier: 'Official Church teaching',
                    note: 'Official Church teaching on adversity and faithful response.'
                }
            ]
        },
        {
            id: 'joseph-smith-death-1844',
            profiles: ['ask', 'pioneers', 'church-history'],
            priority: 120,
            reviewedOn: '2026-09-01',
            integrityKey: 'joseph-smith-death-1844-v2',
            contextLabel: 'Joseph Smith\'s death',
            followup: {
                anchor: 'Joseph Smith death died',
                cues: ['time', 'date', 'year', 'when', 'die', 'died', 'death', 'killed', 'martyred', 'martyrdom'],
                ellipsis: ['What time?', 'And what time?', 'At what time?', 'When exactly?', 'What date?', 'What year?'],
                block: ['joseph']
            },
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
            answer: 'Joseph Smith and his brother Hyrum were killed by a mob at Carthage Jail in Illinois on June 27, 1844. Official sources place the attack and their deaths at about or shortly after 5:00 p.m. They do not establish a more exact minute, so “about 5:00 p.m.” is the most responsible answer to the time question.',
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
                },
                {
                    text: 'Doctrine and Covenants 135',
                    label: 'Doctrine and Covenants 135',
                    url: 'https://www.churchofjesuschrist.org/study/scriptures/dc-testament/dc/135?lang=eng',
                    tier: 'Official scripture',
                    note: 'Records that Joseph and Hyrum were shot at about five o’clock p.m.'
                },
                {
                    text: 'Carthage Jail',
                    label: 'Carthage Jail',
                    url: 'https://www.churchofjesuschrist.org/learn/history/sites/historic-nauvoo/carthage-jail?lang=eng',
                    tier: 'Official historic-site account',
                    note: 'Places the attack soon after 5:00 p.m. on June 27, 1844.'
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
                exact: ['Handcart Companies', 'Latter-day Saint Handcart Companies', 'Pioneer Handcart Companies'],
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
            answer: 'Latter-day Saint handcart travel began in 1856 and continued through 1860. The handcart plan gave emigrants who could not afford wagons a lower-cost way to gather to Utah: they walked while pulling two-wheeled carts carrying their belongings and provisions. Only 10 of the more than 350 Latter-day Saint emigrating companies traveled by handcart. Most arrived safely, but the late-departing Willie and Martin companies were caught in severe 1856 winter storms, and their suffering led to an urgent rescue effort. Their history is remembered for faith and endurance as well as the consequences of inadequate preparation and late travel.',
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
        const exact = (entry.match.exact || []).some(function (candidate) {
            return normalize(candidate) === normalizedQuery;
        });
        if (exact) return true;
        return (entry.match.all || []).every(function (group) {
            return group.some(function (term) { return hasTerm(normalizedQuery, tokenSet, term); });
        });
    }

    function historyQuestion(item) {
        if (!item) return '';
        if (item.role === 'user' && item.content) return String(item.content);
        if (item.question) return String(item.question);
        return '';
    }

    function historyContextEntryId(item) {
        return item && item.contextEntryId ? String(item.contextEntryId) : '';
    }

    function resolveFollowup(question, options) {
        const profile = String(options && options.profile || 'ask');
        const original = String(question || '').trim();
        const direct = ENTRIES
            .filter(function (entry) { return entryMatches(entry, original, profile); })
            .sort(function (left, right) { return right.priority - left.priority; })[0];
        if (direct) return { query: original, resolved: false, entryId: direct.id, contextLabel: direct.contextLabel || '' };

        const normalizedQuery = normalize(original);
        const tokens = normalizedQuery.split(' ').filter(Boolean);
        const referential = /\b(?:he|him|his|she|her|hers|they|them|their|it|its|that|this|there|then)\b/.test(normalizedQuery);
        const elliptical = tokens.length <= 8 && /^(?:and|what|when|where|how|do|did|was|is|about)\b/.test(normalizedQuery);
        if (!normalizedQuery || (!referential && !elliptical)) {
            return { query: original, resolved: false, entryId: null, contextLabel: '' };
        }

        const history = Array.isArray(options && options.history) ? options.history : [];
        let priorQuestion = '';
        let priorContextEntryId = '';
        for (let index = history.length - 1; index >= 0; index -= 1) {
            priorQuestion = historyQuestion(history[index]);
            if (priorQuestion) {
                priorContextEntryId = historyContextEntryId(history[index]);
                break;
            }
        }
        if (!priorQuestion) return { query: original, resolved: false, entryId: null, contextLabel: '' };

        const priorEntry = priorContextEntryId
            ? ENTRIES.find(function (entry) {
                return entry.id === priorContextEntryId && entry.followup && entry.profiles.includes(profile);
            })
            : ENTRIES
                .filter(function (entry) { return entry.followup && entryMatches(entry, priorQuestion, profile); })
                .sort(function (left, right) { return right.priority - left.priority; })[0];
        if (!priorEntry) return { query: original, resolved: false, entryId: null, contextLabel: '' };

        const permittedEllipsis = elliptical && (priorEntry.followup.ellipsis || []).some(function (candidate) {
            return normalize(candidate) === normalizedQuery;
        });
        if (!referential && !permittedEllipsis) return { query: original, resolved: false, entryId: null, contextLabel: '' };

        const tokenSet = new Set(tokens);
        const hasCue = (priorEntry.followup.cues || []).some(function (term) {
            return hasTerm(normalizedQuery, tokenSet, term);
        });
        const isBlocked = (priorEntry.followup.block || []).some(function (term) {
            return hasTerm(normalizedQuery, tokenSet, term);
        });
        if (!hasCue || isBlocked) return { query: original, resolved: false, entryId: null, contextLabel: '' };

        const resolvedQuery = (original + ' ' + priorEntry.followup.anchor).trim();
        if (!entryMatches(priorEntry, resolvedQuery, profile)) {
            return { query: original, resolved: false, entryId: null, contextLabel: '' };
        }
        return {
            query: resolvedQuery,
            resolved: true,
            entryId: priorEntry.id,
            contextLabel: priorEntry.contextLabel || priorEntry.id
        };
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
        match: match,
        resolveFollowup: resolveFollowup
    });
})();
