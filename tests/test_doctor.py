import importlib.util
import io
import json
import subprocess
import sys
import unittest
from email.message import Message
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from unittest.mock import patch, MagicMock
from urllib import error, request

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('doctor', ROOT / 'skills/pixelorama-skills/scripts/doctor.py')
doctor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(doctor)


class URLTests(unittest.TestCase):
    def test_ipv4(self):
        self.assertEqual(doctor.health_url('http://127.0.0.1:7373'), 'http://127.0.0.1:7373/health')

    def test_ipv6(self):
        self.assertEqual(doctor.health_url('http://[::1]:7373/'), 'http://[::1]:7373/health')

    def test_default_port(self):
        self.assertEqual(doctor.health_url('http://127.0.0.1'), 'http://127.0.0.1/health')

    def test_invalid_urls_never_open_network(self):
        invalid = ['https://127.0.0.1', 'http://localhost', 'http://example.com',
                   'http://127.0.0.1.evil.test', 'http://0.0.0.0', 'http://192.168.1.1',
                   'file:///etc/passwd', 'http://user:pass@127.0.0.1',
                   'http://127.0.0.1/command', 'http://127.0.0.1?x=1',
                   'http://127.0.0.1#x', 'http://127.0.0.1:0',
                   'http://127.0.0.1:99999', 'http://[::1', '//127.0.0.1', '']
        with patch.object(doctor.request, 'build_opener') as opener:
            for url in invalid:
                with self.subTest(url=url), self.assertRaises(ValueError):
                    doctor.check_bridge(url)
            opener.assert_not_called()

    def test_invalid_timeout(self):
        for timeout in (0, -1, 31, float('nan'), float('inf')):
            with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                doctor.check_bridge(timeout=timeout)

    def test_redirect_handler_rejects(self):
        req = request.Request('http://127.0.0.1:7373/health')
        with self.assertRaises(error.HTTPError):
            doctor.NoRedirect().redirect_request(req, None, 302, 'Found', {}, 'http://example.com')


class PrerequisiteTests(unittest.TestCase):
    def test_missing_command(self):
        with patch.object(doctor.shutil, 'which', return_value=None):
            self.assertFalse(doctor.check_command('node')['ok'])

    def test_unknown_command(self):
        with self.assertRaises(ValueError):
            doctor.check_command('rm')

    def test_node_minimum_and_malformed(self):
        with patch.object(doctor.shutil, 'which', return_value='/trusted/node'):
            for version, expected in [('v22.16.0', True), ('v18.0.0', True), ('v16.20.0', False), ('unknown', False), ('', False)]:
                cp = subprocess.CompletedProcess([], 0, version, '')
                with self.subTest(version=version), patch.object(doctor.subprocess, 'run', return_value=cp) as call:
                    self.assertEqual(doctor.check_command('node')['ok'], expected)
                    self.assertEqual(call.call_args.args[0], ['/trusted/node', '--version'])
                    self.assertNotIn('shell', call.call_args.kwargs)

    def test_command_failure(self):
        with patch.object(doctor.shutil, 'which', return_value='/trusted/git'), patch.object(
            doctor.subprocess, 'run', return_value=subprocess.CompletedProcess([], 1, '', 'failed')):
            self.assertFalse(doctor.check_command('git')['ok'])

    def test_command_timeout(self):
        with patch.object(doctor.shutil, 'which', return_value='/trusted/git'), patch.object(
            doctor.subprocess, 'run', side_effect=subprocess.TimeoutExpired('git', 5)):
            self.assertEqual(doctor.check_command('git')['reason'], 'TimeoutExpired')

    def test_no_proxy_inheritance(self):
        opener = MagicMock()
        opener.open.side_effect = error.URLError('not running')
        with patch.object(doctor.request, 'build_opener', return_value=opener) as build:
            self.assertFalse(doctor.check_bridge()['ok'])
            self.assertEqual(build.call_args.args[0].proxies, {})
            self.assertIsInstance(build.call_args.args[1], doctor.NoRedirect)

    def test_cli_reports_unverified_gates(self):
        with patch.object(sys, 'argv', ['doctor.py']), patch.object(doctor, 'check_command', return_value={'ok': True}), patch.object(
            doctor, 'check_bridge', return_value={'ok': True}), patch('sys.stdout', new_callable=io.StringIO) as output:
            self.assertEqual(doctor.main(), 0)
            record = json.loads(output.getvalue())
            self.assertEqual(record['editor_drawing'], 'NOT_TESTED')
            self.assertEqual(record['mcp_round_trip'], 'NOT_TESTED')

    def test_cli_failure_exit(self):
        with patch.object(sys, 'argv', ['doctor.py']), patch.object(doctor, 'check_command', return_value={'ok': False}), patch.object(
            doctor, 'check_bridge', return_value={'ok': False}), patch('sys.stdout', new_callable=io.StringIO):
            self.assertEqual(doctor.main(), 1)


class HealthHTTPTests(unittest.TestCase):
    """Exercise real loopback HTTP, not a real Pixelorama/MCP server."""
    @classmethod
    def setUpClass(cls):
        cls.reply_code = 200
        cls.reply_body = b'{}'
        cls.reply_type = 'application/json'
        cls.seen = []
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                cls.seen.append(self.path)
                self.send_response(cls.reply_code)
                self.send_header('Content-Type', cls.reply_type)
                if cls.reply_code == 302:
                    self.send_header('Location', '/forbidden-redirect-target')
                self.end_headers()
                try:
                    self.wfile.write(cls.reply_body)
                except (BrokenPipeError, ConnectionResetError):
                    pass
            def log_message(self, *args):
                pass
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def setUp(self):
        type(self).reply_code = 200
        type(self).reply_type = 'application/json'
        type(self).reply_body = json.dumps({'status':'ok','server':'pix-mcp-bridge','api_version':10}).encode()
        type(self).seen = []

    def test_expected_identity(self):
        self.assertTrue(doctor.check_bridge(self.url)['ok'])
        self.assertEqual(self.seen, ['/health'])

    def test_wrong_identity(self):
        type(self).reply_body = b'{"status":"ok","server":"another-service"}'
        self.assertFalse(doctor.check_bridge(self.url)['ok'])

    def test_wrong_status(self):
        type(self).reply_body = b'{"status":"busy","server":"pix-mcp-bridge"}'
        self.assertFalse(doctor.check_bridge(self.url)['ok'])

    def test_malformed_json(self):
        type(self).reply_body = b'not json'
        self.assertFalse(doctor.check_bridge(self.url)['ok'])

    def test_json_array(self):
        type(self).reply_body = b'[]'
        self.assertFalse(doctor.check_bridge(self.url)['ok'])

    def test_invalid_utf8(self):
        type(self).reply_body = b'\xff'
        self.assertFalse(doctor.check_bridge(self.url)['ok'])

    def test_mime_rejection(self):
        type(self).reply_type = 'text/html'
        self.assertFalse(doctor.check_bridge(self.url)['ok'])

    def test_payload_limit(self):
        type(self).reply_body = b'x' * (doctor.MAX_RESPONSE_BYTES + 1)
        self.assertEqual(doctor.check_bridge(self.url)['reason'], 'Health response too large')

    def test_http_error(self):
        type(self).reply_code = 500
        self.assertFalse(doctor.check_bridge(self.url)['ok'])

    def test_redirect_not_followed(self):
        type(self).reply_code = 302
        self.assertFalse(doctor.check_bridge(self.url)['ok'])
        self.assertEqual(self.seen, ['/health'])

    def test_response_fields_bounded(self):
        type(self).reply_body = json.dumps({'status':'ok','server':'pix-mcp-bridge',
                                          'version':'x'*500,'api_version':True,'secret':'do not return'}).encode()
        result = doctor.check_bridge(self.url)
        self.assertEqual(len(result['version']),160)
        self.assertNotIn('secret',result)
        self.assertNotIn('api_version',result)


if __name__ == '__main__':
    unittest.main()
