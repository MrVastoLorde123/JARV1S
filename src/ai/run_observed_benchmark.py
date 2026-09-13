from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.ai.benchmark_cases import JARVIS_BENCHMARK_CASES, benchmark_score_function
from src.ai.evaluation import ModelCandidate, ModelEvaluator
from src.ai.providers.ollama_provider import OllamaProvider
from src.ai.report_export import write_report_json
from src.ai.role_fitness import DEFAULT_ROLE_FITNESS_PROFILES, evaluate_role_fitness
from src.ai.service import AIService


def main() -> int:
    parser = argparse.ArgumentParser(description="Run an evidence-bearing JARVIS local-model benchmark through Ollama.")
    parser.add_argument("model")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--trace-json", type=Path)
    parser.add_argument("--report-json", type=Path)
    parser.add_argument("--full-responses", action="store_true")
    args = parser.parse_args()

    provider = OllamaProvider(base_url=args.base_url, model=args.model, timeout=args.timeout)
    service = AIService()
    service.register_provider(provider)
    service.set_default_provider("ollama")

    candidate = ModelCandidate(args.model, "ollama", args.model, {"runtime": "ollama"})
    report = ModelEvaluator(service, benchmark_score_function).evaluate(candidate, JARVIS_BENCHMARK_CASES)
    fitness = {profile.role_id: evaluate_role_fitness(report, profile) for profile in DEFAULT_ROLE_FITNESS_PROFILES}

    print(f"Model: {report.candidate.model_id}")
    print(f"Overall score: {report.overall_score:.3f}")
    print(f"Model failures: {report.model_failures}")
    print(f"Infrastructure failures: {report.infrastructure_failures}")
    print(f"Average latency: {report.average_latency_ms / 1000.0:.1f}s")
    print()

    for observation in report.observations:
        score = sum(observation.scores.values()) / len(observation.scores) if observation.scores else None
        score_text = f" score={score:.3f}" if score is not None else ""
        latency_text = f" latency={observation.latency_ms / 1000.0:.1f}s" if observation.latency_ms is not None else ""
        print(f"[{observation.outcome.value.upper()}] {observation.case_id}{score_text}{latency_text}")
        if observation.error:
            print(f"  error: {observation.error}")
        if observation.response is not None:
            response = str(observation.response.content)
            print("  response evidence:")
            if args.full_responses:
                print(response)
            else:
                print(response[:1200] + ("...[truncated]" if len(response) > 1200 else ""))
        print()

    print("Role fitness:")
    for role_id, result in fitness.items():
        unmet = ", ".join(d.value for d in result.unmet_dimensions) or "none"
        print(f"  {role_id}: {'SUITABLE' if result.suitable else 'NOT SUITABLE'} score={result.weighted_score:.3f} unmet={unmet}")

    if args.trace_json and report.trace:
        args.trace_json.parent.mkdir(parents=True, exist_ok=True)
        args.trace_json.write_text(json.dumps(report.trace.as_dict(), indent=2, default=str), encoding="utf-8")
        print(f"Trace JSON: {args.trace_json}")
    if args.report_json:
        write_report_json(report, args.report_json, fitness)
        print(f"Report JSON: {args.report_json}")

    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
