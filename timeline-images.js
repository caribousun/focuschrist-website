/* Existing approved artwork references; original identity pixels remain unchanged. */
(function(){
"use strict";
var registry={
  "life": {
    "0": {
      "src": "/assets/page-art/birth-of-christ/08-annunciation-800.webp",
      "alt": "Mary listens to Gabriel in a modest room.",
      "href": "/birth-of-christ.html#mary-and-elisabeth",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 145
    },
    "1": {
      "src": "/assets/page-art/birth-of-christ/09-mary-elisabeth-800.webp",
      "alt": "Mary and Elisabeth greet one another, holding each other’s arms.",
      "href": "/birth-of-christ.html#mary-and-elisabeth",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 146
    },
    "2": {
      "src": "/assets/page-art/birth-of-christ/14-shepherds-find-800.webp",
      "alt": "Shepherds enter and find Mary, Joseph, and the infant lying in a manger.",
      "href": "/birth-of-christ.html#savior-born",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 151
    },
    "3": {
      "src": "/assets/page-art/birth-of-christ/15-simeon-800.webp",
      "alt": "Simeon holds the infant Jesus and speaks with Mary as Joseph listens.",
      "href": "/birth-of-christ.html#temple-witnesses",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 154
    },
    "4": {
      "src": "/assets/page-art/birth-of-christ/18-egypt-800.webp",
      "alt": "Joseph and Mary travel at night while Mary carries the child close to her.",
      "href": "/birth-of-christ.html#wise-men-and-egypt",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 158
    },
    "5": {
      "src": "/assets/page-art/birth-of-christ/23-nazareth-return-800.webp",
      "alt": "Joseph carries the young Jesus beside Mary at a village doorway.",
      "href": "/birth-of-christ.html#wise-men-and-egypt",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 159
    },
    "9": {
      "src": "/assets/page-art/jesus-journey/mm-cana-jars-960.webp",
      "alt": "Jesus watches a servant pour water from a clay pitcher into one of six large stone jars.",
      "href": "/jesus-christ/mortal-ministry.html#cana",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 82
    },
    "12": {
      "src": "/assets/page-art/jesus-journey/mc-peters-mother-in-law-960.webp",
      "alt": "Jesus takes an older woman by the hand and helps her rise from bedding as they look toward one another.",
      "href": "/jesus-christ/miracles-and-compassion.html#home",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 69
    },
    "16": {
      "src": "/assets/page-art/jesus-journey/mm-transfiguration-960.webp",
      "alt": "Jesus touches Peter's shoulder as Peter, James and John look up from the rocky mountainside.",
      "href": "/jesus-christ/mortal-ministry.html#transfiguration",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 88
    },
    "19": {
      "src": "/assets/page-art/jesus-journey/mm-jerusalem-tears-960.webp",
      "alt": "Jesus looks toward Jerusalem with tearful eyes while a disciple stands quietly behind Him.",
      "href": "/jesus-christ/mortal-ministry.html#jerusalem",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 89
    },
    "21": {
      "src": "/assets/page-art/jesus-journey/rr-judas-morsel-960.webp",
      "alt": "Jesus extends a dipped morsel toward Judas while two disciples watch from behind.",
      "href": "/jesus-christ/redeemer-and-risen-lord.html#sacrament",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 91
    },
    "22": {
      "src": "/assets/page-art/jesus-journey/rr-sleeping-disciples-960.webp",
      "alt": "Jesus speaks earnestly to Peter beneath olive trees while James and John sleep behind them.",
      "href": "/jesus-christ/redeemer-and-risen-lord.html#gethsemane",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 92
    },
    "23": {
      "src": "/assets/page-art/jesus-journey/rr-before-pilate-960.webp",
      "alt": "Jesus inclines His head toward Pilate, who questions Him from his seat.",
      "href": "/jesus-christ/redeemer-and-risen-lord.html#pilate",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 93
    },
    "24": {
      "src": "/assets/page-art/jesus-journey/rr-linen-burial-960.webp",
      "alt": "Joseph of Arimathea and Nicodemus draw linen over Jesus's body inside a stone tomb.",
      "href": "/jesus-christ/redeemer-and-risen-lord.html#burial",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 95
    },
    "26": {
      "src": "/assets/page-art/jesus-journey/rr-broiled-fish--199ddf7a530d-thumb.webp",
      "alt": "The risen Jesus turns toward a disciple while holding a piece of fish, with another disciple watching beside him.",
      "href": "/jesus-christ/redeemer-and-risen-lord.html#risen-witness",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 96
    },
    "28": {
      "src": "/assets/page-art/jesus-journey/rr-cloud-receives-960.webp",
      "alt": "Jesus rises above an olive-covered hillside, looking tenderly down toward the disciples watching Him.",
      "href": "/jesus-christ/redeemer-and-risen-lord.html#ascension",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 97
    },
    "29": {
      "src": "/assets/page-art/jesus-journey/bn-hear-the-voice-960.webp",
      "alt": "People gathered near the temple lift their faces toward the sky.",
      "href": "/jesus-christ/risen-savior-in-the-book-of-mormon.html#voice",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 107
    },
    "30": {
      "src": "/assets/page-art/jesus-journey/bn-scriptures-explained-960.webp",
      "alt": "Jesus speaks with seated listeners while an older man holds a bound set of metal plates.",
      "href": "/jesus-christ/risen-savior-in-the-book-of-mormon.html#scriptures",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 114
    }
  },
  "handcart": {
    "0": {
      "src": "/assets/pioneers/story/04-atlantic-800.webp",
      "alt": "British emigrant families stand on the deck of a nineteenth-century sailing ship.",
      "href": "/pioneers.html#pioneer-story-04-atlantic",
      "caption": "Artistic interpretation of British emigrants aboard a sailing ship; context for departure from Liverpool.",
      "inventoryRow": 9
    },
    "5": {
      "src": "/assets/pioneers/story/05-carts-800.webp",
      "alt": "A carpenter fits a wooden wheel to a handcart beside travelers’ bundles.",
      "href": "/pioneers.html#pioneer-story-05-carts",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 10
    },
    "6": {
      "src": "/assets/pioneers/story/06-florence-800.webp",
      "alt": "Emigrant families gather for a discussion beside their handcarts in late summer.",
      "href": "/pioneers.html#pioneer-story-06-florence",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 11
    },
    "16": {
      "src": "/assets/pioneers/story/16-martin-river-800.webp",
      "alt": "Martin company adults guide a handcart through cold river water.",
      "href": "/pioneers.html#pioneer-story-16-martin-river",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 21
    },
    "22": {
      "src": "/assets/pioneers/story/15-rocky-ridge-800.webp",
      "alt": "Weary emigrants pull a handcart up a low rocky ridge through blowing snow.",
      "href": "/pioneers.html#pioneer-story-15-rocky-ridge",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 20
    },
    "32": {
      "src": "/assets/pioneers/story/18-welcome-800.webp",
      "alt": "Residents help weary emigrants down from a wagon and offer a blanket beside a home.",
      "href": "/pioneers.html#pioneer-story-18-welcome",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 26
    },
    "1": {
      "src": "/assets/timeline/new-york-harbor-staten-island-1855.jpg",
      "alt": "A nineteenth-century painting of sailing ships and steam vessels in the harbor, viewed from a wooded Staten Island shore.",
      "href": "https://www.metmuseum.org/art/collection/search/14836",
      "caption": "View from Staten Island, ca. 1855. Public domain, The Metropolitan Museum of Art. Contemporary harbor context; not a depiction of the handcart companies or their arrival.",
      "credit": "The Edward W. C. Arnold Collection of New York Prints, Maps, and Pictures, Bequest of Edward W. C. Arnold, 1954"
    }
  },
  "history": {
    "0": {
      "src": "/assets/history/first-vision-1400.webp",
      "alt": "Joseph Smith kneeling in a wooded grove as God the Father and Jesus Christ appear in heavenly light",
      "href": "/church-history.html#history-first-vision-title",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 34
    },
    "11": {
      "src": "/assets/page-art/church-history/kirtland-temple-960.webp",
      "alt": "Worshippers approach the Kirtland Temple along a muddy path, beneath its red roof and pale blue-gray walls.",
      "href": "/church-history.html#kirtland-temple",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 39
    },
    "13": {
      "src": "/assets/page-art/church-history/liberty-prayer-960.webp",
      "alt": "Joseph sits among straw beneath a narrow barred window, looking upward in earnest prayer.",
      "href": "/church-history.html#liberty-jail-study",
      "caption": "Artistic interpretation of prayer at Liberty Jail, one part of the broader Missouri persecution described in this event.",
      "inventoryRow": 45
    },
    "15": {
      "src": "/assets/page-art/church-history/relief-society-960.webp",
      "alt": "Emma speaks with women gathered in a simple meeting room, meeting the gaze of a seated listener.",
      "href": "/church-history.html#relief-society-organization",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 48
    },
    "19": {
      "src": "/assets/pioneers/story/01-mississippi-800.webp",
      "alt": "A family and wagon aboard a wooden ferry on the Mississippi near Nauvoo.",
      "href": "/pioneers.html#pioneer-story-01-mississippi",
      "caption": "Artistic interpretation of crossing the Mississippi during the departure from Nauvoo.",
      "inventoryRow": 3
    },
    "21": {
      "src": "/assets/pioneers/first-view-valley-800.webp",
      "alt": "A pioneer husband and wife overlooking the Salt Lake Valley beside their wagon and oxen",
      "href": "/pioneers.html#pioneer-valley-heading",
      "caption": "Existing focusChrist artistic interpretation.",
      "inventoryRow": 23
    },
    "23": {
      "src": "/assets/pioneers/story/13-brigham-appeal-approved-likeness-20260920-800.webp",
      "alt": "Brigham Young appeals for practical help for the emigrants still on the plains.",
      "href": "/pioneers.html#pioneer-story-13-brigham-appeal",
      "caption": "Artistic interpretation of Brigham Young’s call to rescue the emigrants still on the plains.",
      "inventoryRow": 18
    },
    "25": {
      "src": "/assets/pioneers/story/19-railroad-800.webp",
      "alt": "An immigrant family with trunks stands beside a nineteenth-century train in Utah.",
      "href": "/pioneers.html#pioneer-story-19-railroad",
      "caption": "Artistic interpretation of an immigrant family traveling by rail. This provides railroad-era context, not a depiction of the golden-spike ceremony.",
      "inventoryRow": 28
    }
  }
};
var route=location.pathname,kind=route.indexOf('life-of-christ')>=0?'life':route.indexOf('willie-and-martin')>=0?'handcart':route.indexOf('latter-day-saint')>=0?'history':null;
if(!kind)return;
function clear(){document.querySelectorAll('[data-timeline-image]').forEach(function(el){el.remove();});}
function render(index){
 clear();var entry=registry[kind][index];if(!entry)return;
 var container=kind==='history'?document.querySelector('#history-event-'+index+' .detail'):document.querySelector('[data-timeline-pane="detail"]');if(!container)return;
 var figure=document.createElement('figure');figure.className='timeline-waypoint-image';figure.dataset.timelineImage=String(index);
 var link=document.createElement('a');link.href=entry.href;link.setAttribute('aria-label','Explore the related image and story');
 if(/^https:/.test(entry.href)){link.target='_blank';link.rel='noopener noreferrer';}
 var img=document.createElement('img');img.src=entry.src;img.alt=entry.alt;img.loading='lazy';img.decoding='async';link.appendChild(img);figure.appendChild(link);
 var caption=document.createElement('figcaption');caption.textContent=entry.caption;figure.appendChild(caption);
 var source=document.createElement('a');source.href=entry.href;source.textContent=entry.credit?'Image and collection record':'Explore the related story';
 if(entry.credit){source.target='_blank';source.rel='noopener noreferrer';source.title=entry.credit;}caption.appendChild(document.createTextNode(' '));caption.appendChild(source);
 container.appendChild(figure);
}
window.addEventListener('timeline:select',function(e){if(e.detail&&Number.isInteger(e.detail.index))render(e.detail.index);});
window.addEventListener('timeline:filter',clear);
window.TimelineImages={registry:registry,render:render,clear:clear};
if(kind!=='history')render(kind==='handcart'&&window.HandcartTimeline?window.HandcartTimeline.current||0:0);
})();
