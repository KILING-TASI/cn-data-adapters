import unittest,tempfile,json,subprocess,sys,os
from pathlib import Path
from unittest.mock import patch
from cn_data_adapters.source_archive import main

class SourceTests(unittest.TestCase):
 def test_capture_replay_and_raw(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);inp=p/'input.json';inp.write_text(json.dumps({'sourceId':'sse','url':'https://www.sse.com.cn/','purpose':'原创测试'}),encoding='utf-8')
   with patch('cn_data_adapters.source_archive.download',return_value={'raw':b'<html>test</html>','resolvedUrl':'https://www.sse.com.cn/'}):
    self.assertEqual(main(['capture','--input',str(inp),'--online','--out-dir',str(p/'one')]),0)
   self.assertEqual(main(['replay','--input',str(p/'one/snapshot.json'),'--raw',str(p/'one/response.json'),'--out-dir',str(p/'two')]),0)
   a=json.loads((p/'one/snapshot.json').read_text(encoding='utf-8'));b=json.loads((p/'two/snapshot.json').read_text(encoding='utf-8'));self.assertEqual(a['retrievedAt'],b['retrievedAt']);self.assertIsNone(b['publishedAt']);self.assertIsNotNone(b['replayedAt'])
 def test_failure_and_offline(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);inp=p/'input.json';inp.write_text(json.dumps({'sourceId':'sse','url':'https://www.sse.com.cn/','purpose':'原创测试'}),encoding='utf-8')
   with patch('cn_data_adapters.source_archive.download',side_effect=OSError('blocked')) as call:
    self.assertEqual(main(['capture','--input',str(inp),'--out-dir',str(p/'offline')]),2);call.assert_not_called()
    self.assertEqual(main(['capture','--input',str(inp),'--online','--out-dir',str(p/'failed')]),2)
   result=json.loads((p/'failed/snapshot.json').read_text(encoding='utf-8'));self.assertEqual(result['data'],[]);self.assertIsNone(result['retrievedAt'])
 def test_host_mismatch(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);inp=p/'input.json';inp.write_text(json.dumps({'sourceId':'sse','url':'https://127.0.0.1/','purpose':'测试'}),encoding='utf-8')
   with patch('cn_data_adapters.source_archive.download') as call:
    self.assertEqual(main(['capture','--input',str(inp),'--online','--out-dir',str(p/'failed')]),2);call.assert_not_called()
 def test_cli_under_non_chinese_output_encoding(self):
  for module in ['market','source_archive']:
   proc=subprocess.run([sys.executable,'-m','cn_data_adapters.'+module,'--help'],capture_output=True,env=dict(os.environ,PYTHONIOENCODING='ascii',PYTHONUTF8='0'))
   self.assertEqual(proc.returncode,0,proc.stderr.decode('utf-8'));self.assertIn('usage:',proc.stdout.decode('utf-8'))

if __name__=='__main__':unittest.main()
