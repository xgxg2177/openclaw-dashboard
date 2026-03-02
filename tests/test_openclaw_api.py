from __future__ import annotations

import unittest

from src.openclaw_api import OpenClawAPI, get_config, get_sessions, get_skills, get_status


class CustomProvider:
    def sessions_list(self):
        return [{"id": "sess-x", "title": "Custom", "status": "active"}]

    def session_status(self):
        return {"status": "online", "current_task": "Running tests"}

    def agents_list(self):
        return [{"name": "custom-skill", "loaded": True}]

    def config(self):
        return {"model": "test-model", "token_limit": 4096}


class FailingProvider:
    def sessions_list(self):
        raise RuntimeError("sessions unavailable")

    def session_status(self):
        raise RuntimeError("status unavailable")

    def agents_list(self):
        raise RuntimeError("skills unavailable")

    def config(self):
        raise RuntimeError("config unavailable")


class OpenClawAPITestCase(unittest.TestCase):
    def test_api_with_mock_provider_defaults(self):
        api = OpenClawAPI()

        status = api.get_status()
        sessions = api.get_sessions()
        skills = api.get_skills()
        config = api.get_config()

        self.assertIn(status["status"], {"online", "offline"})
        self.assertIn("current_task", status)

        self.assertIsInstance(sessions, list)
        self.assertTrue(sessions)
        self.assertTrue({"id", "title", "status"}.issubset(sessions[0].keys()))

        self.assertIsInstance(skills, list)
        self.assertTrue(skills)
        self.assertTrue({"name", "loaded"}.issubset(skills[0].keys()))

        self.assertIsInstance(config, dict)
        self.assertIn("model", config)
        self.assertIn("token_limit", config)

    def test_api_with_custom_provider(self):
        api = OpenClawAPI(provider=CustomProvider())

        self.assertEqual(api.get_status(), {"status": "online", "current_task": "Running tests"})
        self.assertEqual(api.get_sessions(), [{"id": "sess-x", "title": "Custom", "status": "active"}])
        self.assertEqual(api.get_skills(), [{"name": "custom-skill", "loaded": True}])
        self.assertEqual(api.get_config(), {"model": "test-model", "token_limit": 4096})

    def test_api_fallback_on_provider_error(self):
        api = OpenClawAPI(provider=FailingProvider())

        self.assertEqual(api.get_status(), {"status": "offline", "current_task": None})
        self.assertEqual(api.get_sessions(), [])
        self.assertEqual(api.get_skills(), [])
        self.assertEqual(api.get_config(), {})

    def test_module_level_functions_return_shapes(self):
        status = get_status()
        sessions = get_sessions()
        skills = get_skills()
        config = get_config()

        self.assertIn("status", status)
        self.assertIn("current_task", status)
        self.assertIsInstance(sessions, list)
        self.assertIsInstance(skills, list)
        self.assertIsInstance(config, dict)


if __name__ == "__main__":
    unittest.main()
