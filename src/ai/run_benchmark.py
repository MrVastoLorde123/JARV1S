from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.ai.benchmark_cases import JARVIS_BENCHMARK_CASES, benchmark_score_function
from src.ai.evaluation import ModelCandidate, ModelEvaluator
from src.ai.providers.ollama_provider import OllamaProvider
from src.ai.service import AIService


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the JARVIS local-model benchmark through Ollama.")
    parser.add_argument("model", help="Ollama model tag, for example qwen3:4b or gemma3:4b")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--trace-json", type=Path, help="Write the complete JARVIS execution trace to JSON.")
    args = parser.parse_args()

    provider = OllamaProvider(base_url=args.base_url, model=args.model, timeout=args.timeout)
    service = AIService()
    service.register_provider(provider)
    service.set_default_provider("ollama")

    candidate = ModelCandidate(
        model_id=args.model,
        provider_name="ollama",
        display_name=args.model,
        metadata={"runtime": "ollama"},
    )
    evaluator = ModelEvaluator(service, benchmark_score_function)
    report = evaluator.evaluate(candidate, JARVIS_BENCHMARK_CASES)

    print(f"Model: {report.candidate.model_id}")
    print(f"Overall score: {report.overall_score:.3f}")
    print(f"Passed all cases: {report.passed}")
    print(f"Infrastructure failures: {report.infrastructure_failures}")
    print()
    for observation in report.observations:
        status = "PASS" if observation.passed else observation.outcome.value.upper()
        score = sum(observation.scores.values()) / len(observation.scores) if observation.scores else None
        suffix = f": {score:.3f}" if score is not None else ""
        print(f"{status} {observation.case_id}{suffix}")
        if observation.error:
            print(f"  ERROR: {observation.error}")

    print()
    for dimension, score in sorted(report.dimension_scores.items(), key=lambda item: item[0].value):
        print(f"{dimension.value}: {score:.3f}")

    if report.trace is not None:
        print()
        print("Execution trace:")
        for event in report.trace.events:
            location = f" [{event.case_id}]" if event.case_id else ""
            outcome = f" -> {event.outcome.value}" if event.outcome else ""
            print(f"  #{event.sequence:02d} +{event.elapsed_ms:8.1f}ms {event.kind.value}{location}{outcome}: {event.message}")

        if args.trace_json:
            args.trace_json.parent.mkdir(parents=True, exist_ok=True)
            args.trace_json.write_text(json.dumps(report.trace.as_dict(), indent=2, default=str), encoding="utf-8")
            print()
            print(f"Trace JSON: {args.trace_json}")

    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
