from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Iterable, Mapping

from src.ai.evaluation import EvaluationOutcome, ModelEvaluationReport


@dataclass(frozen=True)
class CaseRepeatability:
    case_id: str
    trial_count: int
    pass_count: int
    model_failure_count: int
    infrastructure_failure_count: int
    other_failure_count: int
    observed_scores: tuple[float, ...]
    average_score: float | None
    score_stddev: float | None
    latencies_ms: tuple[float, ...]
    average_latency_ms: float | None


@dataclass(frozen=True)
class RepeatabilityReport:
    model_id: str
    provider_name: str
    trial_count: int
    successful_trials: int
    trials_with_infrastructure_failures: int
    overall_scores: tuple[float, ...]
    average_overall_score: float | None
    overall_score_stddev: float | None
    average_latency_ms: float | None
    cases: Mapping[str, CaseRepeatability]

    @property
    def model_failure_rate(self) -> float:
        observations = sum(item.model_failure_count for item in self.cases.values())
        trials = sum(item.trial_count for item in self.cases.values())
        return observations / trials if trials else 0.0

    @property
    def infrastructure_failure_rate(self) -> float:
        observations = sum(item.infrastructure_failure_count for item in self.cases.values())
        trials = sum(item.trial_count for item in self.cases.values())
        return observations / trials if trials else 0.0


def _case_summary(reports: tuple[ModelEvaluationReport, ...]) -> dict[str, CaseRepeatability]:
    grouped: dict[str, list[tuple[float | None, EvaluationOutcome, float | None]]] = {}
    for report in reports:
        for observation in report.observations:
            score = None
            if observation.scores:
                score = mean(observation.scores.values())
            grouped.setdefault(observation.case_id, []).append(
                (score, observation.outcome, observation.latency_ms)
            )

    summaries: dict[str, CaseRepeatability] = {}
    for case_id, observations in grouped.items():
        scores = tuple(score for score, _, _ in observations if score is not None)
        latencies = tuple(latency for _, _, latency in observations if latency is not None)
        pass_count = sum(outcome is EvaluationOutcome.PASS for _, outcome, _ in observations)
        model_failure_count = sum(outcome is EvaluationOutcome.MODEL_FAILURE for _, outcome, _ in observations)
        infrastructure_failure_count = sum(
            outcome in {
                EvaluationOutcome.INFRASTRUCTURE_ERROR,
                EvaluationOutcome.TIMEOUT,
            }
            for _, outcome, _ in observations
        )
        other_failure_count = len(observations) - pass_count - model_failure_count - infrastructure_failure_count
        summaries[case_id] = CaseRepeatability(
            case_id=case_id,
            trial_count=len(observations),
            pass_count=pass_count,
            model_failure_count=model_failure_count,
            infrastructure_failure_count=infrastructure_failure_count,
            other_failure_count=other_failure_count,
            observed_scores=scores,
            average_score=round(mean(scores), 3) if scores else None,
            score_stddev=round(pstdev(scores), 3) if len(scores) > 1 else None,
            latencies_ms=latencies,
            average_latency_ms=round(mean(latencies), 3) if latencies else None,
        )
    return summaries


def aggregate_reports(reports: Iterable[ModelEvaluationReport]) -> RepeatabilityReport:
    report_list = tuple(reports)
    if not report_list:
        raise ValueError("at least one evaluation report is required")

    first = report_list[0]
    if any(
        report.candidate.model_id != first.candidate.model_id
        or report.candidate.provider_name != first.candidate.provider_name
        for report in report_list
    ):
        raise ValueError("all reports must use the same model and provider")

    overall_scores = tuple(report.overall_score for report in report_list)
    latencies = tuple(
        report.average_latency_ms
        for report in report_list
        if report.average_latency_ms is not None
    )
    trials_with_infrastructure_failures = sum(
        report.infrastructure_failures > 0 for report in report_list
    )

    return RepeatabilityReport(
        model_id=first.candidate.model_id,
        provider_name=first.candidate.provider_name,
        trial_count=len(report_list),
        successful_trials=sum(report.infrastructure_failures == 0 for report in report_list),
        trials_with_infrastructure_failures=trials_with_infrastructure_failures,
        overall_scores=overall_scores,
        average_overall_score=round(mean(overall_scores), 3),
        overall_score_stddev=round(pstdev(overall_scores), 3) if len(overall_scores) > 1 else None,
        average_latency_ms=round(mean(latencies), 3) if latencies else None,
        cases=_case_summary(report_list),
    )


def repeatability_as_dict(report: RepeatabilityReport) -> dict[str, object]:
    return {
        "model_id": report.model_id,
        "provider_name": report.provider_name,
        "trial_count": report.trial_count,
        "successful_trials": report.successful_trials,
        "trials_with_infrastructure_failures": report.trials_with_infrastructure_failures,
        "overall_scores": list(report.overall_scores),
        "average_overall_score": report.average_overall_score,
        "overall_score_stddev": report.overall_score_stddev,
        "average_latency_ms": report.average_latency_ms,
        "model_failure_rate": round(report.model_failure_rate, 3),
        "infrastructure_failure_rate": round(report.infrastructure_failure_rate, 3),
        "cases": {
            case_id: {
                "trial_count": item.trial_count,
                "pass_count": item.pass_count,
                "model_failure_count": item.model_failure_count,
                "infrastructure_failure_count": item.infrastructure_failure_count,
                "other_failure_count": item.other_failure_count,
                "observed_scores": list(item.observed_scores),
                "average_score": item.average_score,
                "score_stddev": item.score_stddev,
                "latencies_ms": list(item.latencies_ms),
                "average_latency_ms": item.average_latency_ms,
            }
            for case_id, item in report.cases.items()
        },
    }
