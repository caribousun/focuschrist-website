// Human-reviewed source scope, verified against the full official articles on 2026-09-09.
// These notes describe evidence boundaries; they are neither quotations nor new sources.
const contexts = Object.freeze({
  'www.churchofjesuschrist.org/study/history/topics/handcart-companies': 'The rescue totals in this article concern all four named groups: the Willie and Martin handcart companies and the Hunt and Hodgetts wagon companies. Do not attribute the combined death or rescue totals to just the two handcart companies.',
  'rsc.byu.edu/fire-ice/immigration-utah-early-settlement-spanish-fork': 'The author identifies the claim that Danish settlers preceded Icelanders as an unsubstantiated tradition. Footnote 2 reports that membership records provide no evidence of Latter-day Saint Scandinavians in Spanish Fork before the Icelanders. Absence of evidence is not proof that no such individual existed. Preserve the distinction between a tradition being discussed and the author\'s historical assessment; do not present the tradition as established fact.',
  'www.churchofjesuschrist.org/study/manual/primary-5/lesson-39': 'This lesson reports more than six hundred deaths at Winter Quarters. It does not establish that this total includes neighboring settlements or unrecorded burials. Do not add those qualifications as facts supported by this lesson; they require separate evidence.',
  'rsc.byu.edu/john-lyon-life-pioneer-poet/our-ain-mountain-hame-1853': 'The overland daily routine, evening camp chores and Bear River stop in this account concern the Gates company in 1853 and the Lyon family. These details are company-specific examples, not a universal routine for every emigrant company. The earlier river-steamer fuel and water arrangements describe another transportation setting.',
  'rsc.byu.edu/their-footsteps/victorian-england': 'The passage about river water supplies and Saturday restocking for Sabbath observance describes the Wood company, which reached the Great Basin in October 1852. Do not merge that company with the Gates company in 1853 or present the combined details as one company narrative.',
  'rsc.byu.edu/journey-west/introduction': 'The company itinerary uses different date precision: Chimney Rock on 28 May, Fort Laramie by 2 June, and Independence Rock by 21 June. Preserve the word by for the latter two milestones. This overview does not give an exact individual arrival date or quote William Clayton recording arrival on 21 June.',
  'www.churchofjesuschrist.org/study/ensign/1972/07/a-melting-pot-of-pioneer-recipes': 'This article combines travel memories with settled household foodways. Bread is explicitly mixed during wagon travel and baked at a campfire; bacon and sourdough pancakes are explicitly cooked at campfires. Preserves in barrels and produce dried for winter are not explicitly identified as wagon provisions. Near-house berry bushes describe settlement. First-winter shortage foods and later improved household supplies must not be silently presented as wagon packing provisions.',
  'www.churchofjesuschrist.org/study/manual/church-history-in-the-fulness-of-times/chapter-twenty-eight': 'The migration paragraph explicitly describes the 1855 change from New Orleans and river transport to eastern ports and western railheads, followed by an overland journey to Utah. This is an account of that period, not evidence that rail never replaced the overland journey. A comparison across the whole migration era needs later railroad evidence as well.',
});
function reviewedSourceContext(url) {
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== 'https:' || !['www.churchofjesuschrist.org', 'rsc.byu.edu'].includes(parsed.hostname) || parsed.port || parsed.username || parsed.password) return '';
    const note = contexts[parsed.hostname + parsed.pathname.replace(/\/$/, '')];
    return note ? 'REVIEWED SOURCE CONTEXT (editorial scope note, not a source quotation or additional source): ' + note : '';
  } catch { return ''; }
}
export { reviewedSourceContext };
