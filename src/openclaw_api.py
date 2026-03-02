"""OpenClaw API wrapper.

This module provides a stable interface for dashboard code. It defaults to
mock data and supports dependency injection for future MCP integration.
"""

from __future__ import annotations

from dataclasses import dataclass
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


@dataclass
class MockOpenClawProvider:
    """Fallback provider used when MCP data is not available."""

    def sessions_list(self) -> list[dict[str, Any]]:
        return [
            {"id": "sess-001", "title": "Dashboard Build", "status": "active"},
            {"id": "sess-002", "title": "Bug Fix", "status": "idle"},
        ]

    def session_status(self) -> dict[str, Any]:
        return {
            "status": "online",
            "current_task": "Implementing OpenClaw API wrapper",
        }

    def agents_list(self) -> list[dict[str, Any]]:
        return [
            {"name": "skill-creator", "loaded": True},
            {"name": "skill-installer", "loaded": True},
        ]

    def config(self) -> dict[str, Any]:
        return {
            "model": "gpt-5",
            "token_limit": 128000,
            "environment": "development",
        }


class OpenClawAPI:
    """Application-facing API wrapper for OpenClaw runtime data."""

    def __init__(self, provider: OpenClawProvider | None = None) -> None:
        self.provider = provider or MockOpenClawProvider()

    def get_status(self) -> dict[str, Any]:
        """获取运行状态（在线/离线，当前任务）。"""
        try:
            status = self.provider.session_status()
            return {
                "status": status.get("status", "offline"),
                "current_task": status.get("current_task"),
            }
        except Exception:
            return {"status": "offline", "current_task": None}

    def get_sessions(self) -> list[dict[str, Any]]:
        """获取活跃会话列表。"""
        try:
            sessions = self.provider.sessions_list()
            return sessions if isinstance(sessions, list) else []
        except Exception:
            return []

    def get_skills(self) -> list[dict[str, Any]]:
        """获取已加载技能列表。"""
        try:
            skills = self.provider.agents_list()
            return skills if isinstance(skills, list) else []
        except Exception:
            return []

    def get_config(self) -> dict[str, Any]:
        """获取配置信息（模型、token 等）。"""
        try:
            config = self.provider.config()
            return config if isinstance(config, dict) else {}
        except Exception:
            return {}


_default_api = OpenClawAPI()


def get_status() -> dict[str, Any]:
    """获取运行状态（在线/离线，当前任务）。"""
    return _default_api.get_status()


def get_sessions() -> list[dict[str, Any]]:
    """获取活跃会话列表。"""
    return _default_api.get_sessions()


def get_skills() -> list[dict[str, Any]]:
    """获取已加载技能列表。"""
    return _default_api.get_skills()


def get_config() -> dict[str, Any]:
    """获取配置信息（模型、token 等）。"""
    return _default_api.get_config()
