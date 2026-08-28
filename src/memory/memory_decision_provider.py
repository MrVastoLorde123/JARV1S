from abc import ABC, abstractmethod

from src.memory.memory_decision_models import (
    MemoryDecision,
    MemoryDecisionContext,
)


class MemoryDecisionProvider(
    ABC
):
    """
    Provider-neutral contract for deciding what should happen
    to a memory candidate.

    Implementations must make a decision only.

    They must NOT:
        - modify the database
        - create memories
        - delete memories
        - add evidence
    """

    @abstractmethod
    def decide(
        self,
        context: MemoryDecisionContext,
    ) -> MemoryDecision:
        """
        Decide what action should be taken.

        Returns:
            MemoryDecision
        """
        raise NotImplementedError

    @abstractmethod
    def provider_name(
        self,
    ) -> str:
        """
        Return a stable provider identifier.
        """
        raise NotImplementedError