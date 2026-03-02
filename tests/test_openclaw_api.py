from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from src.openclaw_api import (
    OpenClawAPI,
    get_config,
    get_metrics,
    get_recent_activity,
    get_sessions,
    get_skills,
    get_status,
    get_usage,
    get_work_status,
)


class CustomProvider:
    def sessions_list(self):
        return [
            {
                "id": "sess-x",
                "title": "Custom",
                "status": "active",
                "created_at": "2026-03-02T11:00:00",
                "last_activity_at": "2026-03-02T11:10:00",
                "message_count": 8,
            }
        ]

    def session_status(self):
        return {"status": "online", "current_task": "Running tests", "runtime_seconds": 120}

    def agents_list(self):
        return [
            {
                "name": "custom-skill",
                "description": "Custom skill",
                "loaded": True,
                "source": "custom",
            }
        ]

    def config(self):
        return {"model": "test-model", "token_limit": 4096, "token_used": 256, "version": "v1.2.3"}

    def recent_activity(self):
        return [
            {
                "type": "command",
                "action": "pytest",
                "detail": "Executed tests",
                "timestamp": "2026-03-02T11:11:00",
            }
        ]

    def performance_metrics(self):
        return {"response_time_ms": 99, "request_success_rate": 100.0, "error_count": 0}

    def api_usage(self):
        return {
            "today_calls": 3,
            "token_input": 120,
            "token_output": 40,
            "cost_usd": 0.01,
            "recent_calls": [
                {
                    "timestamp": "2026-03-02T11:12:00+00:00",
                    "endpoint": "get_status",
                    "token_input": 30,
                    "token_output": 10,
                    "cost_usd": 0.002,
                }
            ],
        }


class FailingProvider:
    def sessions_list(self):
        raise RuntimeError("sessions unavailable")

    def session_status(self):
        raise RuntimeError("status unavailable")

    def agents_list(self):
        raise RuntimeError("skills unavailable")

    def config(self):
        raise RuntimeError("config unavailable")

    def recent_activity(self):
        raise RuntimeError("activity unavailable")

    def performance_metrics(self):
        raise RuntimeError("metrics unavailable")

    def api_usage(self):
        raise RuntimeError("api usage unavailable")


class OpenClawAPITestCase(unittest.TestCase):
    def setUp(self):
        self._old_state_file = os.environ.get("OPENCLAW_STATE_FILE")
        self._old_sessions_dir = os.environ.get("CODEX_SESSIONS_DIR")

    def tearDown(self):
        if self._old_state_file is None:
            os.environ.pop("OPENCLAW_STATE_FILE", None)
        else:
            os.environ["OPENCLAW_STATE_FILE"] = self._old_state_file

        if self._old_sessions_dir is None:
            os.environ.pop("CODEX_SESSIONS_DIR", None)
        else:
            os.environ["CODEX_SESSIONS_DIR"] = self._old_sessions_dir

    def test_api_with_mock_provider_defaults(self):
        api = OpenClawAPI()

        status = api.get_status()
        sessions = api.get_sessions()
        skills = api.get_skills()
        config = api.get_config()
        recent_activity = api.get_recent_activity()
        metrics = api.get_metrics()
        usage = api.get_usage()
        work_status = api.get_work_status()

        self.assertIn(status["status"], {"online", "offline"})
        self.assertIn("current_task", status)
        self.assertIn("runtime_seconds", status)

        self.assertIsInstance(sessions, list)
        self.assertTrue(sessions)
        self.assertTrue(
            {"id", "title", "status", "created_at", "last_activity_at", "message_count"}.issubset(
                sessions[0].keys(),
            )
        )

        self.assertIsInstance(skills, list)
        self.assertTrue(skills)
        self.assertTrue({"name", "description", "loaded", "source"}.issubset(skills[0].keys()))

        self.assertIsInstance(config, dict)
        self.assertIn("model", config)
        self.assertIn("token_limit", config)
        self.assertIn("token_used", config)
        self.assertIn("version", config)

        self.assertIsInstance(recent_activity, list)
        self.assertTrue(recent_activity)
        self.assertTrue({"type", "action", "detail", "timestamp"}.issubset(recent_activity[0].keys()))

        self.assertEqual(set(metrics.keys()), {"response_time_ms", "request_success_rate", "error_count"})
        self.assertIn("codex", usage)
        self.assertIn("openclaw_api", usage)
        self.assertIn("status", work_status)
        self.assertIn("current_task", work_status)
        self.assertIn("progress", work_status)

    def test_api_with_custom_provider(self):
        api = OpenClawAPI(provider=CustomProvider())

        self.assertEqual(
            api.get_status(),
            {"status": "online", "current_task": "Running tests", "runtime_seconds": 120},
        )
        self.assertEqual(
            api.get_sessions(),
            [
                {
                    "id": "sess-x",
                    "title": "Custom",
                    "status": "active",
                    "created_at": "2026-03-02T11:00:00",
                    "last_activity_at": "2026-03-02T11:10:00",
                    "message_count": 8,
                }
            ],
        )
        self.assertEqual(
            api.get_skills(),
            [
                {
                    "name": "custom-skill",
                    "description": "Custom skill",
                    "loaded": True,
                    "source": "custom",
                }
            ],
        )
        self.assertEqual(
            api.get_config(),
            {
                "model": "test-model",
                "token_limit": 4096,
                "token_used": 256,
                "version": "v1.2.3",
                "environment": "unknown",
            },
        )
        self.assertEqual(
            api.get_recent_activity(),
            [
                {
                    "type": "command",
                    "action": "pytest",
                    "detail": "Executed tests",
                    "timestamp": "2026-03-02T11:11:00",
                }
            ],
        )
        self.assertEqual(
            api.get_metrics(),
            {"response_time_ms": 99, "request_success_rate": 100.0, "error_count": 0},
        )
        usage = api.get_usage()
        self.assertEqual(usage["openclaw_api"]["today_calls"], 3)
        self.assertEqual(usage["openclaw_api"]["token_input"], 120)
        self.assertEqual(usage["openclaw_api"]["token_output"], 40)

    def test_api_fallback_on_provider_error(self):
        api = OpenClawAPI(provider=FailingProvider())

        self.assertEqual(api.get_status(), {"status": "offline", "current_task": None, "runtime_seconds": 0})
        self.assertEqual(api.get_sessions(), [])
        self.assertEqual(api.get_skills(), [])
        self.assertEqual(api.get_config(), {})
        self.assertEqual(api.get_recent_activity(), [])
        self.assertEqual(api.get_metrics(), {"response_time_ms": 0, "request_success_rate": 0.0, "error_count": 0})
        usage = api.get_usage()
        self.assertIn("codex", usage)
        self.assertIn("openclaw_api", usage)

    def test_module_level_functions_return_shapes(self):
        status = get_status()
        sessions = get_sessions()
        skills = get_skills()
        config = get_config()
        recent_activity = get_recent_activity()
        metrics = get_metrics()
        usage = get_usage()
        work_status = get_work_status()

        self.assertIn("status", status)
        self.assertIn("current_task", status)
        self.assertIn("runtime_seconds", status)
        self.assertIsInstance(sessions, list)
        self.assertIsInstance(skills, list)
        self.assertIsInstance(config, dict)
        self.assertIsInstance(recent_activity, list)
        self.assertIsInstance(metrics, dict)
        self.assertIsInstance(usage, dict)
        self.assertIsInstance(work_status, dict)

    def test_work_status_creates_state_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / ".state.json"
            os.environ["OPENCLAW_STATE_FILE"] = str(state_path)

            api = OpenClawAPI(provider=CustomProvider())
            status = api.get_work_status()

            self.assertTrue(state_path.exists())
            self.assertIn(status["status"], {"working", "idle", "thinking", "executing"})
            self.assertIn("current_task", status)
            self.assertIn("activity_log", status)

    def test_usage_reads_codex_sessions_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / ".state.json"
            today = datetime.now(timezone.utc).date()
            sessions_dir = Path(temp_dir) / "sessions" / f"{today.year:04d}" / f"{today.month:02d}" / f"{today.day:02d}"
            sessions_dir.mkdir(parents=True, exist_ok=True)
            os.environ["OPENCLAW_STATE_FILE"] = str(state_path)
            os.environ["CODEX_SESSIONS_DIR"] = str(Path(temp_dir) / "sessions")

            sample_session = sessions_dir / f"rollout-{today.isoformat()}T11-59-00-test.jsonl"
            sample_session.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "timestamp": f"{today.isoformat()}T03:59:00Z",
                                "type": "session_meta",
                                "payload": {"timestamp": f"{today.isoformat()}T03:59:00Z"},
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": f"{today.isoformat()}T04:00:00Z",
                                "type": "response_item",
                                "payload": {
                                    "type": "function_call",
                                    "name": "exec_command",
                                    "arguments": "{\"cmd\":\"pytest\"}",
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "timestamp": f"{today.isoformat()}T04:00:01Z",
                                "type": "event_msg",
                                "payload": {
                                    "type": "token_count",
                                    "info": {"last_token_usage": {"total_tokens": 123}},
                                    "rate_limits": {
                                        "limit_id": "codex",
                                        "primary": {"used_percent": 5.5, "resets_at": 1772432500},
                                        "secondary": {"used_percent": 1.2, "resets_at": 1773019300},
                                    },
                                },
                            }
                        ),
                    ]
                ),
                encoding="utf-8",
            )

            api = OpenClawAPI(provider=CustomProvider())
            usage = api.get_usage()
            self.assertGreaterEqual(usage["codex"]["today_sessions"], 1)
            self.assertGreaterEqual(usage["codex"]["today_token_usage"], 123)
            self.assertTrue(isinstance(usage["codex"]["recent_calls"], list))


if __name__ == "__main__":
    unittest.main()
