// Server-owned source routes for the 29 visible Pioneer timeline controls.
// IDs select reviewed official sources, never a client-supplied URL or evidence.
const history = slug => `https://www.churchofjesuschrist.org/study/history/topics/${slug}?lang=eng`;
const manual = number => `https://www.churchofjesuschrist.org/study/manual/church-history-in-the-fulness-of-times/chapter-${number}?lang=eng`;
const route = (subject, url) => Object.freeze({ subject, url });
const PIONEER_TOPIC_SOURCES = Object.freeze({
  exodus: route('Departure from Nauvoo in 1846: reasons, preparations, and the westward exodus', history('departure-from-nauvoo')),
  winterquarters: route('Winter Quarters: its purpose, living conditions, and preparations for migration', history('winter-quarters')),
  valley: route('Salt Lake Valley: arrival of the 1847 pioneer company and early settlement', history('salt-lake-valley')),
  pioneerday: route('Pioneer Day: remembering the July 1847 arrival in the Salt Lake Valley', 'https://newsroom.churchofjesuschrist.org/article/mormons-celebrate-their-pioneer-heritage'),
  templesquare: route('Temple Square development: the temple, Tabernacle, and surrounding Church headquarters', history('church-headquarters')),
  templestart: route('Salt Lake Temple construction from 1853 to 1893', history('salt-lake-temple')),
  handcart: route('Handcart companies: why handcarts were used and the experience of the companies', history('handcart-companies')),
  railroad: route('The transcontinental railroad and the end of organized overland pioneer migration', history('railroad')),
  statehood: route('Utah statehood: the transition from territory to state in 1896', history('utah')),
  nauvoo: route('Nauvoo: the departure of the Latter-day Saints in 1846', history('departure-from-nauvoo')),
  'garden-grove': route('Garden Grove in Iowa: the 1846 way station and help for following companies', manual('twenty-five')),
  'council-bluffs': route('Missouri River settlements: Winter Quarters, Council Bluffs, and migration preparations', history('winter-quarters')),
  'chimney-rock': route('Chimney Rock as a landmark on the 1847 pioneer company route', manual('twenty-six')),
  'fort-laramie': route('Fort Laramie as a landmark on the 1847 pioneer company route', manual('twenty-six')),
  'independence-rock': route('Independence Rock on the 1847 pioneer company route', manual('twenty-six')),
  sweetwater: route('Sweetwater River on the 1847 pioneer company route', manual('twenty-six')),
  'south-pass': route('South Pass and the Continental Divide on the 1847 pioneer company route', manual('twenty-six')),
  'fort-bridger': route('Fort Bridger and the final mountain approach of the 1847 pioneer company', manual('twenty-six')),
  'echo-canyon': route('Echo Canyon during the final weeks of the 1847 pioneer company journey', 'https://newsroom.churchofjesuschrist.org/article/how-brigham-young-first-arrived-in-the-salt-lake-valley'),
  canyon: route('Emigration Canyon and the final descent into the Salt Lake Valley in 1847', manual('twenty-six')),
  'salt-lake-valley': route('Salt Lake Valley: the 1847 arrival and the work of building a settlement', history('salt-lake-valley')),
  'mountain-meadow': route('Mountain Meadows Massacre: what happened in 1857 and historical responsibility', history('mountain-meadows-massacre')),
  'willie-july': route('Willie and Martin handcart companies: late departure in 1856 and its consequences', manual('twenty-eight')),
  'willie-august': route('Willie and Martin handcart companies: hardships and the onset of severe autumn weather in 1856', manual('twenty-eight')),
  'willie-september': route('Willie and Martin handcart companies: being stranded in Wyoming during October 1856', manual('twenty-eight')),
  'willie-october': route('The rescue of the Willie and Martin handcart companies in 1856', manual('twenty-eight')),
  'martin-september': route('Martins Cove: shelter and suffering of the Martin handcart company in November 1856', 'https://www.churchofjesuschrist.org/study/ensign/2006/12/go-and-bring-them-in?lang=eng'),
  'willie-november': route('Willie and Martin handcart companies: arrival in Salt Lake City and care for survivors', manual('twenty-eight')),
  'martin-november': route('Willie and Martin handcart companies: faith, rescue, and historical legacy', history('handcart-companies')),
});
const PIONEER_FOCAL_PHRASES = Object.freeze({
  'garden-grove': ['garden grove'], 'chimney-rock': ['chimney rock'],
  'fort-laramie': ['fort laramie'], 'independence-rock': ['independence rock'],
  sweetwater: ['sweetwater'], 'south-pass': ['south pass'], 'fort-bridger': ['fort bridger'],
  'echo-canyon': ['echo canyon'], canyon: ['emigration canyon'],
  'willie-july': ['willie', 'martin'],
  'willie-august': ['willie', 'martin'],
  'willie-september': ['willie', 'martin'],
  'willie-october': ['willie', 'martin'],
  'willie-november': ['willie', 'martin'],
  'martin-september': ['cove', 'martin'],
});
const PIONEER_SOURCE_URLS = new Set(Object.values(PIONEER_TOPIC_SOURCES).map(topic => topic.url));
function pioneerTopic(key, page) {
  return page === 'pioneers' && typeof key === 'string' && Object.hasOwn(PIONEER_TOPIC_SOURCES, key)
    ? PIONEER_TOPIC_SOURCES[key] : null;
}
export { PIONEER_TOPIC_SOURCES, PIONEER_FOCAL_PHRASES, PIONEER_SOURCE_URLS, pioneerTopic };
