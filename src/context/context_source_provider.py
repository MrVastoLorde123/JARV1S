from abc import ABC, abstractmethod
from typing import Iterable, Mapping

from src.context.context_source_selection import ContextSource
from src.context.models import ContextItem


class ContextSourceProvider(ABC):
    """Provider-neutral contract for acquiring context sources and items."""

    @abstractmethod
    def get_sources(self, request: str) -> Iterable[ContextSource]:
        """Return persistent sources available for the request."""
        raise NotImplementedError

    @abstractmethod
    def get_context_items(
        self,
        request: str,
        sources: Iterable[ContextSource],
    ) -> Mapping[str, ContextItem] | Iterable[ContextItem]:
        """Return already-available context items with explicit source identity."""
        raise NotImplementedError
