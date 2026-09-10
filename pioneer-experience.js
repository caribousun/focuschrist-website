/* focusChrist Pioneer conversation experience.
 * Page-specific historical context hardening for Journey, Trail, Pioneer Topics,
 * Tell My Story, and free-form pioneer questions.
 */
(function () {
    'use strict';

    const PROXY_URL = 'https://focuschrist-groq-proxy.caribousun.workers.dev';
    const PIONEER_POLICY_VERSION = '2026-09-03.16';
    let pioneerRequestSerial = 0;

    const PIONEER_TOPIC_ANSWERS = Object.freeze({
        'Exodus from Nauvoo': {
            answer: 'The Latter-day Saint exodus from Nauvoo began in February 1846 after years of conflict and mounting hostility made it unsafe for Church members to remain. Although leaders had planned a spring departure, threats of violence pushed the first companies onto the road during winter. Families crossed the Mississippi River, gathered at temporary camps, and began a slow, muddy passage across Iowa.\n\nThe journey exposed how difficult it was to move an entire religious community. Travelers needed animals, wagons, food, shelter, skilled labor, and cooperation. Camps such as Garden Grove and Mount Pisgah were established to plant crops and help those who followed. By the Missouri River, the Saints created Winter Quarters and neighboring settlements where they could survive, organize, and prepare for the next stage.\n\nThe Nauvoo exodus was therefore not one departure on one day. Thousands left between February and September 1846, and later emigrants continued west in organized companies. For believers, the migration became a story of covenant, gathering, loss, and hope. Historically, it also reveals the physical cost of displacement and the extensive planning required before the 1847 journey to the Salt Lake Valley.',
            sources: [['Departure from Nauvoo', 'https://www.churchofjesuschrist.org/study/history/topics/departure-from-nauvoo?lang=eng']]
        },
        'Winter Quarters': {
            answer: 'Winter Quarters was a temporary Latter-day Saint settlement on the west side of the Missouri River in present-day Omaha, Nebraska. It was established in 1846 after mud, sickness, and shortages slowed the Saints’ crossing of Iowa. With winter approaching, families built log cabins, sod structures, and dugouts while nearby settlements developed on both sides of the river.\n\nLife there was demanding. Inadequate shelter, poor nutrition, malaria, scurvy, and other illnesses contributed to hundreds of deaths. Residents cared for the sick, planted crops, operated workshops, organized livestock and supplies, and helped arriving emigrants. The community was temporary, but it functioned as the Church’s principal staging area while leaders prepared a route and an advance company for the West.\n\nBrigham Young left Winter Quarters in April 1847 to join the vanguard pioneer company. Those who remained continued outfitting later companies. As the Saints’ permitted stay on Omaha lands neared its end, most moved across the river into Iowa, and Kanesville became the principal emigration center. Winter Quarters is remembered both for severe loss and for the organized labor that made later migration possible.',
            sources: [['Winter Quarters', 'https://www.churchofjesuschrist.org/study/history/topics/winter-quarters?lang=eng']]
        },
        'Handcart Companies': {
            answer: 'From 1856 through 1860, 10 Latter-day Saint emigrating companies crossed the plains with handcarts. Church leaders introduced the plan to reduce the expense of gathering converts who could not afford wagon travel. Travelers generally walked while pulling two-wheeled carts containing limited clothing, bedding, food, and personal possessions. Supply wagons accompanied the companies with heavier provisions and equipment.\n\nHandcart travel demanded discipline and endurance, but disaster was not inevitable. Eight of the 10 companies completed the journey without the catastrophic mortality associated with the Willie and Martin companies. Those two companies left late in 1856, encountered worsening shortages, and were trapped by severe snow and cold in present-day Wyoming. The Hunt and Hodgetts wagon companies were also stranded.\n\nAfter Brigham Young learned of their condition, rescuers carried food, clothing, wagons, and assistance east from Utah. Approximately 250 people among the stranded companies died after exposure, frostbite, hunger, and exhaustion. A complete handcart history therefore holds several truths together: the plan enabled thousands to gather, most companies arrived safely, the 1856 planning failures had devastating consequences, and the rescue represented remarkable collective service.',
            sources: [['Handcart Companies', 'https://www.churchofjesuschrist.org/study/history/topics/handcart-companies?lang=eng']]
        },
        'Brigham Young': {
            answer: 'Brigham Young was born in Vermont in 1801, joined the Church in 1832, and became an Apostle in 1835. Following the deaths of Joseph and Hyrum Smith in 1844, the Quorum of the Twelve Apostles, with Young as its president, provided Church leadership. He directed preparations to complete temple ordinances in Nauvoo and organize the Saints’ departure.\n\nYoung led the 1847 vanguard company toward the Great Basin. The company mapped the route, recorded landmarks, prepared the way for later travelers, and entered the Salt Lake Valley in July. Young then supervised a much larger migration and encouraged settlements throughout the Intermountain West. He became the second President of the Church in 1847 and later served as the first governor of Utah Territory.\n\nHis legacy is extensive and complicated. Under his leadership, converts gathered from many nations, communities and irrigation systems were established, missionary work expanded, and temples were planned or built. The era also included conflict, plural marriage, restrictive racial policies, and difficult relations with Native peoples and the federal government. Studying Brigham Young responsibly requires both attention to his central role in pioneer survival and settlement and honest engagement with the full historical record.',
            sources: [['Brigham Young', 'https://www.churchofjesuschrist.org/study/history/topics/brigham-young?lang=eng']]
        },
        'Joseph Smith': {
            answer: 'Joseph Smith (1805–1844) was the founding prophet and first President of The Church of Jesus Christ of Latter-day Saints. He organized the Church in 1830, led its early communities through Ohio, Missouri, and Illinois, and directed the building of the Nauvoo Temple before his death in Carthage, Illinois, in June 1844. His leadership shaped the religious community whose members later left Nauvoo and began the westward pioneer migration in 1846.\n\nA Pioneer-page answer should distinguish Joseph Smith from later pioneer leaders. He did not lead the 1846 exodus or the 1847 vanguard company; Brigham Young and other leaders organized those journeys after Joseph Smith’s death. To study his life responsibly, compare the official Church history narrative with specific documents and recognize that his legacy includes both sincere religious devotion and difficult historical questions.',
            sources: [['Joseph Smith', 'https://www.churchofjesuschrist.org/study/history/topics/joseph-smith?lang=eng'], ['The Church in Nauvoo', 'https://www.churchofjesuschrist.org/study/history/topics/nauvoo?lang=eng']]
        },
        'Salt Lake Valley': {
            answer: 'Members of the 1847 vanguard company first entered the Salt Lake Valley on July 22. Brigham Young, delayed by illness, arrived on July 24. The company had traveled more than a thousand miles from the Missouri River, following established portions of western trails before turning through the mountains toward the valley.\n\nWork began immediately. Pioneers diverted water, broke dry soil, planted late crops, surveyed a city, and constructed a fort for protection and shared labor. Later companies arrived that same year, and continued immigration transformed the valley into the administrative and spiritual center of the Church. Irrigation, cooperation, and organized settlement became defining features of early community building.\n\nThe valley was not vacant or without prior claims. Ute, Shoshone, and other Native peoples had long known, traveled through, hunted in, and used the wider region. As Latter-day Saint settlements expanded, different understandings of land and resources contributed to trade and cooperation but also displacement and conflict. The Salt Lake Valley story is therefore both an account of refuge and determined settlement and part of a larger western history whose consequences affected existing Native communities.',
            sources: [['Salt Lake Valley', 'https://www.churchofjesuschrist.org/study/history/topics/salt-lake-valley?lang=eng'], ['Pioneer Settlements', 'https://www.churchofjesuschrist.org/study/history/topics/pioneer-settlements?lang=eng']]
        },
        'Pioneer Life': {
            answer: 'Pioneer life was shaped by work, weather, health, family circumstances, and the resources of each company. On the trail, a day could include yoking animals, loading wagons, pulling handcarts, walking many miles, gathering fuel and water, cooking, washing, repairing equipment, caring for children and the sick, and guarding livestock at night. Progress depended on rivers, storms, terrain, grazing, and the condition of both people and animals.\n\nLife also included worship and community. Companies prayed, held meetings, sang, danced, celebrated, mourned, and recorded experiences in journals. Disagreements, fear, boredom, humor, births, illness, and deaths appear alongside expressions of faith. Sundays were often used for rest and worship when circumstances allowed.\n\nArrival did not end the hardship. Settlers built temporary shelter, planted crops, dug irrigation ditches, made furniture and clothing, established schools, and organized Church and civic life. Neighbors exchanged labor and supplies because few households could meet every need alone. There was no single pioneer experience: wagon owners, handcart travelers, immigrants, children, single adults, enslaved or free Black pioneers, and families from different nations faced distinct opportunities and burdens.',
            sources: [['Pioneer Trek', 'https://www.churchofjesuschrist.org/study/history/topics/pioneer-trek?lang=eng'], ['Pioneer Settlements', 'https://www.churchofjesuschrist.org/study/history/topics/pioneer-settlements?lang=eng']]
        },
        'Women Pioneers': {
            answer: 'Women were not simply passengers in the pioneer migration. They prepared food and clothing, drove teams, pulled handcarts, gathered fuel, cared for animals, nursed the sick, watched children, kept journals, and sometimes managed households or wagons after a husband or family member died. Some gave birth during the journey and then resumed travel under difficult conditions.\n\nTheir responsibilities continued in the settlements. Women cultivated gardens, preserved food, made and repaired clothing, taught children, practiced midwifery and nursing, operated businesses, and helped organize charitable and religious work. Relief Society traditions shaped mutual aid, although formal Relief Society organization changed during the Nauvoo exodus and was renewed in Utah communities.\n\nWomen’s records resist a single heroic stereotype. Some expressed confidence and spiritual conviction; others recorded homesickness, exhaustion, grief, frustration, or disagreement with decisions made around them. Converts arrived from Britain, Scandinavia, Europe, the United States, and elsewhere, bringing different skills and expectations. Reading named women’s journals and biographies allows their choices and voices to remain visible instead of reducing them to anonymous symbols of sacrifice.',
            sources: [['Latter-day Saint Women\'s History', 'https://www.churchofjesuschrist.org/study/church-history/womens-history?lang=eng'], ['Church History Biographical Database', 'https://history.churchofjesuschrist.org/chd/landing?lang=eng']]
        },
        'Pioneer Faith': {
            answer: 'Many Latter-day Saint pioneers understood gathering as a covenant commitment to Jesus Christ. Converts left homes, relatives, languages, and familiar cultures because they believed God had restored the gospel and called the Saints to gather. Temple covenants made in Nauvoo, teachings about Zion, and hope for a community where they could worship together gave religious meaning to the migration.\n\nFaith appeared in daily practices as much as in dramatic stories. Travelers prayed, read scripture, blessed the sick, worshipped on Sundays, sang hymns, shared food, buried loved ones, and served exhausted companions. The hymn Come, Come, Ye Saints, written during the 1846 crossing of Iowa, gave words to both hardship and hope. For many, rescue and mutual care became evidence of discipleship.\n\nTheir records also contain fear, anger, doubt, loneliness, and spiritual struggle. Faith did not make travelers immune to grief or guarantee the outcome they wanted. Some later remembered divine help; others emphasized endurance, practical cooperation, or loss. Pioneer faith is most meaningful when studied through individual voices and when sacrifice is connected to Christlike service rather than romanticized suffering.',
            sources: [['Pioneer Trek', 'https://www.churchofjesuschrist.org/study/history/topics/pioneer-trek?lang=eng'], ['Hymns of the Trail', 'https://history.churchofjesuschrist.org/content/museum/museum-treasures-hymns-of-the-trail?lang=eng']]
        },
        'Pioneer Miracles': {
            answer: 'Pioneer journals and later reminiscences sometimes describe healing, protection, unexpected food, timely rescue, or strength that participants understood as divine help. These accounts mattered because believers interpreted their journey through faith in Jesus Christ and expected God to sustain them, even when deliverance did not remove hardship or prevent death.\n\nThe 1856 handcart rescue is often discussed in this way. Rescuers left Utah with food, clothing, wagons, and teams after learning that late companies were stranded. Their arrival saved lives, but many still died. The event combines providential interpretation with concrete human choices: warnings, delays, weather, inadequate supplies, leadership decisions, and sacrificial service all belong in the history.\n\nAnother familiar story concerns gulls consuming crickets that threatened crops in 1848. Contemporary records support serious crop damage and efforts by gulls and settlers to control the insects, while the fully developed “miracle of the gulls” narrative took shape over time. Responsible study does not mock pioneer belief or repeat every later detail as contemporary fact. It identifies who recorded an event, when it was recorded, and how participants understood it.',
            sources: [['Crickets and Seagulls', 'https://www.churchofjesuschrist.org/study/history/topics/crickets-and-seagulls?lang=eng'], ['Handcart Companies', 'https://www.churchofjesuschrist.org/study/history/topics/handcart-companies?lang=eng']]
        },
        'Pioneer Legacy': {
            answer: 'The Latter-day Saint pioneer legacy includes covenant faith, migration, rescue, family sacrifice, temple building, missionary work, and the creation of communities across the Intermountain West. Tens of thousands of converts gathered from the United States, Britain, Scandinavia, continental Europe, and elsewhere. They carried languages, trades, music, worship practices, and family traditions that shaped the developing settlements.\n\nTheir legacy is also practical. Pioneers organized irrigation, roads, farms, schools, workshops, stores, and systems of mutual aid. Handcart rescue stories continue to teach service and responsibility for people in danger. Modern pioneer remembrance often extends the principle beyond ancestry, recognizing people throughout the world who accept the gospel, establish the Church in a new place, or faithfully begin again after displacement and loss.\n\nHonest remembrance also includes difficult consequences. Settlement altered Native lands and resources and contributed to displacement, conflict, and cultural disruption. Pioneer society reflected 19th-century inequalities and included contested policies and practices. Honoring courage does not require erasing complexity. A mature legacy listens to individual records, distinguishes history from later legend, acknowledges harm, and asks how faith can produce humility, reconciliation, and service today.',
            sources: [['Pioneer Settlements', 'https://www.churchofjesuschrist.org/study/history/topics/pioneer-settlements?lang=eng'], ['Pioneer Trek', 'https://www.churchofjesuschrist.org/study/history/topics/pioneer-trek?lang=eng']]
        },
        'Martin Handcart Company': {
            answer: 'Edward Martin led the fifth handcart company of 1856. Its members were largely European converts who traveled by ship and rail before beginning the overland journey. Delays meant the company left Iowa City in late July and Florence, Nebraska, in late August. That schedule placed hundreds of people far from Utah as autumn weather worsened and provisions diminished.\n\nAfter crossing the North Platte River, travelers faced snow, bitter cold, exhaustion, frostbite, and hunger. The company took shelter near Devil’s Gate at the place now known as Martin’s Cove. Rescuers sent from Utah brought flour, clothing, wagons, teams, and physical assistance, but relief came after severe suffering had already begun. River crossings and continued travel remained dangerous even after rescuers arrived.\n\nThe survivors reached Salt Lake City on November 30. The broader disaster involving the Willie and Martin handcart companies and the Hunt and Hodgetts wagon companies stranded close to 1,500 people; approximately 250 died. The Martin story deserves more than a triumphant summary. It includes sincere faith and extraordinary rescue alongside late departure, inadequate provisions, preventable risk, grief, and the lasting testimony of individual survivors.',
            sources: [['Handcart Companies', 'https://www.churchofjesuschrist.org/study/history/topics/handcart-companies?lang=eng'], ['Go and Bring Them In', 'https://www.churchofjesuschrist.org/study/ensign/2006/12/go-and-bring-them-in?lang=eng']]
        },
        'Willie Handcart Company': {
            answer: 'James G. Willie led the fourth handcart company of 1856. Many company members were European converts with limited resources. They left Iowa City in July and departed Florence, Nebraska, in August, later than was considered safe for crossing the high plains and mountains. As the journey continued, food was rationed and physical strength declined.\n\nAn early winter storm struck in present-day Wyoming. The company became immobilized near the Sweetwater River, and some travelers died from exposure, hunger, illness, and exhaustion. Captain Willie and Joseph Elder went ahead to find rescuers, who reached the company with food and assistance. The climb over Rocky Ridge remained one of the most punishing portions of the journey, even with rescue underway.\n\nSurvivors arrived in Salt Lake City on November 9. The Willie company was one of 10 handcart companies, and most of the others did not suffer comparable catastrophe. Its history should therefore be told specifically rather than made representative of all handcart travel. It preserves devotion, courage, and rescue, but it also demonstrates the consequences of late travel, dwindling supplies, severe weather, and decisions that exposed vulnerable people to extraordinary danger.',
            sources: [['Handcart Companies', 'https://www.churchofjesuschrist.org/study/history/topics/handcart-companies?lang=eng'], ['Five Things about the Handcart Rescue', 'https://www.churchofjesuschrist.org/learn/history/sites/wyoming/discover/five-things-you-might-not-know-about-the-handcart-rescue?lang=eng']]
        },
        'Pioneer Daily Life': {
            answer: 'A travel day commonly began before or near sunrise. Families prepared breakfast, repacked bedding and cooking equipment, gathered animals, and arranged wagons or handcarts. After prayer and instructions, the company moved according to weather, trail conditions, water, grass, health, and the strength of its animals or travelers. Distances varied, and river crossings, steep grades, broken equipment, or missing livestock could consume an entire day.\n\nAt camp, the work continued. Travelers collected water and fuel, cooked, washed, repaired shoes and clothing, greased wagon wheels, tended animals, nursed the sick, watched children, stood guard, and sometimes wrote in journals. Companies also sang, danced, visited, held meetings, and buried those who died. Sundays were often reserved for worship and rest when circumstances permitted.\n\nDaily life changed after arrival. Families first needed shelter, food, water, and winter preparation. They built homes and public structures, planted and harvested, dug irrigation ditches, taught children, practiced trades, and participated in Church and civic life. Routine depended heavily on gender expectations, age, health, wealth, occupation, country of origin, and whether a person traveled by wagon, handcart, or another method.',
            sources: [['Pioneer Trek', 'https://www.churchofjesuschrist.org/study/history/topics/pioneer-trek?lang=eng'], ['1847 Trek Daily Summaries', 'https://newsroom.churchofjesuschrist.org/article/how-brigham-young-first-arrived-in-the-salt-lake-valley']]
        },
        'Pioneer Children': {
            answer: 'Children made the pioneer journey as infants, toddlers, adolescents, and nearly grown workers, so their experiences varied widely. Older children often walked and helped drive animals, gather buffalo chips or wood, fetch water, watch younger siblings, prepare camp, or pull a handcart. Younger children rode when space and circumstances allowed, but crowded wagons and limited weight sometimes required nearly everyone who could walk to do so.\n\nTrail life still contained childhood. Records mention games, songs, friendships, curiosity about landmarks and animals, and excitement over unusual events. Some children learned practical skills from adults or received informal lessons. At the same time, they experienced storms, hunger, illness, accidents, homesickness, and the deaths of parents, siblings, or friends. Babies were born on the trail, and some children were buried beside it.\n\nAfter arrival, children helped with gardens, livestock, household work, water, fuel, and younger family members while settlements built schools and community institutions. Their memories later became an important part of pioneer history. The best way to understand pioneer children is to read named biographies and family records, allowing joy, labor, fear, resilience, and loss to remain together.',
            sources: [['Church History Biographical Database', 'https://history.churchofjesuschrist.org/chd/landing?lang=eng'], ['Pioneer Trek', 'https://www.churchofjesuschrist.org/study/history/topics/pioneer-trek?lang=eng']]
        },
        'Pioneer Food': {
            answer: 'Pioneer food was selected for durability, weight, cost, and ease of cooking. Depending on the company and family, supplies could include flour or meal, bacon, beans, rice, dried fruit, sugar, salt, and other staples. Milk, butter, eggs, fresh meat, or vegetables were available only when animals, trade, hunting, gathering, or local conditions made them possible. Menus therefore changed throughout the journey rather than following one universal pioneer diet.\n\nCooking required water, fuel, tools, and time. Families used campfires, but wood was scarce on some portions of the plains, so travelers gathered brush or dried animal dung. Water could be muddy, alkaline, contaminated, or distant from the trail. Weather and wind complicated cooking, while illness made ordinary food preparation more difficult. Companies carefully managed provisions because every pound had to be carried by a wagon, animal, or handcart.\n\nShortages became dangerous when travel took longer than expected. Rations were reduced in the late 1856 handcart companies, contributing to weakness as severe weather arrived. Food history should distinguish ordinary meals from emergency conditions and use company records where possible. It reveals planning, inequality, ingenuity, cultural preference, environmental limits, and the life-saving importance of supply and rescue.',
            sources: [['Pioneer Trek', 'https://www.churchofjesuschrist.org/study/history/topics/pioneer-trek?lang=eng'], ['Handcart Companies', 'https://www.churchofjesuschrist.org/study/history/topics/handcart-companies?lang=eng']]
        },
        'Pioneer Clothing': {
            answer: 'Latter-day Saint pioneers generally wore the ordinary clothing of their time rather than a special pioneer uniform. Women and girls commonly traveled in dresses or skirts with layers, aprons, shawls, hats or bonnets, stockings, and shoes. Men and boys wore shirts, trousers, suspenders or vests, coats, hats, and boots or shoes. Exact garments varied with age, means, occupation, country of origin, personal preference, and the season of travel.\n\nTrail clothing had to protect against sun, dust, wind, rain, cold, insects, and constant walking. Wool provided warmth; linen and cotton could be used for lighter garments. Aprons and outer layers protected clothing during work. Shoes were especially important and often wore through, requiring patching or replacement. Limited wagon or handcart space meant travelers could not carry a large wardrobe, and repeated repair was part of daily life.\n\nModern costumes can create the misleading impression that every pioneer looked alike. Contemporary photographs, surviving garments, inventories, journals, and named biographies show more variety. Clothing also tells a deeper story about labor and resources: fabric had to be purchased, carried, spun, woven, cut, sewn, altered, handed down, or mended, and that work frequently fell to women and girls.',
            sources: [['Church History Biographical Database', 'https://history.churchofjesuschrist.org/chd/landing?lang=eng'], ['Pioneer Trek', 'https://www.churchofjesuschrist.org/study/history/topics/pioneer-trek?lang=eng']]
        },
        'Pioneer Trails': {
            answer: 'The Latter-day Saint pioneer trail was a connected migration route rather than an entirely separate road. From Nauvoo, the 1846 exodus crossed Iowa toward the Missouri River. Winter Quarters and nearby Iowa settlements became staging areas. Beginning in 1847, companies traveled west along portions of existing Platte River routes also used by other emigrants, traders, missionaries, Native peoples, and the military.\n\nImportant landmarks included the Platte River, Chimney Rock, Scotts Bluff, Fort Laramie, Independence Rock, Devil’s Gate, the Sweetwater River, South Pass, Fort Bridger, Echo Canyon, and Emigration Canyon. Brigham Young’s vanguard company gathered measurements and route information for those who followed. Trail choices depended on water, grass, river conditions, seasons, roads, ferries, and changing outfitting centers.\n\nLater companies did not all begin in Nauvoo or follow every segment in the same way. European converts might arrive by ship, travel by rail or river, outfit in Iowa City or Florence, and then join the overland route. Wagon and handcart companies also differed in pace and carrying capacity. Studying maps alongside company journals helps separate one traveler’s experience from the broader system that moved tens of thousands west.',
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

    function directPioneerQuestion(question) {
        const text = String(question || '').toLowerCase();
        const topic = /\bjoseph smith\b(?!\s+barlow\b)/i.test(text) ? 'Joseph Smith'
            : /winter quarters/i.test(text) ? 'Winter Quarters'
            : /\bwillie\b.*\bhandcart|\bhandcart\b.*\bwillie\b/i.test(text) ? 'Willie Handcart Company'
            : /\bmartin\b.*\bhandcart|\bhandcart\b.*\bmartin\b/i.test(text) ? 'Martin Handcart Company'
            : /handcart(?!\s+racing)/i.test(text) ? 'Handcart Companies'
            : /pioneer children|children.*trail|kids.*pioneer/i.test(text) ? 'Pioneer Children'
            : /pioneer food|what did pioneers eat|pioneer meals/i.test(text) ? 'Pioneer Food'
            : /women pioneers|women.*pioneer|pioneer.*women/i.test(text) ? 'Women Pioneers'
            : /pioneer faith|faith.*pioneer|pioneer.*faith/i.test(text) ? 'Pioneer Faith'
            : /daily life|life on the trail|ordinary day.*pioneer/i.test(text) ? 'Pioneer Daily Life'
            : /\bbrigham young\b/i.test(text) ? 'Brigham Young'
            : null;
        return topic ? reviewedTopicAnswer(topic) : null;
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
        if (!disclosureKey && window.focusChristScriptureReady) {
            try {
                const direct = await (await window.focusChristScriptureReady).lookupRequest(question);
                if (direct) return direct;
            } catch (_) { /* Continue through the guarded service. */ }
        }
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

    function focusPioneerInput() {
        const input = userInput();
        if (!input || input.disabled || !input.isConnected) return;
        try { input.focus({ preventScroll: true }); } catch (_error) { input.focus(); }
        input.setAttribute('data-focuschrist-composer-ready', 'true');
        if (document.activeElement === input && typeof input.setSelectionRange === 'function') {
            const end = input.value.length;
            input.setSelectionRange(end, end);
        }
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

    function promoteLatestExchangeToTop(answerCandidate) {
        const box = chatBox();
        if (!box) return;
        if (box.getAttribute('data-focuschrist-latest-first') === 'true') return;
        const answers = box.querySelectorAll('.bot-message');
        const users = box.querySelectorAll('.user-message');
        const answer = answerCandidate && answerCandidate.classList && answerCandidate.classList.contains('bot-message')
            ? answerCandidate
            : (answers.length ? answers[answers.length - 1] : null);
        const user = answer && answer.previousElementSibling && answer.previousElementSibling.classList.contains('user-message')
            ? answer.previousElementSibling
            : (users.length ? users[users.length - 1] : null);
        if (!answer) return;
        const first = box.firstElementChild;
        if (user && user !== first) box.insertBefore(user, first);
        const answerAnchor = user && user.isConnected ? user.nextSibling : box.firstElementChild;
        if (answer !== answerAnchor) box.insertBefore(answer, answerAnchor);
        box.setAttribute('data-focuschrist-latest-first', 'true');
    }

    function positionAnswer(answerElement) {
        const box = chatBox();
        if (!box || !answerElement) return;
        if (typeof promoteLatestExchangeToTop === 'function') promoteLatestExchangeToTop(answerElement);
        if (!answerElement.classList || !answerElement.classList.contains('bot-message')) answerElement = box.querySelector('.bot-message') || answerElement;
        const questionElement = answerElement.previousElementSibling && answerElement.previousElementSibling.classList.contains('user-message')
            ? answerElement.previousElementSibling
            : null;
        const anchor = questionElement || answerElement;
        const boxRectBefore = box.getBoundingClientRect();
        const internalTop = Math.max(0, anchor.getBoundingClientRect().top - boxRectBefore.top + box.scrollTop - 12);
        // Keep the newest question at the top of the chat viewport so the
        // question and the beginning of its answer are visible together.
        box.scrollTo({ top: internalTop, behavior: 'auto' });
        const header = document.querySelector('.nav[data-focuschrist-header="standard"]');
        const headerHeight = header && getComputedStyle(header).position === 'fixed' ? header.getBoundingClientRect().height : 0;
        const safeTop = headerHeight + 18;
        const boxRect = box.getBoundingClientRect();
        if (boxRect.top < safeTop || boxRect.top > window.innerHeight * 0.72) {
            window.scrollTo({ top: Math.max(0, window.scrollY + boxRect.top - safeTop), behavior: 'auto' });
        }
        // Every completed answer leaves the next-question field clicked,
        // focused, and ready without undoing the question/answer scroll.
        if (typeof focusPioneerInput === 'function') window.setTimeout(focusPioneerInput, 80);
    }

    document.addEventListener('focuschrist:answer-ready', function (event) {
        window.setTimeout(function () {
            const box = chatBox();
            if (box && event.target && event.target.classList && event.target.classList.contains('bot-message')) {
                const newerQuestion = Array.from(box.querySelectorAll('.user-message')).some(function (question) {
                    return Boolean(event.target.compareDocumentPosition(question) & 4);
                });
                if (newerQuestion) return;
                positionAnswer(event.target);
            }
        }, 60);
    });

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

    async function renderDisclosureAnswer(container, answer, sources) {
        const checked = window.focusChristVerifyScriptureAnswer
            ? await window.focusChristVerifyScriptureAnswer(answer, sources)
            : {ok:false,answer:'Scripture verification is temporarily unavailable. Please try again.'};
        answer = checked.answer;
        if (!checked.ok) sources = [];
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
        if (checked.ok && window.focusChristScriptureLibrary) window.focusChristScriptureLibrary.linkify(container);
        return checked;
    }

    async function researchDisclosure(control, aiResponse, mappedTopic, kind) {
        if (aiResponse.dataset.focuschristResearchState === 'pending') return;
        aiResponse.dataset.focuschristResearchState = 'pending';
        control.setAttribute('data-focuschrist-disclosure-mode', 'loading');
        aiResponse.setAttribute('aria-busy', 'true');
        aiResponse.innerHTML = '';
        const loadingText = document.createElement('p');
        loadingText.textContent = 'Researching this topic. The detailed answer will appear here.';
        aiResponse.appendChild(loadingText);
        try {
            const pageReference = controlPageReference(control, kind, mappedTopic);
            const heading = control.querySelector('.timeline-title, .map-content h4, .map-content h3');
            const subject = heading ? heading.textContent.trim() : mappedTopic;
            const query = 'Explain this Latter-day Saint pioneer history topic: ' + subject;
            const result = await requestPioneerAI(query, pageReference, control.getAttribute('data-topic'));
            if (!result || !result.sourceIntegrityPassed || !result.answer) {
                throw new Error('The detailed topic answer could not be verified');
            }
            const displayed = await renderDisclosureAnswer(aiResponse, result.answer, result.sources);
            if (!displayed.ok) throw new Error('Scripture verification rejected the topic answer');
            aiResponse.dataset.focuschristResearchState = 'complete';
            aiResponse.dataset.focuschristLoaded = 'verified-research';
            control.setAttribute('data-focuschrist-disclosure-mode', 'verified-research');
        } catch (error) {
            console.error('Pioneer disclosure error:', error);
            aiResponse.dataset.focuschristResearchState = 'error';
            control.setAttribute('data-focuschrist-disclosure-mode', 'research-unavailable');
            await renderDisclosureAnswer(aiResponse, 'A detailed answer could not be verified right now. You can try again or continue with the historical sources linked on this page.');
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
        const box = chatBox();
        if (box && typeof box.removeAttribute === 'function') box.removeAttribute('data-focuschrist-latest-first');
        window.addMessage(question, true);
        input.value = '';
        button.disabled = true;
        input.disabled = true;
        let loading = null;

        try {
            const contextResolution = resolvePioneerContext(question);
            const reviewed = directPioneerQuestion(question) || reviewedPioneerKnowledge(question, contextResolution);
            if (reviewed) {
                const answer = window.addMessage(reviewed.answer, false, reviewed.sources || []);
                rememberExchange(question, reviewed.answer, reviewed);
                setConversationMode(true);
                positionAnswer(answer);
                return;
            }

            loading = showLoading();

            // Tell My Story, Too is an explicit optional experience. Do not run
            // its loose name matcher for ordinary Pioneer questions: a generic
            // question such as "Who was Joseph Smith?" can otherwise resolve to
            // an unrelated similarly named biography before the normal Pioneer
            // answer path has a chance to respond.
            const response = await requestPioneerAI(contextResolution.query || question, '');
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
