"""Reject the actual appended/text-only regression and cadence workarounds."""
import unittest
from bs4 import BeautifulSoup
from joseph_research_acceptance import ROUTE, check_entry_and_brevity, check_reading_cadence, check_original_manifest, check_reference_scope, check_exact_review, check_evidence_inventory, check_feature_studies

def soup(markup): return BeautifulSoup(markup,'html.parser')

class AcceptanceTests(unittest.TestCase):
    def test_frozen_pdf_source_allows_only_exact_browser_cache_change(self):
        from pathlib import Path
        import json
        from joseph_research_acceptance import check_pdf_source_binding
        site = Path(__file__).resolve().parents[1]
        source = (site/ROUTE).read_bytes()
        reviewed_hash = json.loads((site/'docs/joseph-research-pdf-review.json').read_text())['source_html_sha256']
        check_pdf_source_binding(source, reviewed_hash)
        for changed in (source+b' ', source+b'<link rel="stylesheet" href="site-system.css?v=20261004-source-control-rows-2">', source.replace(b'20261004-source-control-rows-2', b'unknown-version'), source.replace(b'<body', b'<body data-unreviewed="true"', 1), source.replace(b'site-system.css?', b'other.css?', 1)):
            with self.assertRaises(AssertionError):
                check_pdf_source_binding(changed, reviewed_hash)

    def test_sitewide_disclosure_guard_preserves_source_geography_and_footer(self):
        from joseph_research_acceptance import check_no_repeated_artwork_disclosure, ARTWORK_FOOTER_DISCLOSURE
        check_no_repeated_artwork_disclosure('Pin positions mark named places; some crossings use the nearest modern town. The date of Moyle’s injury and details of his prosthetic remain uncertain. A contemporary letterbook copy survives. '+ARTWORK_FOOTER_DISCLOSURE)
        with self.assertRaises(AssertionError):check_no_repeated_artwork_disclosure('The exact home and arrangement are imagined.')
    def test_caption_status_guard_does_not_ban_research_findings(self):
        from joseph_research_acceptance import check_artwork_badges_and_footer, ARTWORK_FOOTER_DISCLOSURE
        markup='<p>His care is documented. A contemporary letterbook copy survives.</p><figure><figcaption>Joseph stays beside Emma.</figcaption></figure><footer><p data-focuschrist-artwork-disclosure="footer">'+ARTWORK_FOOTER_DISCLOSURE+'</p></footer>'
        check_artwork_badges_and_footer(soup(markup))
        with self.assertRaises(AssertionError):check_artwork_badges_and_footer(soup(markup.replace('Joseph stays beside Emma.','His care is documented.')))

    def test_generic_artwork_badges_absent_but_footer_and_source_limits_preserved(self):
        from joseph_research_acceptance import check_artwork_badges_and_footer, check_artwork_disclosure_text, ARTWORK_FOOTER_DISCLOSURE, REJECTED_ARTWORK_BADGES, REJECTED_SCENE_BOILERPLATE
        markup='<p>The surviving cast cannot establish iris color.</p><footer><p data-focuschrist-artwork-disclosure="footer">'+ARTWORK_FOOTER_DISCLOSURE+'</p></footer>'
        check_artwork_badges_and_footer(soup(markup))
        check_artwork_disclosure_text(soup(markup).get_text(' ',strip=True))
        for badge in REJECTED_ARTWORK_BADGES:
            with self.assertRaises(AssertionError):check_artwork_badges_and_footer(soup('<p>'+badge+'</p>'+markup))
            with self.assertRaises(AssertionError):check_artwork_disclosure_text(badge+'\n'+ARTWORK_FOOTER_DISCLOSURE)
        for phrase in REJECTED_SCENE_BOILERPLATE:
            with self.assertRaises(AssertionError):check_artwork_badges_and_footer(soup('<p>'+phrase+'</p>'+markup))
            with self.assertRaises(AssertionError):check_artwork_badges_and_footer(soup('<img alt="'+phrase+'">'+markup))
            with self.assertRaises(AssertionError):check_artwork_badges_and_footer(soup('<a data-full-image-alt="'+phrase+'">View image</a>'+markup))
        for changed in (markup.replace(ARTWORK_FOOTER_DISCLOSURE,''),markup.replace('<p data-','<p hidden data-'),markup.replace('<footer>','<div>').replace('</footer>','</div>')):
            with self.assertRaises(AssertionError):check_artwork_badges_and_footer(soup(changed))

    def test_cadence_rationale_is_bounded_and_exact(self):
        import hashlib
        markup='<section class="research-part"><div data-research-reading-block="section-2-1"><div class="research-reading-copy"><p>Supported means constrained by an actual source.</p></div></div></section>'
        record={'slot':'section-2-1','purpose':'source-key','reason':'A short evidence-label key needs no invented photograph.','content_sha256':hashlib.sha256(b'Supported means constrained by an actual source.').hexdigest()}
        check_reading_cadence(soup(markup),[record])
        for change in [markup.replace('Supported','Unsupported'),markup.replace('</p>','</p><p>Extra prose.</p><p>More prose.</p>'),markup.replace('<p>','<article class="research-trait"><p>').replace('</p>','</p></article>')]:
            with self.assertRaises(AssertionError):check_reading_cadence(soup(change),[record])
        with self.assertRaises(AssertionError):check_reading_cadence(soup(markup),[dict(record,purpose='anything')])
        with self.assertRaises(AssertionError):check_reading_cadence(soup(self.block),[record])

    def test_evidence_route_cannot_launder_generated_or_untracked_images(self):
        reference={'asset':'source.png','sha256':'a'*64,'kind':'historical_document','source_url':'https://archive.org/details/example','rights_basis':'US public domain','processing':'Faithful full-page render','publication_year':'1874'}
        placed={'src':'source.png','sha256':'a'*64}
        result=check_evidence_inventory([placed,placed],[reference],ROUTE)
        self.assertEqual(result,{'unique_reference_assets':1,'reference_placements':2,'new_original_artworks':0})
        for field,value in [('kind','original_scene'),('sha256','b'*64),('rights_basis',''),('source_url','')]:
            with self.assertRaises(AssertionError):check_evidence_inventory([placed],[dict(reference,**{field:value})],ROUTE)
        with self.assertRaises(AssertionError):check_evidence_inventory([dict(placed,src='unknown.png')],[reference],ROUTE)
        with self.assertRaises(AssertionError):check_evidence_inventory([placed],[reference],'other.html')
        with self.assertRaises(AssertionError):check_evidence_inventory([placed],[reference,reference],ROUTE)

    entry='<section id="our-portrait"><a class="fc-button" href="joseph-smith-portrait-research.html">Portrait research</a></section>'
    block='<section class="research-part"><div data-research-reading-block><p>One paragraph.</p><p>Second paragraph.</p><figure><img src="real.jpg"><figcaption>Source context.</figcaption></figure></div></section>'

    def test_entry_and_append_regression(self):
        check_entry_and_brevity(soup(self.entry))
        for bad in [self.entry+'<section class="research-part">Full appended text</section>',self.entry.replace('joseph-smith-portrait-research.html','#portrait-research'),self.entry.replace('fc-button','plain-link'),self.entry+'<section id="portrait-research"><p>'+('word '*121)+'</p></section>']:
            with self.assertRaises(AssertionError):check_entry_and_brevity(soup(bad))

    def test_actual_image_and_cadence(self):
        self.assertEqual(check_reading_cadence(soup(self.block)),1)
        for bad in [self.block.replace('<img src="real.jpg">','<svg role="img"></svg>'),self.block.replace('<figure>','<p>Third unsupported paragraph.</p><figure>'),self.block.replace('</section>','<p>Unaccounted reading.</p></section>'),self.block.replace('<img src="real.jpg">','<a href="other.html#picture">Look elsewhere</a>')]:
            with self.assertRaises(AssertionError):check_reading_cadence(soup(bad))

    def test_short_trait_pair_allowed_but_not_stack(self):
        trait='<article class="research-trait"><p>Observed</p><p>Evidence</p><p>Decision</p></article>'
        good=self.block.replace('<p>One paragraph.</p><p>Second paragraph.</p>',trait)
        check_reading_cadence(soup(good))
        check_reading_cadence(soup(good.replace(trait,trait+trait)))
        with self.assertRaises(AssertionError):check_reading_cadence(soup(good.replace(trait,trait+trait+trait)))

    def test_originals_cannot_be_counted_from_duplicates_or_references(self):
        import copy
        good=[{'id':str(i),'sha256':str(i),'kind':'original_scene','owning_page':ROUTE,'owning_section':'chapter','depicts_christ':i<5} for i in range(10)]
        check_original_manifest(good)
        bads=[good[:9]]
        for key,value in [('sha256','1'),('kind','reference'),('depicts_christ',False),('owning_page','other.html')]:
            bad=copy.deepcopy(good);bad[0][key]=value;bads.append(bad)
        for bad in bads:
            with self.assertRaises(AssertionError):check_original_manifest(bad)

    def test_owner_ratio_override_does_not_allow_rejected_filler(self):
        good=[{'id':str(i),'sha256':str(i),'kind':'original_scene','owning_page':ROUTE,'owning_section':'chapter','depicts_christ':False} for i in range(10)]
        check_original_manifest(good,require_half_christ=False)
        with self.assertRaises(AssertionError):check_original_manifest(good)
        for key,val in [('id','research-source-independence'),('sha256','84c152a2ce978289c0ec5bd05f5e1fcb2154c7d36cc47395b7a27715f368f2eb')]:
            rejected=[dict(x) for x in good];rejected[0][key]=val
            with self.assertRaises(AssertionError):check_original_manifest(rejected,require_half_christ=False)

    def test_bibliography_exception_cannot_hide_history(self):
        notes='<section class="research-part" id="portrait-section-15"><details class="research-source-index"><p class="research-source-note">Source coverage note.</p></details></section>'
        check_reading_cadence(soup(self.block+notes))
        with self.assertRaises(AssertionError):check_reading_cadence(soup(self.block+notes.replace('portrait-section-15','portrait-section-6')))

    def test_numbered_eyebrow_is_metadata_not_prose(self):
        good=self.block.replace('<section class="research-part">','<section class="research-part" id="portrait-section-1">').replace('<div data-research-reading-block>','<p class="fc-eyebrow">Chapter 01</p><div data-research-reading-block>')
        check_reading_cadence(soup(good))
        with self.assertRaises(AssertionError):check_reading_cadence(soup(good.replace('Chapter 01','A historical claim cannot escape as an eyebrow.')))

    def test_modern_identity_exception_is_explicit_and_limited(self):
        good={'identity_scope':'unnamed_contemporary_only','depicts_christ':False,'reference_sha256':[],'reference_not_applicable_reason':'No named historical character depicted.'}
        check_reference_scope(good)
        for key,val in [('depicts_christ',True),('identity_scope','Joseph'),('reference_not_applicable_reason',''),('reference_sha256',None)]:
            with self.assertRaises(AssertionError):check_reference_scope(dict(good,**{key:val}))
        with self.assertRaises(AssertionError):check_reference_scope({'depicts_christ':True,'reference_sha256':'0'*64})
        check_reference_scope({'depicts_christ':True,'reference_sha256':'4e9d4469bd9bd40d4e097eea887410a63f3c2f6dcc6ced3a3affd4813991b15b'})

    def test_receipt_presence_cannot_replace_exact_concurrence(self):
        record={'id':'scene','preflight_prompt_sha256':'prompt','sha256':'pixels'}
        review={'id':'scene','prompt_sha256':'prompt','sha256':'pixels','concur':True}
        check_exact_review(record,{'scenes':[review]},finished=True)
        for key,val in [('id','other'),('prompt_sha256','old'),('sha256','old'),('concur',False)]:
            with self.assertRaises(AssertionError):check_exact_review(record,{'scenes':[dict(review,**{key:val})]},finished=True)

    def test_feature_count_cannot_replace_local_evidence_or_actual_images(self):
        master='assets/identities/joseph-smith-owner-approved-20260914.png'
        features={}; traits={}; markup=''
        for i in range(1,17):
            key=f'{i:02d}'
            traits[key]={'title':key+' trait','observed':'observed '+key,'evidence':'evidence '+key,'verdict':'verdict '+key}
            visuals=[{'src':master,'caption':'adopted','owner':'#owner','sources':[]},{'src':'source.png','caption':'source','owner':'#owner','sources':[{'url':'https://example.org/source'}]}]
            features[key]={'explanation':['reason '+key],'limits':'limit '+key,'visuals':visuals}
            figures=''.join('<figure><a href="'+v['src']+'"><img src="'+v['src']+'"></a><figcaption>'+v['caption']+'<a href="#owner">Return</a><a href="https://example.org/source">Source</a></figcaption></figure>' for v in visuals)
            markup+='<article class="research-feature-study" data-research-feature="'+key+'" id="research-feature-'+key+'">'+' '.join(traits[key].values())+' reason '+key+' limit '+key+figures+'</article>'
        self.assertEqual(len(check_feature_studies(soup(markup),features,traits)),16)
        for bad in [markup.replace('evidence 01','omitted',1),markup.replace('<img src="source.png">','<a href="source.png">View elsewhere</a>',1),markup.replace('data-research-feature="16"','data-research-feature="15"'),markup.replace('https://example.org/source','https://example.org/unrelated')]:
            with self.assertRaises(AssertionError):check_feature_studies(soup(bad),features,traits)

    def test_renamed_original_cannot_be_rendered_on_another_page(self):
        from joseph_research_acceptance import check_original_page_exclusivity
        records=[{'sha256':'exact-pixels','owning_page':'research.html'}]
        check_original_page_exclusivity(records,{'research.html':['exact-pixels'],'main.html':['source-reference']})
        with self.assertRaises(AssertionError):
            check_original_page_exclusivity(records,{'research.html':['exact-pixels'],'main.html':['exact-pixels']})

class NarrativeCoverageTests(unittest.TestCase):
    def test_missing_duplicate_and_changed_evidence_fail(self):
        from joseph_research_narrative_qa import check_coverage
        import copy,hashlib
        original='The original sitting drawing remains unidentified.'
        item=dict(id='section-4/blocks/5/html',original=original,original_sha256=hashlib.sha256(original.encode()).hexdigest(),feature_id=None,field='html')
        root=soup('<section id="evidence"><p>'+original+'</p></section>')
        record=dict(id=item['id'],original_sha256=item['original_sha256'],disposition='preserved',targets=[dict(id='evidence',excerpt=original)],reason='The original drawing uncertainty remains explicit beside the profile.')
        check_coverage(root,[item],{'records':[record]})
        for records in ([],[record,record]):
            with self.assertRaises(AssertionError):check_coverage(root,[item],{'records':records})
        changed=copy.deepcopy(record);changed['targets'][0]['excerpt']='The original sitting drawing has been found.'
        with self.assertRaises(AssertionError):check_coverage(root,[item],{'records':[changed]})
        changed=copy.deepcopy(record);changed['original_sha256']='forged'
        with self.assertRaises(AssertionError):check_coverage(root,[item],{'records':[changed]})
    def test_feature_evidence_cannot_be_replaced_by_distant_source_note(self):
        from joseph_research_narrative_qa import check_coverage
        import hashlib
        value='The eye color accounts conflict.'
        item=dict(id='trait/eye/evidence',original=value,original_sha256=hashlib.sha256(value.encode()).hexdigest(),feature_id='research-feature-06',field='evidence')
        record=dict(id=item['id'],original_sha256=item['original_sha256'],disposition='preserved',targets=[dict(id='source',excerpt=value)],reason='Conflicting observations are retained with their source context.')
        root=soup('<article id="research-feature-06">Blue eyes</article><p id="source">'+value+'</p>')
        with self.assertRaises(AssertionError):check_coverage(root,[item],{'records':[record]})

class MigrationTests(unittest.TestCase):
    def test_missing_replaced_or_misplaced_migrated_art_fails(self):
        from pathlib import Path
        from joseph_research_narrative_qa import check_art_migration
        site=Path(__file__).resolve().parents[1]
        markup=(site/'docs/joseph-research-manuscript.html.inc').read_text(encoding='utf-8')
        check_art_migration(soup(markup),site)
        for fault in ('remove','crop','full_link','reference_destination'):
            root=soup(markup)
            if fault=='reference_destination':
                figure=next(f for f in root.select('#portrait-section-11 figure') if 'hyrum-reconstruction-blue' in f.select_one('img')['src'])
                root.select_one('#portrait-section-1').append(figure.extract())
            else:
                figure=root.select_one('figure[data-research-art="likeness-warmth"]')
                if fault=='remove':figure.decompose()
                elif fault=='crop':figure.select_one('img')['style']='object-fit:cover'
                else:figure.select_one('a:has(img)')['href']='unrelated.webp'
            with self.assertRaises(AssertionError,msg=fault):check_art_migration(root,site)

if __name__=='__main__':unittest.main()
