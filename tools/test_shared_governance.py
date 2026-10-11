# SPDX-License-Identifier: MIT
"""Regression checks for portability, omitted copies and forbidden paths."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
from check_shared_inventory import audit, digest
from check_shared_code import check


def main():
    with tempfile.TemporaryDirectory() as tmp:
        roots = [Path(tmp) / name for name in ('source', 'consumer')]
        for root in roots:
            root.mkdir()
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            (root / 'renamed.py').write_bytes(b'print("sample")\r\n')
            item = dict(localPath='renamed.py', normalizedTextSha256=digest(root / 'renamed.py'), canonicalRepository='source', canonicalPath='original.py', syncPolicy='fixed', licenseScope='MIT')
            (root / 'SHARED_CODE.json').write_text(json.dumps(dict(schemaVersion='fixed-shared-components/1', components=[item])), encoding='utf-8')
            subprocess.run(['git', '-C', str(root), 'add', '.'], check=True)
            assert check(root) == 1
        (roots[1] / 'renamed.py').write_bytes(b'\xef\xbb\xbfprint("sample")\n')
        assert not audit(roots)['errors'], 'LF/CRLF/BOM must agree; renamed path remains registered'
        manifest = roots[1] / 'SHARED_CODE.json'
        saved = manifest.read_text()
        manifest.write_text(json.dumps(dict(schemaVersion='fixed-shared-components/1', components=[])))
        assert any('未登记' in e for e in audit(roots)['errors'])
        manifest.write_text(saved)
        (roots[1] / 'renamed.py').write_text('print("changed")\n')
        assert any('哈希不符' in e for e in audit(roots)['errors'])
        try:
            check(roots[1])
            raise AssertionError('changed content passed')
        except ValueError:
            pass
        invalid = json.loads(saved)
        invalid['components'][0]['localPath'] = '../outside.py'
        manifest.write_text(json.dumps(invalid))
        try:
            check(roots[1])
            raise AssertionError('outside path passed')
        except ValueError:
            pass
    print('共享治理正反例通过：换行/BOM、改名、遗漏、内容变化、路径越界')


if __name__ == '__main__':
    main()
