/* Run in a rendered topic page after fonts and images settle.
 * Checks actual geometry, not stylesheet text. Returns actionable measurements.
 */
(() => {
  const main = document.querySelector('body.fc-topic-page main');
  if (!main) throw new Error('A rendered topic study page is required');
  const failures = [], measurements = [];
  const sections = Array.from(main.children).filter(node => node.tagName === 'SECTION');
  for (const section of sections) {
    const next = section.nextElementSibling;
    if (!next || next.tagName !== 'SECTION' || !section.lastElementChild || !next.firstElementChild) continue;
    const previousStyle = getComputedStyle(section), nextStyle = getComputedStyle(next);
    const edgeGap = next.getBoundingClientRect().top - section.getBoundingClientRect().bottom;
    const visibleGap = next.firstElementChild.getBoundingClientRect().top - section.lastElementChild.getBoundingClientRect().bottom;
    const inset = parseFloat(previousStyle.paddingBottom) + parseFloat(nextStyle.paddingTop);
    const allowed = 48 + inset;
    measurements.push({from: section.id, to: next.id, edgeGap, visibleGap, allowed});
    if (edgeGap < -1 || edgeGap > 49 || visibleGap > allowed + 2) failures.push({from: section.id, to: next.id, edgeGap, visibleGap, allowed});
  }
  const opening = document.querySelector('.fc-topic-opening');
  const openingBottom = opening && opening.getBoundingClientRect().bottom + scrollY;
  if (innerHeight >= 600 && openingBottom !== null && Math.abs(openingBottom - innerHeight) > 2) failures.push({openingBottom, viewportHeight: innerHeight});
  if (document.documentElement.scrollWidth > innerWidth + 1) failures.push({horizontalOverflow: document.documentElement.scrollWidth - innerWidth});
  return {page: location.pathname, viewport: [innerWidth,innerHeight], pass: failures.length === 0, failures, measurements};
})();
