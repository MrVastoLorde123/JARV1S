from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.ai.benchmark_cases import JARVIS_BENCHMARK_CASES, benchmark_score_function
from src.ai.evaluation import ModelCandidate, ModelEvaluator
from src.ai.providers.ollama_provider import OllamaProvider
from src.ai.repeatability import aggregate_reports, repeatability_as_dict
from src.ai.service import AIService


def _run_trial(model: str, base_url: str, timeout: int):
    provider = OllamaProvider(base_url=base_url, model=model, timeout=timeout)
    service = AIService()
    service.register_provider(provider)
    service.set_default_provider("ollama")
    candidate = ModelCandidate(model, "ollama", model, {"runtime": "ollama"})
    return ModelEvaluator(service, benchmark_score_function).evaluate(candidate, JARVIS_BENCHMARK_CASES)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run repeated JARVIS local-model trials and aggregate repeatability evidence.")
    parser.add_argument("model")
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--report-json", type=Path)
    args = parser.parse_args()

    if args.trials < 1:
        parser.error("--trials must be at least 1")

    reports = []
    for trial_number in range(1, args.trials + 1):
        print(f"=== Trial {trial_number}/{args.trials}: {args.model} ===")
        report = _run_trial(args.model, args.base_url, args.timeout)
        reports.append(report)
        print(f"overall={report.overall_score:.3f} model_failures={report.model_failures} infrastructure_failures={report.infrastructure_failures} average_latency={report.average_latency_ms / 1000.0 if report.average_latency_ms is not None else 0.0:.1f}s")
        print()

    summary = aggregate_reports(reports)
    print(f"Repeatability: {summary.model_id}")
    print(f"Trials: {summary.trial_count}")
    print(f"Average overall score: {summary.average_overall_score:.3f}")
    print(f"Overall score stddev: {summary.overall_score_stddev if summary.overall_score_stddev is not None else 0.0:.3f}")
    print(f"Trials with infrastructure failures: {summary.trials_with_infrastructure_failures}")
    print(f"Evaluable observations: {summary.evaluable_observation_count}")
    print(f"Model failure rate (evaluable only): {summary.model_failure_rate:.3f}")
    print(f"Infrastructure failure rate (all attempts): {summary.infrastructure_failure_rate:.3f}")
    print()

    for case_id, case in summary.cases.items():
        print(
            f"{case_id}: pass={case.pass_count} model_failure={case.model_failure_count} "
            f"infra={case.infrastructure_failure_count} avg_score={case.average_score if case.average_score is not None else 0.0:.3f} "
            f"score_stddev={case.score_stddev if case.score_stddev is not None else 0.0:.3f}"
        )

    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(
            json.dumps(repeatability_as_dict(summary), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"Repeatability JSON: {args.report_json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
