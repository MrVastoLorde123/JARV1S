"""M23.20: filesystem persistence adapter for the current world model.

This boundary provides a concrete durable adapter behind the M23.19 store contract.
Persistence is explicit state retention; it does not establish truth or authority.
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from src.core.environment_world_model import EnvironmentWorldModel
from src.core.environment_world_model_store import (
    EnvironmentWorldModelStoreError,
)


class EnvironmentWorldModelPersistenceError(RuntimeError):
    """Raised when a persisted world-model artifact cannot be read or written safely."""


def _restore(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _restore(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_restore(item) for item in value]
    return value


def _json_safe(value: Any) -> Any:
    """Convert recursively frozen containers into JSON-compatible containers."""
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return [_json_safe(item) for item in value]
    return value


def _serialize_model(model: EnvironmentWorldModel) -> dict[str, Any]:
    return {
        "model_id": model.model_id,
        "environment_id": model.environment_id,
        "state_by_domain": _json_safe(model.state_by_domain),
        "represented_domains": _json_safe(model.represented_domains),
        "missing_domains": _json_safe(model.missing_domains),
        "context_ids": _json_safe(model.context_ids),
        "qualification_ids": _json_safe(model.qualification_ids),
        "provenance_ids": _json_safe(model.provenance_ids),
        "readiness_id": model.readiness_id,
        "source_bundle_id": model.source_bundle_id,
        "lineage": _json_safe(model.lineage),
    }


def _deserialize_model(payload: Any) -> EnvironmentWorldModel:
    if not isinstance(payload, dict):
        raise EnvironmentWorldModelPersistenceError("persisted payload must be an object")
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
        raise EnvironmentWorldModelPersistenceError(
            "persisted payload does not satisfy the world-model contract"
        ) from exc


class FileEnvironmentWorldModelStore:
    """Durable JSON-file adapter implementing the M23.19 store semantics."""

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)
        if not self._root.is_dir():
            raise EnvironmentWorldModelPersistenceError("root must be a directory")

    def _validate_environment_id(self, environment_id: str) -> None:
        if not isinstance(environment_id, str) or not environment_id.strip():
            raise ValueError("environment_id must be a non-empty string")
        if Path(environment_id).name != environment_id or environment_id in {".", ".."}:
            raise ValueError("environment_id must be a simple path-safe key")

    def _path_for(self, environment_id: str) -> Path:
        self._validate_environment_id(environment_id)
        return self._root / f"{environment_id}.json"

    def get(self, environment_id: str) -> EnvironmentWorldModel | None:
        path = self._path_for(environment_id)
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise EnvironmentWorldModelPersistenceError(
                "persisted world-model file could not be read"
            ) from exc
        model = _deserialize_model(payload)
        if model.environment_id != environment_id:
            raise EnvironmentWorldModelPersistenceError(
                "persisted model environment identity does not match store key"
            )
        return model

    def put(
        self,
        model: EnvironmentWorldModel,
        *,
        expected_model_id: str | None = None,
    ) -> EnvironmentWorldModel:
        if type(model) is not EnvironmentWorldModel:
            raise TypeError("model must be EnvironmentWorldModel")
        current = self.get(model.environment_id)
        if expected_model_id is not None:
            if not isinstance(expected_model_id, str) or not expected_model_id.strip():
                raise ValueError("expected_model_id must be a non-empty string when provided")
            if current is None:
                raise EnvironmentWorldModelPersistenceError("expected current model is absent")
            if current.model_id != expected_model_id:
                raise EnvironmentWorldModelPersistenceError(
                    "expected current model identity does not match persisted model"
                )

        path = self._path_for(model.environment_id)
        temporary = path.with_suffix(".json.tmp")
        try:
            temporary.write_text(
                json.dumps(_serialize_model(model), ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            temporary.replace(path)
        except (OSError, TypeError) as exc:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
            raise EnvironmentWorldModelPersistenceError(
                "world-model persistence write failed"
            ) from exc
        return model

    def remove(self, environment_id: str) -> EnvironmentWorldModel | None:
        path = self._path_for(environment_id)
        current = self.get(environment_id)
        if current is None:
            return None
        try:
            path.unlink()
        except OSError as exc:
            raise EnvironmentWorldModelPersistenceError(
                "world-model persistence removal failed"
            ) from exc
        return current


__all__ = [
    "EnvironmentWorldModelPersistenceError",
    "FileEnvironmentWorldModelStore",
    "EnvironmentWorldModelStoreError",
]
