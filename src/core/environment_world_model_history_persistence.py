"""M23.22: filesystem persistence adapter for world-model history.

This boundary durably retains ordered descriptive world-model history without
introducing rollback, authority, truth, or synchronization semantics.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_history import (
    EnvironmentWorldModelHistory,
    EnvironmentWorldModelHistoryError,
)


class EnvironmentWorldModelHistoryPersistenceError(RuntimeError):
    """Raised when persisted world-model history cannot be read or written safely."""


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if hasattr(value, "items"):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_json_safe(item) for item in value]
    return value


def _restore(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _restore(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_restore(item) for item in value]
    return value


def _serialize_model(model: EnvironmentWorldModel) -> dict[str, Any]:
    return {
        "model_id": model.model_id,
        "environment_id": model.environment_id,
        "state_by_domain": _json_safe(model.state_by_domain),
        "represented_domains": list(model.represented_domains),
        "missing_domains": list(model.missing_domains),
        "context_ids": list(model.context_ids),
        "qualification_ids": list(model.qualification_ids),
        "provenance_ids": list(model.provenance_ids),
        "readiness_id": model.readiness_id,
        "source_bundle_id": model.source_bundle_id,
        "lineage": _json_safe(model.lineage),
    }


def _deserialize_model(payload: Any) -> EnvironmentWorldModel:
    if not isinstance(payload, dict):
        raise EnvironmentWorldModelHistoryPersistenceError("persisted model must be an object")
    try:
        return EnvironmentWorldModel(
            model_id=payload["model_id"],
            environment_id=payload["environment_id"],
            state_by_domain=_restore(payload["state_by_domain"]),
            represented_domains=tuple(payload["represented_domains"]),
            missing_domains=tuple(payload["missing_domains"]),
            context_ids=tuple(payload["context_ids"]),
            qualification_ids=tuple(payload["qualification_ids"]),
            provenance_ids=tuple(payload["provenance_ids"]),
            readiness_id=payload["readiness_id"],
            source_bundle_id=payload["source_bundle_id"],
            lineage=_restore(payload.get("lineage", {})),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise EnvironmentWorldModelHistoryPersistenceError(
            "persisted model does not satisfy the world-model contract"
        ) from exc


class FileEnvironmentWorldModelHistoryStore:
    """Filesystem-backed JSON store for ordered world-model histories."""

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)
        if not self._root.is_dir():
            raise EnvironmentWorldModelHistoryPersistenceError("root must be a directory")

    @staticmethod
    def _validate_environment_id(environment_id: str) -> None:
        if not isinstance(environment_id, str) or not environment_id.strip():
            raise ValueError("environment_id must be a non-empty string")
        if Path(environment_id).name != environment_id or environment_id in {".", ".."}:
            raise ValueError("environment_id must be a simple path-safe key")

    def _path_for(self, environment_id: str) -> Path:
        self._validate_environment_id(environment_id)
        return self._root / f"{environment_id}.json"

    def get(self, environment_id: str) -> EnvironmentWorldModelHistory | None:
        path = self._path_for(environment_id)
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise EnvironmentWorldModelHistoryPersistenceError(
                "persisted world-model history file could not be read"
            ) from exc
        if not isinstance(payload, dict):
            raise EnvironmentWorldModelHistoryPersistenceError("persisted history must be an object")
        if payload.get("environment_id") != environment_id:
            raise EnvironmentWorldModelHistoryPersistenceError(
                "persisted history environment identity does not match store key"
            )
        try:
            models = tuple(_deserialize_model(item) for item in payload["models"])
            return EnvironmentWorldModelHistory(
                environment_id=payload["environment_id"],
                models=models,
                lineage=_restore(payload.get("lineage", {})),
            )
        except (KeyError, TypeError, ValueError, EnvironmentWorldModelHistoryError) as exc:
            raise EnvironmentWorldModelHistoryPersistenceError(
                "persisted history does not satisfy the history contract"
            ) from exc

    def put(self, history: EnvironmentWorldModelHistory) -> EnvironmentWorldModelHistory:
        if type(history) is not EnvironmentWorldModelHistory:
            raise TypeError("history must be EnvironmentWorldModelHistory")
        path = self._path_for(history.environment_id)
        temporary = path.with_suffix(".json.tmp")
        payload = {
            "environment_id": history.environment_id,
            "models": [_serialize_model(model) for model in history.models],
            "lineage": _json_safe(history.lineage),
        }
        try:
            temporary.write_text(
                json.dumps(payload, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            temporary.replace(path)
        except OSError as exc:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
            raise EnvironmentWorldModelHistoryPersistenceError(
                "world-model history persistence write failed"
            ) from exc
        return history

    def remove(self, environment_id: str) -> EnvironmentWorldModelHistory | None:
        path = self._path_for(environment_id)
        history = self.get(environment_id)
        if history is None:
            return None
        try:
            path.unlink()
        except OSError as exc:
            raise EnvironmentWorldModelHistoryPersistenceError(
                "world-model history persistence removal failed"
            ) from exc
        return history


__all__ = [
    "EnvironmentWorldModelHistoryPersistenceError",
    "FileEnvironmentWorldModelHistoryStore",
]
