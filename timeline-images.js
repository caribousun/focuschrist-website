/* Existing approved artwork references; original identity pixels remain unchanged. */
(function(){
"use strict";
var registry={
  "life": {
    "0": {
      "src": "/assets/page-art/birth-of-christ/08-annunciation-800.webp",
      "alt": "Mary listens to Gabriel in a modest room.",
      "href": "/birth-of-christ.html#mary-and-elisabeth",
      "caption": "Mary listens to Gabriel in a modest room.",
      "inventoryRow": 145,
      "width": 800,
      "height": 533
    },
    "1": {
      "src": "/assets/page-art/birth-of-christ/09-mary-elisabeth-800.webp",
      "alt": "Mary and Elisabeth greet one another, holding each other’s arms.",
      "href": "/birth-of-christ.html#mary-and-elisabeth",
      "caption": "Mary and Elisabeth greet one another, holding each other’s arms.",
      "inventoryRow": 146,
      "width": 800,
      "height": 533
    },
    "2": {
      "src": "/assets/page-art/birth-of-christ/14-shepherds-find-800.webp",
      "alt": "Shepherds enter and find Mary, Joseph, and the infant lying in a manger.",
      "href": "/birth-of-christ.html#savior-born",
      "caption": "Shepherds enter and find Mary, Joseph, and the infant lying in a manger.",
      "inventoryRow": 151,
      "width": 800,
      "height": 533
    },
    "3": {
      "src": "/assets/page-art/birth-of-christ/15-simeon-800.webp",
      "alt": "Simeon holds the infant Jesus and speaks with Mary as Joseph listens.",
      "href": "/birth-of-christ.html#temple-witnesses",
      "caption": "Simeon holds the infant Jesus and speaks with Mary as Joseph listens.",
      "inventoryRow": 154,
      "width": 800,
      "height": 533
    },
    "4": {
      "src": "/assets/page-art/birth-of-christ/18-egypt-800.webp",
      "alt": "Joseph and Mary travel at night while Mary carries the child close to her.",
      "href": "/birth-of-christ.html#wise-men-and-egypt",
      "caption": "Joseph and Mary travel at night while Mary carries the child close to her.",
      "inventoryRow": 158,
      "width": 800,
      "height": 533
    },
    "5": {
      "src": "/assets/page-art/birth-of-christ/23-nazareth-return-800.webp",
      "alt": "Joseph carries the young Jesus beside Mary at a village doorway.",
      "href": "/birth-of-christ.html#wise-men-and-egypt",
      "caption": "Joseph carries the young Jesus beside Mary at a village doorway.",
      "inventoryRow": 159,
      "width": 800,
      "height": 533
    },
    "6": {
      "src": "/assets/page-art/temples/temple-young-jesus-960.webp",
      "alt": "Twelve-year-old Jesus listens and speaks with adult teachers in a temple courtyard.",
      "href": "/answers/why-latter-day-saints-build-temples.html#temple-young-jesus",
      "caption": "Twelve-year-old Jesus listens and speaks with adult teachers in a temple courtyard.",
      "artworkId": "art-6fed26ba4ceb",
      "width": 960,
      "height": 640
    },
    "7": {
      "src": "/art/thumbs/Jesus-baptized.webp",
      "alt": "John stands beside Jesus in the river while people watch from the bank.",
      "href": "/art.html#art-gallery",
      "caption": "John stands beside Jesus in the river while people watch from the bank.",
      "artworkId": "art-4f5759d8edad",
      "width": 640,
      "height": 338
    },
    "8": {
      "src": "/assets/page-art/bible-together/christ-wilderness-temptation-960.webp",
      "alt": "Jesus, weary but resolute, sits among wilderness rocks and answers an unseen tempter; ordinary stones lie nearby.",
      "href": "/answers/bible-and-book-of-mormon-together.html#study-christ-wilderness-temptation",
      "caption": "Jesus, weary but resolute, sits among wilderness rocks and answers an unseen tempter; ordinary stones lie nearby.",
      "artworkId": "art-c5c83791e8cf",
      "width": 960,
      "height": 640
    },
    "9": {
      "src": "/assets/page-art/jesus-journey/mm-cana-jars-960.webp",
      "alt": "Jesus watches a servant pour water from a clay pitcher into one of six large stone jars.",
      "href": "/jesus-christ/mortal-ministry.html#cana",
      "caption": "Jesus watches a servant pour water from a clay pitcher into one of six large stone jars.",
      "inventoryRow": 82,
      "width": 960,
      "height": 640
    },
    "10": {
      "src": "/assets/page-art/ask-well-800.webp",
      "alt": "Jesus Christ speaking with the Samaritan woman at the well",
      "href": "/ask.html#topic-heading",
      "caption": "Jesus Christ speaking with the Samaritan woman at the well",
      "artworkId": "art-3b1016debbad",
      "width": 800,
      "height": 533
    },
    "11": {
      "src": "/assets/page-art/bible-together/christ-isaiah-nazareth-960.webp",
      "alt": "Jesus stands reading an open scroll before attentive adults in a modest synagogue.",
      "href": "/answers/bible-and-book-of-mormon-together.html#study-christ-isaiah-nazareth",
      "caption": "Jesus stands reading an open scroll before attentive adults in a modest synagogue.",
      "artworkId": "art-3a640be78eb4",
      "width": 960,
      "height": 640
    },
    "12": {
      "src": "/assets/page-art/jesus-journey/mc-peters-mother-in-law-960.webp",
      "alt": "Jesus takes an older woman by the hand and helps her rise from bedding as they look toward one another.",
      "href": "/jesus-christ/miracles-and-compassion.html#home",
      "caption": "Jesus takes an older woman by the hand and helps her rise from bedding as they look toward one another.",
      "inventoryRow": 69,
      "width": 960,
      "height": 640
    },
    "13": {
      "src": "/assets/page-art/art-study/thumbs/still-storm-boat.webp",
      "alt": "Jesus Christ standing steady in a storm-tossed boat as frightened disciples work around Him",
      "href": "/art-study/be-still.html#psalm-context",
      "caption": "Jesus Christ standing steady in a storm-tossed boat as frightened disciples work around Him",
      "artworkId": "art-b8ea4e64b3a7",
      "width": 800,
      "height": 533
    },
    "14": {
      "src": "/art/thumbs/Jesus-feeding-people.webp",
      "alt": "Jesus shares bread and fish with people gathered on the hillside.",
      "href": "/art.html#art-gallery",
      "caption": "Jesus shares bread and fish with people gathered on the hillside.",
      "artworkId": "art-838305f993f7",
      "width": 640,
      "height": 338
    },
    "15": {
      "src": "/assets/timeline/banias-frith-1862-loc.jpg",
      "alt": "Stone buildings and vegetation at Banias, ancient Caesarea Philippi, in Francis Frith’s 1862 photograph.",
      "caption": "Stone buildings and vegetation at Banias, ancient Caesarea Philippi, in Francis Frith’s 1862 photograph.",
      "href": "https://www.loc.gov/item/00653006/",
      "credit": "Francis Frith / Library of Congress",
      "width": 1024,
      "height": 823,
      "frame": "banias-photo"
    },
    "16": {
      "src": "/assets/page-art/jesus-journey/mm-transfiguration-960.webp",
      "alt": "Jesus touches Peter's shoulder as Peter, James and John look up from the rocky mountainside.",
      "href": "/jesus-christ/mortal-ministry.html#transfiguration",
      "caption": "Jesus touches Peter's shoulder as Peter, James and John look up from the rocky mountainside.",
      "inventoryRow": 88,
      "width": 960,
      "height": 640
    },
    "17": {
      "src": "/assets/page-art/jesus-journey/tp-zacchaeus-response-960.webp",
      "alt": "Zacchaeus speaks with open hands as Jesus listens across a simple meal.",
      "href": "/jesus-christ/teachings-and-parables.html#picture-tp-zacchaeus-response",
      "caption": "Zacchaeus speaks with open hands as Jesus listens across a simple meal.",
      "artworkId": "art-6163f4e7a48c",
      "width": 960,
      "height": 640
    },
    "18": {
      "src": "/assets/page-art/life-after-death/martha-800.webp",
      "alt": "Jesus listens to Martha outside Bethany as she speaks with Him after Lazarus’s death.",
      "href": "/answers/what-happens-after-death.html#christ-and-grief",
      "caption": "Jesus listens to Martha outside Bethany as she speaks with Him after Lazarus’s death.",
      "artworkId": "art-dcbee2660a2a",
      "width": 800,
      "height": 533
    },
    "19": {
      "src": "/assets/page-art/jesus-journey/mm-jerusalem-tears-960.webp",
      "alt": "Jesus looks toward Jerusalem with tearful eyes while a disciple stands quietly behind Him.",
      "href": "/jesus-christ/mortal-ministry.html#jerusalem",
      "caption": "Jesus looks toward Jerusalem with tearful eyes while a disciple stands quietly behind Him.",
      "inventoryRow": 89,
      "width": 960,
      "height": 640
    },
    "20": {
      "src": "/assets/page-art/jesus-journey/mm-temple-tables-960.webp",
      "alt": "Jesus stands beside an overturned table and scattered coins while sellers gather their belongings in the temple court.",
      "href": "/jesus-christ/mortal-ministry.html#picture-mm-temple-tables",
      "caption": "Jesus stands beside an overturned table and scattered coins while sellers gather their belongings in the temple court.",
      "artworkId": "art-88ba66d9c484",
      "width": 960,
      "height": 640
    },
    "21": {
      "src": "/assets/page-art/jesus-journey/rr-judas-morsel-960.webp",
      "alt": "Jesus extends a dipped morsel toward Judas while two disciples watch from behind.",
      "href": "/jesus-christ/redeemer-and-risen-lord.html#sacrament",
      "caption": "Jesus extends a dipped morsel toward Judas while two disciples watch from behind.",
      "inventoryRow": 91,
      "width": 960,
      "height": 640
    },
    "22": {
      "src": "/assets/page-art/jesus-journey/rr-sleeping-disciples-960.webp",
      "alt": "Jesus speaks earnestly to Peter beneath olive trees while James and John sleep behind them.",
      "href": "/jesus-christ/redeemer-and-risen-lord.html#gethsemane",
      "caption": "Jesus speaks earnestly to Peter beneath olive trees while James and John sleep behind them.",
      "inventoryRow": 92,
      "width": 960,
      "height": 640
    },
    "23": {
      "src": "/assets/page-art/jesus-journey/rr-before-pilate-960.webp",
      "alt": "Jesus inclines His head toward Pilate, who questions Him from his seat.",
      "href": "/jesus-christ/redeemer-and-risen-lord.html#pilate",
      "caption": "Jesus inclines His head toward Pilate, who questions Him from his seat.",
      "inventoryRow": 93,
      "width": 960,
      "height": 640
    },
    "24": {
      "src": "/assets/page-art/jesus-journey/rr-linen-burial-960.webp",
      "alt": "Joseph of Arimathea and Nicodemus draw linen over Jesus's body inside a stone tomb.",
      "href": "/jesus-christ/redeemer-and-risen-lord.html#burial",
      "caption": "Joseph of Arimathea and Nicodemus draw linen over Jesus's body inside a stone tomb.",
      "inventoryRow": 95,
      "width": 960,
      "height": 640
    },
    "25": {
      "src": "/assets/page-art/atonement/emmaus-v2-960.webp",
      "alt": "Jesus opens the scriptures to two disciples walking toward Emmaus.",
      "href": "/atonement.html#resurrection",
      "caption": "Jesus opens the scriptures to two disciples walking toward Emmaus.",
      "artworkId": "art-62b14c5b9dde",
      "width": 960,
      "height": 640
    },
    "26": {
      "src": "/assets/page-art/jesus-journey/rr-broiled-fish--199ddf7a530d-thumb.webp",
      "alt": "The risen Jesus turns toward a disciple while holding a piece of fish, with another disciple watching beside him.",
      "href": "/jesus-christ/redeemer-and-risen-lord.html#risen-witness",
      "caption": "The risen Jesus turns toward a disciple while holding a piece of fish, with another disciple watching beside him.",
      "inventoryRow": 96,
      "width": 960,
      "height": 640
    },
    "27": {
      "src": "/assets/page-art/art-study/thumbs/living-breakfast-shore-20260919.webp",
      "alt": "The risen Jesus Christ shares bread with disciples beside a small fire on the shore.",
      "href": "/art-study/the-living-christ.html#personal-study",
      "caption": "The risen Jesus Christ shares bread with disciples beside a small fire on the shore.",
      "artworkId": "art-f6d313c50a8b",
      "width": 800,
      "height": 533
    },
    "28": {
      "src": "/assets/page-art/jesus-journey/rr-cloud-receives-960.webp",
      "alt": "Jesus rises above an olive-covered hillside, looking tenderly down toward the disciples watching Him.",
      "href": "/jesus-christ/redeemer-and-risen-lord.html#ascension",
      "caption": "Jesus rises above an olive-covered hillside, looking tenderly down toward the disciples watching Him.",
      "inventoryRow": 97,
      "width": 960,
      "height": 640
    },
    "29": {
      "src": "/assets/page-art/jesus-journey/bn-hear-the-voice-960.webp",
      "alt": "People gathered near the temple lift their faces toward the sky.",
      "href": "/jesus-christ/risen-savior-in-the-book-of-mormon.html#voice",
      "caption": "People gathered near the temple lift their faces toward the sky.",
      "inventoryRow": 107,
      "width": 960,
      "height": 640
    },
    "30": {
      "src": "/assets/page-art/jesus-journey/bn-scriptures-explained-960.webp",
      "alt": "Jesus speaks with seated listeners while an older man holds a bound set of metal plates.",
      "href": "/jesus-christ/risen-savior-in-the-book-of-mormon.html#scriptures",
      "caption": "Jesus speaks with seated listeners while an older man holds a bound set of metal plates.",
      "inventoryRow": 114,
      "width": 960,
      "height": 640
    },
    "31": {
      "src": "/assets/history/first-vision-1400.webp",
      "href": "/church-history.html#history-first-vision-title",
      "alt": "Joseph Smith kneeling in a wooded grove as God the Father and Jesus Christ appear in heavenly light",
      "caption": "Joseph kneels among the trees as heavenly light fills the grove. His prayer began the Restoration story.",
      "artworkId": "art-52dc5f55c32e",
      "width": 1400,
      "height": 468
    },
    "32": {
      "src": "/assets/page-art/jesus-journey/rt-vision-1832-960.webp",
      "href": "/jesus-christ/restoration-and-today.html#picture-rt-vision-1832",
      "alt": "Joseph Smith and Sidney Rigdon look toward the risen Savior in a vision above their scriptural work.",
      "caption": "Joseph Smith and Sidney Rigdon look toward the risen Savior while studying the scriptures together.",
      "artworkId": "art-c7761e72c36e",
      "width": 960,
      "height": 640
    },
    "33": {
      "src": "/assets/timeline/history/newel-whitney-store-6faf4c5-1920.jpg",
      "href": "https://www.churchofjesuschrist.org/media/image/newel-whitney-store-6faf4c5?lang=eng",
      "alt": "The white wooden Whitney store stands in Kirtland, where members of the School of the Prophets gathered upstairs.",
      "caption": "The white wooden Whitney store stands in Kirtland, where members of the School of the Prophets gathered upstairs.",
      "credit": "The Church of Jesus Christ of Latter-day Saints, Gospel Media",
      "width": 1920,
      "height": 1445
    },
    "34": {
      "src": "/assets/timeline/history/kirtland-temple-6aca5ae.jpg",
      "href": "https://www.churchofjesuschrist.org/media/image/kirtland-temple-6aca5ae?lang=eng",
      "alt": "The Kirtland Temple stands among green trees, recalling the house where Joseph received the vision of the celestial kingdom.",
      "caption": "The Kirtland Temple stands among green trees, recalling the house where Joseph received the vision of the celestial kingdom.",
      "credit": "The Church of Jesus Christ of Latter-day Saints, Gospel Media",
      "width": 1920,
      "height": 1440
    },
    "35": {
      "src": "/assets/page-art/church-history/kirtland-temple-960.webp",
      "href": "/church-history.html#kirtland-temple",
      "alt": "Worshippers approach the Kirtland Temple along a muddy path, beneath its red roof and pale blue-gray walls.",
      "caption": "Worshippers make their way toward the Kirtland Temple, a house raised through the sacrifice of the early Saints.",
      "artworkId": "art-85a07f6b9325",
      "width": 960,
      "height": 640
    },
    "36": {
      "src": "/assets/timeline/history/lorenzo-snow-cb940d3.jpg",
      "href": "https://www.churchofjesuschrist.org/media/image/lorenzo-snow-cb940d3?lang=eng",
      "alt": "Lorenzo Snow appears in a painted portrait, remembered here for his testimony of seeing the Savior in the temple.",
      "caption": "Lorenzo Snow appears in a painted portrait, remembered here for his testimony of seeing the Savior in the temple.",
      "credit": "The Church of Jesus Christ of Latter-day Saints, Gospel Media",
      "width": 1006,
      "height": 1280
    },
    "37": {
      "src": "/assets/page-art/plan-of-salvation/redemption-dead-800.webp",
      "href": "/answers/plan-of-salvation.html#picture-pos-redemption-dead",
      "alt": "Joseph F. Smith sits with an open Bible.",
      "caption": "Joseph F. Smith sits with an open Bible as he ponders the Savior’s work among the dead.",
      "artworkId": "art-5e7d2eaa1e3a",
      "width": 800,
      "height": 533
    }
  },
  "handcart": {
    "0": {
      "src": "/assets/pioneers/story/04-atlantic-800.webp",
      "alt": "British emigrant families stand on the deck of a nineteenth-century sailing ship.",
      "href": "/pioneers.html#pioneer-story-04-atlantic",
      "caption": "British emigrant families stand on the deck of a nineteenth-century sailing ship.",
      "inventoryRow": 9,
      "width": 800,
      "height": 533
    },
    "1": {
      "src": "/assets/timeline/new-york-harbor-staten-island-1855.jpg",
      "alt": "A nineteenth-century painting of sailing ships and steam vessels in the harbor, viewed from a wooded Staten Island shore.",
      "href": "https://www.metmuseum.org/art/collection/search/14836",
      "caption": "Sailing vessels and waterfront buildings fill this view from Staten Island, painted around 1855.",
      "credit": "The Metropolitan Museum of Art · Edward W. C. Arnold Collection, 1954",
      "width": 1200,
      "height": 901
    },
    "2": {
      "src": "/assets/timeline/boston-harbor-loc.jpg",
      "alt": "Entering Boston Harbor, an 1883 lithograph published by American Art Publishing Co., shows a later view of the arrival port.",
      "caption": "Entering Boston Harbor, an 1883 lithograph published by American Art Publishing Co., shows a later view of the arrival port.",
      "href": "https://www.loc.gov/item/2018756541/",
      "credit": "Library of Congress · American Art Publishing Co., 1883",
      "width": 1024,
      "height": 792
    },
    "3": {
      "src": "/assets/timeline/albany-hudson-1846-loc.jpg",
      "alt": "Michael Seymour’s watercolor of the Hudson River at Albany, July 18, 1846, shows the river setting ten years before the company’s journey.",
      "caption": "Michael Seymour’s watercolor of the Hudson River at Albany, July 18, 1846, shows the river setting ten years before the company’s journey.",
      "href": "https://www.loc.gov/item/2011647342/",
      "credit": "Library of Congress · Michael Seymour, 1846",
      "width": 1024,
      "height": 850
    },
    "4": {
      "src": "/assets/timeline/buffalo-harbor-loc.jpg",
      "alt": "Buffalo harbor entrance and lighthouses, photographed between 1900 and 1915, show a later view of this Lake Erie city.",
      "caption": "Buffalo harbor entrance and lighthouses, photographed between 1900 and 1915, show a later view of this Lake Erie city.",
      "href": "https://www.loc.gov/item/2016814971/",
      "credit": "Library of Congress · Detroit Publishing Company",
      "width": 1024,
      "height": 807
    },
    "5": {
      "src": "/assets/pioneers/story/05-carts-800.webp",
      "alt": "A carpenter fits a wooden wheel to a handcart beside travelers’ bundles.",
      "href": "/pioneers.html#pioneer-story-05-carts",
      "caption": "A carpenter fits a wooden wheel to a handcart beside travelers’ bundles.",
      "inventoryRow": 10,
      "width": 800,
      "height": 533
    },
    "6": {
      "src": "/assets/pioneers/story/06-florence-800.webp",
      "alt": "Emigrant families gather for a discussion beside their handcarts in late summer.",
      "href": "/pioneers.html#pioneer-story-06-florence",
      "caption": "Emigrant families gather for a discussion beside their handcarts in late summer.",
      "inventoryRow": 11,
      "width": 800,
      "height": 533
    },
    "7": {
      "src": "/assets/timeline/elkhorn-crossing-nps.jpg",
      "alt": "The Elkhorn River beside a modern interpretive sign at the historic ferry crossing.",
      "caption": "The Elkhorn River beside a modern interpretive sign at the historic ferry crossing.",
      "href": "https://npgallery.nps.gov/AssetDetail/c8978772-bf73-4f0e-9452-ba829c8513dc",
      "credit": "National Park Service",
      "width": 789,
      "height": 525
    },
    "8": {
      "src": "/assets/timeline/genoa-ruts-nps.jpg",
      "alt": "Trail ruts near Genoa in the Loup River country, marked by a modern interpretive sign.",
      "caption": "Trail ruts near Genoa in the Loup River country, marked by a modern interpretive sign.",
      "href": "https://npgallery.nps.gov/AssetDetail/6d5632af-2ed0-4254-98de-e044b4861d1e",
      "credit": "National Park Service",
      "width": 1000,
      "height": 750
    },
    "9": {
      "src": "/assets/timeline/wood-river-loc.jpg",
      "alt": "A present-day farmstead in Wood River, Nebraska, photographed in 2021.",
      "caption": "A present-day farmstead in Wood River, Nebraska, photographed in 2021.",
      "href": "https://www.loc.gov/item/2021757717/",
      "credit": "Carol M. Highsmith; Library of Congress",
      "width": 1024,
      "height": 683
    },
    "10": {
      "src": "/assets/timeline/fort-kearny-nps.jpg",
      "alt": "A reconstructed sod-roof building and wagon display at Fort Kearny State Historical Park.",
      "caption": "A reconstructed sod-roof building and wagon display at Fort Kearny State Historical Park.",
      "href": "https://npgallery.nps.gov/AssetDetail/658de764-155d-451f-677d-0ecf872974a0",
      "credit": "National Park Service",
      "width": 1000,
      "height": 750
    },
    "11": {
      "src": "/assets/timeline/platte-confluence-nasa.jpg",
      "alt": "The North and South Platte river valleys meet near the upper right in this September 2007 astronaut photograph; modern fields trace the floodplains.",
      "caption": "The North and South Platte river valleys meet near the upper right in this September 2007 astronaut photograph; modern fields trace the floodplains.",
      "href": "https://science.nasa.gov/earth/earth-observatory/north-and-south-platte-rivers-nebraska-8105/",
      "credit": "NASA / Expedition 15 crew / ISS Crew Earth Observations",
      "width": 1000,
      "height": 663
    },
    "12": {
      "src": "/assets/timeline/ash-hollow-nps.jpg",
      "alt": "A grass-covered slope and scattered trees at Ash Hollow State Park.",
      "caption": "A grass-covered slope and scattered trees at Ash Hollow State Park.",
      "href": "https://npgallery.nps.gov/AssetDetail/d725282b-2c48-4932-b6e3-2f5afbcdf371",
      "credit": "National Park Service",
      "width": 1000,
      "height": 750
    },
    "13": {
      "src": "/assets/timeline/chimney-rock-nps.jpg",
      "alt": "Wagon teams at the foot of Chimney Rock in a 2007 National Park Service photograph.",
      "caption": "Wagon teams at the foot of Chimney Rock in a 2007 National Park Service photograph.",
      "href": "https://npgallery.nps.gov/AssetDetail/282d8078-ebb5-402d-bea7-63e7c51208a9",
      "credit": "National Park Service",
      "width": 999,
      "height": 665
    },
    "14": {
      "src": "/assets/timeline/scotts-bluff-nps.jpg",
      "alt": "A covered wagon display stands beneath the layered cliffs of Scotts Bluff National Monument.",
      "caption": "A covered wagon display stands beneath the layered cliffs of Scotts Bluff National Monument.",
      "href": "https://npgallery.nps.gov/AssetDetail/b25e0315-2213-41b1-a8fa-6867556b9382",
      "credit": "National Park Service",
      "width": 1000,
      "height": 750
    },
    "15": {
      "src": "/assets/timeline/fort-laramie-nps.jpg",
      "alt": "Historic buildings border the grass parade ground at Fort Laramie National Historic Site.",
      "caption": "Historic buildings border the grass parade ground at Fort Laramie National Historic Site.",
      "href": "https://npgallery.nps.gov/AssetDetail/87ecb685-4aa2-475d-a7ce-2fb0388ec03e",
      "credit": "National Park Service",
      "width": 1000,
      "height": 750
    },
    "16": {
      "src": "/assets/pioneers/story/16-martin-river-800.webp",
      "alt": "Martin company adults guide a handcart through cold river water.",
      "href": "/pioneers.html#pioneer-story-16-martin-river",
      "caption": "Martin company adults guide a handcart through cold river water.",
      "inventoryRow": 21,
      "width": 800,
      "height": 533
    },
    "17": {
      "src": "/assets/timeline/red-buttes-nps.jpg",
      "alt": "The North Platte River at Red Buttes Crossing and Bessemer Bend, south of Casper.",
      "caption": "The North Platte River at Red Buttes Crossing and Bessemer Bend, south of Casper.",
      "href": "https://npgallery.nps.gov/AssetDetail/a1fdf41c-aaec-4808-bb8b-c1f4878d889d",
      "credit": "National Park Service",
      "width": 1000,
      "height": 750
    },
    "18": {
      "src": "/assets/timeline/independence-rock-nps.jpg",
      "alt": "Independence Rock rises behind the entrance sign at the Wyoming historic site.",
      "caption": "Independence Rock rises behind the entrance sign at the Wyoming historic site.",
      "href": "https://npgallery.nps.gov/AssetDetail/0b9b2cdf-d2fa-473a-9723-af88f3e87801",
      "credit": "NPS/Lee Kreutzer",
      "width": 999,
      "height": 665
    },
    "19": {
      "src": "/assets/timeline/devils-gate-nps.jpg",
      "alt": "The narrow gap at Devil’s Gate cuts through the rocky ridge above the trail.",
      "caption": "The narrow gap at Devil’s Gate cuts through the rocky ridge above the trail.",
      "href": "https://npgallery.nps.gov/AssetDetail/45898a46-c844-40c1-ac05-96ec25972b19",
      "credit": "National Park Service",
      "width": 1000,
      "height": 750
    },
    "20": {
      "src": "/assets/timeline/martins-cove-nps.jpg",
      "alt": "The sheltered valley at Martin’s Cove lies beneath broad granite slopes.",
      "caption": "The sheltered valley at Martin’s Cove lies beneath broad granite slopes.",
      "href": "https://npgallery.nps.gov/AssetDetail/b5cb96c9-50aa-48c3-b357-57a3400f2e79",
      "credit": "National Park Service",
      "width": 1296,
      "height": 864
    },
    "21": {
      "src": "/assets/timeline/sixth-crossing-nps.jpg",
      "alt": "The modern Sixth Crossing welcome center at the Willie Handcart Historic Site.",
      "caption": "The modern Sixth Crossing welcome center at the Willie Handcart Historic Site.",
      "href": "https://npgallery.nps.gov/AssetDetail/07e2fc96-0a1e-4972-82ef-f70f8ced5a5d",
      "credit": "National Park Service",
      "width": 1000,
      "height": 750
    },
    "22": {
      "src": "/assets/pioneers/story/15-rocky-ridge-800.webp",
      "alt": "Weary emigrants pull a handcart up a low rocky ridge through blowing snow.",
      "href": "/pioneers.html#pioneer-story-15-rocky-ridge",
      "caption": "Weary emigrants pull a handcart up a low rocky ridge through blowing snow.",
      "inventoryRow": 20,
      "width": 800,
      "height": 533
    },
    "23": {
      "src": "/assets/timeline/south-pass-nps.jpg",
      "alt": "The open landscape at South Pass Overlook stretches toward distant mountains.",
      "caption": "The open landscape at South Pass Overlook stretches toward distant mountains.",
      "href": "https://npgallery.nps.gov/AssetDetail/eab101cb-f48c-45ad-afa8-df6d2cb9261e",
      "credit": "National Park Service",
      "width": 999,
      "height": 667
    },
    "24": {
      "src": "/assets/timeline/pacific-springs-nps.jpg",
      "alt": "The remains of the later Pacific Springs Hotel and Pony Express station stand in open country near Pacific Springs.",
      "caption": "The remains of the later Pacific Springs Hotel and Pony Express station stand in open country near Pacific Springs.",
      "href": "https://npgallery.nps.gov/AssetDetail/8f0fda00-155d-451f-67e9-7b583e965c8a",
      "credit": "National Park Service",
      "width": 1000,
      "height": 750
    },
    "25": {
      "src": "/assets/timeline/green-river-ferry-nps.jpg",
      "alt": "The Green River beside the interpretive marker for Lombard Ferry and Mormon Ferry.",
      "caption": "The Green River beside the interpretive marker for Lombard Ferry and Mormon Ferry.",
      "href": "https://npgallery.nps.gov/AssetDetail/2e585715-fe81-47cc-9ed5-4ee9b45708a6",
      "credit": "National Park Service",
      "width": 1000,
      "height": 750
    },
    "26": {
      "src": "/assets/timeline/fort-bridger-nps.jpg",
      "alt": "Whitewashed buildings and a stone marker at Fort Bridger State Historic Site.",
      "caption": "Whitewashed buildings and a stone marker at Fort Bridger State Historic Site.",
      "href": "https://npgallery.nps.gov/AssetDetail/4d283a2a-e9bb-4421-9a6b-2ef7cf15e783",
      "credit": "National Park Service",
      "width": 999,
      "height": 562
    },
    "27": {
      "src": "/assets/timeline/bear-river-crossing-beartown-nps.jpg",
      "alt": "The Bear River at the historic Beartown crossing, with bare trees and patches of snow along its modern banks.",
      "caption": "The Bear River at the historic Beartown crossing, with bare trees and patches of snow along its modern banks.",
      "href": "https://www.nps.gov/places/bear-river-crossing-beartown.htm",
      "credit": "National Park Service / L. Kreutzer",
      "width": 1600,
      "height": 900
    },
    "28": {
      "src": "/assets/timeline/the-needles-and-yellow-creek-camp-nps.jpg",
      "alt": "The jagged ridge of The Needles rises above sagebrush near the historic Yellow Creek camp in Wyoming.",
      "caption": "The jagged ridge of The Needles rises above sagebrush near the historic Yellow Creek camp in Wyoming.",
      "href": "https://www.nps.gov/places/the-needles-and-yellow-creek-camp.htm",
      "credit": "National Park Service / L. Kreutzer",
      "width": 1600,
      "height": 900
    },
    "29": {
      "src": "/assets/timeline/echo-canyon-nps.jpg",
      "alt": "Visitors pause beside red rock cliffs along the modern road through Echo Canyon.",
      "caption": "Visitors pause beside red rock cliffs along the modern road through Echo Canyon.",
      "href": "https://npgallery.nps.gov/AssetDetail/26105b91-0b5f-4073-8e99-64a10bc6e728",
      "credit": "National Park Service",
      "width": 1000,
      "height": 667
    },
    "30": {
      "src": "/assets/timeline/big-mountain-nps.jpg",
      "alt": "The winding modern road descends through wooded slopes below Big Mountain Pass.",
      "caption": "The winding modern road descends through wooded slopes below Big Mountain Pass.",
      "href": "https://npgallery.nps.gov/AssetDetail/82a6113c-9ece-418d-8402-1715a4475a38",
      "credit": "National Park Service",
      "width": 1000,
      "height": 585
    },
    "31": {
      "src": "/assets/timeline/emigration-road-nps.jpg",
      "alt": "A modern reservoir and trail marker seen from Little Mountain Summit on Emigration Canyon Road.",
      "caption": "A modern reservoir and trail marker seen from Little Mountain Summit on Emigration Canyon Road.",
      "href": "https://npgallery.nps.gov/AssetDetail/7cd060ef-fd47-4f68-91ec-f8afb44ebbfa",
      "credit": "National Park Service",
      "width": 1000,
      "height": 667
    },
    "32": {
      "src": "/assets/pioneers/story/18-welcome-800.webp",
      "alt": "Residents help weary emigrants down from a wagon and offer a blanket beside a home.",
      "href": "/pioneers.html#pioneer-story-18-welcome",
      "caption": "Residents help weary emigrants down from a wagon and offer a blanket beside a home.",
      "inventoryRow": 26,
      "width": 800,
      "height": 533
    }
  },
  "history": {
    "0": {
      "src": "/assets/history/first-vision-1400.webp",
      "href": "/church-history.html#history-first-vision-title",
      "alt": "Joseph Smith kneeling in a wooded grove as God the Father and Jesus Christ appear in heavenly light",
      "caption": "Joseph kneels among the trees as heavenly light fills the grove. His prayer began the Restoration story.",
      "artworkId": "art-52dc5f55c32e",
      "width": 1400,
      "height": 468
    },
    "1": {
      "src": "/assets/page-art/bible-together/moroni-quotes-malachi-960.webp",
      "href": "/answers/bible-and-book-of-mormon-together.html#study-moroni-quotes-malachi",
      "alt": "Seventeen-year-old Joseph Smith listens from his bed as Moroni speaks in a softly illuminated room.",
      "caption": "Seventeen-year-old Joseph listens from his bed as Moroni speaks of the work that lay ahead.",
      "artworkId": "art-e51655f6579a",
      "width": 960,
      "height": 640
    },
    "2": {
      "src": "/assets/page-art/book-of-mormon-stories/40-moroni-joseph-960.webp",
      "href": "/answers/what-is-the-book-of-mormon.html#moroni-and-joseph",
      "alt": "A youthful Joseph Smith receives a cloth-wrapped stack of plates from Moroni on a wooded hillside at night.",
      "caption": "On the wooded hillside, Joseph receives the plates from Moroni, beginning a new responsibility to protect and translate the record.",
      "artworkId": "art-61a73b7c8aa7",
      "width": 960,
      "height": 640
    },
    "3": {
      "src": "/assets/page-art/church-history/aaronic-priesthood-960.webp",
      "href": "/answers/aaronic-priesthood-restoration.html#aaronic-priesthood-restoration",
      "alt": "Joseph and Oliver kneel with bowed heads as John the Baptist places a hand on each man’s head.",
      "caption": "Joseph and Oliver kneel beneath John the Baptist’s hands as authority to baptize is restored.",
      "artworkId": "art-d98ccbf176b8",
      "width": 960,
      "height": 540
    },
    "4": {
      "src": "/assets/history/restoration-print-shop-1400.webp",
      "href": "/church-history.html",
      "alt": "Printers set type and prepare sheets, with Christ portrayed beside the press.",
      "caption": "Printers set type and prepare sheets, with Christ portrayed beside the press.",
      "artworkId": "art-6e45c602be15",
      "width": 1400,
      "height": 467
    },
    "5": {
      "src": "/assets/timeline/history/peter-whitmer-home-55a1412.jpg",
      "href": "https://www.churchofjesuschrist.org/media/image/peter-whitmer-home-55a1412?lang=eng",
      "alt": "The reconstructed Whitmer home stands among trees and a wooden fence, recalling the small household where the Church was organized.",
      "caption": "The reconstructed Whitmer home stands among trees and a wooden fence, recalling the small household where the Church was organized.",
      "credit": "The Church of Jesus Christ of Latter-day Saints, Gospel Media",
      "width": 960,
      "height": 1280
    },
    "6": {
      "src": "/assets/timeline/history/newel-whitney-store-6faf4c5-1920.jpg",
      "href": "https://www.churchofjesuschrist.org/media/image/newel-whitney-store-6faf4c5?lang=eng",
      "alt": "The white wooden Whitney store recalls the welcome Joseph and Emma found when they arrived in Kirtland, where a new community of Saints was gathering.",
      "caption": "The white wooden Whitney store recalls the welcome Joseph and Emma found when they arrived in Kirtland, where a new community of Saints was gathering.",
      "credit": "The Church of Jesus Christ of Latter-day Saints, Gospel Media",
      "width": 1920,
      "height": 1445
    },
    "7": {
      "src": "/assets/page-art/jesus-journey/rt-vision-1832-960.webp",
      "href": "/jesus-christ/restoration-and-today.html#picture-rt-vision-1832",
      "alt": "Joseph Smith and Sidney Rigdon look toward the risen Savior in a vision above their scriptural work.",
      "caption": "Joseph Smith and Sidney Rigdon look toward the risen Savior while studying the scriptures together.",
      "artworkId": "art-c7761e72c36e",
      "width": 960,
      "height": 640
    },
    "8": {
      "src": "/assets/timeline/history/newel-k-whitney-store-ac5e72d-1920.jpg",
      "href": "https://www.churchofjesuschrist.org/media/image/newel-k-whitney-store-ac5e72d?lang=eng",
      "alt": "Barrels and household goods fill the Whitney store, the building where Joseph received the Word of Wisdom in an upstairs room.",
      "caption": "Barrels and household goods fill the Whitney store, the building where Joseph received the Word of Wisdom in an upstairs room.",
      "credit": "The Church of Jesus Christ of Latter-day Saints, Gospel Media",
      "width": 1920,
      "height": 1280
    },
    "9": {
      "src": "/assets/timeline/history/independence-courthouse-square2003.jpg",
      "href": "https://www.nps.gov/media/photo/gallery-item.htm?gid=C9CDB9A0-AC19-44DA-A2FE-1AD807FC92E2&id=29931ac7-54ad-45eb-a4e9-62fb9fb7b121",
      "alt": "Independence’s courthouse square appears here in 2003, a present-day view of the community from which the Saints were driven in 1833.",
      "caption": "Independence’s courthouse square appears here in 2003, a present-day view of the community from which the Saints were driven in 1833.",
      "credit": "National Park Service",
      "width": 2048,
      "height": 1536
    },
    "10": {
      "src": "/assets/timeline/history/kirtland-temple-6aca5ae.jpg",
      "href": "https://www.churchofjesuschrist.org/media/image/kirtland-temple-6aca5ae?lang=eng",
      "alt": "The Kirtland Temple stands between green trees in a later photograph of the town where the Twelve were first organized.",
      "caption": "The Kirtland Temple stands between green trees in a later photograph of the town where the Twelve were first organized.",
      "credit": "The Church of Jesus Christ of Latter-day Saints, Gospel Media",
      "width": 1920,
      "height": 1440
    },
    "11": {
      "src": "/assets/page-art/church-history/kirtland-temple-960.webp",
      "href": "/church-history.html#kirtland-temple",
      "alt": "Worshippers approach the Kirtland Temple along a muddy path, beneath its red roof and pale blue-gray walls.",
      "caption": "Worshippers make their way toward the Kirtland Temple, a house raised through the sacrifice of the early Saints.",
      "artworkId": "art-85a07f6b9325",
      "width": 960,
      "height": 640
    },
    "12": {
      "src": "/assets/missionary/early-missionaries-liverpool-1400.webp",
      "href": "/missionary.html#early-missionaries-heading",
      "alt": "Historical portrayal of early missionaries arriving at Liverpool by sailing ship",
      "caption": "Early missionaries step ashore at Liverpool after crossing the Atlantic to share their witness in Britain.",
      "artworkId": "art-ade36c4f04b4",
      "width": 1400,
      "height": 933
    },
    "13": {
      "src": "/assets/page-art/church-history/liberty-prayer-960.webp",
      "href": "/church-history.html#liberty-jail-study",
      "alt": "Joseph sits among straw beneath a narrow barred window, looking upward in earnest prayer.",
      "caption": "Joseph looks upward in prayer beneath the narrow window at Liberty Jail, seeking comfort for a suffering people.",
      "artworkId": "art-cf16adc08ee1",
      "width": 960,
      "height": 640
    },
    "14": {
      "src": "/assets/page-art/church-history/nauvoo-temple-960.webp",
      "href": "/church-history.html#nauvoo-temple",
      "alt": "The original Nauvoo Temple rises above wooden homes near the Mississippi River, with a horizontal angel weather vane on its tower.",
      "caption": "The Nauvoo Temple rises above homes near the Mississippi, part of the city the Saints built together.",
      "artworkId": "art-de52b61d82e8",
      "width": 960,
      "height": 640
    },
    "15": {
      "src": "/assets/page-art/church-history/relief-society-torso-v3-960.webp",
      "href": "/church-history.html#relief-society-organization",
      "alt": "Emma speaks with women gathered in a simple meeting room, meeting the gaze of a seated listener.",
      "caption": "Emma speaks with the women gathered around her as the Relief Society begins its work of faith and care.",
      "artworkId": "art-82ed9c00b587",
      "width": 960,
      "height": 540
    },
    "16": {
      "src": "/assets/page-art/temples/temple-nauvoo-hope-960.webp",
      "href": "/answers/why-latter-day-saints-build-temples.html#picture-temple-nauvoo-hope",
      "alt": "An early Nauvoo family pauses with travel belongings as the temple rises behind them.",
      "caption": "A family pauses near the Nauvoo Temple with their belongings, holding to the promise of blessings that reach beyond death.",
      "artworkId": "art-9bdd8608f45c",
      "width": 960,
      "height": 640
    },
    "17": {
      "src": "/assets/timeline/history/carthage-jail.jpg",
      "href": "https://npgallery.nps.gov/AssetDetail/00e7e7cd-155d-451f-67fe-478e24602de8",
      "alt": "The stone walls of Carthage Jail preserve the place where Joseph and Hyrum’s mortal lives ended, and where their witness is remembered.",
      "caption": "The stone walls of Carthage Jail preserve the place where Joseph and Hyrum’s mortal lives ended, and where their witness is remembered.",
      "credit": "National Park Service",
      "width": 1839,
      "height": 1224
    },
    "18": {
      "src": "/assets/timeline/history/brigham-young-brady-handy.jpg",
      "href": "https://www.loc.gov/item/2017895830/",
      "alt": "Two views of Brigham Young appear on this archival portrait plate, photographed after he began leading the Saints following Joseph Smith’s death.",
      "caption": "Two views of Brigham Young appear on this archival portrait plate, photographed after he began leading the Saints following Joseph Smith’s death.",
      "credit": "Library of Congress · Brady-Handy Collection",
      "width": 1024,
      "height": 783
    },
    "19": {
      "src": "/assets/pioneers/story/01-mississippi-800.webp",
      "href": "/pioneers.html#pioneer-story-01-mississippi",
      "alt": "A family and wagon aboard a wooden ferry on the Mississippi near Nauvoo.",
      "caption": "A family and its wagon cross the Mississippi by ferry, leaving Nauvoo for an uncertain road west.",
      "artworkId": "art-1bff6987275b",
      "width": 800,
      "height": 533
    },
    "20": {
      "src": "/assets/timeline/history/mormon-battalion-monument.jpg",
      "href": "https://www.loc.gov/item/2023697767/",
      "alt": "The Mormon Battalion monument honors the volunteers whose long march became part of the Saints’ westward story.",
      "caption": "The Mormon Battalion monument honors the volunteers whose long march became part of the Saints’ westward story.",
      "credit": "Carol M. Highsmith · Library of Congress",
      "width": 1024,
      "height": 683
    },
    "21": {
      "src": "/assets/pioneers/first-view-valley-800.webp",
      "href": "/pioneers.html#pioneer-valley-heading",
      "alt": "A pioneer husband and wife overlooking the Salt Lake Valley beside their wagon and oxen",
      "caption": "A husband and wife pause beside their wagon to look across the Salt Lake Valley after the long journey west.",
      "artworkId": "art-f44b3a832404",
      "width": 800,
      "height": 450
    },
    "22": {
      "src": "/assets/timeline/history/seagull-monument-plaque.jpg",
      "href": "https://www.loc.gov/item/2023697755/",
      "alt": "A relief on the Seagull Monument remembers the struggle to save the settlers’ crops in 1848.",
      "caption": "A relief on the Seagull Monument remembers the struggle to save the settlers’ crops in 1848.",
      "credit": "Carol M. Highsmith · Library of Congress",
      "width": 904,
      "height": 1024
    },
    "23": {
      "src": "/assets/pioneers/story/13-brigham-appeal-approved-likeness-20260920-800.webp",
      "href": "/pioneers.html#pioneer-story-13-brigham-appeal",
      "alt": "Brigham Young appeals for practical help for the emigrants still on the plains.",
      "caption": "Brigham Young calls for food, clothing, and wagons to reach the emigrants still stranded on the plains.",
      "artworkId": "art-05abec60a2a3",
      "width": 800,
      "height": 533
    },
    "24": {
      "src": "/assets/timeline/history/mountain-meadows-landscape.jpg",
      "href": "https://npgallery.nps.gov/AssetDetail/a269aa71a8cd40e2bbbabc86be6c61a1",
      "alt": "Sagebrush and open ground mark Mountain Meadows in this 1964 photograph—a quiet place to remember lives lost and the weight of this history.",
      "caption": "Sagebrush and open ground mark Mountain Meadows in this 1964 photograph—a quiet place to remember lives lost and the weight of this history.",
      "credit": "Courtesy Zion National Park, Photographer Roland H. Wauer, Museum Catalog Number ZION 9098",
      "width": 1200,
      "height": 929
    },
    "25": {
      "src": "/assets/pioneers/story/19-railroad-800.webp",
      "href": "/pioneers.html#pioneer-story-19-railroad",
      "alt": "An immigrant family with trunks stands beside a nineteenth-century train in Utah.",
      "caption": "An immigrant family stands with its trunks beside a train in Utah as rail travel changes the journey west.",
      "artworkId": "art-04d53038a59e",
      "width": 800,
      "height": 533
    },
    "26": {
      "src": "/assets/page-art/temples/temple-pioneer-temples-960.webp",
      "href": "/answers/why-latter-day-saints-build-temples.html#picture-temple-pioneer-temples",
      "alt": "Craftsmen work beside timber scaffolding around the St. George Temple during its construction.",
      "caption": "Craftsmen work around the rising St. George Temple, preparing the first completed temple in Utah for worship.",
      "artworkId": "art-18e67438d8c5",
      "width": 960,
      "height": 640
    },
    "27": {
      "src": "/assets/timeline/history/aurelia-spencer-rogers-portrait-83ea2b2.jpg",
      "href": "https://www.churchofjesuschrist.org/media/image/aurelia-spencer-rogers-portrait-83ea2b2?lang=eng",
      "alt": "Aurelia Spencer Rogers appears in a painted portrait wearing a dark dress and cameo brooch, remembered for her care for children and the beginnings of Primary.",
      "caption": "Aurelia Spencer Rogers appears in a painted portrait wearing a dark dress and cameo brooch, remembered for her care for children and the beginnings of Primary.",
      "credit": "The Church of Jesus Christ of Latter-day Saints, Gospel Media",
      "width": 1018,
      "height": 1280
    },
    "28": {
      "src": "/assets/timeline/history/wilford-woodruff-a04d784.jpg",
      "href": "https://www.churchofjesuschrist.org/media/image/wilford-woodruff-a04d784?lang=eng",
      "alt": "Wilford Woodruff sits beside a table in H. E. Peterson’s portrait, the prophet who issued the 1890 Manifesto.",
      "caption": "Wilford Woodruff sits beside a table in H. E. Peterson’s portrait, the prophet who issued the 1890 Manifesto.",
      "credit": "The Church of Jesus Christ of Latter-day Saints, Gospel Media",
      "width": 984,
      "height": 1280
    },
    "29": {
      "src": "/assets/pioneers/salt-lake-temple-800.webp",
      "href": "/pioneers.html#pioneer-valley-heading",
      "alt": "Distinct nineteenth-century workers constructing the Salt Lake Temple",
      "caption": "Workers labor around the Salt Lake Temple, whose completion followed forty years of patient effort.",
      "artworkId": "art-4bee76727d47",
      "width": 800,
      "height": 450
    },
    "30": {
      "src": "/assets/timeline/history/utah-statehood-herald1896.jpg",
      "href": "https://www.loc.gov/resource/sn85058130/1896-01-05/ed-1/?sp=1",
      "alt": "The Salt Lake Herald’s January 5, 1896 front page announces Utah’s admission to statehood the preceding day.",
      "caption": "The Salt Lake Herald’s January 5, 1896 front page announces Utah’s admission to statehood the preceding day.",
      "credit": "Library of Congress; digitized by University of Utah, Marriott Library",
      "width": 792,
      "height": 1096
    },
    "31": {
      "src": "/assets/timeline/history/lorenzo-snow-cb940d3.jpg",
      "href": "https://www.churchofjesuschrist.org/media/image/lorenzo-snow-cb940d3?lang=eng",
      "alt": "Lorenzo Snow appears in a painted portrait, remembered here for his teaching on tithing.",
      "caption": "Lorenzo Snow appears in a painted portrait, remembered here for his teaching on tithing.",
      "credit": "The Church of Jesus Christ of Latter-day Saints, Gospel Media",
      "width": 1006,
      "height": 1280
    },
    "32": {
      "src": "/assets/page-art/topics/family-study-800.webp",
      "href": "/answers/why-families-are-important.html#hope-reflection",
      "alt": "A multigenerational family listening to a teenager during a shared reading",
      "caption": "A family listens to a teenager during shared reading. Time together at home remains at the heart of family home evening.",
      "artworkId": "art-88af70985f7c",
      "width": 800,
      "height": 533
    },
    "33": {
      "src": "/assets/page-art/plan-of-salvation/redemption-dead-800.webp",
      "href": "/answers/plan-of-salvation.html#picture-pos-redemption-dead",
      "alt": "Joseph F. Smith sits with an open Bible.",
      "caption": "Joseph F. Smith sits with an open Bible as he ponders the Savior’s work among the dead.",
      "artworkId": "art-5e7d2eaa1e3a",
      "width": 800,
      "height": 533
    },
    "34": {
      "src": "/assets/missionary/service-missionaries-food-pantry-1400.webp",
      "href": "/missionary.html#ways-to-serve",
      "alt": "Portrayal of young and senior service missionaries helping at a food pantry",
      "caption": "Service missionaries work together in a food pantry, continuing the practical care at the heart of Church welfare.",
      "artworkId": "art-45e710bbdf57",
      "width": 1400,
      "height": 933
    },
    "35": {
      "src": "/assets/timeline/history/george-albert-smith-cf3844a.jpg",
      "href": "https://www.churchofjesuschrist.org/media/image/george-albert-smith-cf3844a?lang=eng",
      "alt": "George Albert Smith’s painted portrait recalls the president who led the Church through its pioneer centennial and the million-member milestone.",
      "caption": "George Albert Smith’s painted portrait recalls the president who led the Church through its pioneer centennial and the million-member milestone.",
      "credit": "The Church of Jesus Christ of Latter-day Saints, Gospel Media",
      "width": 995,
      "height": 1280
    },
    "36": {
      "src": "/assets/timeline/history/david-o-mckay-11055d9.jpg",
      "href": "https://www.churchofjesuschrist.org/media/image/david-o-mckay-11055d9?lang=eng",
      "alt": "David O. McKay rests his clasped hands in Alvin Gittins’s portrait, recalling his leadership during the growth of correlation.",
      "caption": "David O. McKay rests his clasped hands in Alvin Gittins’s portrait, recalling his leadership during the growth of correlation.",
      "credit": "The Church of Jesus Christ of Latter-day Saints, Gospel Media",
      "width": 994,
      "height": 1280
    },
    "37": {
      "src": "/assets/timeline/history/joseph-fielding-smith-dc8268e.jpg",
      "href": "https://www.churchofjesuschrist.org/media/image/joseph-fielding-smith-dc8268e?lang=eng",
      "alt": "Joseph Fielding Smith sits in a leather chair in Shauna Clinger’s portrait, the Church’s president when members gathered in Manchester in 1971.",
      "caption": "Joseph Fielding Smith sits in a leather chair in Shauna Clinger’s portrait, the Church’s president when members gathered in Manchester in 1971.",
      "credit": "The Church of Jesus Christ of Latter-day Saints, Gospel Media",
      "width": 995,
      "height": 1280
    },
    "38": {
      "src": "/assets/page-art/priesthood-history/original-kimball-study.png",
      "href": "/answers/race-priesthood-and-temple-blessings.html#picture-history-kimball-study",
      "alt": "Historical artistic interpretation of President Spencer W. Kimball in quiet study.",
      "caption": "President Spencer W. Kimball studies quietly while seeking the Lord’s direction.",
      "artworkId": "art-7e4fd69ad4f8",
      "width": 1536,
      "height": 1024
    },
    "39": {
      "src": "/assets/page-art/exclusive/two-witnesses-readers-800.webp",
      "href": "/answers/bible-and-book-of-mormon-together.html#guided-practice",
      "alt": "An older woman and an adult man discussing their open scripture books on a park bench",
      "caption": "Two readers compare open scripture volumes on a park bench, continuing the connected study encouraged by the Church’s scripture editions.",
      "artworkId": "art-e827a6264f85",
      "width": 800,
      "height": 533
    },
    "40": {
      "src": "/assets/heroes/topics/families-full.webp",
      "href": "/answers/why-families-are-important.html#nested-page-title",
      "alt": "A grandmother, father, and young daughter knead bread together in a home kitchen.",
      "caption": "A grandmother, father, and young daughter work bread dough together, sharing the daily care of family life.",
      "artworkId": "art-3334c3fb6909",
      "width": 2172,
      "height": 724
    },
    "41": {
      "src": "/assets/missionary/light-across-world.webp",
      "href": "/missionary.html#worldwide-heading",
      "alt": "Symbolic artwork of missionary companionships serving communities across a world map",
      "caption": "Missionary companionships serve communities across a world map as the gospel reaches people in many nations.",
      "artworkId": "art-14bef8b3622b",
      "width": 2172,
      "height": 724
    },
    "42": {
      "src": "/art/thumbs/The-Living-Christ.webp",
      "href": "/art.html#art-gallery",
      "alt": "The Living Christ",
      "caption": "The Savior’s portrait accompanies the Apostles’ witness that He lives.",
      "artworkId": "art-d12945c2d847",
      "width": 640,
      "height": 338
    },
    "43": {
      "src": "/assets/timeline/history/gordon-b-hinckley-f26378f.jpg",
      "href": "https://www.churchofjesuschrist.org/media/image/gordon-b-hinckley-f26378f?lang=eng",
      "alt": "Gordon B. Hinckley smiles in his official portrait, remembered here for opening new opportunities through the Perpetual Education Fund.",
      "caption": "Gordon B. Hinckley smiles in his official portrait, remembered here for opening new opportunities through the Perpetual Education Fund.",
      "credit": "The Church of Jesus Christ of Latter-day Saints, Gospel Media",
      "width": 1025,
      "height": 1280
    },
    "44": {
      "src": "/assets/missionary/sister-missionaries-teaching-1400.webp",
      "href": "/missionary.html#ways-to-serve",
      "alt": "Portrayal of sister missionaries listening to and teaching a family",
      "caption": "Sister missionaries listen and teach together as they share the gospel with a family.",
      "artworkId": "art-59ac2f38de36",
      "width": 1400,
      "height": 933
    },
    "45": {
      "src": "/assets/page-art/uniqueness-repairs/cfm-family-resources-960.webp",
      "href": "/come-follow-me.html#cfm-family-resources",
      "alt": "A woman and a teenager preparing a basket of home study supplies",
      "caption": "A woman and a teenager gather supplies for scripture study at home, part of the renewed emphasis on learning together.",
      "artworkId": "art-4001c2d17e20",
      "width": 960,
      "height": 640
    },
    "46": {
      "src": "/assets/timeline/history/pd80007757-000-coverart-png-991a641.jpg",
      "href": "https://www.churchofjesuschrist.org/media/image/pd80007757-000-coverart-png-991a641?lang=eng",
      "alt": "The Restoration proclamation sets the Church’s bicentennial testimony on a single page, inviting renewed faith in Jesus Christ.",
      "caption": "The Restoration proclamation sets the Church’s bicentennial testimony on a single page, inviting renewed faith in Jesus Christ.",
      "credit": "The Church of Jesus Christ of Latter-day Saints, Gospel Media",
      "width": 989,
      "height": 1280
    },
    "47": {
      "src": "/assets/page-art/priesthood-history/original-ghana-study.png",
      "href": "/answers/race-priesthood-and-temple-blessings.html#picture-history-ghana-study",
      "alt": "Symbolic illustration of Ghanaian adults studying together.",
      "caption": "Adults in Ghana gather around their scriptures, one local expression of a growing worldwide Church.",
      "artworkId": "art-5032dd394b0d",
      "width": 1536,
      "height": 1024
    },
    "48": {
      "src": "/assets/page-art/temples/temple-worldwide-gathering-960.webp",
      "href": "/answers/why-latter-day-saints-build-temples.html#picture-temple-worldwide-gathering",
      "alt": "The Laie Hawaii Temple stands among palms and tropical greenery with visitors on its grounds.",
      "caption": "Visitors walk among palms on the grounds of the Laie Hawaii Temple, one of the houses of the Lord serving Saints around the world.",
      "artworkId": "art-2d33f4194e1f",
      "width": 960,
      "height": 640
    },
    "49": {
      "src": "/assets/timeline/history/dallin-oaks-official-portrait-2018-56caf7d.jpg",
      "href": "https://www.churchofjesuschrist.org/media/image/dallin-oaks-official-portrait-2018-56caf7d?lang=eng",
      "alt": "Dallin H. Oaks appears in his official 2018 portrait, several years before the succession remembered in this entry.",
      "caption": "Dallin H. Oaks appears in his official 2018 portrait, several years before the succession remembered in this entry.",
      "credit": "The Church of Jesus Christ of Latter-day Saints, Gospel Media",
      "width": 1024,
      "height": 1280
    },
    "50": {
      "src": "/assets/page-art/priesthood-history/original-welcome.png",
      "href": "/answers/race-priesthood-and-temple-blessings.html#picture-history-welcome",
      "alt": "People greeting one another warmly in a shared gathering.",
      "caption": "People welcome one another at a shared gathering, where belonging begins with personal kindness.",
      "artworkId": "art-bb9906af80ff",
      "width": 1536,
      "height": 1024
    }
  }
};
var route=location.pathname,kind=route.indexOf('life-of-christ')>=0?'life':route.indexOf('willie-and-martin')>=0?'handcart':route.indexOf('latter-day-saint')>=0?'history':null;
if(!kind)return;
function clear(){document.querySelectorAll('[data-timeline-image]').forEach(function(el){el.remove();});}
function render(index){
 if(kind!=='history')clear();var entry=registry[kind][index];if(!entry)return;
 var container=kind==='history'?document.querySelector('#history-event-'+index+' .detail'):document.querySelector('[data-timeline-pane="detail"]');if(!container)return;
 container.querySelectorAll('[data-timeline-image]').forEach(function(el){el.remove();});
 var figure=document.createElement('figure');figure.className='timeline-waypoint-image';figure.dataset.timelineImage=String(index);
 var link=document.createElement('a');link.href=entry.href;link.setAttribute('aria-label','Explore the related image and story');
 if(/^https:/.test(entry.href)){link.target='_blank';link.rel='noopener noreferrer';}
 var img=document.createElement('img');img.src=entry.src;img.alt=entry.alt;img.loading='lazy';img.decoding='async';if(entry.width&&entry.height){img.width=entry.width;img.height=entry.height;}if(entry.frame)link.dataset.imageFrame=entry.frame;link.appendChild(img);figure.appendChild(link);
 var caption=document.createElement('figcaption');caption.textContent=entry.caption;figure.appendChild(caption);
 var source=document.createElement('a');source.href=entry.href;source.textContent=entry.credit?'Image and collection record':'Explore the related story';
 if(entry.credit){source.target='_blank';source.rel='noopener noreferrer';source.title=entry.credit;var credit=document.createElement('span');credit.className='timeline-image-credit';credit.textContent=' '+entry.credit+'.';caption.appendChild(credit);}caption.appendChild(document.createTextNode(' '));caption.appendChild(source);
 container.appendChild(figure);
}
window.addEventListener('timeline:select',function(e){if(e.detail&&Number.isInteger(e.detail.index))render(e.detail.index);});
window.addEventListener('timeline:filter',clear);
window.TimelineImages={registry:registry,render:render,clear:clear};
if(kind==='history'){if(window.HistoryTimeline&&Number.isInteger(window.HistoryTimeline.selectedIndex))render(window.HistoryTimeline.selectedIndex);}
else render(kind==='handcart'&&window.HandcartTimeline?window.HandcartTimeline.current||0:kind==='life'&&window.LifeTimeline?window.LifeTimeline.current||0:0);
})();
