from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

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
                   'modelUsage': {'helper': {'outputTokens': 10}, 'selected-opus': {'outputTokens': 200}}}
        (output / 'stdout.log').write_text(json.dumps(payload), encoding='utf-8')
        answer, model = peer.extract_response('claude', output)
        self.assertEqual(model, 'selected-opus')
        self.assertIn('Useful answer', answer)
        payload['is_error'] = True
        (output / 'stdout.log').write_text(json.dumps(payload), encoding='utf-8')
        with self.assertRaises(ValueError):
            peer.extract_response('claude', output)

    def test_codex_requires_artifact_and_completed_turn(self):
        output = self.root / 'codex'
        output.mkdir()
        (output / 'stdout.log').write_text('{"type":"thread.started"}\n', encoding='utf-8')
        (output / 'provider-response.md').write_text('partial answer', encoding='utf-8')
        with self.assertRaises(ValueError):
            peer.extract_response('codex', output)
        (output / 'stdout.log').write_text('{"type":"turn.completed"}\n', encoding='utf-8')
        self.assertEqual(peer.extract_response('codex', output)[0], 'partial answer\n')

    def test_codex_malformed_event_is_not_a_valid_answer(self):
        output = self.root / 'malformed'
        output.mkdir()
        (output / 'provider-response.md').write_text('answer', encoding='utf-8')
        (output / 'stdout.log').write_text('[]\n{"type":"turn.completed"}\n', encoding='utf-8')
        with self.assertRaises(ValueError):
            peer.extract_response('codex', output)


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
