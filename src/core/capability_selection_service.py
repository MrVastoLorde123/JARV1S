"""Application service for selecting from registered JARVIS capabilities."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.capability_catalog import CapabilityCatalog
from src.core.capability_selection import CapabilitySelection, CapabilitySelector
from src.tools.models import ToolDefinition


@dataclass(frozen=True)
class CapabilityDiscoverySelection:
    """Immutable discovery-plus-selection snapshot.

    This is an inspectable proposal/result boundary only. It contains the
    capabilities discovered at the time of selection and the selector's
    ranked candidates. It never authorizes or invokes a capability.
    """

    query: str
    discovered: tuple[ToolDefinition, ...]
    selection: CapabilitySelection

    def __post_init__(self) -> None:
        if not isinstance(self.query, str) or not self.query.strip():
            raise ValueError("query must be a non-empty string")
        if not isinstance(self.discovered, tuple) or not all(
            isinstance(item, ToolDefinition) for item in self.discovered
        ):
            raise TypeError("discovered must contain only ToolDefinition values")
        if not isinstance(self.selection, CapabilitySelection):
            raise TypeError("selection must be a CapabilitySelection")
        if self.selection.query != self.query:
            raise ValueError("selection query must match snapshot query")
        discovered_set = set(self.discovered)
        if not all(
            candidate.capability in discovered_set
            for candidate in self.selection.candidates
        ):
            raise ValueError("selection contains a capability not present in discovered")

    @property
    def best(self):
        """Return the best selected capability proposal, if any."""
        return self.selection.best

    def to_context(self) -> dict[str, object]:
        return {
            "query": self.query,
            "discovered_count": len(self.discovered),
            "selected": self.best is not None,
            "best_capability": self.best.capability.name if self.best else None,
            "authority_granted": False,
            "permission_granted": False,
            "authorization_granted": False,
            "execution_requested": False,
        }


class CapabilitySelectionService:
    """Coordinate catalog discovery and capability ranking."""

    def __init__(
        self,
        catalog: CapabilityCatalog,
        selector: CapabilitySelector,
    ) -> None:
        if not isinstance(catalog, CapabilityCatalog):
            raise TypeError("catalog must be a CapabilityCatalog")
        if not isinstance(selector, CapabilitySelector):
            raise TypeError("selector must implement CapabilitySelector")
        self._catalog = catalog
        self._selector = selector

    def discover(self) -> tuple[ToolDefinition, ...]:
        """Return the current immutable capability discovery snapshot."""
        return self._catalog.list()

    def select(self, query: str) -> CapabilitySelection:
        """Rank registered capabilities for the given intent.

        This service only produces a proposal. It never invokes a tool and
        therefore cannot cross the tool policy/confirmation boundary.
        """
        return self._selector.select(query, self.discover())

    def discover_and_select(self, query: str) -> CapabilityDiscoverySelection:
        """Return one inspectable discovery + selection snapshot.

        Discovery and selection remain strictly read-only proposal operations.
        No permission, authorization, sandbox admission, or execution is
        performed by this method.
        """
        discovered = self.discover()
        selection = self._selector.select(query, discovered)
        return CapabilityDiscoverySelection(
            query=query,
            discovered=discovered,
            selection=selection,
        )
