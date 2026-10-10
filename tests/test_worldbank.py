import json, unittest
from cn_data_adapters.worldbank import parse, request

class WDITests(unittest.TestCase):
    def spec(self):return dict(countries=['CHN'],indicator='SP.POP.TOTL',start=2020,end=2024)
    def raw(self,value=None):return json.dumps([{'page':1,'pages':1,'total':1},[{'countryiso3code':'CHN','country':{'value':'China'},'indicator':{'id':'SP.POP.TOTL','value':'Population'},'date':'2024','value':value,'unit':''}]]).encode()
    def test_unknown_and_unit_are_not_guessed(self):
        row=parse(self.raw(),self.spec(),1)[1][0]
        self.assertIsNone(row['value']);self.assertIsNone(row['unit'])
    def test_wrong_identity_and_page_rejected(self):
        with self.assertRaises(ValueError):parse(self.raw(),dict(self.spec(),countries=['USA']),1)
        with self.assertRaises(ValueError):parse(self.raw(),self.spec(),2)
    def test_error_and_bool_rejected(self):
        with self.assertRaises(ValueError):parse(b'[{"message":"error"}]',self.spec(),1)
        with self.assertRaises(ValueError):parse(self.raw(True),self.spec(),1)
    def test_request_no_future_or_code_injection(self):
        with self.assertRaises(ValueError):request(dict(self.spec(),indicator='x?evil'))
        with self.assertRaises(ValueError):request(dict(self.spec(),end=9999))
