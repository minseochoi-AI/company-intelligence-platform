"""Generate an explicitly selected set of research instances through the common engine.

The historical six filenames and row counts are not program defaults.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from cil_cli.research import main as research_main


def main(argv=None):
    parser = argparse.ArgumentParser(description='명시한 조사 인스턴스 목록으로 Excel을 생성합니다.')
    parser.add_argument('--instances', required=True, type=Path, help='request/snapshot/instance_id 배열 JSON')
    parser.add_argument('--output', required=True, type=Path, help='새 실행 결과 디렉터리')
    args = parser.parse_args(argv)
    instances = json.loads(args.instances.read_text(encoding='utf-8'))
    if not isinstance(instances, list) or not instances:
        raise ValueError('nonempty instance array required')
    seen = set()
    results = []
    for row in instances:
        if set(row) != {'instance_id', 'request', 'snapshot'} or not isinstance(row['instance_id'], str) or not row['instance_id'].replace('-', '').replace('_', '').isalnum() or row['instance_id'] in seen:
            raise ValueError('unique safe instance_id and exact request/snapshot paths required')
        seen.add(row['instance_id'])
        paths = []
        for field in ('request', 'snapshot'):
            path = Path(row[field])
            paths.append(path if path.is_absolute() else args.instances.parent / path)
        code = research_main(['run', '--request', str(paths[0]), '--snapshot', str(paths[1]), '--output', str(args.output / row['instance_id'])])
        results.append(code)
    return 2 if any(results) else 0


if __name__ == '__main__':
    raise SystemExit(main())
