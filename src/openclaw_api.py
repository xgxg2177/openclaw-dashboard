"""OpenClaw API wrapper.

This module provides a stable interface for dashboard code. It defaults to
mock data and supports dependency injection for future MCP integration.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
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

    def api_usage(self) -> dict[str, Any]:
        """Return API usage statistics."""


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

    def api_usage(self) -> dict[str, Any]:
        return {
            "today_calls": 26,
            "token_input": 16420,
            "token_output": 4244,
            "cost_usd": 0.29,
            "recent_calls": [
                {
                    "timestamp": (datetime.now() - timedelta(minutes=1)).isoformat(timespec="seconds"),
                    "endpoint": "get_status",
                    "token_input": 182,
                    "token_output": 46,
                    "cost_usd": 0.0021,
                }
            ],
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

    @staticmethod
    def _state_file_path() -> Path:
        configured = os.getenv("OPENCLAW_STATE_FILE")
        if configured:
            return Path(configured).expanduser()
        return Path.home() / ".openclaw" / "workspace" / ".state.json"

    @staticmethod
    def _sessions_dir_path() -> Path:
        configured = os.getenv("CODEX_SESSIONS_DIR")
        if configured:
            return Path(configured).expanduser()
        return Path.home() / ".codex" / "sessions"

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        if not isinstance(value, str) or not value.strip():
            return None
        candidate = value.strip()
        if candidate.endswith("Z"):
            candidate = f"{candidate[:-1]}+00:00"
        try:
            dt = datetime.fromisoformat(candidate)
        except ValueError:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    def _default_state(self) -> dict[str, Any]:
        now = self._now_iso()
        return {
            "status": "idle",
            "current_task": "暂无任务",
            "started_at": now,
            "progress": 0,
            "last_update": now,
            "activity_log": [],
            "api_usage": {
                "today_calls": 0,
                "token_input": 0,
                "token_output": 0,
                "cost_usd": 0.0,
                "recent_calls": [],
            },
        }

    def _ensure_state_file(self) -> dict[str, Any]:
        state_path = self._state_file_path()
        default_state = self._default_state()

        try:
            state_path.parent.mkdir(parents=True, exist_ok=True)
            if not state_path.exists():
                state_path.write_text(
                    json.dumps(default_state, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                return default_state

            raw = state_path.read_text(encoding="utf-8")
            if not raw.strip():
                state_path.write_text(
                    json.dumps(default_state, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                return default_state

            data = json.loads(raw)
            if not isinstance(data, dict):
                return default_state

            merged = default_state.copy()
            merged.update({k: v for k, v in data.items() if k in merged})

            if not isinstance(merged.get("activity_log"), list):
                merged["activity_log"] = []

            api_usage = merged.get("api_usage")
            if not isinstance(api_usage, dict):
                merged["api_usage"] = default_state["api_usage"]
            else:
                merged_api_usage = default_state["api_usage"].copy()
                merged_api_usage.update({k: v for k, v in api_usage.items() if k in merged_api_usage})
                if not isinstance(merged_api_usage.get("recent_calls"), list):
                    merged_api_usage["recent_calls"] = []
                merged["api_usage"] = merged_api_usage

            return merged
        except Exception:
            return default_state

    @staticmethod
    def _extract_json_argument(arguments: Any, key: str, default: str) -> str:
        if not isinstance(arguments, str):
            return default
        try:
            parsed = json.loads(arguments)
        except json.JSONDecodeError:
            return default
        value = parsed.get(key)
        if value is None:
            return default
        return str(value)

    def _collect_codex_usage(self) -> dict[str, Any]:
        sessions_dir = self._sessions_dir_path()
        today = datetime.now(timezone.utc).date()

        session_count = 0
        total_tokens_today = 0
        recent_calls: list[dict[str, Any]] = []
        latest_rate_limit: dict[str, Any] | None = None
        latest_rate_limit_time: datetime | None = None

        if not sessions_dir.exists():
            return {
                "today_sessions": 0,
                "today_token_usage": 0,
                "recent_calls": [],
                "rate_limit": None,
            }

        for file_path in sorted(sessions_dir.rglob("*.jsonl")):
            token_events: list[tuple[datetime, int]] = []
            call_events: list[tuple[datetime, str]] = []
            session_date: datetime.date | None = None
            session_total_tokens = 0

            try:
                for line in file_path.read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    timestamp = self._parse_datetime(record.get("timestamp"))
                    record_type = record.get("type")

                    if record_type == "session_meta":
                        payload = record.get("payload", {})
                        meta_dt = self._parse_datetime(payload.get("timestamp"))
                        session_date = (meta_dt or timestamp).date() if (meta_dt or timestamp) else None

                    if record_type == "event_msg":
                        payload = record.get("payload", {})
                        payload_type = payload.get("type")

                        if payload_type == "token_count":
                            total_usage = (payload.get("info") or {}).get("last_token_usage") or {}
                            last_total = int(total_usage.get("total_tokens", 0) or 0)
                            if timestamp is not None:
                                token_events.append((timestamp, last_total))
                            session_total_tokens = max(session_total_tokens, last_total)

                            rate_limit = payload.get("rate_limits")
                            if isinstance(rate_limit, dict) and timestamp is not None:
                                if latest_rate_limit_time is None or timestamp > latest_rate_limit_time:
                                    latest_rate_limit = rate_limit
                                    latest_rate_limit_time = timestamp

                    if record_type == "response_item":
                        payload = record.get("payload", {})
                        if payload.get("type") == "function_call" and timestamp is not None:
                            name = str(payload.get("name") or "tool_call")
                            command = self._extract_json_argument(payload.get("arguments"), "cmd", "")
                            task = f"{name}: {command}" if command else name
                            call_events.append((timestamp, task))

                inferred_date = session_date
                if inferred_date is None:
                    inferred_date = self._parse_datetime(file_path.stem).date() if self._parse_datetime(file_path.stem) else None

                if inferred_date != today:
                    continue

                session_count += 1
                total_tokens_today += session_total_tokens

                token_events.sort(key=lambda item: item[0])
                for call_time, task in call_events:
                    token_cost = 0
                    for token_time, token_value in token_events:
                        if token_time >= call_time:
                            token_cost = token_value
                            break
                    recent_calls.append(
                        {
                            "timestamp": call_time.isoformat(timespec="seconds"),
                            "task": task,
                            "token_usage": token_cost,
                        }
                    )
            except Exception:
                continue

        recent_calls.sort(key=lambda item: item.get("timestamp", ""), reverse=True)

        rate_limit = None
        if isinstance(latest_rate_limit, dict):
            primary = latest_rate_limit.get("primary") if isinstance(latest_rate_limit.get("primary"), dict) else {}
            secondary = latest_rate_limit.get("secondary") if isinstance(latest_rate_limit.get("secondary"), dict) else {}
            rate_limit = {
                "limit_id": str(latest_rate_limit.get("limit_id") or ""),
                "primary_used_percent": float(primary.get("used_percent", 0.0) or 0.0),
                "secondary_used_percent": float(secondary.get("used_percent", 0.0) or 0.0),
                "primary_resets_at": int(primary.get("resets_at", 0) or 0),
                "secondary_resets_at": int(secondary.get("resets_at", 0) or 0),
            }

        return {
            "today_sessions": session_count,
            "today_token_usage": total_tokens_today,
            "recent_calls": recent_calls[:10],
            "rate_limit": rate_limit,
        }

    def _collect_openclaw_usage(self, state: dict[str, Any]) -> dict[str, Any]:
        provider_usage = self._provider_call("api_usage", {})
        provider_activity = self.get_recent_activity()

        state_api_usage = state.get("api_usage") if isinstance(state.get("api_usage"), dict) else {}
        today_calls = int(state_api_usage.get("today_calls", 0) or 0)
        token_input = int(state_api_usage.get("token_input", 0) or 0)
        token_output = int(state_api_usage.get("token_output", 0) or 0)
        cost_usd = float(state_api_usage.get("cost_usd", 0.0) or 0.0)

        if isinstance(provider_usage, dict):
            today_calls = max(today_calls, int(provider_usage.get("today_calls", 0) or 0))
            token_input = max(token_input, int(provider_usage.get("token_input", 0) or 0))
            token_output = max(token_output, int(provider_usage.get("token_output", 0) or 0))
            cost_usd = max(cost_usd, float(provider_usage.get("cost_usd", 0.0) or 0.0))

        recent_calls: list[dict[str, Any]] = []
        source_recent = state_api_usage.get("recent_calls")
        if isinstance(source_recent, list):
            for item in source_recent:
                if not isinstance(item, dict):
                    continue
                recent_calls.append(
                    {
                        "timestamp": item.get("timestamp"),
                        "endpoint": str(item.get("endpoint") or "unknown"),
                        "token_input": int(item.get("token_input", 0) or 0),
                        "token_output": int(item.get("token_output", 0) or 0),
                        "cost_usd": float(item.get("cost_usd", 0.0) or 0.0),
                    }
                )

        if isinstance(provider_usage, dict) and isinstance(provider_usage.get("recent_calls"), list):
            for item in provider_usage["recent_calls"]:
                if not isinstance(item, dict):
                    continue
                recent_calls.append(
                    {
                        "timestamp": item.get("timestamp"),
                        "endpoint": str(item.get("endpoint") or "unknown"),
                        "token_input": int(item.get("token_input", 0) or 0),
                        "token_output": int(item.get("token_output", 0) or 0),
                        "cost_usd": float(item.get("cost_usd", 0.0) or 0.0),
                    }
                )

        if not recent_calls:
            for activity in provider_activity:
                activity_type = str(activity.get("type") or "")
                if activity_type not in {"tool_call", "command"}:
                    continue
                recent_calls.append(
                    {
                        "timestamp": activity.get("timestamp"),
                        "endpoint": str(activity.get("action") or "unknown"),
                        "token_input": 0,
                        "token_output": 0,
                        "cost_usd": 0.0,
                    }
                )

        recent_calls.sort(key=lambda item: str(item.get("timestamp") or ""), reverse=True)
        return {
            "today_calls": today_calls,
            "token_input": token_input,
            "token_output": token_output,
            "cost_usd": round(cost_usd, 6),
            "recent_calls": recent_calls[:10],
        }

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

    def get_work_status(self) -> dict[str, Any]:
        """获取实时工作状态（工作中/空闲/思考中/执行中）。"""
        state = self._ensure_state_file()
        activity_log = state.get("activity_log") if isinstance(state.get("activity_log"), list) else []

        normalized_activity: list[dict[str, Any]] = []
        for item in activity_log[-20:]:
            if not isinstance(item, dict):
                continue
            normalized_activity.append(
                {
                    "timestamp": item.get("timestamp"),
                    "message": str(item.get("message") or ""),
                    "type": str(item.get("type") or "info"),
                }
            )

        return {
            "status": str(state.get("status") or "idle"),
            "current_task": str(state.get("current_task") or "暂无任务"),
            "started_at": state.get("started_at"),
            "progress": int(state.get("progress", 0) or 0),
            "last_update": state.get("last_update") or self._now_iso(),
            "activity_log": normalized_activity,
        }

    def get_usage(self) -> dict[str, Any]:
        """获取 Codex CLI 与 OpenClaw API 用量统计。"""
        state = self._ensure_state_file()
        return {
            "updated_at": self._now_iso(),
            "codex": self._collect_codex_usage(),
            "openclaw_api": self._collect_openclaw_usage(state),
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


def get_work_status() -> dict[str, Any]:
    """获取实时工作状态（工作中/空闲/思考中/执行中）。"""
    return _default_api.get_work_status()


def get_usage() -> dict[str, Any]:
    """获取 Codex CLI 与 OpenClaw API 用量统计。"""
    return _default_api.get_usage()


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
