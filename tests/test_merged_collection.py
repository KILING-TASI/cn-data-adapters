import unittest,copy
from cn_data_adapters.contracts.collection import request,record,validate,canonical,digest,amount,loads

def req():
    return dict(id='teaching',source='eastmoney-fund-nav',fundCode='900001',start='2026-01-02',end='2026-01-03',asOf='2026-01-03',currency='CNY',frequency='daily',fields=['unit_nav','distribution_text'])

class CollectionTests(unittest.TestCase):
    def test_identity_is_not_numeric(self):
        r=req();r['fundCode']=900001
        with self.assertRaises(ValueError):request(r)
    def test_date_window_not_silently_repaired(self):
        r=req();r['asOf']='2026-01-01'
        with self.assertRaises(ValueError):request(r)
    def test_unknown_metadata_not_zero_or_verified(self):
        r=record(req(),[{'date':'2026-01-02','nav':'1.01'}]);validate(r)
        self.assertIsNone(r['dates']['retrievedAt']);self.assertFalse(r['verification']['sourceVerified'])
        self.assertEqual(r['coverage']['completeness'],'unknown')
    def test_duplicate_date_rejected(self):
        with self.assertRaises(ValueError):record(req(),[{'date':'2026-01-02','nav':1}]*2)
    def test_failure_has_no_fabricated_price(self):
        r=record(req(),[],failure='network failed');validate(r)
        self.assertEqual(r['data'],[]);self.assertIsNone(r['coverage']['observedStart'])
    def test_changed_result_rejected(self):
        r=record(req(),[{'date':'2026-01-02','nav':'1.01'}]);r['data'][0]['unit_nav']='2'
        with self.assertRaises(ValueError):validate(r)
    def test_decimal_is_not_float_rounded(self):
        self.assertEqual(amount('1.123456789012345678901234567890'),'1.12345678901234567890123456789')
    def test_duplicate_json_and_nonfinite_rejected(self):
        for text in ['{"x":1,"x":2}','{"x":NaN}']:
            with self.assertRaises(ValueError):loads(text)
    def test_boolean_price_rejected(self):
        with self.assertRaises(ValueError):amount(True)
    def test_no_timezone_is_not_acquisition_time(self):
        with self.assertRaises(ValueError):record(req(),[{'date':'2026-01-02','nav':1}],retrieved_at='2026-01-03T10:00:00')

if __name__=='__main__':unittest.main()
