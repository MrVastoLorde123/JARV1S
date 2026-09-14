from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow direct execution from the repository root, e.g.
# ``python scripts/run_llm_tournament.py ...``.
# In that mode Python puts ``scripts/`` on sys.path rather than the project root.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.ai.evaluation import ModelCandidate
from src.ai.providers.local_provider import LocalProvider
from src.ai.providers.ollama_provider import OllamaProvider
from src.ai.service import AIService
from src.ai.tournament import evaluate_model_tournament


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the same JARVIS benchmark suite against multiple local LLM candidates."
    )
    parser.add_argument(
        "--provider",
        choices=("local", "ollama"),
        default="ollama",
        help="Provider runtime to evaluate.",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="OpenAI-compatible local server URL. Defaults to the provider's local default.",
    )
    parser.add_argument(
        "--model",
        dest="models",
        action="append",
        required=True,
        help="Model identifier. Repeat --model for additional candidates.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        help="Provider request timeout in seconds.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional JSON output path for the tournament summary.",
    )
    return parser


def build_provider(provider_name: str, *, base_url: str | None, timeout: int | None):
    if provider_name == "ollama":
        return OllamaProvider(
            base_url=base_url or "http://127.0.0.1:11434",
            model="unknown",
            timeout=timeout or 300,
        )
    return LocalProvider(
        base_url=base_url or "http://127.0.0.1:8080",
        model="unknown",
        timeout=timeout or 120,
    )


def main() -> int:
    args = build_parser().parse_args()

    provider = build_provider(
        args.provider,
        base_url=args.base_url,
        timeout=args.timeout,
    )
    service = AIService(default_provider=provider.provider_name())
    service.register_provider(provider)

    candidates = tuple(
        ModelCandidate(model_id=model_id, provider_name=provider.provider_name())
        for model_id in args.models
    )
    report = evaluate_model_tournament(service, candidates)

    print("\nJARVIS LOCAL LLM TOURNAMENT")
    print("=" * 72)
    for position, entry in enumerate(report.leaderboard, start=1):
        print(
            f"{position:>2}. {entry.candidate.model_id} "
            f"| overall={entry.report.overall_score:.3f} "
            f"| passed={entry.passed_case_count}/{entry.total_case_count} "
            f"| model_failures={entry.report.model_failures} "
            f"| infra_failures={entry.report.infrastructure_failures} "
            f"| avg_latency_ms={entry.report.average_latency_ms} "
            f"| suitable_roles={entry.suitable_role_count}"
        )
        for role_id, fitness in entry.role_fitness.items():
            print(
                f"    {role_id}: {'SUITABLE' if fitness.suitable else 'NOT SUITABLE'} "
                f"score={fitness.weighted_score:.3f} "
                f"unmet={[dimension.value for dimension in fitness.unmet_dimensions]}"
            )

    if report.winner is not None:
        print(f"\nLeader by deterministic tournament ordering: {report.winner.candidate.model_id}")
        print("This is evaluation evidence only; it does not assign the model to a JARVIS role.")

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report.as_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"JSON report: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
