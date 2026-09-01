"""Application service for selecting from registered JARVIS capabilities."""

from __future__ import annotations

from src.core.capability_catalog import CapabilityCatalog
from src.core.capability_selection import CapabilitySelection, CapabilitySelector


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

    def select(self, query: str) -> CapabilitySelection:
        """Rank registered capabilities for the given intent.

        This service only produces a proposal. It never invokes a tool and
        therefore cannot cross the tool policy/confirmation boundary.
        """
        return self._selector.select(query, self._catalog.list())
