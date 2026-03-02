"""OpenClaw API wrapper.

This module provides a stable interface for dashboard code. It defaults to
mock data and supports dependency injection for future MCP integration.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Protocol


class OpenClawProvider(Protocol):
    """Provider interface for OpenClaw data backends."""

    def sessions_list(self) -> list[dict[str, Any]]:
        """Return active sessions list."""

    def session_status(self) -> dict[str, Any]:
        """Return current runtime status."""

    def agents_list(self) -> list[dict[str, Any]]:
        """Return loaded skills/agents list."""

    def config(self) -> dict[str, Any]:
        """Return runtime configuration."""

    def recent_activity(self) -> list[dict[str, Any]]:
        """Return latest tool/command/file activity."""

    def performance_metrics(self) -> dict[str, Any]:
        """Return performance metrics."""


@dataclass
class MockOpenClawProvider:
    """Fallback provider used when MCP data is not available."""

    def sessions_list(self) -> list[dict[str, Any]]:
        now = datetime.now()
        return [
            {
                "id": "sess-001",
                "title": "Dashboard Build",
                "status": "active",
                "created_at": (now - timedelta(hours=5, minutes=35)).isoformat(timespec="seconds"),
                "last_activity_at": (now - timedelta(minutes=2)).isoformat(timespec="seconds"),
                "message_count": 48,
            },
            {
                "id": "sess-002",
                "title": "Bug Fix",
                "status": "idle",
                "created_at": (now - timedelta(hours=17)).isoformat(timespec="seconds"),
                "last_activity_at": (now - timedelta(hours=1, minutes=12)).isoformat(timespec="seconds"),
                "message_count": 21,
            },
            {
                "id": "sess-003",
                "title": "Release Notes Draft",
                "status": "active",
                "created_at": (now - timedelta(hours=2, minutes=9)).isoformat(timespec="seconds"),
                "last_activity_at": (now - timedelta(minutes=8)).isoformat(timespec="seconds"),
                "message_count": 12,
            },
        ]

    def session_status(self) -> dict[str, Any]:
        return {
            "status": "online",
            "current_task": "Optimizing dashboard content",
            "runtime_seconds": 20640,
        }

    def agents_list(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "skill-creator",
                "description": "Guide for creating effective Codex skills",
                "loaded": True,
                "source": "builtin",
            },
            {
                "name": "skill-installer",
                "description": "Install Codex skills from curated sources",
                "loaded": True,
                "source": "builtin",
            },
            {
                "name": "issue-tracker",
                "description": "Issue template and execution workflow helper",
                "loaded": False,
                "source": "custom",
            },
        ]

    def config(self) -> dict[str, Any]:
        return {
            "model": "gpt-5.3-codex",
            "token_limit": 128000,
            "token_used": 31240,
            "version": "v0.4.2",
            "environment": "development",
        }

    def recent_activity(self) -> list[dict[str, Any]]:
        now = datetime.now()
        return [
            {
                "type": "tool_call",
                "action": "sessions_list",
                "detail": "Fetched active sessions",
                "timestamp": (now - timedelta(minutes=1, seconds=10)).isoformat(timespec="seconds"),
            },
            {
                "type": "command",
                "action": "pytest",
                "detail": "Executed dashboard API tests",
                "timestamp": (now - timedelta(minutes=4, seconds=8)).isoformat(timespec="seconds"),
            },
            {
                "type": "file",
                "action": "write",
                "detail": "Updated src/templates/index.html",
                "timestamp": (now - timedelta(minutes=7, seconds=24)).isoformat(timespec="seconds"),
            },
            {
                "type": "tool_call",
                "action": "agents_list",
                "detail": "Loaded skill state",
                "timestamp": (now - timedelta(minutes=9, seconds=33)).isoformat(timespec="seconds"),
            },
        ]

    def performance_metrics(self) -> dict[str, Any]:
        return {
            "response_time_ms": 128,
            "request_success_rate": 99.2,
            "error_count": 1,
        }


class OpenClawAPI:
    """Application-facing API wrapper for OpenClaw runtime data."""

    def __init__(self, provider: OpenClawProvider | None = None) -> None:
        self.provider = provider or MockOpenClawProvider()

    def _provider_call(self, method_name: str, default: Any) -> Any:
        method = getattr(self.provider, method_name, None)
        if not callable(method):
            return default
        try:
            return method()
        except Exception:
            return default

    def get_status(self) -> dict[str, Any]:
        """获取运行状态（在线/离线，当前任务，运行时长）。"""
        status = self._provider_call("session_status", {})
        if not isinstance(status, dict):
            return {"status": "offline", "current_task": None, "runtime_seconds": 0}
        return {
            "status": status.get("status", "offline"),
            "current_task": status.get("current_task"),
            "runtime_seconds": int(status.get("runtime_seconds", 0) or 0),
        }

    def get_sessions(self) -> list[dict[str, Any]]:
        """获取活跃会话列表。"""
        sessions = self._provider_call("sessions_list", [])
        if not isinstance(sessions, list):
            return []

        result: list[dict[str, Any]] = []
        for session in sessions:
            if not isinstance(session, dict):
                continue
            result.append(
                {
                    "id": str(session.get("id", "")),
                    "title": str(session.get("title") or "Untitled Session"),
                    "status": str(session.get("status") or "idle"),
                    "created_at": session.get("created_at"),
                    "last_activity_at": session.get("last_activity_at"),
                    "message_count": int(session.get("message_count", 0) or 0),
                }
            )
        return result

    def get_skills(self) -> list[dict[str, Any]]:
        """获取已加载技能列表。"""
        skills = self._provider_call("agents_list", [])
        if not isinstance(skills, list):
            return []

        result: list[dict[str, Any]] = []
        for skill in skills:
            if not isinstance(skill, dict):
                continue
            result.append(
                {
                    "name": str(skill.get("name") or "unknown-skill"),
                    "description": str(skill.get("description") or "No description"),
                    "loaded": bool(skill.get("loaded", False)),
                    "source": str(skill.get("source") or "builtin"),
                }
            )
        return result

    def get_config(self) -> dict[str, Any]:
        """获取配置信息（模型、token、版本等）。"""
        config = self._provider_call("config", {})
        if not isinstance(config, dict):
            return {}
        if not config:
            return {}
        return {
            "model": str(config.get("model") or "unknown"),
            "token_limit": int(config.get("token_limit", 0) or 0),
            "token_used": int(config.get("token_used", 0) or 0),
            "version": str(config.get("version") or "v0.0.0"),
            "environment": str(config.get("environment") or "unknown"),
        }

    def get_recent_activity(self) -> list[dict[str, Any]]:
        """获取最近活动日志。"""
        activities = self._provider_call("recent_activity", [])
        if not isinstance(activities, list):
            return []

        result: list[dict[str, Any]] = []
        for activity in activities:
            if not isinstance(activity, dict):
                continue
            result.append(
                {
                    "type": str(activity.get("type") or "unknown"),
                    "action": str(activity.get("action") or "unknown"),
                    "detail": str(activity.get("detail") or ""),
                    "timestamp": activity.get("timestamp"),
                }
            )
        return result

    def get_metrics(self) -> dict[str, Any]:
        """获取性能指标。"""
        metrics = self._provider_call("performance_metrics", {})
        if not isinstance(metrics, dict):
            return {"response_time_ms": 0, "request_success_rate": 0.0, "error_count": 0}
        return {
            "response_time_ms": int(metrics.get("response_time_ms", 0) or 0),
            "request_success_rate": float(metrics.get("request_success_rate", 0.0) or 0.0),
            "error_count": int(metrics.get("error_count", 0) or 0),
        }


_default_api = OpenClawAPI()


def get_status() -> dict[str, Any]:
    """获取运行状态（在线/离线，当前任务，运行时长）。"""
    return _default_api.get_status()


def get_sessions() -> list[dict[str, Any]]:
    """获取活跃会话列表。"""
    return _default_api.get_sessions()


def get_skills() -> list[dict[str, Any]]:
    """获取已加载技能列表。"""
    return _default_api.get_skills()


def get_config() -> dict[str, Any]:
    """获取配置信息（模型、token、版本等）。"""
    return _default_api.get_config()


def get_recent_activity() -> list[dict[str, Any]]:
    """获取最近活动日志。"""
    return _default_api.get_recent_activity()


def get_metrics() -> dict[str, Any]:
    """获取性能指标。"""
    return _default_api.get_metrics()
