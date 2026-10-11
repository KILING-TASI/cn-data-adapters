import copy,unittest
from cn_data_adapters.capabilities import review

class Tests(unittest.TestCase):
    def sample(self):
        return {'inputSchema':'source-capabilities/1','asOf':'2026-10-11','sources':[dict(id='a',provider='test',entry='test',scope='selected',frequency='annual',unitPolicy='explicit',versionPolicy='frozen',rightsNote='unknown',access='public',implementation='partial',attemptStatus='missing',lastAttemptAt=None,latestObservationDate=None,maxAgeDays=None)]}
    def test_unknown_is_not_fresh(self):self.assertEqual(review(self.sample())['sources'][0]['freshness'],'unknown')
    def test_catalog_not_success(self):
        s=self.sample();s['sources'][0].update(implementation='catalog-only',attemptStatus='available')
        with self.assertRaises(ValueError):review(s)
    def test_stale_and_cutoff(self):
        s=self.sample();s['sources'][0].update(latestObservationDate='2025-12-31',maxAgeDays=30)
        self.assertEqual(review(s)['sources'][0]['freshness'],'stale')
        s['sources'][0]['latestObservationDate']='2026-10-12';self.assertEqual(review(s)['sources'][0]['reviewStatus'],'after-cutoff')
    def test_source_switch_requires_explicit_changes(self):
        s=self.sample();s['sources'].append(dict(s['sources'][0],id='b'));s['switches']=[{'from':'a','to':'b','methodologyChanges':[]}]
        with self.assertRaises(ValueError):review(s)
        s['switches'][0]['methodologyChanges']=['复权范围须重新核对'];self.assertFalse(review(s)['switches'][0]['equivalenceCertified'])
