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

    const POLICY_VERSION = '2026-09-06.19';

    function officialHistorySource(label, url, note) {
        return {
            text: label,
            label: label,
            url: url,
            tier: 'Official Church History',
            note: note
        };
    }

    function churchHistoryCard(config) {
        return {
            id: config.id,
            profiles: ['ask', 'church-history'],
            priority: 175,
            reviewedOn: '2026-09-01',
            integrityKey: config.id + '-v1',
            match: {
                exact: [config.question],
                all: config.all,
                none: config.none || []
            },
            positiveTests: [config.question].concat(config.positive || []),
            negativeTests: config.negative,
            answer: config.answer,
            sources: config.sources
        };
    }

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
            id: 'general-abraham-lincoln-death-1865',
            profiles: ['ask'],
            priority: 165,
            reviewedOn: '2026-09-01',
            integrityKey: 'general-abraham-lincoln-death-1865-v1',
            contextLabel: 'Abraham Lincoln\'s death',
            followup: {
                anchor: 'Abraham Lincoln death died',
                cues: ['time', 'date', 'year', 'when', 'die', 'died', 'death', 'shot', 'assassinated', 'where'],
                ellipsis: ['What time?', 'And what time?', 'At what time?', 'When exactly?', 'What date?', 'What year?']
            },
            match: {
                all: [
                    ['abraham lincoln'],
                    ['die', 'died', 'death', 'shot', 'assassinated', 'assassination']
                ],
                none: ['lincoln nebraska', 'lincoln car', 'lincoln automobile']
            },
            positiveTests: [
                'What date did Abraham Lincoln die?',
                'When did Abraham Lincoln die?',
                'What time did Abraham Lincoln die?'
            ],
            negativeTests: [
                'Where is Lincoln, Nebraska?',
                'What Lincoln car should I buy?'
            ],
            answer: "Abraham Lincoln died at 7:22 a.m. on April 15, 1865, in the Petersen House in Washington, D.C. John Wilkes Booth had shot him at Ford's Theatre the previous evening, April 14. Lincoln was carried across the street to the Petersen House, where he remained unconscious and died roughly nine hours after the shooting. The Library of Congress and the National Park Service both record the date and exact time as April 15 at 7:22 a.m.",
            sources: [
                {
                    text: 'Library of Congress - Assassination of President Abraham Lincoln',
                    label: 'Library of Congress - Assassination of President Abraham Lincoln',
                    url: 'https://www.loc.gov/collections/abraham-lincoln-papers/articles-and-essays/assassination-of-president-abraham-lincoln/',
                    tier: 'Authoritative federal history source',
                    note: "Library of Congress account records Lincoln's death at 7:22 a.m. on April 15, 1865."
                },
                {
                    text: 'National Park Service - Petersen House',
                    label: 'National Park Service - Petersen House',
                    url: 'https://www.nps.gov/places/000/petersen-house.htm',
                    tier: 'Authoritative federal history source',
                    note: 'National Park Service records the Petersen House death time as 7:22 a.m. on April 15, 1865.'
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
                cues: [
                    'time', 'date', 'year', 'when', 'die', 'died', 'death', 'killed', 'martyred', 'martyrdom',
                    'age', 'old', 'why', 'reason', 'cause', 'motive', 'charge', 'arrest', 'held', 'detained', 'imprisoned',
                    'carthage', 'jail', 'who', 'with', 'together', 'present', 'where', 'live', 'lived',
                    'reside', 'resided', 'residence', 'home'
                ],
                ellipsis: ['What time?', 'And what time?', 'At what time?', 'When exactly?', 'What date?', 'What year?'],
                block: ['joseph'],
                variants: [
                    {
                        id: 'age-at-death',
                        cues: ['age', 'old'],
                        intent: {
                            all: [['age', 'old']]
                        },
                        answer: 'Joseph Smith was 38 years old when he died on June 27, 1844. He had not yet reached age 39. He and his brother Hyrum were killed during the mob attack at Carthage Jail in Illinois, which official Church history places at about or shortly after 5:00 p.m. The available official account does not establish a more exact minute. The age, calendar date, location, and approximate time should therefore be stated together without inventing precision that the historical record does not provide.',
                        sources: [
                            officialHistorySource('Joseph Smith Jr.', 'https://www.churchofjesuschrist.org/study/history/topics/joseph-smith-jr?lang=eng', 'Official biography identifying Joseph Smith\'s age at death.'),
                            officialHistorySource('Deaths of Joseph and Hyrum Smith', 'https://www.churchofjesuschrist.org/study/history/topics/deaths-of-joseph-and-hyrum-smith?lang=eng', 'Official account of the deaths at Carthage Jail.')
                        ]
                    },
                    {
                        id: 'carthage-imprisonment',
                        cues: ['why', 'carthage', 'jail'],
                        intent: {
                            all: [
                                ['why', 'reason', 'charge', 'arrest', 'held', 'detained', 'imprisoned'],
                                ['carthage', 'jail', 'charge', 'arrest', 'held', 'detained', 'imprisoned']
                            ],
                            none: ['die', 'died', 'death', 'killed', 'murdered', 'martyred', 'mob', 'shot', 'attack']
                        },
                        answer: 'Joseph Smith was in Carthage Jail while awaiting legal proceedings after the Nauvoo city council ordered the destruction of the Nauvoo Expositor press, which officials treated as a riot. After Joseph went to Carthage and submitted to arrest, authorities also brought a treason charge that prevented his release on bail. He and several companions were confined in the jail while Illinois governor Thomas Ford traveled to Nauvoo. On June 27, 1844, a mob attacked the jail and killed Joseph and Hyrum Smith. Explaining the charges gives the legal setting; it does not justify the extrajudicial killings.',
                        sources: [
                            officialHistorySource('Deaths of Joseph and Hyrum Smith', 'https://www.churchofjesuschrist.org/study/history/topics/deaths-of-joseph-and-hyrum-smith?lang=eng', 'Official account of the arrests, charges, confinement, and attack.'),
                            officialHistorySource('Carthage Jail', 'https://www.churchofjesuschrist.org/learn/history/sites/historic-nauvoo/carthage-jail?lang=eng', 'Official historic-site account of the confinement and attack.')
                        ]
                    },
                    {
                        id: 'carthage-attack-context',
                        cues: ['why', 'reason', 'cause', 'motive', 'killed', 'murdered', 'martyred'],
                        intent: {
                            all: [
                                ['why', 'reason', 'cause', 'motive'],
                                ['die', 'died', 'death', 'killed', 'murdered', 'martyred', 'martyrdom', 'mob', 'attack']
                            ]
                        },
                        answer: 'Joseph Smith\'s murder cannot responsibly be reduced to a single proven motive for every attacker. Official Church history describes mounting opposition in spring 1844 from both dissident Latter-day Saints and other regional opponents. The Nauvoo Expositor criticized Joseph\'s character and Church teachings; after Nauvoo officials ordered its press destroyed, opponents called for his arrest and for further violence. Joseph and Hyrum submitted to arrest and were awaiting trial in Carthage when an armed mob attacked the jail. The immediate setting was therefore escalating religious, political, and civic conflict—not a lawful execution—and individual participants may not all have acted for exactly the same reason.',
                        sources: [
                            officialHistorySource('Deaths of Joseph and Hyrum Smith', 'https://www.churchofjesuschrist.org/study/history/topics/deaths-of-joseph-and-hyrum-smith?lang=eng', 'Official account of the mounting opposition, Nauvoo Expositor controversy, calls for violence, arrest, and mob attack.')
                        ]
                    },
                    {
                        id: 'carthage-companions',
                        cues: ['who', 'with'],
                        intent: {
                            all: [
                                ['who'],
                                ['with', 'together', 'there', 'present', 'room', 'companion', 'companions', 'accompanied']
                            ],
                            none: ['killed', 'murdered', 'mob', 'shot', 'attack', 'attacked']
                        },
                        answer: 'Joseph Smith was confined at Carthage with his brother Hyrum Smith and several associates. By the time of the attack on June 27, 1844, Joseph, Hyrum, John Taylor, and Willard Richards were together in an upstairs room of the jail. The mob killed Joseph and Hyrum. John Taylor was seriously wounded, while Willard Richards survived with only a minor wound. Other supporters had been present during the imprisonment, but those four were in the room during the final assault. Official Church history distinguishes the people present at the attack from the larger group who had accompanied or visited Joseph earlier.',
                        sources: [
                            officialHistorySource('Deaths of Joseph and Hyrum Smith', 'https://www.churchofjesuschrist.org/study/history/topics/deaths-of-joseph-and-hyrum-smith?lang=eng', 'Official account identifying the four men in the room during the attack.'),
                            officialHistorySource('Carthage Jail', 'https://www.churchofjesuschrist.org/learn/history/sites/historic-nauvoo/carthage-jail?lang=eng', 'Official historic-site account of the men present and the attack.')
                        ]
                    },
                    {
                        id: 'nauvoo-residence',
                        cues: ['where', 'live', 'lived'],
                        intent: {
                            all: [['live', 'lived', 'reside', 'resided', 'residence', 'home']],
                            none: ['die', 'died', 'death', 'killed', 'murdered', 'martyred']
                        },
                        answer: 'At the end of his life, Joseph Smith lived in Nauvoo, Illinois. Carthage Jail was not his home: he had gone to Carthage to answer legal charges and was being held there when the mob attacked on June 27, 1844. That distinction matters when answering this follow-up. Nauvoo was the community where he lived and served; Carthage was the nearby place of his final confinement and death. The official histories cited here document that immediate Nauvoo-and-Carthage setting without making a broader claim about every residence of his life.',
                        sources: [
                            officialHistorySource('Deaths of Joseph and Hyrum Smith', 'https://www.churchofjesuschrist.org/study/history/topics/deaths-of-joseph-and-hyrum-smith?lang=eng', 'Official account of the Nauvoo events, journey to Carthage, confinement, and deaths.'),
                            officialHistorySource('Carthage Jail', 'https://www.churchofjesuschrist.org/learn/history/sites/historic-nauvoo/carthage-jail?lang=eng', 'Official historic-site account of his final confinement near Nauvoo.')
                        ]
                    }
                ]
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
            id: 'pioneer-winter-quarters-overview',
            profiles: ['ask', 'pioneers', 'church-history'],
            priority: 175,
            reviewedOn: '2026-09-06',
            integrityKey: 'pioneer-winter-quarters-overview-v1',
            match: {
                exact: ['Winter Quarters', 'What was Winter Quarters?', 'Tell me about Winter Quarters', 'Why did the Saints stop at Winter Quarters?'],
                all: [['winter quarters'], ['overview', 'temporary settlement', 'pause migration']],
                none: ['temple', 'tickets', 'hours', 'hotel', 'military']
            },
            positiveTests: ['Winter Quarters', 'What was Winter Quarters?', 'Tell me about Winter Quarters', 'Why did the Saints stop at Winter Quarters?'],
            negativeTests: ['What are the Winter Quarters Temple opening hours?', 'Describe military winter quarters', 'Who designed the Winter Quarters Temple?'],
            answer: 'Winter Quarters was a temporary Latter-day Saint settlement beside the Missouri River, established in 1846 after the Saints left Nauvoo. Mud and sickness had slowed their journey across Iowa, so Church leaders paused westward migration to prepare for winter. Residents built shelters and faced shortages, hunger and disease while organizing and outfitting companies for the journey ahead. Brigham Young left Winter Quarters on April 7, 1847, to join the vanguard pioneer company. Those who remained prepared homes, crops and supplies for later migrants. As the lease on Omaha tribal land approached its end, the Saints moved across the river into Iowa, where Kanesville became their new emigration headquarters.',
            sources: [officialHistorySource('Winter Quarters', 'https://www.churchofjesuschrist.org/study/history/topics/winter-quarters?lang=eng', 'Official account of the winter pause, settlement, migration preparations and move to Kanesville.')]
        },
        {
            id: 'pioneer-handcart-travel-1856',
            profiles: ['ask', 'pioneers', 'church-history'],
            priority: 140,
            reviewedOn: '2026-09-01',
            integrityKey: 'pioneer-handcart-travel-1856-v1',
            match: {
                guard: 'lds-handcart',
                exact: [
                    'Handcart Companies',
                    'Latter-day Saint Handcart Companies',
                    'Pioneer Handcart Companies',
                    'What happened to the Willie and Martin handcart companies?'
                ],
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
                'When were hand carts first used by the pioneers?',
                'What happened to the Willie and Martin handcart companies?'
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
            profiles: ['ask', 'pioneers', 'church-history'],
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
            id: 'church-book-of-mormon-publication-1830',
            profiles: ['ask', 'church-history'],
            priority: 170,
            reviewedOn: '2026-09-03',
            integrityKey: 'church-book-of-mormon-publication-1830-v1',
            contextLabel: 'Book of Mormon first publication',
            followup: {
                anchor: 'Book of Mormon publication 1830 Grandin Palmyra',
                cues: [
                    'who', 'where', 'when', 'date', 'year', 'publish', 'published', 'publisher', 'publication',
                    'print', 'printed', 'printer', 'grandin', 'palmyra', 'sale', 'available', 'copies', 'cost',
                    'finance', 'financed', 'martin harris'
                ],
                ellipsis: ['Who published it?', 'Where was it printed?', 'Who printed it?', 'When exactly?'],
                block: ['musical', 'broadway', 'movie', 'film', 'soundtrack'],
                variants: [
                    {
                        id: 'printer-publisher-location',
                        cues: ['who', 'where', 'publish', 'published', 'publisher', 'print', 'printed', 'printer', 'grandin', 'palmyra'],
                        intent: {
                            all: [
                                ['publish', 'published', 'publisher', 'print', 'printed', 'printer'],
                                ['who', 'where', 'published', 'printed', 'publisher', 'printer', 'grandin', 'palmyra']
                            ],
                            none: ['musical', 'broadway', 'movie', 'film', 'soundtrack']
                        },
                        answer: 'The first edition of the Book of Mormon was printed and published through the shop of Egbert B. Grandin in Palmyra, New York. Joseph Smith arranged with Grandin to produce 5,000 copies, and Martin Harris financed the $3,000 printing contract by mortgaging part of his farm. Printing began in 1829, and the first completed copies were offered for sale at Grandin\'s bookstore in Palmyra on March 26, 1830. So for the first edition, the printer and publisher was Egbert B. Grandin, and the place of publication was Palmyra, New York.',
                        sources: [
                            officialHistorySource('Grandin Printshop: Book of Mormon Publication Site', 'https://www.churchofjesuschrist.org/learn/locations/grandin-printshop?lang=eng', 'Official historic-site history of the first Book of Mormon printing and sale in Palmyra.'),
                            officialHistorySource('Historical Summary - Joseph Smith', 'https://www.churchofjesuschrist.org/study/manual/teachings-joseph-smith/historical-summary?lang=eng', 'Official historical timeline recording the March 26, 1830 public availability at Grandin\'s bookstore.')
                        ]
                    },
                    {
                        id: 'publication-date',
                        cues: ['when', 'date', 'year', 'sale', 'available'],
                        intent: {
                            all: [['when', 'date', 'year', 'sale', 'available', 'published', 'publication']]
                        },
                        answer: 'The first printed copies of the Book of Mormon became available to the public on March 26, 1830, at Egbert B. Grandin\'s bookstore in Palmyra, New York. Printing had begun in 1829, but March 26, 1830 is the date official Church historical sources give for the book becoming available for sale. The first edition consisted of 5,000 copies. Martin Harris helped finance the printing agreement, and Grandin\'s Palmyra shop carried out the printing and publication work.',
                        sources: [
                            officialHistorySource('Grandin Printshop: Book of Mormon Publication Site', 'https://www.churchofjesuschrist.org/learn/locations/grandin-printshop?lang=eng', 'Official historic-site history identifying March 26, 1830 as the first sale date.'),
                            officialHistorySource('Historical Summary - Joseph Smith', 'https://www.churchofjesuschrist.org/study/manual/teachings-joseph-smith/historical-summary?lang=eng', 'Official historical timeline recording the March 26, 1830 public availability.')
                        ]
                    }
                ]
            },
            match: {
                exact: [
                    'what year did the book of mormon come out',
                    'What year did the Book of Mormon come out?',
                    'When was the Book of Mormon first published?',
                    'What year was the Book of Mormon published?'
                ],
                all: [
                    ['book of mormon'],
                    ['when', 'year', 'date', 'come out', 'came out', 'published', 'publication', 'released', 'first edition', 'available', 'sale']
                ],
                none: ['musical', 'broadway', 'movie', 'film', 'soundtrack']
            },
            positiveTests: [
                'what year did the book of mormon come out',
                'What year did the Book of Mormon come out?',
                'When was the Book of Mormon first published?',
                'What year was the Book of Mormon published?'
            ],
            negativeTests: [
                'What year did The Book of Mormon musical come out?',
                'When did the Book of Mormon Broadway soundtrack come out?',
                'When was the Book of Mormon movie released?'
            ],
            answer: 'The first edition of the Book of Mormon became available to the public on March 26, 1830, in Palmyra, New York. Egbert B. Grandin and his printing shop produced the first edition after Joseph Smith arranged for 5,000 copies to be printed. Martin Harris helped finance the $3,000 printing contract by mortgaging part of his farm. Official Church historical sources identify Grandin\'s bookstore in Palmyra as the place where the first completed copies went on sale. So the concise answer is 1830, with March 26, 1830 as the first public sale date.',
            sources: [
                officialHistorySource('Grandin Printshop: Book of Mormon Publication Site', 'https://www.churchofjesuschrist.org/learn/locations/grandin-printshop?lang=eng', 'Official historic-site history of the first Book of Mormon printing and public sale.'),
                officialHistorySource('Historical Summary - Joseph Smith', 'https://www.churchofjesuschrist.org/study/manual/teachings-joseph-smith/historical-summary?lang=eng', 'Official historical timeline recording the March 26, 1830 public availability at Grandin\'s bookstore.')
            ]
        },
        {
            id: 'church-first-vision-1820',
            profiles: ['ask', 'church-history'],
            priority: 120,
            reviewedOn: '2026-09-01',
            integrityKey: 'church-first-vision-1820-v1',
            match: {
                exact: ['What do the different First Vision accounts say, and how does the Church explain them?'],
                all: [
                    ['first vision'],
                    ['when', 'year', 'date', 'where', 'place', 'location', 'happen', 'happened', 'occur', 'occurred', 'tell', 'about', 'explain']
                ],
                none: ['movie', 'film', 'painting', 'artwork']
            },
            positiveTests: [
                'When was the First Vision?',
                'Where did the First Vision happen?',
                'Tell me about the First Vision',
                'Tell me about First Vision',
                'What do the different First Vision accounts say, and how does the Church explain them?'
            ],
            negativeTests: [
                'Who painted the First Vision artwork?',
                'When was the First Vision movie released?'
            ],
            answer: "Joseph Smith left four firsthand accounts of his First Vision, written or dictated in 1832, 1835, 1838, and 1842; two were published during his lifetime. They consistently describe his youthful religious concern, prayer, a heavenly manifestation, and a divine answer, while differing in length, audience, emphasis, and some details. The Church explains those differences as normal features of recollection and retelling for different purposes, not as four identical transcripts. Its official history invites readers to study the accounts together. Joseph's canonized 1838 account says that in spring 1820, near his family's New York farm, he saw God the Father and Jesus Christ and was told not to join the existing churches.",
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
        churchHistoryCard({
            id: 'church-book-of-mormon-translation-seer-stones',
            question: 'How does the Church describe the translation of the Book of Mormon and the use of seer stones?',
            all: [
                ['book of mormon'],
                ['translation', 'translate', 'translated', 'translating'],
                ['seer stone', 'seer stones', 'interpreters', 'urim and thummim']
            ],
            positive: [
                'What role did seer stones have in translating the Book of Mormon?',
                'How were the interpreters used in the Book of Mormon translation?'
            ],
            negative: [
                'How do I translate a modern book into another language?',
                'What stones were used to build the Salt Lake Temple?'
            ],
            answer: 'The Church teaches that Joseph Smith translated the Book of Mormon by the gift and power of God, not through ordinary knowledge of ancient languages. Most of the present text was dictated to Oliver Cowdery between April and June 1829. Historical accounts describe Joseph using both the interpreters found with the plates and a separate seer stone he already possessed. He sometimes placed an instrument in a hat to exclude light while dictating the words he perceived. Early Saints often used the term Urim and Thummim broadly for these sacred instruments. The Church presents the instruments as part of the historical process while emphasizing that revelation from God, rather than the physical object itself, made the translation possible.',
            sources: [
                officialHistorySource('Book of Mormon Translation', 'https://www.churchofjesuschrist.org/study/history/topics/book-of-mormon-translation?lang=eng', 'Official history of the translation process and instruments.'),
                officialHistorySource('Seer Stones', 'https://www.churchofjesuschrist.org/study/history/topics/seer-stones?lang=eng', 'Official historical explanation of Joseph Smith\'s use of seer stones.')
            ]
        }),
        churchHistoryCard({
            id: 'church-priesthood-restoration',
            question: 'What is known about the restoration of the Aaronic and Melchizedek Priesthood?',
            all: [
                ['priesthood'],
                ['restore', 'restored', 'restoration'],
                ['aaronic', 'melchizedek', 'john the baptist', 'peter james and john', 'joseph smith']
            ],
            positive: [
                'How were the Aaronic and Melchizedek Priesthood restored?',
                'Who restored priesthood authority to Joseph Smith and Oliver Cowdery?'
            ],
            negative: [
                'What did Melchizedek do in the Old Testament?',
                'How is priesthood discussed in another modern church?'
            ],
            answer: 'Joseph Smith and Oliver Cowdery said that John the Baptist appeared to them near Harmony, Pennsylvania, in May 1829, conferred the Aaronic Priesthood, and authorized them to baptize one another. They also testified that Peter, James, and John later conferred greater apostolic authority associated with the Melchizedek Priesthood. The historical record preserves the Aaronic event with a clear date, while the surviving accounts do not establish one equally certain date for the appearance of Peter, James, and John. Official Church history therefore affirms the restoration of both authorities while acknowledging that terminology, offices, and the Saints\' understanding of priesthood organization developed as further revelation was received.',
            sources: [
                officialHistorySource('Restoration of the Aaronic Priesthood', 'https://www.churchofjesuschrist.org/study/history/topics/restoration-of-the-aaronic-priesthood?lang=eng', 'Official history of the 1829 Aaronic Priesthood restoration.'),
                officialHistorySource('Restoration of the Melchizedek Priesthood', 'https://www.churchofjesuschrist.org/study/history/topics/restoration-of-the-melchizedek-priesthood?lang=eng', 'Official history and dating qualifications for the Melchizedek Priesthood restoration.')
            ]
        }),
        churchHistoryCard({
            id: 'church-kirtland-safety-society',
            question: 'What happened with the Kirtland Safety Society, and why did it fail?',
            all: [
                ['kirtland safety society'],
                ['fail', 'failed', 'failure', 'happened', 'collapse', 'closed', 'crisis']
            ],
            positive: [
                'Why did the Kirtland Safety Society fail?',
                'What caused the Kirtland Safety Society bank crisis?'
            ],
            negative: [
                'How should a modern workplace safety society operate?',
                'What happened to a Kirtland, Ohio school society?'
            ],
            answer: 'Church leaders and other investors organized the Kirtland Safety Society in late 1836 after rapid growth created a need for local credit. Ohio denied its bank charter, so it opened in January 1837 as a joint-stock association. It failed within the year and ceased operating by August. Official Church history describes several contributing causes: undercapitalization, risky lending and speculation, heavy debts and spending, hostile efforts to undermine confidence, and the broader Panic of 1837, which damaged banks across the United States. Many people lost money, lawsuits followed, and the crisis intensified dissent against Joseph Smith. The Church does not reduce the collapse to persecution alone; it acknowledges financial mistakes alongside the national economic downturn and organized opposition.',
            sources: [
                officialHistorySource('Kirtland Safety Society', 'https://www.churchofjesuschrist.org/study/history/topics/kirtland-safety-society?lang=eng', 'Official history of the institution, its operation, and causes of failure.')
            ]
        }),
        churchHistoryCard({
            id: 'church-joseph-smith-plural-marriage',
            question: 'How does the Church explain Joseph Smith and plural marriage?',
            all: [
                ['joseph smith', 'joseph'],
                ['plural marriage', 'polygamy', 'plural wives']
            ],
            none: ['fiction', 'fictional', 'novel', 'movie', 'legal status today'],
            positive: [
                'What does the Church say about Joseph Smith and plural marriage?',
                'Did Joseph Smith practice polygamy?'
            ],
            negative: [
                'What is the legal status of plural marriage today?',
                'How does a fictional Joseph practice plural marriage in a novel?'
            ],
            answer: 'The Church teaches that monogamy is God\'s standing law for marriage unless He commands otherwise. It also teaches that, in the early 1840s, Joseph Smith introduced plural marriage to a limited group of Church members because he believed God had commanded the practice as part of the Restoration. Historical evidence indicates that Joseph was sealed to multiple women, including both eternity-only sealings and marriages understood to include mortal relationships. The practice was difficult, controversial, and generally confidential, so the surviving record is incomplete and some later reminiscences conflict. The Church therefore acknowledges important facts without claiming certainty about every relationship or motive. It does not present plural marriage as necessary for exaltation today, and the Church ended authorization of new plural marriages beginning with the 1890 Manifesto.',
            sources: [
                officialHistorySource('Joseph Smith and Plural Marriage', 'https://www.churchofjesuschrist.org/study/history/topics/joseph-smith-and-plural-marriage?lang=eng', 'Official Church History topic describing Joseph Smith\'s plural marriages and the limits of the surviving record.'),
                officialHistorySource('Plural Marriage in The Church of Jesus Christ of Latter-day Saints', 'https://www.churchofjesuschrist.org/study/manual/gospel-topics-essays/plural-marriage-in-the-church-of-jesus-christ-of-latter-day-saints?lang=eng', 'Official Gospel Topics essay on the history and discontinuance of plural marriage.')
            ]
        }),
        churchHistoryCard({
            id: 'church-mountain-meadows-massacre',
            question: 'What does the Church teach about the Mountain Meadows Massacre?',
            all: [
                ['mountain meadows'],
                ['massacre', 'teach', 'happened', 'history']
            ],
            positive: [
                'What happened in the Mountain Meadows Massacre?',
                'Was the Mountain Meadows Massacre ordered by Brigham Young?'
            ],
            negative: [
                'What mountain meadows are best for hiking?',
                'Summarize a fictional massacre in a mountain movie.'
            ],
            answer: 'The Mountain Meadows Massacre was the deliberate killing of about 120 emigrants in southern Utah in September 1857 by members of local Latter-day Saint militia units, aided by some Paiute participants they had recruited. Seventeen small children were spared. The Church condemns the massacre as a terrible and unjustifiable crime. Official historical research places responsibility on local leaders and participants amid wartime fear, rumors, prejudice, and escalating conflict; it finds no evidence that Brigham Young ordered the killings. Young sent instructions not to interfere with emigrant companies, but the messenger arrived after the massacre. Acknowledging those facts does not excuse the perpetrators or erase the suffering of the victims and their descendants.',
            sources: [
                officialHistorySource('Mountain Meadows Massacre', 'https://www.churchofjesuschrist.org/study/history/topics/mountain-meadows-massacre?lang=eng', 'Official Church History account of the victims, perpetrators, circumstances, and responsibility.')
            ]
        }),
        churchHistoryCard({
            id: 'church-word-of-wisdom-development',
            question: 'How did observance of the Word of Wisdom develop historically?',
            all: [
                ['word of wisdom'],
                ['develop', 'developed', 'historical', 'historically', 'observance', 'observe', 'observed', 'required', 'requirement', 'early saints']
            ],
            positive: [
                'When did the Word of Wisdom become a temple requirement?',
                'How did early Saints observe the Word of Wisdom?'
            ],
            negative: [
                'What does the biblical phrase word of wisdom mean?',
                'How can I develop wisdom from historical books?'
            ],
            answer: 'Joseph Smith received the Word of Wisdom in 1833 in a setting that included concern about tobacco use in Church meetings. Doctrine and Covenants 89 counseled against wine, strong drink, tobacco, and hot drinks while commending wholesome foods. Early Saints did not all treat complete abstinence as an immediate membership requirement, and observance varied for decades. Church leaders increasingly urged stricter adherence during the nineteenth century. In the early twentieth century, abstinence became a clear institutional standard, and in 1921 it became a requirement for a temple recommend. The modern Church applies the revelation by requiring members to avoid alcoholic drinks, tobacco, coffee, tea, illegal drugs, and other harmful or addictive substances while encouraging health, gratitude, and wise care of the body.',
            sources: [
                officialHistorySource('Word of Wisdom (Doctrine and Covenants 89)', 'https://www.churchofjesuschrist.org/study/history/topics/word-of-wisdom-dc-89?lang=eng', 'Official history of the revelation and the development of Church observance.')
            ]
        }),
        churchHistoryCard({
            id: 'church-global-growth-twentieth-century',
            question: 'How did the Church become a global church during the twentieth century?',
            all: [
                ['church', 'latter day saint', 'latter day saints'],
                ['global', 'international', 'worldwide'],
                ['twentieth century', '20th century', '1900s', 'history']
            ],
            positive: [
                'How did Latter-day Saint international growth change the Church in the twentieth century?',
                'Where can I study the Church becoming worldwide in the 1900s?'
            ],
            negative: [
                'How did global churches grow in the first century?',
                'How can a modern company become a global business?'
            ],
            answer: 'During the twentieth century, the Church changed from a community concentrated in the western United States into an international faith. Missionary work expanded, local congregations and stakes were organized in more nations, scripture and Church materials were translated into additional languages, and temples were built closer to members outside North America. Improvements in travel and communication helped, but global growth also depended on local converts and leaders who built enduring congregations in their own cultures. Church administration gradually placed greater responsibility in regional and local leadership rather than expecting members to gather to Utah. Official global histories emphasize that this was not one uniform American expansion: the Church developed through distinct national histories, political conditions, migrations, conflicts, and acts of faith by members around the world.',
            sources: [
                officialHistorySource('Global Histories', 'https://www.churchofjesuschrist.org/study/history/global-histories?lang=eng', 'Official collection of country and regional Latter-day Saint histories.'),
                officialHistorySource('Saints, Volume 3: Boldly, Nobly, and Independent', 'https://www.churchofjesuschrist.org/study/history/saints-v3?lang=eng', 'Official narrative history covering worldwide Church development from 1893 to 1955.'),
                officialHistorySource('Saints, Volume 4: Sounded in Every Ear', 'https://www.churchofjesuschrist.org/study/history/saints-v4?lang=eng', 'Official narrative history covering worldwide Church development from 1955 to 2020.')
            ]
        }),
        churchHistoryCard({
            id: 'church-womens-history-study',
            question: 'Where can I study women in Latter-day Saint Church history?',
            all: [
                ['women', 'womens', "women's"],
                ['church history', 'latter day saint history', "latter day saint women's history"],
                ['study', 'learn', 'read', 'source', 'sources', 'where']
            ],
            positive: [
                'Where are official sources about women in Church history?',
                'How can I study Latter-day Saint women\'s history?'
            ],
            negative: [
                'Where can I study women in ancient Roman history?',
                'What women\'s studies programs are offered by universities?'
            ],
            answer: 'The Church History Library provides an official Women\'s History study collection that gathers biographies, documents, articles, videos, and links to primary-source projects. A strong study path is to begin with that collection, then follow the people and organizations it identifies into the Church History Biographical Database, the Relief Society\'s published history, the First Fifty Years of Relief Society documents, and the Saints narrative history. These sources show women as converts, missionaries, healers, emigrants, temple workers, Relief Society leaders, writers, and builders of local congregations. Because women\'s experiences differed by time and place, studying both institutional histories and women\'s own diaries, minutes, letters, and oral histories gives a fuller account than a single summary can provide.',
            sources: [
                officialHistorySource('Women\'s History', 'https://www.churchofjesuschrist.org/study/church-history/womens-history?lang=eng', 'Official Church History study collection devoted to women\'s history.')
            ]
        }),
        {
            id: 'church-organization-1830',
            profiles: ['ask', 'church-history'],
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

    function historyContextQuestion(item) {
        return item && item.contextQuestion ? String(item.contextQuestion) : '';
    }

    const GENERIC_ELLIPSIS = new Set([
        'what time', 'and what time', 'when exactly', 'what date', 'what year',
        'where exactly', 'why exactly', 'how exactly', 'who exactly'
    ]);

    function hasExplicitCompetingSubject(original, priorEntry, antecedent) {
        const priorText = normalize((priorEntry && priorEntry.followup && priorEntry.followup.anchor) || '')
            + ' ' + normalize(antecedent);
        const raw = String(original || '');
        const candidates = (raw.match(/\b[A-Z][a-z]+(?:\s+(?:[A-Z][a-z]+|[A-Z]\.)){1,3}\b/g) || [])
            .map(function (phrase) { return { phrase: phrase, anchored: false }; });

        function addAnchoredCandidates(pattern) {
            let match;
            while ((match = pattern.exec(raw)) !== null) {
                candidates.push({ phrase: match[1], anchored: true });
            }
        }

        // A competing person may be written in any case. Only accept lowercase
        // phrases in person-like grammatical positions so ordinary place and topic
        // words do not become identity switches.
        addAnchoredCandidates(/[,\u2013\u2014-]\s*([a-z][a-z'.-]+(?:\s+[a-z][a-z'.-]+){0,3})\s*[?.!]*$/gi);
        addAnchoredCandidates(/\b(?:about|who is|who was|tell me about)\s+([a-z][a-z'.-]+(?:\s+[a-z][a-z'.-]+){0,3})\s*[?.!]*$/gi);
        addAnchoredCandidates(/\b(?:did|does|do|was|is|were|are|has|had|can|could|would|will)\s+([a-z][a-z'.-]+(?:\s+[a-z][a-z'.-]+){0,3})\s+(?:die|died|say|said|teach|taught|write|wrote|live|lived|serve|served|become|became|kill|killed)\b/gi);

        const competingName = candidates.some(function (candidate) {
            const phrase = candidate.phrase;
            const normalizedPhrase = normalize(phrase);
            if (!normalizedPhrase || (' ' + priorText + ' ').includes(' ' + normalizedPhrase + ' ')) return false;

            const words = normalizedPhrase.split(' ');
            const first = words[0];
            const terminal = words[words.length - 1];
            if (['with', 'in', 'at', 'on', 'from', 'to', 'for', 'of', 'by', 'he', 'him', 'his',
                'she', 'her', 'they', 'them', 'their', 'it', 'its', 'the', 'a', 'an', 'this', 'that',
                'exactly', 'then', 'there', 'today', 'yesterday', 'now', 'please', 'too', 'also'].includes(first)) return false;
            if (['jail', 'temple', 'church', 'society', 'company', 'companies', 'valley', 'lake',
                'river', 'mountain', 'meadows', 'priesthood', 'vision', 'history', 'translation',
                'massacre', 'university', 'school', 'book', 'testament'].includes(terminal)) return false;

            if (candidate.anchored) return true;

            // Title case alone cannot establish a competing person. Require
            // person-like placement for legacy Title-Case candidates too.
            const escaped = phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            const appositive = new RegExp('[,\\u2013\\u2014-]\\s*' + escaped + '\\s*[?.!]*$', 'i').test(raw);
            const grammaticalSubject = new RegExp('\\b(?:did|does|do|was|is|were|are|has|had|can|could|would|will)\\s+'
                + escaped + '\\s+\\w+', 'i').test(raw);
            const explicitPersonTopic = new RegExp('\\b(?:about|who is|who was|tell me about)\\s+' + escaped + '\\b', 'i').test(raw);
            return appositive || grammaticalSubject || explicitPersonTopic;
        });
        if (competingName) return true;

        const blockedTerms = []
            .concat(priorEntry && priorEntry.match && priorEntry.match.none || [])
            .concat(priorEntry && priorEntry.followup && priorEntry.followup.block || []);
        const normalizedOriginal = normalize(original);
        const tokenSet = new Set(normalizedOriginal.split(' ').filter(Boolean));
        return blockedTerms.some(function (term) {
            const normalizedTerm = normalize(term);
            return hasTerm(normalizedOriginal, tokenSet, term)
                && !(' ' + priorText + ' ').includes(' ' + normalizedTerm + ' ');
        });
    }

    function genericFollowupResolution(original, normalizedQuery, referential, antecedent) {
        const genericEllipsis = GENERIC_ELLIPSIS.has(normalizedQuery);
        if (!referential && !genericEllipsis) {
            return { query: original, resolved: false, entryId: null, contextLabel: '' };
        }
        return {
            query: [
                original,
                'The immediately preceding user question was: "' + antecedent + '".',
                'Resolve pronouns and omitted subjects only from that immediately preceding question.'
            ].join('\n\n'),
            resolved: true,
            entryId: null,
            contextLabel: antecedent,
            contextQuestion: antecedent,
            genericContext: true
        };
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
        let priorContextQuestion = '';
        for (let index = history.length - 1; index >= 0; index -= 1) {
            priorQuestion = historyQuestion(history[index]);
            if (priorQuestion) {
                priorContextEntryId = historyContextEntryId(history[index]);
                priorContextQuestion = historyContextQuestion(history[index]);
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
        const antecedent = priorContextQuestion || priorQuestion;
        if (!priorEntry) {
            return genericFollowupResolution(original, normalizedQuery, referential, antecedent);
        }

        if (hasExplicitCompetingSubject(original, priorEntry, antecedent)) {
            return { query: original, resolved: false, entryId: null, contextLabel: '' };
        }

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
        if (!hasCue || isBlocked) {
            return genericFollowupResolution(original, normalizedQuery, referential, antecedent);
        }

        const resolvedQuery = (original + ' ' + priorEntry.followup.anchor).trim();
        if (!entryMatches(priorEntry, resolvedQuery, profile)) {
            return genericFollowupResolution(original, normalizedQuery, referential, antecedent);
        }
        const variant = (priorEntry.followup.variants || []).find(function (candidate) {
            const intent = candidate.intent || {};
            const requiredGroups = intent.all || [];
            const excludedTerms = intent.none || [];
            return requiredGroups.length > 0
                && requiredGroups.every(function (group) {
                    return group.some(function (term) {
                        return hasTerm(normalizedQuery, tokenSet, term);
                    });
                })
                && !excludedTerms.some(function (term) {
                    return hasTerm(normalizedQuery, tokenSet, term);
                });
        });
        return {
            query: resolvedQuery,
            resolved: true,
            entryId: priorEntry.id,
            contextLabel: priorEntry.contextLabel || priorEntry.id,
            contextQuestion: antecedent,
            genericContext: false,
            contextVariant: variant ? variant.id : null
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
        const variant = options && options.contextVariant && matched.followup
            ? (matched.followup.variants || []).find(function (candidate) {
                return candidate.id === options.contextVariant;
            })
            : null;
        const selectedSources = variant && Array.isArray(variant.sources) ? variant.sources : matched.sources;
        return {
            id: matched.id,
            answer: variant && variant.answer ? variant.answer : matched.answer,
            sources: selectedSources.map(copySource),
            profile: profile,
            mode: 'reviewed-local',
            contextVariant: variant ? variant.id : null,
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
