"""Core execution and capability-boundary interfaces."""

from .plugin_boundary import (
    CapabilityBinding,
    CapabilityExecutionAdapter,
    CapabilityPlugin,
    CapabilityPluginRegistry,
    PluginDefinition,
)

__all__ = [
    "CapabilityBinding",
    "CapabilityExecutionAdapter",
    "CapabilityPlugin",
    "CapabilityPluginRegistry",
    "PluginDefinition",
]
