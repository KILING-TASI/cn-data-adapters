import unittest
from cn_data_adapters.contracts.observations import validate,SCHEMA
class ObservationTests(unittest.TestCase):
 def spec(self):return {'schemaVersion':SCHEMA,'asOf':'2026-02-01T12:00:00+08:00','rawSourceSha256':'0'*64,'origin':'teaching-tabular-bytes','rows':[{'id':'teaching-1','entity':'教学宏观地区','metric':'同比','value':'-1.25','unit':'percent','currency':None,'basis':'year-over-year-declared','periodStart':'2026-01-01','periodEnd':'2026-01-31','observedAt':None,'publishedAt':None,'availableAt':None,'retrievedAt':'2026-02-01T10:00:00+08:00','sourceUrl':'https://example.org/teaching','sourceVersion':'teaching-1','locator':'原创CSV第1行','verification':'declared-not-original-verified'}]}
 def test_unknown_availability(self):self.assertEqual(validate(self.spec())['historicalAvailabilityUnknownIds'],['teaching-1'])
 def test_zero_not_unknown(self):
  s=self.spec();s['rows'][0]['value']='0';self.assertEqual(validate(s)['count'],1)
 def test_nonfinite(self):
  s=self.spec();s['rows'][0]['value']='NaN'
  with self.assertRaises(ValueError):validate(s)
 def test_duplicate_ids(self):
  s=self.spec();s['rows'].append(s['rows'][0])
  with self.assertRaises(ValueError):validate(s)
 def test_missing_metadata(self):
  s=self.spec();del s['rows'][0]['unit']
  with self.assertRaises(ValueError):validate(s)
