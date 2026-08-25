from src.ai.models import AIRequest
from src.ai.service import AIService
from src.context.context_builder import build_context
from src.context.models import ContextOptions
from src.core.conversation import ConversationState
from src.core.models import JARVISResponse
from src.memory.memory_formation import process_turn


class JARVIS:
    """
    Core orchestration layer for JARVIS.

    JARVIS coordinates:

        user request
        conversation state
        context construction
        AI request creation
        AI provider execution
        optional memory formation

    JARVIS does not directly access databases or provider
    implementations.
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
        """
        Process one user request.
        """

        if not isinstance(
            query,
            str,
        ):
            raise TypeError(
                "JARVIS query must be a string."
            )

        query = query.strip()

        if not query:
            raise ValueError(
                "JARVIS query cannot be empty."
            )

        # ---------------------------------------------------------
        # 1. Record the user turn.
        # ---------------------------------------------------------

        self.conversation.add_turn(
            "user",
            query,
        )

        state_snapshot = (
            self.conversation.snapshot()
        )

        # The newest state turn is the user's source message.
        source_created_at = None

        if state_snapshot.turns:
            source_created_at = (
                state_snapshot
                .turns[-1]
                .timestamp
            )

        # ---------------------------------------------------------
        # 2. Build provider-neutral context.
        # ---------------------------------------------------------

        context = build_context(
            query,
            options=self.context_options,
            state_snapshot=(
                state_snapshot
                if self.context_options.include_state
                else None
            ),
        )

        # ---------------------------------------------------------
        # 3. Create provider-neutral AI request.
        # ---------------------------------------------------------

        request = AIRequest(
            task=query,
            context=context,
        )

        # ---------------------------------------------------------
        # 4. Ask the configured AI provider.
        # ---------------------------------------------------------

        ai_response = self.ai_service.generate(
            request,
            provider_name=provider_name,
        )

        response_content = str(
            ai_response.content
        )

        # ---------------------------------------------------------
        # 5. Record the assistant turn.
        # ---------------------------------------------------------

        self.conversation.add_turn(
            "assistant",
            response_content,
        )

        # ---------------------------------------------------------
        # 6. Optional memory formation.
        #
        # Important:
        # The temporary ConversationState ID is NOT passed as
        # conversation_id because it may not exist in the
        # persistent conversations table.
        #
        # A persistent conversation ID can be supplied later
        # once conversation persistence exists.
        # ---------------------------------------------------------

        formation_result = None

        if self._enable_memory_formation:

            formation_result = process_turn(
                user_query=query,
                assistant_response=response_content,
                conversation_id=None,
                message_id=None,
                source_created_at=(
                    source_created_at
                ),
            )

        # ---------------------------------------------------------
        # 7. Build JARVIS-level metadata.
        # ---------------------------------------------------------

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
                "errors": (
                    formation_result.errors
                ),
            }

        return JARVISResponse(
            content=response_content,
            ai_response=ai_response,
            context=context,
            metadata=metadata,
        )