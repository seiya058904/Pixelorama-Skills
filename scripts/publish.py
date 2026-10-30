#!/usr/bin/env python3
"""Publish a fresh repository from an authorized cloud workspace with gh; dry-run by default."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from package import PROJECT_FILES
from validate import validate

ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str], *, input_text: str | None = None, timeout: int = 120) -> str:
    completed = subprocess.run(args, cwd=ROOT, input=input_text, text=True,
                               capture_output=True, timeout=timeout, check=False)
    if completed.returncode:
        # No commands include tokens. Do not print environment or credential files.
        raise RuntimeError(f'{args[0]} {args[1] if len(args) > 1 else ""} failed: {completed.stderr.strip()[:1200]}')
    return completed.stdout.strip()


def plan() -> dict:
    config = json.loads((ROOT / '.github/repository.json').read_text())
    return {'repository': f'{config["owner"]}/{config["name"]}',
            'visibility': config['visibility'], 'description': config['description'],
            'topics': config['topics'], 'branch': 'main',
            'actions': ['validate', 'verify authenticated owner', 'refuse existing repo/worktree',
                        'commit explicit source files', 'create and push', 'apply About metadata',
                        'read back remote state'],
            'not_included': ['force push', 'cleanup', 'release creation', 'desktop validation']}


def publish() -> dict:
    issues = validate()
    if issues:
        raise RuntimeError('Repository checks failed: ' + '; '.join(issues))
    if not shutil.which('git') or not shutil.which('gh'):
        raise RuntimeError('Git and an authenticated GitHub CLI are required on this cloud host.')
    run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'])
    config = json.loads((ROOT / '.github/repository.json').read_text())
    owner, name = config['owner'], config['name']
    repo = f'{owner}/{name}'
    profile = json.loads(run(['gh', 'api', 'user', '--jq', '{login: .login, id: .id}']))
    if profile.get('login') != owner or not isinstance(profile.get('id'), int):
        raise RuntimeError('Authenticated account is not the intended owner; no repository was created.')
    worktree = subprocess.run(['git', 'rev-parse', '--show-toplevel'], cwd=ROOT, capture_output=True, text=True)
    if worktree.returncode == 0 or (ROOT / '.git').exists():
        raise RuntimeError('An existing Git worktree was found. Inspect it; this fresh-publish helper will not modify it.')
    exists = subprocess.run(['gh', 'api', f'repos/{repo}'], cwd=ROOT, capture_output=True, text=True, timeout=30)
    if exists.returncode == 0:
        raise RuntimeError('Destination repository already exists. Refusing to overwrite or reuse it.')
    if 'HTTP 404' not in exists.stderr:
        raise RuntimeError('Could not establish that the destination is absent; no writes attempted.')
    # All writes below are authorized only by an explicit --execute invocation.
    run(['git', 'init', '-b', 'main', '.'])
    run(['git', 'config', 'user.name', 'seiya'])
    run(['git', 'config', 'user.email', f'{profile["id"]}+{owner}@users.noreply.github.com'])
    run(['git', 'add', '--', *PROJECT_FILES])
    run(['git', 'commit', '-m', 'feat: publish Pixelorama Skills v1.1.0'])
    run(['gh', 'repo', 'create', repo, '--public', '--description', config['description'],
         '--source', '.', '--remote', 'origin', '--push'])
    run(['gh', 'api', '--method', 'PUT', f'repos/{repo}/topics', '--input', '-'],
        input_text=json.dumps({'names': config['topics']}))
    edit_args = ['gh', 'repo', 'edit', repo, '--default-branch', 'main']
    if config.get('homepage'):
        edit_args.extend(['--homepage', config['homepage']])
    run(edit_args)
    current = json.loads(run(['gh', 'api', f'repos/{repo}']))
    if (current.get('private') or current.get('description') != config['description']
            or current.get('default_branch') != 'main' or current.get('homepage', '') != config.get('homepage', '')
            or set(current.get('topics', [])) != set(config['topics'])):
        raise RuntimeError('Repository was created, but read-back metadata does not match. Inspect before further writes.')
    head = run(['git', 'rev-parse', 'HEAD'])
    remote = run(['git', 'ls-remote', 'origin', 'refs/heads/main']).split()
    if not remote or remote[0] != head:
        raise RuntimeError('Push read-back does not match the local commit.')
    dirty = run(['git', 'status', '--porcelain'])
    if dirty:
        raise RuntimeError('Remote created, but working tree is not clean. Inspect remaining files without deleting them.')
    return {'repository': current['html_url'], 'commit': head, 'about_verified': True,
            'main_matches': True, 'working_tree_clean': True,
            'github_actions': 'Check actual remote run before reporting success.',
            'release_created': False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true', help='Explicitly authorize public repository creation and push.')
    args = parser.parse_args()
    if not args.execute:
        print(json.dumps({'mode': 'DRY_RUN_NO_WRITES', **plan()}, indent=2))
        return 0
    try:
        print(json.dumps(publish(), indent=2))
        return 0
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f'Publication stopped: {exc}\nInspect any partial state; no rollback, deletion, or force-push was attempted.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
