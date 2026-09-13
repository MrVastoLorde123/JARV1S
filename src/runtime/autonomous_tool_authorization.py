"""Runtime-owned, request-bound authorization for resumed autonomous tool work."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


def tool_request_fingerprint(tool_name: str, arguments: Mapping[str, Any]) -> str:
    if not isinstance(tool_name, str) or not tool_name.strip():
        raise ValueError("tool_name must be a non-empty string")
    if not isinstance(arguments, Mapping):
        raise TypeError("arguments must be a mapping")
    payload = json.dumps(
        {"tool_name": tool_name.strip().lower(), "arguments": dict(arguments)},
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_tool_resume_authorization(tool_name: str, arguments: Mapping[str, Any]) -> dict[str, str]:
    return {
        "kind": "TOOL",
        "request_fingerprint": tool_request_fingerprint(tool_name, arguments),
    }


def matches_tool_resume_authorization(
    authorization: Mapping[str, Any] | None,
    tool_name: str,
    arguments: Mapping[str, Any],
) -> bool:
    if not isinstance(authorization, Mapping):
        return False
    if authorization.get("kind") != "TOOL":
        return False
    expected = authorization.get("request_fingerprint")
    if not isinstance(expected, str) or not expected.strip():
        return False
    return expected == tool_request_fingerprint(tool_name, arguments)


__all__ = [
    "build_tool_resume_authorization",
    "matches_tool_resume_authorization",
    "tool_request_fingerprint",
]
