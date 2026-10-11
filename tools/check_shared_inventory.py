# SPDX-License-Identifier: MIT
"""Audit tracked original Python duplicates across explicitly supplied checkouts."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import subprocess


def digest(path):
    return hashlib.sha256(path.read_text(encoding='utf-8-sig').encode('utf-8')).hexdigest()


def audit(roots):
    groups = collections.defaultdict(list)
    registered = {}
    errors = []
    for root in roots:
        root = root.resolve()
        manifest = root / 'SHARED_CODE.json'
        entries = json.loads(manifest.read_text(encoding='utf-8'))['components'] if manifest.exists() else []
        for item in entries:
            key = (root.name, item['localPath'])
            if key in registered:
                errors.append(f'重复登记：{key}')
            registered[key] = item
            path = (root / item['localPath']).resolve()
            if not path.is_relative_to(root) or not path.is_file() or digest(path) != item['normalizedTextSha256']:
                errors.append(f'固定副本缺失或哈希不符：{key}')
        names = subprocess.run(['git', '-C', str(root), 'ls-files', '-z'], check=True, capture_output=True).stdout.decode('utf-8').split('\0')
        for name in names:
            path = root / name
            if path.suffix != '.py' or not path.is_file():
                continue
            if any(part in {'tests', 'test', 'build', 'dist'} for part in Path(name).parts) or path.name.startswith('test_'):
                continue
            if not path.read_text(encoding='utf-8-sig').strip():
                continue
            groups[digest(path)].append({'repository': root.name, 'path': name})
    shared = []
    for sha, copies in sorted(groups.items()):
        if len({c['repository'] for c in copies}) < 2:
            continue
        for copy in copies:
            if (copy['repository'], copy['path']) not in registered:
                errors.append(f"共享副本未登记：{copy['repository']}/{copy['path']}")
        shared.append({'normalizedTextSha256': sha, 'copies': copies})
    return {'scope': 'Git 跟踪的非空 Python 文件；排除 tests/test/build/dist 和 test_ 文件；按 UTF-8、LF、无 BOM 比较。相同文本不证明接口语义等价；历史固定版不要求跟随权威源最新版。', 'repositories': [r.name for r in roots], 'groups': shared, 'errors': errors}


def main():
    import sys
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('roots', nargs='+', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = audit(args.roots)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    for error in result['errors']:
        print(error)
    print(f"跨仓检查：{len(result['repositories'])} 仓，{len(result['groups'])} 组；问题 {len(result['errors'])} 项")
    return 1 if result['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
