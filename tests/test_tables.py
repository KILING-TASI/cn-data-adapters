import unittest,json
from pathlib import Path
from cn_data_adapters.tables import normalize
class TableTests(unittest.TestCase):
 def spec(self):return json.loads((Path(__file__).resolve().parents[1]/'examples/tables-teaching.json').read_text(encoding='utf-8'))
 def test_signed_macro_and_unknown_available(self):
  r=normalize(self.spec());self.assertEqual(r['snapshot']['rows'][0]['value'],'-1.25');self.assertEqual(r['validation']['historicalAvailabilityUnknownIds'],['教学-1'])
 def test_unknown_column(self):
  s=self.spec();s['mapping']['value']='missing'
  with self.assertRaises(ValueError):normalize(s)
 def test_duplicate_headers(self):
  s=self.spec();s['csvText']='编号,编号\nx,y\n'
  with self.assertRaises(ValueError):normalize(s)
 def test_missing_units(self):
  s=self.spec();del s['constants']['unit']
  with self.assertRaises(ValueError):normalize(s)
