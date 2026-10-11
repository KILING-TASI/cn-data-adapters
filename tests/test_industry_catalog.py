import json,unittest
from pathlib import Path
from cn_data_adapters.source_archive import HOSTS


class Tests(unittest.TestCase):
 def test_catalog_preserves_namespaces_and_does_not_promote_candidates(self):
  root=Path(__file__).parents[1]/'catalogs'
  coverage=json.loads((root/'industry-coverage.json').read_text('utf-8'))['items']
  items=json.loads((root/'industry-indicators.json').read_text('utf-8'))['items']
  mapping={r['name']:(r['code'],r['indexCode']) for r in coverage}
  self.assertEqual(len(mapping),31);self.assertEqual(len({r['id'] for r in items}),len(items))
  for row in items:
   self.assertEqual((row['classificationCode'],row['indexCode']),mapping[row['industryName']])
   self.assertNotEqual(row['classificationCode'],row['indexCode']);self.assertIsNone(row['currentValue'])
   self.assertIsNone(row['firstAvailableAt']);self.assertTrue(set(row['sourceCandidates'])<=set(HOSTS))
   if row['existingAnnualExamples']:self.assertEqual(row['acquisitionStatus'],'annual-selected-cells-only')
  retired=[r for r in items if 'BB值' in r['metricName']]
  self.assertEqual(len(retired),1);self.assertTrue(retired[0]['acquisitionStatus'].startswith('blocked'))


if __name__=='__main__':unittest.main()
