import unittest,json,tempfile
from pathlib import Path
from cn_data_adapters.market import parse,replay,export,publish,url_for

SPEC={'market':'SSE','code':'510300','kind':'etf','start':'2025-01-02','end':'2025-01-03'}
RAW=json.dumps({'data':{'code':'510300','market':1,'name':'合成教学','klines':['2025-01-02,4,4.1,4.2,3.9,20,8000','2025-01-03,4.1,4.2,4.3,4,25,10000']}}).encode()
class MarketTests(unittest.TestCase):
    def test_replay_and_available(self):
        s=parse(RAW,SPEC,'2025-01-04T08:00:00+08:00');r=replay(s,RAW)
        self.assertEqual(s['retrievedAt'],r['retrievedAt']);self.assertIsNotNone(r['replayedAt']);self.assertEqual(s['data'],r['data']);self.assertIsNone(s['data'][0]['volume_shares']);self.assertEqual(s['data'][0]['providerVolume'],'20')
        text=export(s,{'priceFactor':'1','factorEvidence':'原创教学已声明无行动','category':'宽基','indexId':'teaching-only'}).decode()
        self.assertIn('2025-01-04T08:00:00+08:00',text);self.assertIn('SSE:510300',text)
    def test_unknown_factor_blocked(self):
        s=parse(RAW,SPEC,'2025-01-04T08:00:00+08:00')
        for factor in (None,'2'):
            with self.assertRaises(ValueError):export(s,{'priceFactor':factor,'factorEvidence':'x','category':'宽基','indexId':''})
    def test_raw_and_snapshot_tampering(self):
        s=parse(RAW,SPEC,'2025-01-04T08:00:00+08:00')
        with self.assertRaises(ValueError):replay(s,RAW+b' ')
        s['data'][0]['close']='9'
        with self.assertRaises(ValueError):replay(s,RAW)
    def test_identity_date_and_numbers(self):
        for patch in ({'code':'000001'},{'market':0},{'klines':['2025-01-02,4,4.1,4.2,3.9,20,8000']*2},{'klines':['2025-01-02,4,4.1,3,3.9,20,8000']},{'klines':['2025-01-02,4,4.1,4.2,3.9,-1,8000']}):
            obj=json.loads(RAW);obj['data'].update(patch)
            with self.assertRaises(ValueError):parse(json.dumps(obj).encode(),SPEC,'2025-01-04T08:00:00+08:00')
    def test_window_and_no_overwrite(self):
        with self.assertRaises(ValueError):url_for(dict(SPEC,start='2020-01-01'))
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'new';s=parse(RAW,SPEC,'2025-01-04T08:00:00+08:00');publish(out,SPEC,s,RAW)
            with self.assertRaises(ValueError):publish(out,SPEC,s,RAW)
            self.assertEqual((out/'response.json').read_bytes(),RAW)
    def test_public_hosts(self):
        from cn_data_adapters.public_download import check_host
        with self.assertRaises(ValueError):check_host('https://localhost/',{'push2his.eastmoney.com'})

if __name__=='__main__':unittest.main()
