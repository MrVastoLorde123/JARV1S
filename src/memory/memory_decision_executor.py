from src.memory.evidence_store import (
    add_evidence,
)

from src.memory.memory_decision_models import (
    CREATE,
    CONFIRM,
    UPDATE,
    CONTRADICT,
    IGNORE,
    MemoryDecision,
)

from src.memory.memory_execution_models import (
    FAILED,
    NO_OP,
    SUCCESS,
    MemoryExecutionResult,
)

from src.memory.memory_store import (
    add_memory,
    update_memory,
    update_memory_status,
)


class MemoryDecisionExecutor:
    """
    Executes an already-approved MemoryDecision.

    Responsibilities:

        CREATE       -> create memory + direct evidence
        CONFIRM      -> add repeated evidence
        UPDATE       -> update existing memory + repeated evidence
        CONTRADICT   -> supersede existing memory + create replacement
        IGNORE       -> perform no mutation

    This class is deliberately separate from MemoryDecisionService.

    MemoryDecisionService answers:

        "What should happen?"

    MemoryDecisionExecutor performs:

        "Make it happen."
    """

    def execute(
        self,
        decision: MemoryDecision,
        conversation_id=None,
        message_id=None,
        source_created_at=None,
    ):
        """
        Execute a memory decision.

        Returns:
            MemoryExecutionResult
        """

        if not isinstance(
            decision,
            MemoryDecision,
        ):
            raise TypeError(
                "decision must be a "
                "MemoryDecision."
            )

        action = decision.action

        if action == IGNORE:

            return MemoryExecutionResult(
                status=NO_OP,
                action=action,
                memory_id=(
                    decision.memory_id
                ),
                reason=(
                    "Decision was IGNORE; "
                    "no memory mutation performed."
                ),
            )

        if action == CREATE:

            return self._execute_create(
                decision,
                conversation_id,
                message_id,
                source_created_at,
            )

        if action == CONFIRM:

            return self._execute_confirm(
                decision,
                conversation_id,
                message_id,
                source_created_at,
            )

        if action == UPDATE:

            return self._execute_update(
                decision,
                conversation_id,
                message_id,
                source_created_at,
            )

        if action == CONTRADICT:

            return self._execute_contradict(
                decision,
                conversation_id,
                message_id,
                source_created_at,
            )

        return MemoryExecutionResult(
            status=FAILED,
            action=action,
            reason=(
                f"Unsupported decision action: "
                f"{action}"
            ),
        )

    def _execute_create(
        self,
        decision,
        conversation_id,
        message_id,
        source_created_at,
    ):

        candidate = decision.candidate

        memory_id = add_memory(
            content=candidate.content,
            category=candidate.category,
            memory_key=candidate.memory_key,
            source_conversation_id=(
                conversation_id
            ),
            confidence=candidate.confidence,
            importance=candidate.importance,
            status="ACTIVE",
        )

        if memory_id is None:

            return MemoryExecutionResult(
                status=FAILED,
                action=CREATE,
                reason=(
                    "Memory could not be created."
                ),
            )

        evidence_id = add_evidence(
            memory_id=memory_id,
            evidence_text=(
                candidate.evidence_text
            ),
            evidence_type=(
                candidate.evidence_type
            ),
            confidence=candidate.confidence,
            conversation_id=(
                conversation_id
            ),
            message_id=message_id,
            source_created_at=(
                source_created_at
            ),
        )

        if evidence_id is None:

            return MemoryExecutionResult(
                status=FAILED,
                action=CREATE,
                memory_id=memory_id,
                reason=(
                    "Memory was created but "
                    "direct evidence could not "
                    "be stored."
                ),
            )

        return MemoryExecutionResult(
            status=SUCCESS,
            action=CREATE,
            memory_id=memory_id,
            evidence_id=evidence_id,
            reason=(
                "Memory created with direct "
                "user evidence."
            ),
        )

    def _execute_confirm(
        self,
        decision,
        conversation_id,
        message_id,
        source_created_at,
    ):

        candidate = decision.candidate

        memory_id = decision.memory_id

        if memory_id is None:

            return MemoryExecutionResult(
                status=FAILED,
                action=CONFIRM,
                reason=(
                    "CONFIRM requires an "
                    "existing memory ID."
                ),
            )

        evidence_id = add_evidence(
            memory_id=memory_id,
            evidence_text=(
                candidate.evidence_text
            ),
            evidence_type="REPEATED",
            confidence=candidate.confidence,
            conversation_id=(
                conversation_id
            ),
            message_id=message_id,
            source_created_at=(
                source_created_at
            ),
        )

        if evidence_id is None:

            return MemoryExecutionResult(
                status=FAILED,
                action=CONFIRM,
                memory_id=memory_id,
                reason=(
                    "Confirmation evidence "
                    "could not be stored."
                ),
            )

        return MemoryExecutionResult(
            status=SUCCESS,
            action=CONFIRM,
            memory_id=memory_id,
            evidence_id=evidence_id,
            reason=(
                "Existing memory confirmed "
                "with new evidence."
            ),
        )

    def _execute_update(
        self,
        decision,
        conversation_id,
        message_id,
        source_created_at,
    ):

        candidate = decision.candidate

        memory_id = decision.memory_id

        if memory_id is None:

            return MemoryExecutionResult(
                status=FAILED,
                action=UPDATE,
                reason=(
                    "UPDATE requires an "
                    "existing memory ID."
                ),
            )

        updated = update_memory(
            memory_id=memory_id,
            content=candidate.content,
            confidence=candidate.confidence,
            importance=candidate.importance,
        )

        if not updated:

            return MemoryExecutionResult(
                status=FAILED,
                action=UPDATE,
                memory_id=memory_id,
                reason=(
                    "Existing memory could "
                    "not be updated."
                ),
            )

        evidence_id = add_evidence(
            memory_id=memory_id,
            evidence_text=(
                candidate.evidence_text
            ),
            evidence_type="REPEATED",
            confidence=candidate.confidence,
            conversation_id=(
                conversation_id
            ),
            message_id=message_id,
            source_created_at=(
                source_created_at
            ),
        )

        if evidence_id is None:

            return MemoryExecutionResult(
                status=FAILED,
                action=UPDATE,
                memory_id=memory_id,
                reason=(
                    "Memory was updated but "
                    "update evidence could "
                    "not be stored."
                ),
            )

        return MemoryExecutionResult(
            status=SUCCESS,
            action=UPDATE,
            memory_id=memory_id,
            evidence_id=evidence_id,
            reason=(
                "Existing memory updated "
                "with additional information."
            ),
        )

    def _execute_contradict(
        self,
        decision,
        conversation_id,
        message_id,
        source_created_at,
    ):

        candidate = decision.candidate

        existing_memory_id = (
            decision.memory_id
        )

        if existing_memory_id is None:

            return MemoryExecutionResult(
                status=FAILED,
                action=CONTRADICT,
                reason=(
                    "CONTRADICT requires an "
                    "existing memory ID."
                ),
            )

        superseded = update_memory_status(
            memory_id=existing_memory_id,
            status="SUPERSEDED",
        )

        if not superseded:

            return MemoryExecutionResult(
                status=FAILED,
                action=CONTRADICT,
                memory_id=(
                    existing_memory_id
                ),
                reason=(
                    "Existing memory could "
                    "not be superseded."
                ),
            )

        replacement_id = add_memory(
            content=candidate.content,
            category=candidate.category,
            memory_key=candidate.memory_key,
            source_conversation_id=(
                conversation_id
            ),
            confidence=candidate.confidence,
            importance=candidate.importance,
            status="ACTIVE",
        )

        if replacement_id is None:

            return MemoryExecutionResult(
                status=FAILED,
                action=CONTRADICT,
                memory_id=(
                    existing_memory_id
                ),
                affected_memory_ids=(
                    existing_memory_id,
                ),
                reason=(
                    "Original memory was "
                    "superseded but replacement "
                    "memory could not be created."
                ),
            )

        evidence_id = add_evidence(
            memory_id=replacement_id,
            evidence_text=(
                candidate.evidence_text
            ),
            evidence_type=(
                "DIRECT"
            ),
            confidence=candidate.confidence,
            conversation_id=(
                conversation_id
            ),
            message_id=message_id,
            source_created_at=(
                source_created_at
            ),
        )

        if evidence_id is None:

            return MemoryExecutionResult(
                status=FAILED,
                action=CONTRADICT,
                memory_id=(
                    replacement_id
                ),
                affected_memory_ids=(
                    existing_memory_id,
                    replacement_id,
                ),
                reason=(
                    "Replacement memory was "
                    "created but direct evidence "
                    "could not be stored."
                ),
            )

        return MemoryExecutionResult(
            status=SUCCESS,
            action=CONTRADICT,
            memory_id=replacement_id,
            evidence_id=evidence_id,
            affected_memory_ids=(
                existing_memory_id,
                replacement_id,
            ),
            reason=(
                "Existing memory was superseded "
                "and replacement memory created."
            ),
        )