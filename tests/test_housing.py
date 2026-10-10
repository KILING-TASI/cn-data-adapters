import unittest
from cn_data_adapters.housing_model import build_house_price_series
from cn_data_adapters.housing import request

class HousingTests(unittest.TestCase):
    def test_region_and_partial_coverage(self):
        row=dict(CITY='北京',REPORT_DATE='2025-01-01',FIRST_COMHOUSE_SAME=99,FIRST_COMHOUSE_SEQUENTIAL=100.1,SECOND_HOUSE_SAME=None,SECOND_HOUSE_SEQUENTIAL=99.8)
        result=build_house_price_series([row]);self.assertIsNone(result['latest'])
        self.assertEqual(result['citySeries']['北京']['series']['new_mom'],[100.1])
        self.assertIsNone(result['citySeries']['北京']['series']['second_yoy'][0])
    def test_duplicate_and_future(self):
        row=dict(CITY='北京',REPORT_DATE='2025-01-01')
        with self.assertRaises(ValueError):build_house_price_series([row,row])
        with self.assertRaises(ValueError):request(dict(start='2025-01',end='9999-01'))
