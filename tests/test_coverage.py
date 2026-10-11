import hashlib,tempfile,unittest
from pathlib import Path
from cn_data_adapters.coverage import review

class CoverageTests(unittest.TestCase):
    def sample(self,root):
        data=b'\xff\xd8\xffbounded fixture';(root/'C01-01.jpg').write_bytes(data)
        return {'schemaVersion':'cn-yearbook-archive/1.0','edition':2025,'tables':[{'id':'C01-01','chapter':1,'title':'教学','status':'original-archived','file':'C01-01.jpg','format':'jpg','sha256':hashlib.sha256(data).hexdigest()},{'id':'C02-01','chapter':2,'title':'失败','status':'failed'}]}
    def test_archive_is_not_numeric_coverage(self):
        with tempfile.TemporaryDirectory() as d:
            r=review(self.sample(Path(d)),Path(d));self.assertEqual(r['fullTablesVerified'],0);self.assertEqual(r['verifiedSelectedCells'],0);self.assertEqual(r['archiveStatusCounts']['failed'],1)
    def test_changed_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);s=self.sample(root);(root/'C01-01.jpg').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'摘要'):review(s,root)
    def test_partial_review_and_no_full_table_claim(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);s=self.sample(root);r={'tableId':'C01-01','sourceSha256':s['tables'][0]['sha256'],'method':'visual-transcription','scope':'第1行第1列','verifiedCells':1,'unit':'元','observationPeriod':'2024','reviewer':'test','reviewedAt':'2026-10-11T00:00:00Z','fullTableVerified':False}
            self.assertEqual(review(s,root,[r])['verifiedSelectedCells'],1)
            r['fullTableVerified']=True
            with self.assertRaisesRegex(ValueError,'全表'):review(s,root,[r])
    def test_review_for_failed_original_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);s=self.sample(root);r={'tableId':'C02-01','sourceSha256':'0'*64,'method':'ocr-reviewed','scope':'x','verifiedCells':1,'unit':'元','observationPeriod':'2024','reviewer':'test','reviewedAt':'2026-10-11T00:00:00Z','fullTableVerified':False}
            with self.assertRaisesRegex(ValueError,'未绑定'):review(s,root,[r])
