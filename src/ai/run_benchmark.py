from __future__ import annotations

import argparse

from src.ai.benchmark_cases import JARVIS_BENCHMARK_CASES, benchmark_score_function
from src.ai.evaluation import ModelCandidate, ModelEvaluator
from src.ai.providers.ollama_provider import OllamaProvider
from src.ai.service import AIService


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the JARVIS local-model benchmark through Ollama.")
    parser.add_argument("model", help="Ollama model tag, for example qwen3:4b or gemma3:4b")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--timeout", type=int, default=120)
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
    print()
    for observation in report.observations:
        status = "PASS" if observation.passed else "FAIL"
        score = sum(observation.scores.values()) / len(observation.scores)
        print(f"{status} {observation.case_id}: {score:.3f}")
        if observation.error:
            print(f"  ERROR: {observation.error}")

    print()
    for dimension, score in sorted(report.dimension_scores.items(), key=lambda item: item[0].value):
        print(f"{dimension.value}: {score:.3f}")

    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
