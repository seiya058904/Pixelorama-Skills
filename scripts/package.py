#!/usr/bin/env python3
"""Build deterministic source and installable-skill ZIPs; refuse overwrites."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.1.0'
PROJECT_FILES = (
    '.gitattributes', '.gitignore', '.github/repository.json', '.github/workflows/validate.yml',
    'README.md', 'README.zh-CN.md', 'LICENSE', 'THIRD_PARTY_NOTICES.md', 'SECURITY.md', 'CHANGELOG.md',
    'assets/banner.svg', 'docs/VALIDATION.md', 'docs/UPSTREAM.md', 'docs/SMOKE_TEST.md', 'docs/PUBLISH.md',
    'skills/pixelorama-skills/SKILL.md', 'skills/pixelorama-skills/LICENSE',
    'skills/pixelorama-skills/references/setup.md', 'skills/pixelorama-skills/references/drawing.md',
    'skills/pixelorama-skills/scripts/doctor.py',
    'scripts/validate.py', 'scripts/package.py', 'scripts/publish.py',
    'tests/test_doctor.py', 'tests/test_validate.py', 'tests/test_package.py', 'tests/test_publish.py',
)


def zip_bytes(root: Path, skill_only: bool = False) -> bytes:
    output = io.BytesIO()
    prefix = 'skills/pixelorama-skills/'
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for relative in sorted(PROJECT_FILES):
            if skill_only and not relative.startswith(prefix):
                continue
            path = root / relative
            if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
                raise ValueError(f'Unsafe source path: {relative}')
            name = 'pixelorama-skills/' + relative[len(prefix):] if skill_only else 'Pixelorama-Skills/' + relative
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 30, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    return output.getvalue()


def build(out: Path, root: Path = ROOT) -> dict[str, str]:
    archives = {
        f'Pixelorama-Skills-v{VERSION}-source.zip': zip_bytes(root),
        f'pixelorama-skills-v{VERSION}.zip': zip_bytes(root, skill_only=True),
    }
    if out.resolve().is_relative_to((root / 'skills').resolve()):
        raise ValueError('Do not put build artifacts inside the installable skill.')
    hashes = {name: hashlib.sha256(data).hexdigest() for name, data in archives.items()}
    archives['SHA256SUMS.txt'] = ''.join(f'{value}  {name}\n' for name, value in hashes.items()).encode()
    if any((out / name).exists() for name in archives):
        raise FileExistsError('Output already exists. Choose a new output directory; no files were overwritten.')
    out.mkdir(parents=True, exist_ok=True)
    for name, data in archives.items():
        with (out / name).open('xb') as f:
            f.write(data)
    return hashes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.out), indent=2))
    except (OSError, ValueError) as exc:
        parser.exit(1, f'Packaging failed: {exc}\n')
