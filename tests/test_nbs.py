import json,unittest
from cn_data_adapters.nbs import request,parse

class NbsTests(unittest.TestCase):
    def spec(self):return dict(database='fsnd',indicator='A020101',period='2024')
    def payload(self,known=True,value='42'):
        return {'returncode':200,'returndata':{'wds':[{'wdcode':'zb','nodes':[{'code':'A020101','name':'地区生产总值','unit':'亿元'}]},{'wdcode':'reg','nodes':[{'code':'110000','name':'北京'}]},{'wdcode':'sj','nodes':[{'code':'2024','name':'2024年'}]}],'datanodes':[{'wds':[{'wdcode':'zb','valuecode':'A020101'},{'wdcode':'reg','valuecode':'110000'},{'wdcode':'sj','valuecode':'2024'}],'data':{'hasdata':known,'data':value}}]}}
    def test_missing_is_not_zero(self):
        row=parse(json.dumps(self.payload(False,None)).encode(),self.spec())[0]
        self.assertIsNone(row['value']);self.assertEqual(row['unit'],'亿元')
    def test_duplicate_and_wrong_period(self):
        value=self.payload();value['returndata']['datanodes']*=2
        with self.assertRaises(ValueError):parse(json.dumps(value).encode(),self.spec())
        with self.assertRaises(ValueError):parse(json.dumps(self.payload()).encode(),dict(self.spec(),period='2023'))
    def test_error_and_future_not_accepted(self):
        with self.assertRaises(ValueError):parse(b'{"returncode":403}',self.spec())
        with self.assertRaises(ValueError):request(dict(self.spec(),period='9999'))
