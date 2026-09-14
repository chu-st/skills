from __future__ import annotations
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
PEER = ROOT / 'skills/dual-model-review/scripts/peer.py'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


peer = load('chust_peer', PEER)
installer = load('chust_install', ROOT / 'scripts/install.py')


class PeerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.brief = self.root / 'brief.md'
        self.brief.write_text('Вопрос: 2 + 2?\nDo not execute $(echo data).', encoding='utf-8')
        self.provider_runs = 0

    def tearDown(self):
        self.tmp.cleanup()

    def invoke(self, body, model='test-model', timeout=10):
        fake = self.root / 'fake.py'
        fake.write_text(body, encoding='utf-8')
        config = self.root / 'command.json'
        config.write_text(json.dumps([sys.executable, str(fake), '{model}']), encoding='utf-8')
        out = self.root / 'result'
        result = subprocess.run([sys.executable, str(PEER), '--provider', 'command', '--model', model,
                                 '--command-file', str(config), '--prompt', str(self.brief),
                                 '--output', str(out), '--timeout', str(timeout)],
                                capture_output=True, timeout=30)
        return result, out, json.loads((out / 'receipt.json').read_text(encoding='utf-8'))

    def invoke_claude(self, payload, model='opus', exit_code=0):
        self.provider_runs += 1
        out = self.root / f'claude-result-{self.provider_runs}'
        fake = self.root / 'fake-provider.py'
        fake.write_text('import sys\nsys.stdin.read()\n'
                        f'print({json.dumps(payload)!r})\nsys.exit({exit_code})\n', encoding='utf-8')
        args = argparse.Namespace(provider='claude', model=model, prompt=str(self.brief),
                                  output=str(out), timeout=10, executable=None, command_file=None)
        printed = io.StringIO()
        with mock.patch.object(peer, 'command_for', return_value=[sys.executable, str(fake)]):
            with contextlib.redirect_stdout(printed):
                code = peer.run(args)
        return code, out, json.loads((out / 'receipt.json').read_text(encoding='utf-8')), \
            json.loads(printed.getvalue().splitlines()[-1])

    def test_complete_stdin_and_literal_arguments(self):
        model = 'literal;$(echo nope)& data'
        result, out, receipt = self.invoke(
            'import sys, json\nprint(json.dumps([sys.argv[1], sys.stdin.read()], ensure_ascii=False))\n', model)
        self.assertEqual(result.returncode, 0, result.stderr)
        answer = json.loads((out / 'response.md').read_text(encoding='utf-8'))
        self.assertEqual(answer, [model, self.brief.read_text(encoding='utf-8')])
        self.assertEqual(receipt['execution_status'], 'PASS')
        self.assertEqual(receipt['quality_verdict'], 'NOT ASSESSED')
        self.assertIsNone(receipt['reported_model'])
        self.assertEqual(receipt['model_identity']['status'], 'UNVERIFIED')
        for name in ('input', 'response'):
            self.assertEqual(hashlib.sha256((out / f'{name}.md').read_bytes()).hexdigest(),
                             receipt[f'{name}_sha256'])

    def test_byte_hashes_for_bom_and_windows_line_endings(self):
        self.brief.write_bytes(b'\xef\xbb\xbfFirst line\r\nSecond line\r\n')
        result, out, receipt = self.invoke('import sys\nsys.stdout.buffer.write(sys.stdin.buffer.read())\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in ('input', 'response'):
            data = (out / f'{name}.md').read_bytes()
            self.assertEqual(data, b'First line\nSecond line\n')
            self.assertEqual(hashlib.sha256(data).hexdigest(), receipt[f'{name}_sha256'])

    def test_empty_exit_zero_is_not_success(self):
        result, out, receipt = self.invoke('import sys\nsys.stdin.read()\n')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(receipt['execution_status'], 'NOT RUN')
        self.assertFalse((out / 'response.md').exists())

    def test_nonzero_preserves_partial_output(self):
        result, out, receipt = self.invoke('import sys\nprint("partial"); print("failure", file=sys.stderr); sys.exit(7)\n')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(receipt['exit_code'], 7)
        self.assertIn('partial', (out / 'stdout.log').read_text())
        self.assertIn('failure', (out / 'stderr.log').read_text())

    def test_timeout_preserves_and_marks_not_run(self):
        result, out, receipt = self.invoke('import time\nprint("started", flush=True)\ntime.sleep(30)\n', timeout=0.3)
        self.assertEqual(result.returncode, 2)
        self.assertIn('timed out', receipt['error'])
        self.assertIn('started', (out / 'stdout.log').read_text())

    def test_existing_result_is_never_overwritten(self):
        out = self.root / 'result'
        out.mkdir()
        marker = out / 'input.md'
        marker.write_text('valuable existing input')
        args = argparse.Namespace(prompt=str(self.brief), timeout=1, output=str(out))
        with self.assertRaises(FileExistsError):
            peer.run(args)
        self.assertEqual(marker.read_text(), 'valuable existing input')

    def test_claude_envelope_and_reported_model(self):
        output = self.root / 'claude'
        output.mkdir()
        payload = {'type': 'result', 'subtype': 'success', 'result': 'Useful answer',
                   'modelUsage': {'helper': {'outputTokens': 0}, 'selected-opus': {'outputTokens': 200}}}
        (output / 'stdout.log').write_text(json.dumps(payload), encoding='utf-8')
        answer, model = peer.extract_response('claude', output)
        self.assertEqual(model, 'selected-opus')
        self.assertIn('Useful answer', answer)
        payload['is_error'] = True
        (output / 'stdout.log').write_text(json.dumps(payload), encoding='utf-8')
        with self.assertRaises(ValueError):
            peer.extract_response('claude', output)

    def test_multiple_usage_models_do_not_identify_the_responder(self):
        output = self.root / 'ambiguous'
        output.mkdir()
        payload = {'subtype': 'success', 'result': 'Answer', 'modelUsage': {
            'claude-opus-5': {'outputTokens': 200}, 'claude-haiku-4-5-20251001': {'outputTokens': 10}}}
        (output / 'stdout.log').write_text(json.dumps(payload), encoding='utf-8')
        self.assertIsNone(peer.extract_response('claude', output)[1])
        payload['model'] = 'claude-opus-5'
        (output / 'stdout.log').write_text(json.dumps(payload), encoding='utf-8')
        self.assertEqual(peer.extract_response('claude', output)[1], 'claude-opus-5')

    def test_wrong_model_is_not_accepted_and_remains_inspectable(self):
        payload = {'subtype': 'success', 'model': 'claude-haiku-4-5-20251001', 'result': 'Wrong-model answer',
                   'usage': {'output_tokens': 4}, 'total_cost_usd': 0.01}
        code, out, receipt, summary = self.invoke_claude(payload)
        self.assertEqual(code, 2)
        self.assertEqual(receipt['execution_status'], 'NOT RUN')
        self.assertEqual(receipt['model_identity']['status'], 'MISMATCH')
        self.assertEqual(summary['requested_model'], 'opus')
        self.assertEqual(summary['reported_model'], payload['model'])
        self.assertEqual(summary['model_identity'], receipt['model_identity'])
        self.assertIn('Wrong-model answer', (out / 'response.md').read_text())
        self.assertEqual(hashlib.sha256((out / 'response.md').read_bytes()).hexdigest(),
                         receipt['response_sha256'])
        self.assertEqual(receipt['usage']['reported_cost_usd'], 0.01)

    def test_identity_is_visible_for_exact_family_and_unknown_cases(self):
        for requested, reported, status in [('claude-opus-5', 'claude-opus-5', 'MATCH'),
                                             ('opus', 'claude-opus-5', 'FAMILY_MATCH'),
                                             ('opus', None, 'UNVERIFIED')]:
            with self.subTest(requested=requested, reported=reported):
                code, _, receipt, summary = self.invoke_claude(
                    {'subtype': 'success', 'model': reported, 'result': 'Answer'}, model=requested)
                self.assertEqual(code, 0)
                self.assertEqual(receipt['execution_status'], 'PASS')
                self.assertEqual(summary['model_identity']['status'], status)

    def test_aliases_are_not_claimed_to_be_exact_model_ids(self):
        cases = [('claude', 'opus', 'opus', 'UNVERIFIED'),
                 ('claude', 'sonnet', 'claude-3-5-sonnet-20241022', 'FAMILY_MATCH'),
                 ('claude', 'opus', 'claude-sonnet-4-6', 'MISMATCH'),
                 ('claude', 'claude-sonnet-4-5', 'claude-sonnet-4-5-20250929', 'UNVERIFIED'),
                 ('claude', 'claude-sonnet-4-5-20250929', 'claude-sonnet-4-5-20260929', 'MISMATCH'),
                 ('claude', 'claude-opus-5', 'opus', 'UNVERIFIED'),
                 ('codex', 'gpt-5.6-sol', 'gpt-5.5', 'MISMATCH'),
                 ('codex', 'gpt-5.6-sol', 'gpt-5.6-sol', 'MATCH'),
                 ('codex', 'gpt-5.6-sol', 'provider-alias', 'UNVERIFIED'),
                 ('codex', 'default', 'default', 'UNVERIFIED'),
                 ('codex', 'team-alias', 'gpt-5.6-sol', 'UNVERIFIED')]
        for provider, requested, reported, status in cases:
            with self.subTest(provider=provider, requested=requested, reported=reported):
                self.assertEqual(peer.model_identity(provider, requested, reported)['status'], status)

    def test_executable_path_survives_changing_child_directory(self):
        fake = self.root / 'fake-native.exe'
        fake.write_bytes(b'fixture')
        before = Path.cwd()
        try:
            os.chdir(self.root)
            self.assertEqual(Path(peer.native_executable('./fake-native.exe')), fake.resolve())
        finally:
            os.chdir(before)

    def test_codex_requires_artifact_and_completed_turn(self):
        output = self.root / 'codex'
        output.mkdir()
        (output / 'stdout.log').write_text('{"type":"thread.started"}\n', encoding='utf-8')
        (output / 'provider-response.md').write_text('partial answer', encoding='utf-8')
        with self.assertRaises(ValueError):
            peer.extract_response('codex', output)
        (output / 'stdout.log').write_text('{"type":"turn.completed"}\n', encoding='utf-8')
        self.assertEqual(peer.extract_response('codex', output)[0], 'partial answer\n')

    def test_conflicting_codex_model_reports_stay_unverified(self):
        output = self.root / 'codex-models'
        output.mkdir()
        (output / 'provider-response.md').write_text('Answer', encoding='utf-8')
        events = [{'type': 'thread.started', 'model': 'gpt-5.6-sol'},
                  {'type': 'turn.completed', 'model': 'gpt-5.5'}]
        (output / 'stdout.log').write_text('\n'.join(map(json.dumps, events)), encoding='utf-8')
        self.assertIsNone(peer.extract_response('codex', output)[1])

    def test_codex_malformed_event_is_not_a_valid_answer(self):
        output = self.root / 'malformed'
        output.mkdir()
        (output / 'provider-response.md').write_text('answer', encoding='utf-8')
        (output / 'stdout.log').write_text('[]\n{"type":"turn.completed"}\n', encoding='utf-8')
        with self.assertRaises(ValueError):
            peer.extract_response('codex', output)


    def test_usage_preserves_provider_units_and_zero(self):
        output = self.root / 'usage'
        output.mkdir()
        (output / 'stdout.log').write_text(json.dumps({
            'usage': {'input_tokens': 0, 'cache_read_input_tokens': 120, 'output_tokens': 9},
            'total_cost_usd': 0.02}), encoding='utf-8')
        usage = peer.extract_usage('claude', output)
        self.assertEqual(usage['tokens'], {'input_tokens': 0, 'output_tokens': 9,
                                         'cache_read_input_tokens': 120})
        self.assertEqual(usage['reported_cost_usd'], 0.02)
        (output / 'stdout.log').write_text(json.dumps({'type': 'turn.completed', 'usage': {
            'input_tokens': 100, 'cached_input_tokens': 60, 'output_tokens': 10}}), encoding='utf-8')
        usage = peer.extract_usage('codex', output)
        self.assertEqual(usage['tokens']['input_tokens'], 100)
        self.assertEqual(usage['tokens']['cached_input_tokens'], 60)
        self.assertNotIn('reported_cost_usd', usage)

    def test_usage_missing_or_invalid_stays_unknown(self):
        output = self.root / 'unknown-usage'
        output.mkdir()
        for content in ['bad json', '[]', '{"usage":null}',
                        '{"usage":{"input_tokens":true,"output_tokens":-1}}']:
            (output / 'stdout.log').write_text(content, encoding='utf-8')
            self.assertIsNone(peer.extract_usage('claude', output))

    def test_failure_usage_preserves_reported_zero_and_paid_attempts(self):
        for cost in (0, 0.03):
            with self.subTest(cost=cost):
                payload = {'subtype': 'error_during_execution', 'is_error': True,
                           'usage': {'input_tokens': 0, 'output_tokens': 0}, 'total_cost_usd': cost}
                code, _, receipt, _ = self.invoke_claude(payload, exit_code=1)
                self.assertEqual(code, 2)
                self.assertEqual(receipt['execution_status'], 'NOT RUN')
                self.assertEqual(receipt['usage']['reported_cost_usd'], cost)
                self.assertEqual(receipt['usage']['result_status'], 'error_during_execution')

    def test_codex_failed_turn_usage_is_not_lost(self):
        output = self.root / 'codex-failed-usage'
        output.mkdir()
        (output / 'stdout.log').write_text(json.dumps({'type': 'turn.failed',
            'usage': {'input_tokens': 5, 'output_tokens': 2}}), encoding='utf-8')
        usage = peer.extract_usage('codex', output)
        self.assertEqual(usage['tokens']['output_tokens'], 2)
        self.assertEqual(usage['result_status'], 'turn.failed')


class InstallerTests(unittest.TestCase):
    def test_install_drift_backup_and_exact_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, target = root / 'source', root / 'installed'
            source.mkdir()
            (source / 'SKILL.md').write_text('source v1')
            self.assertTrue(installer.install(source, target))
            self.assertTrue(installer.install(source, target, check=True))
            (target / 'local-note.md').write_text('keep me')
            self.assertFalse(installer.install(source, target, check=True))
            with self.assertRaises(ValueError):
                installer.install(source, target)
            self.assertTrue(installer.install(source, target, replace=True))
            backups = list((root / '.install-backups').iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual((backups[0] / 'local-note.md').read_text(), 'keep me')
            self.assertEqual(installer.inventory(source), installer.inventory(target))


class PackageTests(unittest.TestCase):
    def test_markdown_local_links_resolve(self):
        for path in ROOT.rglob('*.md'):
            if any(p.startswith('.') for p in path.relative_to(ROOT).parts):
                continue
            text = path.read_text(encoding='utf-8-sig')
            for target in re.findall(r'\]\(([^)]+)\)', text):
                if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
                    continue
                target = target.split('#', 1)[0]
                if target:
                    self.assertTrue((path.parent / target).exists(), f'{path}: broken link {target}')

    def test_research_control_arithmetic(self):
        ai = (900 * 8 + 100 * 40) / 1000
        plain = (100 * 6 + 900 * 35) / 1000
        self.assertAlmostEqual(ai, 11.2)
        self.assertAlmostEqual(plain, 32.1)
        self.assertGreater(8, 6)
        self.assertGreater(40, 35)
        self.assertAlmostEqual((plain - ai) / plain, .6510903427)


if __name__ == '__main__':
    unittest.main()
