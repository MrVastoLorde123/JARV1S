from src.ai.models import AIRequest
from src.ai.service import AIService
from src.context.context_builder import build_context
from src.context.models import ContextOptions
from src.core.conversation import ConversationState
from src.core.models import JARVISResponse
from src.memory.memory_formation import process_turn


class JARVIS:
    """
    Core orchestration layer for the JARVIS system.

    JARVIS coordinates:
        user request
        context construction
        AI request creation
        AI provider execution
        memory formation

    It does not directly access databases, memories,
    or provider-specific implementations.
    """

    def __init__(
            self,
            ai_service: AIService,
            context_options: ContextOptions | None = None,
            conversation: ConversationState | None = None,
            enable_memory_formation: bool = False,
    ):

        self.ai_service = ai_service

        self.context_options = (
            context_options
            if context_options is not None
            else ContextOptions()
        )

        self.conversation = (
            conversation
            if conversation is not None
            else ConversationState()
        )

        self._enable_memory_formation = (
            enable_memory_formation
        )

    def ask(
            self,
            query: str,
            provider_name: str | None = None,
    ) -> JARVISResponse:

        if not isinstance(query, str):
            raise TypeError(
                "JARVIS query must be a string."
            )

        query = query.strip()

        if not query:
            raise ValueError(
                "JARVIS query cannot be empty."
            )

        self.conversation.add_turn(
            "user",
            query,
        )

        state_snapshot = (
            self.conversation.snapshot()
        )

        context = build_context(
            query,
            options=self.context_options,
            state_snapshot=(
                state_snapshot
                if self.context_options.include_state
                else None
            ),
        )

        request = AIRequest(
            task=query,
            context=context,
        )

        ai_response = self.ai_service.generate(
            request,
            provider_name=provider_name,
        )

        response_content = str(
            ai_response.content
        )

        self.conversation.add_turn(
            "assistant",
            response_content,
        )

        # -------------------------------------------------
        # Memory Formation
        #
        # After each turn, JARVIS decides whether to
        # form new memories from the conversation.
        #
        # This is a JARVIS-level decision.
        # The AI provider knows nothing about it.
        # -------------------------------------------------

        formation_result = None

        if self._enable_memory_formation:

            formation_result = process_turn(
                user_query=query,
                assistant_response=response_content,
                conversation_id=(
                    self.conversation.conversation_id
                ),
            )

        metadata = {
            "context_items": len(
                context.items
            ),
            "provider": (
                ai_response.provider
            ),
            "model": (
                ai_response.model
            ),
            "conversation_id": (
                self.conversation.conversation_id
            ),
        }

        if formation_result is not None:
            metadata["memory_formation"] = {
                "candidates_extracted": (
                    formation_result
                    .candidates_extracted
                ),
                "memories_created": (
                    formation_result
                    .memories_created
                ),
                "memories_deduplicated": (
                    formation_result
                    .memories_deduplicated
                ),
                "evidence_added": (
                    formation_result
                    .evidence_added
                ),
            }

        return JARVISResponse(
            content=response_content,
            ai_response=ai_response,
            context=context,
            metadata=metadata,
        )