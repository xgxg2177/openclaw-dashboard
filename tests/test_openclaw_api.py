from __future__ import annotations

import unittest

from src.openclaw_api import (
    OpenClawAPI,
    get_config,
    get_metrics,
    get_recent_activity,
    get_sessions,
    get_skills,
    get_status,
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


class OpenClawAPITestCase(unittest.TestCase):
    def test_api_with_mock_provider_defaults(self):
        api = OpenClawAPI()

        status = api.get_status()
        sessions = api.get_sessions()
        skills = api.get_skills()
        config = api.get_config()
        recent_activity = api.get_recent_activity()
        metrics = api.get_metrics()

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

    def test_api_fallback_on_provider_error(self):
        api = OpenClawAPI(provider=FailingProvider())

        self.assertEqual(api.get_status(), {"status": "offline", "current_task": None, "runtime_seconds": 0})
        self.assertEqual(api.get_sessions(), [])
        self.assertEqual(api.get_skills(), [])
        self.assertEqual(api.get_config(), {})
        self.assertEqual(api.get_recent_activity(), [])
        self.assertEqual(api.get_metrics(), {"response_time_ms": 0, "request_success_rate": 0.0, "error_count": 0})

    def test_module_level_functions_return_shapes(self):
        status = get_status()
        sessions = get_sessions()
        skills = get_skills()
        config = get_config()
        recent_activity = get_recent_activity()
        metrics = get_metrics()

        self.assertIn("status", status)
        self.assertIn("current_task", status)
        self.assertIn("runtime_seconds", status)
        self.assertIsInstance(sessions, list)
        self.assertIsInstance(skills, list)
        self.assertIsInstance(config, dict)
        self.assertIsInstance(recent_activity, list)
        self.assertIsInstance(metrics, dict)


if __name__ == "__main__":
    unittest.main()
