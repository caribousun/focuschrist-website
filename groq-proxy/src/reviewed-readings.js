import registry from './reviewed-readings.json' with {type:'json'};
export const REVIEWED_SOURCE_EXTRACTION_VERSION = 'visible-paragraph-scope-v1';
export async function sha256Text(value) {
  const bytes = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(value));
  return Array.from(new Uint8Array(bytes), byte=>byte.toString(16).padStart(2,'0')).join('');
}
export async function fingerprintReviewedParagraphs(url, paragraphs) {
  const normalized = paragraphs.map(paragraph=>String(paragraph).normalize('NFC').replace(/\s+/g,' ').trim());
  return {sourceUrl:url, sourceSha256:await sha256Text(REVIEWED_SOURCE_EXTRACTION_VERSION+'\n'+url+'\n'+normalized.join('\n')),
    extractionVersion:REVIEWED_SOURCE_EXTRACTION_VERSION, paragraphs:normalized};
}
// Only server-owned entries and actually retrieved source fingerprints can
// authorize publication. The optional registry argument is for offline tests.
export async function verifyReviewedReading(key, evidence, expectedUrls, entries=registry) {
  if (entries?.schemaVersion!==1 || !Object.hasOwn(entries.readings || {},key)) return null;
  const entry=entries.readings[key];
  if (!entry || typeof entry.answer!=='string' || !entry.answer.trim() || entry.answer.length>6000
    || typeof entry.reviewRevision!=='string' || !entry.reviewRevision.trim()
    || !/^[a-f0-9]{64}$/.test(entry.answerSha256 || '') || !Array.isArray(entry.sources)
    || entry.sources.length!==expectedUrls.length || new Set(expectedUrls).size!==expectedUrls.length
    || new Set(entry.sources.map(source=>source.url)).size!==entry.sources.length
    || await sha256Text(entry.answer)!==entry.answerSha256) return null;
  const indexes=[];
  for(const approved of entry.sources){
    if(!expectedUrls.includes(approved.url) || approved.extractionVersion!==REVIEWED_SOURCE_EXTRACTION_VERSION
      || !/^[a-f0-9]{64}$/.test(approved.sourceSha256 || '')) return null;
    const index=evidence.findIndex(source=>source.url===approved.url
      && source.sourceSha256===approved.sourceSha256
      && source.sourceExtractionVersion===approved.extractionVersion);
    if(index<0)return null;
    indexes.push(index+1);
  }
  return {recoveryId:'reviewed-reading-'+key,answer:entry.answer,sourceIndexes:indexes,reviewRevision:entry.reviewRevision};
}
