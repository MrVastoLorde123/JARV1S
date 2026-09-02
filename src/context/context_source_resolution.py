"""Resolve selected persistent context sources into working-context items."""

from dataclasses import dataclass
from typing import Iterable, Mapping

from src.context.context_source_selection import ContextSourceSelection
from src.context.models import ContextItem


@dataclass(frozen=True)
class ContextSourceResolution:
    """Provider-neutral result of resolving a prior source selection."""

    selection: ContextSourceSelection
    items: tuple[ContextItem, ...]
    missing_source_ids: tuple[str, ...] = ()


class ContextSourceResolver:
    """Resolve only sources explicitly selected by ContextSourceSelector."""

    def resolve(
        self,
        selection: ContextSourceSelection,
        sources: Mapping[str, ContextItem] | Iterable[ContextItem],
    ) -> ContextSourceResolution:
        if not isinstance(selection, ContextSourceSelection):
            raise TypeError("selection must be a ContextSourceSelection.")

        indexed = self._index_sources(sources)
        items = []
        missing = []

        for decision in selection.selected:
            item = indexed.get(decision.source_id)
            if item is None:
                missing.append(decision.source_id)
                continue
            items.append(item)

        return ContextSourceResolution(
            selection=selection,
            items=tuple(items),
            missing_source_ids=tuple(missing),
        )

    @staticmethod
    def _index_sources(
        sources: Mapping[str, ContextItem] | Iterable[ContextItem],
    ) -> dict[str, ContextItem]:
        if isinstance(sources, Mapping):
            indexed = dict(sources)
        else:
            indexed = {}
            for item in sources:
                if not isinstance(item, ContextItem):
                    raise TypeError("sources must contain ContextItem values.")
                source_id = item.provenance.get("source_id")
                if source_id is None:
                    raise ValueError("each ContextItem must provide provenance.source_id.")
                indexed[str(source_id)] = item

        for source_id, item in indexed.items():
            if not isinstance(source_id, str) or not source_id.strip():
                raise ValueError("source IDs must be non-empty strings.")
            if not isinstance(item, ContextItem):
                raise TypeError("sources must map source IDs to ContextItem values.")

        return indexed
