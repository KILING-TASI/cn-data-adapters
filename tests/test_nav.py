import unittest,tempfile,copy
from pathlib import Path
from cn_data_adapters.teaching import build
from cn_data_adapters.nav import parse,fetch,from_native,replay
from cn_data_adapters._contract import validate,digest
from cn_data_adapters.__main__ import publish,main

class NavTests(unittest.TestCase):
    def test_requires_online_before_fetch(self):
        snapshot,_=build()
        with self.assertRaises(ValueError):fetch(snapshot['request'],fetcher=lambda _:self.fail('network called'))
    def test_offline_keeps_original_time(self):
        snapshot,raw=build();result=replay(snapshot,raw)
        self.assertEqual(result['dates']['retrievedAt'],snapshot['dates']['retrievedAt'])
        self.assertIsNotNone(result['dates']['replayedAt']);self.assertEqual(result['data'],snapshot['data'])
    def test_changed_response_refuses_replay(self):
        snapshot,raw=build()
        with self.assertRaises(ValueError):replay(snapshot,raw+b'changed')
    def test_fetch_failure_has_reason_and_no_price(self):
        snapshot,_=build()
        def fail(_):raise OSError('offline')
        result,raw=fetch(snapshot['request'],online=True,fetcher=fail)
        self.assertEqual(result['status'],'failed');self.assertIsNone(raw);self.assertEqual(result['data'],[])
    def test_bad_received_bytes_retained(self):
        snapshot,_=build();result,raw=fetch(snapshot['request'],online=True,fetcher=lambda _:b'bad response')
        self.assertEqual(result['status'],'failed');self.assertEqual(raw,b'bad response')
        self.assertIsNotNone(result['dates']['retrievedAt'])
    def test_wrong_fund_rejected(self):
        snapshot,raw=build()
        with self.assertRaises(ValueError):parse(raw.replace(b'900001',b'900002'),snapshot['request'],retrieved_at=None)
    def test_two_native_formats_same_data(self):
        snapshot,raw=build();r=snapshot['request'];stamp=snapshot['dates']['retrievedAt']
        history=[dict(date=x['date'],nav=float(x['unit_nav']),distribution=x['distribution_text']) for x in snapshot['data']]
        wb={'type':'research-bundle','asOf':r['asOf'],'rows':[dict(code=r['fundCode'],kind='fund',history=history,historyBasis='nav-with-distributions',identity={'name':'Teaching synthetic fund'},retrievedAt=stamp,source='declared-source',errors=None)]}
        history2=[dict(date=x['date'],nav=float(x['unit_nav']),distribution_text=x['distribution_text']) for x in snapshot['data']]
        pde={'type':'portfolio-source-archive','results':[dict(code=r['fundCode'],name='Teaching synthetic fund',provider='eastmoney_fund_nav',basis='nav_with_unverified_events',status='observed',history=history2,requested_start=r['start'],requested_end=r['end'],retrieved_at=stamp,response_sha256=digest(raw),response_file='response-0.txt')]}
        self.assertEqual(from_native(wb,r)['data'],from_native(pde,r)['data'])
        self.assertEqual(from_native(wb,r)['data'],snapshot['data'])
        self.assertFalse(from_native(wb,r)['provenance']['rawBytesAvailable'])
    def test_cached_failure_stays_partial(self):
        snapshot,_=build();r=snapshot['request']
        wb={'type':'research-bundle','asOf':r['asOf'],'rows':[dict(code=r['fundCode'],kind='fund',history=[{'date':'2026-01-02','nav':1}],historyBasis='nav-with-distributions',retrievedAt='2026-01-03T10:00:00+08:00',errors='refresh failed')]}
        self.assertEqual(from_native(wb,r)['status'],'partial')
    def test_no_overwrite_and_saved_raw(self):
        snapshot,raw=build()
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'report';publish(snapshot,out,raw=raw)
            old=(out/'snapshot.json').read_bytes()
            with self.assertRaises(ValueError):publish(snapshot,out,raw=raw)
            self.assertEqual((out/'snapshot.json').read_bytes(),old);self.assertEqual((out/'response.txt').read_bytes(),raw)
    def test_raw_path_traversal_rejected(self):
        snapshot,raw=build();r=snapshot['request']
        pde={'type':'portfolio-source-archive','results':[dict(code=r['fundCode'],provider='eastmoney_fund_nav',basis='nav_with_unverified_events',history=[],requested_start=r['start'],requested_end=r['end'],response_file='../secret')]}
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):from_native(pde,r,raw_directory=t)

if __name__=='__main__':unittest.main()
