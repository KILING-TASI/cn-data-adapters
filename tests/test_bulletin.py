import unittest
from cn_data_adapters.bulletin import extract, map_cells

class BulletinTests(unittest.TestCase):
    def test_spans_missing_and_script(self):
        raw='<table><tr><th rowspan="2">收入</th><td>..</td></tr><tr><td><script>fake()</script>42</td></tr></table>'.encode()
        table=extract(raw)[0]
        self.assertEqual(table[0][0]['rowspan'],2)
        self.assertEqual(table[0][1]['text'],'..')
        self.assertEqual(table[1][0]['text'],'42')
    def test_no_tables_does_not_succeed(self):
        with self.assertRaises(ValueError):extract(b'<html>captcha</html>')
    def test_invalid_span(self):
        with self.assertRaises(ValueError):extract(b'<table><tr><td colspan="-1">x</td></tr></table>')
    def test_mapping_requires_exact_header_and_unique_label(self):
        tables=extract('<table><tr><td>指标</td><td>元</td></tr><tr><td>收入</td><td>42.5</td></tr></table>'.encode())
        item=dict(indicatorId='income',tableIndex=0,rowLabel='收入',columnIndex=1,expectedHeader='元',period='2025',unit='CNY/person',scope='全国')
        self.assertEqual(map_cells(tables,[item])[0]['value'],'42.5')
        with self.assertRaises(ValueError):map_cells(tables,[dict(item,expectedHeader='万元')])
        with self.assertRaises(ValueError):map_cells(tables,[item,item])
        tables[0].append(tables[0][1])
        with self.assertRaises(ValueError):map_cells(tables,[item])
