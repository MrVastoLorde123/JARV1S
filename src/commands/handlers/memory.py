from src.commands.handler import (
    CommandHandler,
)

from src.commands.models import (
    CommandRequest,
    CommandResult,
)

from src.memory.memory_decision import (
    MemoryDecisionService,
)

from src.memory.memory_decision_executor import (
    MemoryDecisionExecutor,
)

from src.memory.memory_decision_models import (
    CREATE,
    MemoryDecisionContext,
)

from src.memory.memory_models import (
    CandidateMemory,
)

from src.memory.memory_retrieval import (
    get_memory,
    get_memory_with_evidence,
    search_memories,
)


class ShowMemoryHandler(
    CommandHandler
):
    """
    Read-only handler for:

        /SHOW-MEMORY <memory-key-or-query>

    The command never mutates memory.

    Lookup order:

        1. Exact memory-key lookup
        2. Semantic memory search
    """

    def command_name(
        self,
    ) -> str:
        return "SHOW-MEMORY"

    def execute(
        self,
        request: CommandRequest,
    ) -> CommandResult:

        if not isinstance(
            request,
            CommandRequest,
        ):
            raise TypeError(
                "request must be a CommandRequest."
            )

        if len(request.arguments) != 1:
            return CommandResult(
                success=False,
                command=request.name,
                message=(
                    "Usage: "
                    "/SHOW-MEMORY <memory-key-or-query>"
                ),
            )

        target = request.arguments[0].strip()

        if not target:
            return CommandResult(
                success=False,
                command=request.name,
                message=(
                    "Memory key or query cannot "
                    "be empty."
                ),
            )

        memory = get_memory(
            target
        )

        if memory is not None:
            return self._build_result(
                memory
            )

        results = search_memories(
            target,
            limit=5,
        )

        if not results:
            return CommandResult(
                success=False,
                command=request.name,
                message=(
                    f"No memory found for: "
                    f"{target}"
                ),
            )

        memory = results[0]

        return self._build_result(
            memory
        )

    def _build_result(
        self,
        memory,
    ) -> CommandResult:

        memory_with_evidence = (
            get_memory_with_evidence(
                memory.memory_id
            )
        )

        evidence_count = 0

        if memory_with_evidence is not None:
            evidence_count = len(
                memory_with_evidence.evidence
            )

        message = (
            "Memory\n"
            "--------------------------------------------------\n"
            f"ID: {memory.memory_id}\n"
            f"Key: {memory.memory_key}\n"
            f"Category: {memory.category}\n"
            f"Status: {memory.status}\n"
            f"Confidence: {memory.confidence:.2f}\n"
            f"Importance: {memory.importance:.2f}\n"
            f"Evidence: {evidence_count}\n"
            f"Content: {memory.content}"
        )

        metadata = {
            "memory_id": memory.memory_id,
            "memory_key": memory.memory_key,
            "category": memory.category,
            "status": memory.status,
            "confidence": memory.confidence,
            "importance": memory.importance,
            "evidence_count": evidence_count,
        }

        return CommandResult(
            success=True,
            command="SHOW-MEMORY",
            message=message,
            metadata=metadata,
        )


class RememberMemoryHandler(
    CommandHandler
):
    """
    Explicit memory creation command.

    V1 syntax:

        /REMEMBER <memory statement>

    Example:

        /REMEMBER I prefer local AI.

    The handler creates an explicit CandidateMemory and submits
    it to the normal MemoryDecisionService + MemoryDecisionExecutor
    pipeline.

    It does not write directly to the database.
    """

    def __init__(
        self,
        decision_service: MemoryDecisionService | None = None,
        executor: MemoryDecisionExecutor | None = None,
    ):
        self.decision_service = (
            decision_service
            if decision_service is not None
            else self._build_default_decision_service()
        )

        self.executor = (
            executor
            if executor is not None
            else MemoryDecisionExecutor()
        )

    def command_name(
        self,
    ) -> str:
        return "REMEMBER"

    def execute(
        self,
        request: CommandRequest,
    ) -> CommandResult:

        if not isinstance(
            request,
            CommandRequest,
        ):
            raise TypeError(
                "request must be a CommandRequest."
            )

        if not request.arguments:
            return CommandResult(
                success=False,
                command=request.name,
                message=(
                    "Usage: "
                    "/REMEMBER <memory statement>"
                ),
            )

        statement = " ".join(
            request.arguments
        ).strip()

        if not statement:
            return CommandResult(
                success=False,
                command=request.name,
                message=(
                    "Memory statement cannot "
                    "be empty."
                ),
            )

        candidate = (
            self._build_candidate(
                statement
            )
        )

        if candidate is None:
            return CommandResult(
                success=False,
                command=request.name,
                message=(
                    "The statement could not be "
                    "converted into a supported "
                    "memory candidate."
                ),
            )

        decision_context = (
            MemoryDecisionContext(
                candidate=candidate,
                existing_memory=None,
                metadata={
                    "source": "explicit_command",
                    "command": "REMEMBER",
                },
            )
        )

        try:

            decision = (
                self.decision_service.decide(
                    decision_context
                )
            )

        except Exception as exc:

            return CommandResult(
                success=False,
                command=request.name,
                message=(
                    "Memory decision failed: "
                    f"{exc}"
                ),
            )

        # -----------------------------------------------------
        # Explicit REMEMBER requires a CREATE decision in V1.
        #
        # We do not allow the deterministic automatic decision
        # system to silently reinterpret an explicit creation
        # command as UPDATE/CONTRADICT/anything else.
        #
        # Existing-memory handling will be formalized later.
        # -----------------------------------------------------

        if decision.action != CREATE:

            return CommandResult(
                success=False,
                command=request.name,
                message=(
                    "JARVIS did not approve this "
                    "memory for creation."
                ),
                metadata={
                    "decision_action": (
                        decision.action
                    ),
                    "decision_confidence": (
                        decision.confidence
                    ),
                    "decision_reason": (
                        decision.reason
                    ),
                },
            )

        try:

            execution = (
                self.executor.execute(
                    decision=decision
                )
            )

        except Exception as exc:

            return CommandResult(
                success=False,
                command=request.name,
                message=(
                    "Memory execution failed: "
                    f"{exc}"
                ),
            )

        if execution.status != "SUCCESS":

            return CommandResult(
                success=False,
                command=request.name,
                message=(
                    execution.reason
                    or
                    "Memory could not be created."
                ),
                metadata={
                    "execution_status": (
                        execution.status
                    ),
                    "memory_id": (
                        execution.memory_id
                    ),
                },
            )

        return CommandResult(
            success=True,
            command=request.name,
            message=(
                "Memory created successfully."
            ),
            metadata={
                "memory_id": (
                    execution.memory_id
                ),
                "evidence_id": (
                    execution.evidence_id
                ),
                "decision_action": (
                    decision.action
                ),
                "decision_confidence": (
                    decision.confidence
                ),
            },
        )

    @staticmethod
    def _build_default_decision_service():
        """
        Build the deterministic decision service used by default.

        This mirrors Memory Formation's current deterministic
        baseline while keeping the handler provider-neutral.
        """

        from src.memory.providers.deterministic_memory_decision import (
            DeterministicMemoryDecisionProvider,
        )

        service = MemoryDecisionService(
            default_provider="deterministic"
        )

        service.register_provider(
            DeterministicMemoryDecisionProvider()
        )

        return service

    @staticmethod
    def _build_candidate(
        statement: str,
    ) -> CandidateMemory | None:
        """
        Build a conservative explicit candidate.

        V1 intentionally uses the user's statement as the
        evidence itself.
        """

        statement = statement.strip()

        if not statement:
            return None

        # Explicit command syntax does not require the sentence
        # to match one of Memory Formation's automatic extraction
        # rules. The user has explicitly told JARVIS to remember it.
        #
        # We use a generic FACT candidate until richer command
        # syntax for category/key is introduced.

        memory_key = (
            RememberMemoryHandler
            ._normalize_memory_key(
                statement
            )
        )

        if not memory_key:
            return None

        return CandidateMemory(
            content=statement,
            category="FACT",
            memory_key=memory_key,
            subject=statement,
            confidence=1.0,
            importance=0.75,
            evidence_text=statement,
            evidence_type="DIRECT",
            source_role="user",
        )

    @staticmethod
    def _normalize_memory_key(
        statement: str,
    ) -> str:
        import re

        key = statement.casefold()

        key = re.sub(
            r"\b(?:i|am|a|an|the|that|to|and|my|is|it|"
            r"this|please|remember)\b",
            " ",
            key,
        )

        key = re.sub(
            r"[^a-z0-9]+",
            "_",
            key,
        )

        key = key.strip("_")

        if not key:
            return ""

        return (
            "explicit_"
            + key[:80]
        )