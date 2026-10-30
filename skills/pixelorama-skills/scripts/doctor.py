#!/usr/bin/env python3
"""Read-only prerequisites and loopback health checks. No installs or mutations."""
from __future__ import annotations
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any
from urllib import error, parse, request

MAX_RESPONSE_BYTES = 65536
DEFAULT_BRIDGE = 'http://127.0.0.1:7373'


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise error.HTTPError(req.full_url, code, 'Redirects are not allowed', headers, fp)


def health_url(base: str) -> str:
    """Accept literal loopback only; no DNS, credentials, queries, or redirects."""
    try:
        p = parse.urlsplit(base)
        port = p.port
        if (p.scheme != 'http' or p.hostname not in ('127.0.0.1', '::1')
                or p.username is not None or p.password is not None
                or p.path not in ('', '/') or p.query or p.fragment
                or (port is not None and not 1 <= port <= 65535)):
            raise ValueError('Unsupported URL')
        host = '[::1]' if p.hostname == '::1' else '127.0.0.1'
        authority = f'{host}:{port}' if port is not None else host
        return f'http://{authority}/health'
    except (ValueError, TypeError) as exc:
        raise ValueError('Only http://127.0.0.1[:port] or http://[::1][:port] is allowed, without paths or credentials.') from exc


def check_command(name: str) -> dict[str, Any]:
    if name not in ('node', 'npm', 'git'):
        raise ValueError('Unexpected command')
    executable = shutil.which(name)
    if executable is None:
        return {'ok': False, 'reason': 'not found'}
    try:
        result = subprocess.run([executable, '--version'], capture_output=True,
                                text=True, timeout=5, check=False)
        version = result.stdout.strip()[:160]
        ok = result.returncode == 0 and bool(version)
        if name == 'node':
            match = re.match(r'^v?(\d+)\.', version)
            ok = ok and match is not None and int(match.group(1)) >= 18
        return {'ok': bool(ok), 'version': version,
                'note': 'Checks upstream minimum, not support lifecycle.' if name == 'node' else ''}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'ok': False, 'reason': type(exc).__name__}


def check_bridge(base: str = DEFAULT_BRIDGE, timeout: float = 2.5) -> dict[str, Any]:
    url = health_url(base)
    if not 0.1 <= timeout <= 30:
        raise ValueError('Timeout must be between 0.1 and 30 seconds.')
    opener = request.build_opener(request.ProxyHandler({}), NoRedirect())
    req = request.Request(url, headers={'Accept': 'application/json'}, method='GET')
    try:
        with opener.open(req, timeout=timeout) as response:
            if response.status != 200:
                return {'ok': False, 'reason': f'HTTP {response.status}'}
            if response.headers.get_content_type() != 'application/json':
                return {'ok': False, 'reason': 'Unexpected content type'}
            data = response.read(MAX_RESPONSE_BYTES + 1)
            if len(data) > MAX_RESPONSE_BYTES:
                return {'ok': False, 'reason': 'Health response too large'}
            body = json.loads(data.decode('utf-8'))
            if not isinstance(body, dict) or body.get('status') != 'ok' or body.get('server') != 'pix-mcp-bridge':
                return {'ok': False, 'reason': 'Unexpected bridge identity or health status'}
            details = {key: body[key] for key in ('version', 'pixelorama_version', 'api_version')
                       if key in body and isinstance(body[key], (str, int, float)) and not isinstance(body[key], bool)}
            details = {key: value[:160] if isinstance(value, str) else value for key, value in details.items()}
            return {'ok': True, 'identity': 'pix-mcp-bridge', **details}
    except error.HTTPError as exc:
        code = exc.code
        exc.close()
        return {'ok': False, 'reason': 'HTTPError', 'status': code}
    except (error.URLError, OSError, UnicodeError, ValueError) as exc:
        return {'ok': False, 'reason': type(exc).__name__}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bridge-url', default=DEFAULT_BRIDGE)
    parser.add_argument('--timeout', type=float, default=2.5)
    parser.add_argument('--server-entry', type=Path, help='Optional built MCP dist/index.js; never executed.')
    args = parser.parse_args()
    try:
        health_url(args.bridge_url)
        if not 0.1 <= args.timeout <= 30:
            raise ValueError('Timeout must be between 0.1 and 30 seconds.')
        result = {'prerequisites': {name: check_command(name) for name in ('node', 'npm', 'git')},
                  'bridge': check_bridge(args.bridge_url, args.timeout),
                  'mcp_round_trip': 'NOT_TESTED', 'editor_drawing': 'NOT_TESTED',
                  'visual_quality': 'NOT_TESTED',
                  'notice': 'Read-only checks. Health is not authentication, MCP connectivity, or editor validation.'}
        if args.server_entry is not None:
            result['server_entry'] = {'ok': args.server_entry.is_file() and args.server_entry.suffix == '.js'}
        ok = all(item['ok'] for item in result['prerequisites'].values()) and result['bridge']['ok']
        if 'server_entry' in result:
            ok = ok and result['server_entry']['ok']
        result['diagnostic_ok'] = ok
        print(json.dumps(result, indent=2))
        return 0 if ok else 1
    except ValueError as exc:
        parser.error(str(exc))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
