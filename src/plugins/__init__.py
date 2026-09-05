"""Bounded JARVIS plugin/capability ecosystem contracts."""

from .ecosystem import CapabilityDescriptor, CapabilityRegistry, PluginRegistryError
from .lifecycle import (
    CapabilityLifecycleError,
    CapabilityLifecycleRegistry,
    CapabilityVersion,
    LifecycleStatus,
    SemanticVersion,
)
from .policy import (
    CapabilityPermissionBinding,
    CapabilityPolicyBindingRegistry,
    CapabilityPolicyError,
    PermissionEffect,
)
from .sandbox import (
    IsolationMode,
    PluginIsolationError,
    SandboxAdmissionEvaluator,
    SandboxAdmissionResult,
    SandboxAdmissionStatus,
    SandboxProfile,
    SandboxProfileRegistry,
)
from .trust import (
    CapabilityProvenance,
    CapabilityTrustAssessment,
    CapabilityTrustError,
    ProvenanceEvidence,
    TrustStatus,
)

__all__ = [
    "CapabilityDescriptor",
    "CapabilityRegistry",
    "PluginRegistryError",
    "CapabilityLifecycleError",
    "CapabilityLifecycleRegistry",
    "CapabilityVersion",
    "LifecycleStatus",
    "SemanticVersion",
    "CapabilityPermissionBinding",
    "CapabilityPolicyBindingRegistry",
    "CapabilityPolicyError",
    "PermissionEffect",
    "IsolationMode",
    "PluginIsolationError",
    "SandboxAdmissionEvaluator",
    "SandboxAdmissionResult",
    "SandboxAdmissionStatus",
    "SandboxProfile",
    "SandboxProfileRegistry",
    "CapabilityProvenance",
    "CapabilityTrustAssessment",
    "CapabilityTrustError",
    "ProvenanceEvidence",
    "TrustStatus",
]
