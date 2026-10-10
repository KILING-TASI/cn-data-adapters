import unittest
from cn_data_adapters.yearbook import discover, main
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch
import json

class YearbookTests(unittest.TestCase):
    def test_chapters_appendix_and_unknown_values(self):
        raw = ('<a href="html/C04-01.jpg">就业</a><a href="html/C28-01.jpg">台湾</a>'
               '<a href="html/Cfu-01.jpg">国际</a><a href="html/C04-01.jpg">重复</a>').encode('gb18030')
        rows = discover(raw,2025)
        self.assertEqual([r['chapter'] for r in rows],[4,28,'appendix'])
        self.assertTrue(all(r['structuredValues'] is None for r in rows))
    def test_wrong_origin_and_year_are_excluded(self):
        raw = b'<a href="https://evil.test/sj/ndsj/2025/html/C01-01.jpg">x</a><a href="../2024/html/C01-01.jpg">x</a>'
        with self.assertRaises(ValueError): discover(raw,2025)
    def test_error_page_not_success(self):
        with self.assertRaises(ValueError): discover(b'<html>captcha</html>',2025)
    def test_offline_and_no_overwrite(self):
        with TemporaryDirectory() as tmp:
            raw=Path(tmp)/'raw'; raw.write_bytes(b'<a href="html/C01-01.jpg">1-1</a>')
            out=Path(tmp)/'out'
            args=['--year','2025','--index-raw',str(raw),'--out-dir',str(out)]
            self.assertEqual(main(args),0)
            self.assertEqual(main(args),2)
            self.assertTrue((out/'打开这里.html').exists())
    def test_bad_image_stops_and_preserves_response(self):
        with TemporaryDirectory() as tmp:
            index=Path(tmp)/'index';index.write_bytes(b'<a href="html/C01-01.jpg">a</a><a href="html/C01-02.jpg">b</a>')
            out=Path(tmp)/'out'
            with patch('cn_data_adapters.yearbook.fetch',return_value={'raw':b'<html>verification</html>'}) as fetch:
                self.assertEqual(main(['--year','2025','--index-raw',str(index),'--online','--max-tables','2','--out-dir',str(out)]),2)
                self.assertEqual(fetch.call_count,1)
            rows=json.loads((out/'snapshot.json').read_text(encoding='utf-8'))['tables']
            self.assertEqual(rows[0]['status'],'failed');self.assertEqual(rows[1]['status'],'not-attempted')
            self.assertEqual((out/rows[0]['failedResponseFile']).read_bytes(),b'<html>verification</html>')
