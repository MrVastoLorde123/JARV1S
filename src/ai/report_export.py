from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from src.ai.evaluation import EvaluationDimension, ModelEvaluationReport
from src.ai.role_fitness import RoleFitnessResult


def report_as_dict(
    report: ModelEvaluationReport,
    role_fitness: Mapping[str, RoleFitnessResult] | None = None,
) -> dict[str, object]:
    observations: list[dict[str, object]] = []
    for observation in report.observations:
        response_text = None
        if observation.response is not None:
            response_text = str(observation.response.content)
        observations.append(
            {
                "case_id": observation.case_id,
                "model_id": observation.model_id,
                "outcome": observation.outcome.value,
                "passed": observation.passed,
                "scores": {dimension.value: score for dimension, score in observation.scores.items()},
                "error": observation.error,
                "latency_ms": observation.latency_ms,
                "response": response_text,
                "response_preview": observation.response_preview,
            }
        )

    payload: dict[str, object] = {
        "model_id": report.candidate.model_id,
        "provider_name": report.candidate.provider_name,
        "display_name": report.candidate.display_name,
        "overall_score": report.overall_score,
        "passed": report.passed,
        "model_failures": report.model_failures,
        "infrastructure_failures": report.infrastructure_failures,
        "average_latency_ms": report.average_latency_ms,
        "total_latency_ms": report.total_latency_ms,
        "dimension_scores": {dimension.value: score for dimension, score in report.dimension_scores.items()},
        "observations": observations,
        "trace": report.trace.as_dict() if report.trace else None,
    }

    if role_fitness:
        payload["role_fitness"] = {
            role_id: {
                "suitable": result.suitable,
                "weighted_score": result.weighted_score,
                "unmet_dimensions": [dimension.value for dimension in result.unmet_dimensions],
                "infrastructure_failures": result.infrastructure_failures,
            }
            for role_id, result in role_fitness.items()
        }

    return payload


def write_report_json(
    report: ModelEvaluationReport,
    path: str | Path,
    role_fitness: Mapping[str, RoleFitnessResult] | None = None,
) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(report_as_dict(report, role_fitness), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
