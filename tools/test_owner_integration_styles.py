"""Exact scoped-style owners and normal shared stylesheet successor."""
import unittest
import owner_integration_styles as s

class IntegrationStyleTests(unittest.TestCase):
    def sources(self):
        return {p:(s.ROOT/p).read_text() for p in (*s.OWNERS,s.CSS)}

    def test_actual_three_owners(self):
        self.assertTrue(s.validate_scoped_style(self.sources()))

    def test_each_missing_or_unknown_owner_fails(self):
        for p in s.OWNERS:
            data=self.sources();del data[p]
            with self.assertRaises(AssertionError):s.validate_scoped_style(data)
        data=self.sources();data['unknown.html']=data[s.INTRO]
        with self.assertRaises(AssertionError):s.validate_scoped_style(data)

    def test_changed_ref_and_duplicate_fail(self):
        for p in s.OWNERS:
            for addition in (' ', '<link rel="stylesheet" href="adams-integration.css">'):
                data=self.sources();data[p]+=addition
                with self.assertRaises(AssertionError):s.validate_scoped_style(data)

    def test_exact_intro_shared_version(self):
        self.assertTrue(s.timeline_binding(s.INTRO,[('link',{'rel':'stylesheet','href':s.TIMELINE_REF})]))
        for refs in ([],[s.TIMELINE_REF+'-wrong'],[s.TIMELINE_REF,s.TIMELINE_REF]):
            self.assertFalse(s.timeline_binding(s.INTRO,[('link',{'rel':'stylesheet','href':x}) for x in refs]))
        with self.assertRaises(AssertionError):s.timeline_binding('unknown.html',[])

    def test_exact_added_intro_owner_and_retained_historical_set(self):
        old={'timelines/old-one.html','timelines/old-two.html'}
        sources={p:'historical source' for p in old};sources[s.INTRO]=(s.ROOT/s.INTRO).read_text()
        self.assertTrue(s.timeline_consumers(sources,old))
        for p in sources:
            changed=dict(sources);del changed[p]
            self.assertFalse(s.timeline_consumers(changed,old))
        self.assertFalse(s.timeline_consumers(dict(sources,**{'unknown.html':'x'}),old))

    def test_intro_changed_data_does_not_pass_owner_partition(self):
        data={s.INTRO:(s.ROOT/s.INTRO).read_text()+' '}
        self.assertFalse(s.timeline_consumers(data,set()))

if __name__=='__main__':unittest.main()
