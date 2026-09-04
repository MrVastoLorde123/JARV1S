"""Provider-neutral context boundaries."""

from .cross_domain import (
    MAX_DOMAINS,
    MAX_ID_LENGTH,
    MAX_LABEL_LENGTH,
    MAX_LINKS,
    MAX_METADATA_ITEMS,
    MAX_REFERENCES,
    CrossDomainContext,
    CrossDomainContextValidationError,
    CrossDomainLink,
    DomainReference,
)
from .goal_project import (
    GoalContext,
    GoalProjectContext,
    GoalProjectContextValidationError,
    GoalStatus,
    ProjectContext,
    ProjectStatus,
)
from .situational import (
    MAX_SIGNALS,
    MAX_SIGNAL_ID_LENGTH,
    MAX_VALUE_LENGTH,
    SituationSignal,
    SituationalContext,
    SituationalContextValidationError,
)
from .temporal import (
    MAX_HISTORY_ITEMS,
    MAX_QUERY_RESULTS,
    TemporalContext,
    TemporalContextValidationError,
)
from .world_state import (
    ContextState,
    ContextStateValidationError,
    MAX_CONTEXT_ID_LENGTH,
    MAX_REFERENCE_LENGTH,
    MAX_STATE_ITEMS,
)

__all__ = [
    "CrossDomainContext",
    "CrossDomainContextValidationError",
    "CrossDomainLink",
    "DomainReference",
    "MAX_DOMAINS",
    "MAX_ID_LENGTH",
    "MAX_LABEL_LENGTH",
    "MAX_LINKS",
    "MAX_METADATA_ITEMS",
    "MAX_REFERENCES",
    "GoalContext",
    "GoalProjectContext",
    "GoalProjectContextValidationError",
    "GoalStatus",
    "ProjectContext",
    "ProjectStatus",
    "SituationSignal",
    "SituationalContext",
    "SituationalContextValidationError",
    "MAX_SIGNALS",
    "MAX_SIGNAL_ID_LENGTH",
    "MAX_VALUE_LENGTH",
    "ContextState",
    "ContextStateValidationError",
    "MAX_CONTEXT_ID_LENGTH",
    "MAX_REFERENCE_LENGTH",
    "MAX_STATE_ITEMS",
    "TemporalContext",
    "TemporalContextValidationError",
    "MAX_HISTORY_ITEMS",
    "MAX_QUERY_RESULTS",
]
