from src.ai.models import AIRequest
from src.ai.service import AIService

from src.commands.models import (
    CommandResult,
)

from src.commands.parser import (
    CommandParser,
)

from src.commands.registry import (
    CommandRegistry,
)

from src.commands.service import (
    CommandService,
)

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

from src.core.execution_executor_models import (
    PlanExecutionResult,
    PlanExecutionStatus,
)

from src.core.execution_policy_models import (
    ExecutionPolicyResult,
    PolicyDecision,
)

from src.core.execution_plan_models import (
    ExecutionPlan,
)

from src.core.execution_planner import (
    ExecutionPlanner,
)

from src.core.models import (
    JARVISResponse,
)

from src.core.plan_executor import (
    PlanExecutor,
)

from src.core.plan_validator import (
    PlanValidator,
)

from src.core.request_router import (
    RequestRouter,
)

from src.core.task_models import (
    TaskRequest,
)

from src.memory.memory_formation import (
    process_turn,
)


class JARVIS:
    """
    Core orchestration layer for JARVIS.

    JARVIS coordinates:

        request routing
        command execution
        task planning
        plan validation
        execution policy
        plan execution
        conversation state
        persistence
        context construction
        AI request creation
        AI provider execution
        optional memory formation

    JARVIS is an orchestrator. Individual subsystems remain
    responsible for their own specialized behavior.
    """

    def __init__(
        self,
        ai_service: AIService,
        context_options: ContextOptions | None = None,
        conversation: ConversationState | None = None,
        conversation_store: ConversationStore | None = None,
        conversation_id: str | None = None,
        enable_memory_formation: bool = False,
        request_router: RequestRouter | None = None,
        command_service: CommandService | None = None,
        execution_planner: ExecutionPlanner | None = None,
        plan_validator: PlanValidator | None = None,
        execution_policy=None,
        plan_executor: PlanExecutor | None = None,
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

        self.request_router = (
            request_router
            if request_router is not None
            else RequestRouter()
        )

        if command_service is None:
            command_registry = CommandRegistry()
            command_service = CommandService(
                registry=command_registry,
                parser=CommandParser(),
            )

        self.command_service = command_service

        self.execution_planner = (
            execution_planner
            if execution_planner is not None
            else ExecutionPlanner()
        )

        self.plan_validator = (
            plan_validator
            if plan_validator is not None
            else PlanValidator()
        )

        if execution_policy is None:
            from src.core.execution_policy import (
                ExecutionPolicy,
            )

            execution_policy = ExecutionPolicy()

        self.execution_policy = execution_policy

        self.plan_executor = (
            plan_executor
            if plan_executor is not None
            else PlanExecutor()
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
        """
        Main JARVIS entry point.

        Explicit command syntax is routed to CommandService.
        Everything else remains a normal conversation in V1.

        Task execution is exposed through `ask_task`, because
        V1 request routing intentionally does not infer task intent
        from ordinary natural language.
        """

        if not isinstance(
            query,
            str,
        ):
            raise TypeError(
                "JARVIS query must be a string."
            )

        original_query = query
        query = query.strip()

        if not query:
            raise ValueError(
                "JARVIS query cannot be empty."
            )

        route = self.request_router.route(
            query
        )

        if route.request_type.value == "COMMAND":
            return self._handle_command(
                route.original_input
            )

        return self._handle_conversation(
            query,
            provider_name=provider_name,
            original_input=original_query,
        )

    def ask_task(
        self,
        task: TaskRequest,
    ) -> JARVISResponse:
        """
        Execute the V1 task orchestration path.

        Task intent must be explicit in V1 rather than inferred
        from ordinary conversational text.
        """

        route = self.request_router.route_task(
            task
        )

        return self._handle_task(
            route.task
        )

    def _handle_command(
        self,
        text: str,
    ) -> JARVISResponse:

        result = self.command_service.execute_text(
            text
        )

        if result is None:
            return JARVISResponse(
                content="Input is not a command.",
                ai_response=None,
                context=None,
                metadata={
                    "route": "COMMAND",
                    "success": False,
                },
            )

        return JARVISResponse(
            content=result.message,
            ai_response=None,
            context=None,
            metadata={
                "route": "COMMAND",
                "command": result.command,
                "success": result.success,
                **result.metadata,
            },
        )

    def _handle_task(
        self,
        task: TaskRequest,
    ) -> JARVISResponse:

        plan = self.execution_planner.plan(
            task
        )

        validation = self.plan_validator.validate(
            plan
        )

        if not validation.valid:
            return self._validation_response(
                validation
            )

        policy = self.execution_policy.evaluate(
            plan
        )

        if policy.decision == PolicyDecision.DENY:
            return self._policy_response(
                policy
            )

        if (
            policy.decision
            == PolicyDecision.REQUIRE_CONFIRMATION
        ):
            return self._policy_response(
                policy
            )

        execution = self.plan_executor.execute(
            plan,
            policy,
        )

        return self._execution_response(
            execution,
            plan,
            policy,
        )

    def _handle_conversation(
        self,
        query: str,
        provider_name: str | None = None,
        original_input: str | None = None,
    ) -> JARVISResponse:

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

        self._persist_state()

        # ---------------------------------------------------------
        # 6. Optional memory formation.
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
        # 7. Response metadata.
        # ---------------------------------------------------------

        metadata = {
            "route": "CONVERSATION",
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

    @staticmethod
    def _validation_response(
        validation,
    ) -> JARVISResponse:

        reasons = "\n".join(
            f"- {issue.message}"
            for issue in validation.issues
        )

        return JARVISResponse(
            content=(
                "I could not produce a valid execution plan.\n\n"
                f"{reasons}"
            ),
            ai_response=None,
            context=None,
            metadata={
                "route": "TASK",
                "stage": "VALIDATION",
                "valid": False,
                "plan_id": validation.plan.plan_id,
                "issues": tuple(
                    issue.code
                    for issue in validation.issues
                ),
            },
        )

    @staticmethod
    def _policy_response(
        policy: ExecutionPolicyResult,
    ) -> JARVISResponse:

        if policy.decision == PolicyDecision.DENY:
            prefix = "I cannot execute that task."
        else:
            prefix = (
                "The task is ready, but confirmation is required "
                "before execution."
            )

        reason_text = "\n".join(
            f"- {issue.message}"
            for issue in policy.issues
        )

        content = prefix

        if reason_text:
            content += f"\n\n{reason_text}"

        return JARVISResponse(
            content=content,
            ai_response=None,
            context=None,
            metadata={
                "route": "TASK",
                "stage": "POLICY",
                "plan_id": policy.plan.plan_id,
                "policy_decision": policy.decision.value,
                "issues": tuple(
                    issue.code
                    for issue in policy.issues
                ),
            },
        )

    @staticmethod
    def _execution_response(
        execution: PlanExecutionResult,
        plan: ExecutionPlan,
        policy: ExecutionPolicyResult,
    ) -> JARVISResponse:

        if execution.status == PlanExecutionStatus.COMPLETED:
            content = (
                "Task completed successfully.\n\n"
                f"Completed {execution.step_count} step(s)."
            )
        else:
            content = (
                "The task could not be completed.\n\n"
                + (
                    execution.error
                    or "Execution failed."
                )
            )

        return JARVISResponse(
            content=content,
            ai_response=None,
            context=None,
            metadata={
                "route": "TASK",
                "stage": "EXECUTION",
                "plan_id": plan.plan_id,
                "policy_decision": policy.decision.value,
                "execution_status": execution.status.value,
                "step_count": execution.step_count,
                "failed_steps": tuple(
                    step.step_id
                    for step in execution.failed_steps
                ),
            },
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
