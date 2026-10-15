import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from cn_data_adapters.response_archive import ResponseArchive
from cn_data_adapters.matching import match
from cn_data_adapters.tail_import import convert
from cn_data_adapters.worldbank import parse

class Pipeline(unittest.TestCase):
 def test_capture_replay_without_transport(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'source';a=ResponseArchive(p,lambda u,post:b'first');self.assertEqual(a('https://example.com'),b'first');stamp=a.finish();b=ResponseArchive(p,replay=True);self.assertEqual(b('https://example.com'),b'first');self.assertEqual(b.finish(),stamp)
 def test_corrupt_response_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'source';a=ResponseArchive(p,lambda u,post:b'first');a('https://example.com');a.finish();next(p.glob('*.bin')).write_bytes(b'changed');self.assertRaises(ValueError,ResponseArchive(p,replay=True),'https://example.com')
 def test_unknown_request_no_network(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'source';a=ResponseArchive(p,lambda u,post:b'first');a.finish();self.assertRaises(ValueError,ResponseArchive(p,replay=True),'https://other.example.com')
 def test_failed_request_replayed_as_failure(self):
  def fail(u,post):raise OSError('fixture failure')
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'source';a=ResponseArchive(p,fail);self.assertRaises(OSError,a,'https://example.com');a.finish();self.assertRaises(OSError,ResponseArchive(p,replay=True),'https://example.com')
 def test_archive_cannot_overwrite(self):
  with tempfile.TemporaryDirectory() as td:self.assertRaises(FileExistsError,ResponseArchive,td)
 def test_repeated_url_preserves_versions(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'source';vals=iter([b'one',b'two']);a=ResponseArchive(p,lambda u,post:next(vals));a('https://example.com');a('https://example.com');a.finish();b=ResponseArchive(p,replay=True);self.assertEqual([b('https://example.com'),b('https://example.com')],[b'one',b'two'])
 def test_public_wdi_frozen_bytes_and_identity(self):
  root=Path(__file__).resolve().parents[1]/'examples';snap=json.loads((root/'public-wdi/snapshot.json').read_text(encoding='utf-8'));raw=(root/'public-wdi/page-1.json').read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),snap['pages'][0]['sha256']);meta,rows=parse(raw,snap['request'],1);self.assertEqual(len(rows),9);self.assertEqual({r['regionCode'] for r in rows},{'CHN','USA','JPN'})
 def test_public_wdi_future_period_mutation_blocked(self):
  root=Path(__file__).resolve().parents[1]/'examples';snap=json.loads((root/'public-wdi/snapshot.json').read_text(encoding='utf-8'));raw=json.loads((root/'public-wdi/page-1.json').read_text(encoding='utf-8'));raw[1][0]['date']='2099';self.assertRaises(ValueError,parse,json.dumps(raw).encode(),snap['request'],1)
 def test_bridge_keeps_unknown_publication(self):
  raw=json.dumps(dict(schemaVersion='context-v1',asOf='2026-10-14',retrievedAt='2026-10-15T05:00:00+00:00',records=[dict(entityId='CHN',metric='gdp',period='2024',value=5,sourceDecimalText='5.0',currency=None,basis='latest revised',unit='%',sourceUrl='https://example.com',version='2026-10-01')])).encode();table,receipt=convert(raw);self.assertIsNone(table['rows'][0]['availableAt']);self.assertEqual(receipt['validation']['historicalAvailabilityUnknownIds'],[table['rows'][0]['id']]);self.assertEqual(receipt['inputResearchCutoff'],'2026-10-14');self.assertEqual(table['asOf'],'2026-10-15T05:00:00+00:00')
 def test_matcher_rejects_currency_and_unknown_vintage(self):
  a=dict(entityId='x',metric='market_price',region='CHN',frequency='daily',period='2026-10-14',value=1,unit='per-unit',currency='CNY',basis='unit-price',sourceUrl='https://example.com',shareClass='listed');b=dict(a,metric='published_unit_nav',currency='USD');self.assertEqual(match(a,b,'premium')['status'],'rejected');self.assertEqual(match(a,a,cutoff='2026-10-14',point_in_time=True)['status'],'rejected')
