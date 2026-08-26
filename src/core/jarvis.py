from src.ai.models import AIRequest
from src.ai.service import AIService

from src.context.context_builder import (
    build_context,
)

from src.context.models import (
    ContextOptions,
)

from src.core.conversation import (
    ConversationState,
)

from src.core.conversation_store import (
    ConversationStore,
)

from src.core.models import (
    JARVISResponse,
)

from src.memory.memory_formation import (
    process_turn,
)


class JARVIS:
    """
    Core orchestration layer for JARVIS.

    JARVIS coordinates:

        user request
        conversation state
        persistence
        context construction
        AI request creation
        AI provider execution
        optional memory formation
    """

    def __init__(
        self,
        ai_service: AIService,
        context_options: ContextOptions | None = None,
        conversation: ConversationState | None = None,
        conversation_store: ConversationStore | None = None,
        conversation_id: str | None = None,
        enable_memory_formation: bool = False,
    ):
        self.ai_service = ai_service

        self.context_options = (
            context_options
            if context_options is not None
            else ContextOptions()
        )

        self.conversation_store = (
            conversation_store
        )

        self._enable_memory_formation = (
            enable_memory_formation
        )

        if conversation is not None:

            self.conversation = (
                conversation
            )

        elif conversation_store is not None:

            if conversation_id is not None:

                restored = (
                    conversation_store
                    .load_state(
                        conversation_id
                    )
                )

                if restored is None:
                    raise ValueError(
                        "Persistent conversation "
                        "does not exist."
                    )

                self.conversation = (
                    restored
                )

            else:

                record = (
                    conversation_store
                    .create_conversation()
                )

                self.conversation = (
                    conversation_store
                    .load_state(
                        record.conversation_id
                    )
                )

        else:

            self.conversation = (
                ConversationState()
            )

    def _persist_state(
        self,
    ):
        if self.conversation_store is None:
            return

        self.conversation_store.save_state(
            self.conversation.snapshot()
        )

    def ask(
        self,
        query: str,
        provider_name: str | None = None,
    ) -> JARVISResponse:

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
        # 1. Record the user turn in active state.
        # ---------------------------------------------------------

        self.conversation.add_turn(
            "user",
            query,
        )

        user_snapshot = (
            self.conversation.snapshot()
        )

        source_created_at = None

        if user_snapshot.turns:

            source_created_at = (
                user_snapshot
                .turns[-1]
                .timestamp
            )

        user_message_id = None

        if self.conversation_store is not None:

            previous_message_id = (
                self._get_last_persistent_message_id()
            )

            stored_user_message = (
                self.conversation_store
                .append_message(
                    conversation_id=(
                        self.conversation
                        .conversation_id
                    ),
                    role="user",
                    content=query,
                    parent_id=(
                        previous_message_id
                    ),
                    created_at=(
                        source_created_at
                    ),
                )
            )

            user_message_id = (
                stored_user_message[
                    "message_id"
                ]
            )

        # Persist state even before AI generation.
        self._persist_state()

        # ---------------------------------------------------------
        # 2. Build provider-neutral context.
        # ---------------------------------------------------------

        context = build_context(
            query,
            options=self.context_options,
            state_snapshot=(
                user_snapshot
                if self.context_options.include_state
                else None
            ),
        )

        # ---------------------------------------------------------
        # 3. Create AI request.
        # ---------------------------------------------------------

        request = AIRequest(
            task=query,
            context=context,
        )

        # ---------------------------------------------------------
        # 4. Ask the AI provider.
        # ---------------------------------------------------------

        ai_response = self.ai_service.generate(
            request,
            provider_name=provider_name,
        )

        response_content = str(
            ai_response.content
        )

        # ---------------------------------------------------------
        # 5. Record assistant response.
        # ---------------------------------------------------------

        self.conversation.add_turn(
            "assistant",
            response_content,
        )

        assistant_created_at = None

        if (
            self.conversation.snapshot().turns
        ):

            assistant_created_at = (
                self.conversation
                .snapshot()
                .turns[-1]
                .timestamp
            )

        if self.conversation_store is not None:

            self.conversation_store.append_message(
                conversation_id=(
                    self.conversation
                    .conversation_id
                ),
                role="assistant",
                content=response_content,
                parent_id=user_message_id,
                created_at=(
                    assistant_created_at
                ),
            )

        # ---------------------------------------------------------
        # 6. Persist state again after assistant response.
        # ---------------------------------------------------------

        self._persist_state()

        # ---------------------------------------------------------
        # 7. Optional memory formation.
        # ---------------------------------------------------------

        formation_result = None

        if self._enable_memory_formation:

            formation_result = process_turn(
                user_query=query,
                assistant_response=response_content,
                conversation_id=(
                    self.conversation
                    .conversation_id
                    if self.conversation_store
                    is not None
                    else None
                ),
                message_id=user_message_id,
                source_created_at=(
                    source_created_at
                ),
            )

        # ---------------------------------------------------------
        # 8. Response metadata.
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
                self.conversation
                .conversation_id
            ),
            "persistent": (
                self.conversation_store
                is not None
            ),
        }

        if formation_result is not None:

            metadata[
                "memory_formation"
            ] = {
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

    def _get_last_persistent_message_id(
        self,
    ):
        """
        Retrieve the latest persisted message ID.

        Used to maintain the linear parent chain.
        """

        if self.conversation_store is None:
            return None

        rows = (
            self.conversation_store
            .get_messages(
                self.conversation
                .conversation_id
            )
        )

        if not rows:
            return None

        return rows[-1][0]