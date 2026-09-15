"""Explicit initial role-fitness policy for the discovered local model roster.

This is configuration, not benchmark truth. A model receives a role only when
JARVIS explicitly declares that role here; provider discovery never creates it.
"""
from __future__ import annotations

from src.ai.model_role_policy import ModelRolePolicy, ModelRolePolicyRule
from src.ai.model_routing import ModelRole


_LOCAL_ROLE_RULES = (
    ModelRolePolicyRule(
        "qwen3-coder:30b",
        frozenset({ModelRole.CODING}),
        priority=120,
        notes="Primary coding role in the initial local policy.",
    ),
    ModelRolePolicyRule(
        "qwen2.5-coder:7b",
        frozenset({ModelRole.CODING, ModelRole.LIGHTWEIGHT}),
        priority=80,
        notes="Lower-resource coding fallback.",
    ),
    ModelRolePolicyRule(
        "qwen3:30b",
        frozenset({ModelRole.GENERAL, ModelRole.DIAGNOSTIC}),
        priority=110,
        notes="General and diagnostic reasoning role.",
    ),
    ModelRolePolicyRule(
        "gpt-oss:20b",
        frozenset({ModelRole.GENERAL, ModelRole.DIAGNOSTIC}),
        priority=105,
        notes="General and diagnostic alternative.",
    ),
    ModelRolePolicyRule(
        "qwen3:14b",
        frozenset({ModelRole.GENERAL, ModelRole.DIAGNOSTIC}),
        priority=95,
        notes="Mid-size general and diagnostic fallback.",
    ),
    ModelRolePolicyRule(
        "hf.co/mradermacher/Hermes-4-14B-GGUF:Q4_K_M",
        frozenset({ModelRole.GENERAL, ModelRole.DIAGNOSTIC}),
        priority=90,
        notes="General reasoning alternative.",
    ),
    ModelRolePolicyRule(
        "hf.co/ibm-granite/granite-4.2-30b-GGUF:Q4_K_M",
        frozenset({ModelRole.DIAGNOSTIC, ModelRole.GENERAL}),
        priority=90,
        notes="Large diagnostic/general alternative.",
    ),
    ModelRolePolicyRule(
        "hf.co/ibm-granite/granite-4.2-8b-GGUF:Q4_K_M",
        frozenset({ModelRole.VERIFICATION, ModelRole.LIGHTWEIGHT}),
        priority=85,
        notes="Initial independent verification-oriented policy role.",
    ),
    ModelRolePolicyRule(
        "qwen3:8b",
        frozenset({ModelRole.GENERAL, ModelRole.LIGHTWEIGHT}),
        priority=70,
        notes="Lower-resource general fallback.",
    ),
    ModelRolePolicyRule(
        "phi4-mini:latest",
        frozenset({ModelRole.LIGHTWEIGHT}),
        priority=65,
        notes="Small local lightweight role.",
    ),
    ModelRolePolicyRule(
        "qwen3:4b",
        frozenset({ModelRole.LIGHTWEIGHT}),
        priority=60,
        notes="Small local lightweight fallback.",
    ),
    ModelRolePolicyRule(
        "gemma3:4b",
        frozenset({ModelRole.LIGHTWEIGHT}),
        priority=55,
        notes="Small local lightweight alternative.",
    ),
)


def build_local_model_role_policy() -> ModelRolePolicy:
    """Return a fresh deterministic policy for the discovered local roster."""
    return ModelRolePolicy(_LOCAL_ROLE_RULES)


__all__ = ["build_local_model_role_policy"]
