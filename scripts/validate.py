#!/usr/bin/env python3
"""Validate this repository's intentionally simple Agent Skills profile offline."""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKILL = Path('skills/pixelorama-skills/SKILL.md')


def parse_frontmatter(text: str) -> dict:
    lines = text.splitlines()
    if not lines or lines[0] != '---':
        raise ValueError('Missing opening frontmatter delimiter')
    try:
        end = lines.index('---', 1)
    except ValueError as exc:
        raise ValueError('Missing closing frontmatter delimiter') from exc
    data: dict = {}
    metadata = False
    for line in lines[1:end]:
        if not line.strip():
            continue
        match = re.fullmatch(r'(  )?([a-z][a-z0-9_-]*):(?: (.*))?', line)
        if not match:
            raise ValueError('Unsupported frontmatter syntax; use plain strings and metadata strings')
        indent, key, value = match.groups()
        if indent and not metadata:
            raise ValueError('Unexpected nested field')
        target = data['metadata'] if indent else data
        if key in target:
            raise ValueError(f'Duplicate field: {key}')
        if not indent:
            metadata = key == 'metadata'
        if key == 'metadata' and not indent:
            if value:
                raise ValueError('Metadata must be a string mapping')
            target[key] = {}
            continue
        if value is None:
            raise ValueError(f'Empty field: {key}')
        quoted = value.startswith('"')
        if quoted:
            value = json.loads(value)
        elif value.startswith(("'", '[', '{', '|', '>')) or ': ' in value:
            raise ValueError('Use a quoted JSON-compatible string for this value')
        if (not isinstance(value, str) or (not quoted and (value.lower() in ('true', 'false', 'null', '~', 'yes', 'no', 'on', 'off', '.nan', '.inf')
                or re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?', value)))):
            raise ValueError('Metadata values must be strings')
        target[key] = value
    return data


def unfenced(text: str) -> str:
    return re.sub(r'^```[^\n]*\n.*?^```\s*$', '', text, flags=re.M | re.S)


def anchors(text: str) -> set[str]:
    result: set[str] = set()
    counts: dict[str, int] = {}
    for heading in re.findall(r'^#{1,6}\s+(.+?)\s*#*$', unfenced(text), flags=re.M):
        slug = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        result.add(f'{slug}-{count}' if count else slug)
    result.update(re.findall(r'\bid=["\']([^"\']+)', text))
    return result


def check_links(path: Path, root: Path) -> list[str]:
    text = unfenced(path.read_text(encoding='utf-8'))
    targets = re.findall(r'\]\(([^\s)]+)(?:\s+"[^"]*")?\)', text)
    targets += re.findall(r'\b(?:href|src)=["\']([^"\']+)', text)
    errors = []
    root = root.resolve()
    for target in targets:
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc:
            if parsed.scheme not in ('https', 'http', 'mailto'):
                errors.append(f'{path.name}: unsupported link scheme: {target}')
            continue
        local = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path.resolve()
        try:
            local.relative_to(root)
        except ValueError:
            errors.append(f'{path.name}: link escapes repository: {target}')
            continue
        if not local.is_file():
            errors.append(f'{path.name}: missing link target: {target}')
        elif parsed.fragment and local.suffix == '.md':
            if unquote(parsed.fragment) not in anchors(local.read_text(encoding='utf-8')):
                errors.append(f'{path.name}: missing anchor: {target}')
    return errors


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    path = root / SKILL
    try:
        text = path.read_text(encoding='utf-8')
        meta = parse_frontmatter(text)
        name = meta.get('name', '')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or len(name) > 64:
            errors.append('Invalid skill name')
        if name != path.parent.name:
            errors.append('Skill name and folder differ')
        if not 1 <= len(meta.get('description', '')) <= 1024:
            errors.append('Invalid description length')
        if not 1 <= len(meta.get('compatibility', '')) <= 500:
            errors.append('Invalid compatibility length')
        if meta.get('metadata', {}).get('version') != '1.1.0':
            errors.append('Unexpected skill version')
        if len(text.split()) > 900:
            errors.append('Core skill exceeded 900-word budget')
        if meta.get('license') != 'MIT':
            errors.append('Missing license declaration')
        if (root / 'LICENSE').read_bytes() != (path.parent / 'LICENSE').read_bytes():
            errors.append('Skill and repository licenses differ')
    except (ValueError, OSError) as exc:
        errors.append(f'Skill metadata: {exc}')
    for doc in sorted(root.rglob('*.md')):
        if any(part in ('.git', 'dist', '.validation') for part in doc.relative_to(root).parts):
            continue
        content = doc.read_text(encoding='utf-8')
        if len(re.findall(r'^```', content, flags=re.M)) % 2:
            errors.append(f'{doc.name}: unbalanced code fences')
        errors += check_links(doc, root)
    try:
        banner = ET.parse(root / 'assets/banner.svg').getroot()
        if not banner.tag.endswith('svg') or not banner.attrib.get('viewBox'):
            errors.append('Invalid SVG root/viewBox')
        for elem in banner.iter():
            if elem.tag.rsplit('}', 1)[-1] in ('script', 'foreignObject'):
                errors.append('Active content in SVG')
            if any(key.lower().startswith('on') for key in elem.attrib):
                errors.append('Event handler in SVG')
        config = json.loads((root / '.github/repository.json').read_text())
        if config['name'] != 'Pixelorama-Skills' or config['owner'] != 'seiya058904':
            errors.append('Unexpected publication target')
        if config['visibility'] != 'public' or not 1 <= len(config['description']) <= 350:
            errors.append('Invalid repository metadata')
        if not 1 <= len(config['topics']) <= 20 or len(set(config['topics'])) != len(config['topics']):
            errors.append('Invalid topics')
        for topic in config['topics']:
            if not re.fullmatch(r'[a-z0-9-]{1,50}', topic):
                errors.append('Invalid topic format')
    except (OSError, ValueError, KeyError, ET.ParseError) as exc:
        errors.append(f'Assets/metadata: {exc}')
    return errors


if __name__ == '__main__':
    issues = validate()
    if issues:
        print('\n'.join(f'FAIL: {item}' for item in issues), file=sys.stderr)
        raise SystemExit(1)
    print('PASS: skill metadata, word budget, licenses, local links/anchors, SVG and repository metadata.')
    print('Scope: offline repository checks; not desktop/MCP integration or artistic quality.')
