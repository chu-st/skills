from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/dual-model-review/scripts/configure.py"
spec = importlib.util.spec_from_file_location("review_configuration", SCRIPT)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)


def role(provider, product=None, model=None, transport="auto"):
    return {"provider": provider, "product": product or provider,
            "model": model, "transport": transport}


def profile():
    value = config.empty_profile()
    value["roles"] = {"orchestrator": role("anthropic", "Claude", "fable"),
                      "second": role("openai", "ChatGPT"),
                      "third": role("google", "Gemini")}
    return value


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.user = self.root / "user/review.json"
        self.env = mock.patch.dict(os.environ, {}, clear=True)
        self.env.start()
        self.user_patch = mock.patch.object(config, "user_path", return_value=self.user)
        self.user_patch.start()

    def tearDown(self):
        self.user_patch.stop()
        self.env.stop()
        self.tmp.cleanup()

    def save(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_template_is_neutral_and_needs_selection(self):
        value, source = config.load_profile()
        self.assertIsNone(source)
        self.assertEqual(list(value["roles"].values()), [None, None, None])
        result = config.plan(value)
        self.assertEqual(result["participants"], 2)
        self.assertEqual(result["missing_roles"], ["orchestrator", "second"])
        self.assertEqual(result["selection_status"], "NEEDS_CONFIGURATION")

    def test_third_is_opt_in_and_product_choices_are_preserved(self):
        value = profile()
        original = copy.deepcopy(value)
        two = config.plan(value)
        three = config.plan(value, 3)
        self.assertEqual(list(two["roles"]), ["orchestrator", "second"])
        self.assertEqual(three["roles"]["third"]["product"], "Gemini")
        self.assertEqual(two["roles"]["second"]["product"], "ChatGPT")
        self.assertIsNone(two["roles"]["second"]["model"])
        self.assertEqual(two["roles"]["orchestrator"]["model"], "fable")
        for result in (two, three):
            self.assertEqual(result["execution_status"], "NOT RUN")
            self.assertEqual(result["access_status"], "NOT CHECKED")
            self.assertEqual(result["identity_status"], "NOT CHECKED")
        self.assertEqual(value, original)

    def test_task_count_overrides_default_without_mutating_it(self):
        value = profile()
        value["default_participants"] = 3
        self.assertEqual(config.plan(value, 2)["participants"], 2)
        self.assertEqual(value["default_participants"], 3)

    def test_missing_third_does_not_downgrade_three(self):
        value = profile()
        value["roles"]["third"] = None
        self.assertEqual(config.plan(value)["selection_status"], "READY_TO_CHECK_ACCESS")
        result = config.plan(value, 3)
        self.assertEqual(result["participants"], 3)
        self.assertEqual(result["missing_roles"], ["third"])
        self.assertEqual(result["selection_status"], "NEEDS_CONFIGURATION")

    def test_arbitrary_providers_and_atomic_role_replacement(self):
        value = profile()
        replacement = role("future-provider", "Local runner", "model-z", "cli")
        result = config.plan(value, overrides={"second": replacement})
        self.assertEqual(result["roles"]["second"], replacement)
        self.assertEqual(value["roles"]["second"]["product"], "ChatGPT")
        with self.assertRaises(ValueError):
            config.plan(value, overrides={"second": {"model": "model-z"}})
        with self.assertRaises(ValueError):
            config.plan(value, overrides={"fourth": replacement})

    def test_provider_preference_and_explicit_same_provider_override(self):
        value = profile()
        value["roles"]["second"] = role("anthropic", "Claude", "sonnet")
        with self.assertRaises(ValueError):
            config.plan(value)
        result = config.plan(value, allow_same_provider=True)
        self.assertEqual(result["selection_status"], "READY_TO_CHECK_ACCESS")
        self.assertTrue(value["require_distinct_providers"])
        value["require_distinct_providers"] = False
        self.assertEqual(config.plan(value)["selection_status"], "READY_TO_CHECK_ACCESS")
        value["roles"]["second"]["model"] = "fable"
        value["roles"]["second"]["product"] = "Different interface"
        with self.assertRaisesRegex(ValueError, "same model"):
            config.plan(value, allow_same_provider=True)

    def test_inactive_third_does_not_affect_pair_provider_check(self):
        value = profile()
        value["roles"]["third"] = copy.deepcopy(value["roles"]["second"])
        self.assertEqual(config.plan(value)["participants"], 2)
        with self.assertRaises(ValueError):
            config.plan(value, 3)

    def test_path_precedence_and_no_implicit_merge(self):
        user = profile()
        user["default_participants"] = 3
        self.save(self.user, user)
        project = self.root / "project"
        project.mkdir()
        self.assertEqual(config.load_profile(project=project)[0], user)
        project_value = config.empty_profile()
        self.save(project / ".chust-review.json", project_value)
        self.assertEqual(config.load_profile(project=project)[0], project_value)
        env_path = self.save(self.root / "env.json", profile())
        os.environ["CHUST_REVIEW_CONFIG"] = str(env_path)
        self.assertEqual(config.load_profile(project=project)[1], str(env_path))
        explicit = self.save(self.root / "explicit.json", project_value)
        self.assertEqual(config.load_profile(explicit, project)[1], str(explicit))

    def test_explicit_missing_invalid_and_empty_env_never_fall_back(self):
        self.save(self.user, profile())
        with self.assertRaises(FileNotFoundError):
            config.load_profile(self.root / "missing.json")
        broken = self.root / "broken.json"
        broken.write_text("not json", encoding="utf-8")
        with self.assertRaises(ValueError):
            config.load_profile(broken)
        os.environ["CHUST_REVIEW_CONFIG"] = ""
        with self.assertRaises(ValueError):
            config.load_profile()
        os.environ["CHUST_REVIEW_CONFIG"] = str(self.root / "missing.json")
        with self.assertRaises(FileNotFoundError):
            config.load_profile()

    def test_schema_rejects_typos_and_wrong_types(self):
        mutations = [lambda p: p.update(schema_version=True),
                     lambda p: p.update(schema_version=2),
                     lambda p: p.update(default_participants=4),
                     lambda p: p.update(default_participants=True),
                     lambda p: p.update(require_distinct_providers="false"),
                     lambda p: p.update(unrecognized="value"),
                     lambda p: p["roles"]["second"].update(provider="OpenAI"),
                     lambda p: p["roles"]["second"].update(transport=[]),
                     lambda p: p["roles"]["second"].update(model=""),
                     lambda p: p["roles"].pop("third")]
        for mutate in mutations:
            value = profile()
            mutate(value)
            with self.subTest(value=value), self.assertRaises(ValueError):
                config.validate(value)

    def test_initialization_preserves_existing_file(self):
        config.initialize(self.user, profile())
        saved = self.user.read_bytes()
        with self.assertRaises(FileExistsError):
            config.initialize(self.user, config.empty_profile())
        self.assertEqual(self.user.read_bytes(), saved)

    def test_project_init_targets_project_not_existing_user(self):
        project = self.root / "project"
        project.mkdir()
        self.save(self.user, profile())
        self.assertEqual(config.select_path(project=project, for_write=True)[0],
                         project / ".chust-review.json")

    def test_cli_roundtrip_and_nonzero_incomplete_plan(self):
        path = self.root / "preferences.json"
        env = {**os.environ, "PYTHONUTF8": "1"}
        def invoke(*args):
            return subprocess.run([sys.executable, str(SCRIPT), *args, "--config", str(path)],
                                  capture_output=True, text=True, encoding="utf-8", timeout=15, env=env)
        initialized = invoke("init")
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        self.assertEqual(invoke("plan", "--participants", "3").returncode, 2)
        self.save(path, profile())
        planned = invoke("plan", "--participants", "3")
        self.assertEqual(planned.returncode, 0, planned.stderr)
        self.assertEqual(json.loads(planned.stdout)["roles"]["third"]["product"], "Gemini")
        self.assertEqual(invoke("init").returncode, 2)


if __name__ == "__main__":
    unittest.main()
