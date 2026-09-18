from src.ai.model_routing import ModelRole
from src.ai.service import AIService
from src.commands.parser import CommandParser
from src.commands.registry import CommandRegistry
from src.commands.service import CommandService
from src.context.memory_context_source_provider import MemoryContextSourceProvider
from src.context.models import ContextOptions
from src.context.working_context_consumption import WorkingContextConsumptionBoundary
from src.context.working_context import WorkingContext
from src.context.working_context_runtime import WorkingContextRuntime
from src.core.canonical_cognitive_runtime import CanonicalCognitiveRuntime
from src.core.capability_argument_planner import (
    AIRequestArgumentPlanner,
    CapabilityInvocationError,
    CapabilityInvocationService,
)
from src.core.capability_catalog import CapabilityCatalog
from src.core.capability_realization import CapabilityRealizationService
from src.core.capability_selection import DeterministicCapabilitySelector
from src.core.capability_selection_service import CapabilitySelectionService
from src.core.conversation import ConversationState
from src.core.conversation_store import ConversationStore
from src.core.execution_confirmation import (
    ExecutionConfirmationService,
    execution_plan_fingerprint,
)
from src.core.execution_executor_models import PlanExecutionResult, PlanExecutionStatus
from src.core.execution_plan_models import ExecutionPlan
from src.core.execution_planner import ExecutionPlanner
from src.core.execution_policy_models import ExecutionPolicyResult, PolicyDecision
from src.core.intelligent_request_router import IntelligentRequestRouter
from src.core.models import JARVISResponse
from src.core.operational_learning import OperationalLearningRuntime
from src.core.plan_executor import PlanExecutor
from src.core.plan_validator import PlanValidator
from src.core.request_router import RequestRouter
from src.core.task_models import TaskRequest, TaskType
from src.core.tool_execution import ToolCapabilityGateway, ToolInvoker, ToolPlanStepHandler
from src.memory.memory_formation import process_turn


class JARVIS:
    """Core orchestration layer for JARVIS."""

    def __init__(
        self,
        ai_service: AIService,
        context_options: ContextOptions | None = None,
        conversation: ConversationState | None = None,
        conversation_store: ConversationStore | None = None,
        conversation_id: str | None = None,
        enable_memory_formation: bool = False,
        request_router: RequestRouter | None = None,
        intelligent_request_router: IntelligentRequestRouter | None = None,
        command_service: CommandService | None = None,
        execution_planner: ExecutionPlanner | None = None,
        plan_validator: PlanValidator | None = None,
        execution_policy=None,
        plan_executor: PlanExecutor | None = None,
        execution_confirmation_service: ExecutionConfirmationService | None = None,
        tool_invoker: ToolInvoker | None = None,
        capability_selection_service: CapabilitySelectionService | None = None,
        capability_invocation_service: CapabilityInvocationService | None = None,
        capability_realization_service: CapabilityRealizationService | None = None,
        cognitive_runtime: CanonicalCognitiveRuntime | None = None,
        working_context_runtime: WorkingContextRuntime | None = None,
        working_context_consumption_boundary: WorkingContextConsumptionBoundary | None = None,
        operational_learning_runtime: OperationalLearningRuntime | None = None,
    ):
        self.ai_service = ai_service
        self.context_options = context_options if context_options is not None else ContextOptions()
        self.conversation_store = conversation_store
        self._last_working_context_error = None
        self._enable_memory_formation = enable_memory_formation
        self.request_router = request_router if request_router is not None else RequestRouter()
        self.intelligent_request_router = intelligent_request_router
        if cognitive_runtime is not None and not callable(getattr(cognitive_runtime, "run", None)):
            raise TypeError("cognitive_runtime must provide a callable run method")
        self.cognitive_runtime = cognitive_runtime or CanonicalCognitiveRuntime()
        if operational_learning_runtime is not None and not isinstance(
            operational_learning_runtime, OperationalLearningRuntime
        ):
            raise TypeError(
                "operational_learning_runtime must be an OperationalLearningRuntime or None."
            )
        self.operational_learning_runtime = (
            operational_learning_runtime
            if operational_learning_runtime is not None
            else OperationalLearningRuntime()
        )

        if working_context_runtime is not None and not isinstance(working_context_runtime, WorkingContextRuntime):
            raise TypeError("working_context_runtime must be a WorkingContextRuntime.")
        if working_context_consumption_boundary is not None and not isinstance(
            working_context_consumption_boundary,
            WorkingContextConsumptionBoundary,
        ):
            raise TypeError(
                "working_context_consumption_boundary must be a WorkingContextConsumptionBoundary."
            )

        if working_context_runtime is None:
            source_provider = MemoryContextSourceProvider(
                include_memories=self.context_options.include_memories,
                include_evidence=self.context_options.include_evidence,
                max_memories=self.context_options.max_memories,
                max_evidence=self.context_options.max_evidence,
            )
            working_context_runtime = WorkingContextRuntime(source_provider)
        self.working_context_runtime = working_context_runtime
        self.working_context_consumption_boundary = (
            working_context_consumption_boundary
            if working_context_consumption_boundary is not None
            else WorkingContextConsumptionBoundary()
        )

        if command_service is None:
            command_service = CommandService(
                registry=CommandRegistry(),
                parser=CommandParser(),
            )
        self.command_service = command_service

        self.execution_planner = execution_planner if execution_planner is not None else ExecutionPlanner()
        self.plan_validator = plan_validator if plan_validator is not None else PlanValidator()

        if execution_policy is None:
            from src.core.execution_policy import ExecutionPolicy
            execution_policy = ExecutionPolicy()
        self.execution_policy = execution_policy

        self.plan_executor = plan_executor if plan_executor is not None else PlanExecutor()
        self.execution_confirmation_service = (
            execution_confirmation_service
            if execution_confirmation_service is not None
            else ExecutionConfirmationService()
        )
        self.tool_invoker = tool_invoker

        if tool_invoker is not None:
            self.plan_executor.register_handler(
                ToolPlanStepHandler.ACTION,
                ToolPlanStepHandler(tool_invoker),
            )

        if capability_selection_service is not None and not isinstance(
            capability_selection_service,
            CapabilitySelectionService,
        ):
            raise TypeError("capability_selection_service must be a CapabilitySelectionService")
        if capability_invocation_service is not None and not isinstance(
            capability_invocation_service,
            CapabilityInvocationService,
        ):
            raise TypeError("capability_invocation_service must be a CapabilityInvocationService")
        if capability_realization_service is not None and not isinstance(
            capability_realization_service,
            CapabilityRealizationService,
        ):
            raise TypeError("capability_realization_service must be a CapabilityRealizationService")

        if capability_realization_service is not None:
            self.capability_realization_service = capability_realization_service
        else:
            if capability_selection_service is None and isinstance(tool_invoker, ToolCapabilityGateway):
                capability_selection_service = CapabilitySelectionService(
                    CapabilityCatalog(tool_invoker),
                    DeterministicCapabilitySelector(),
                )
            if capability_invocation_service is None and capability_selection_service is not None:
                capability_invocation_service = CapabilityInvocationService(
                    AIRequestArgumentPlanner(ai_service),
                )

            self.capability_realization_service = None
            if capability_selection_service is not None and capability_invocation_service is not None:
                self.capability_realization_service = CapabilityRealizationService(
                    capability_selection_service,
                    capability_invocation_service,
                )

        if conversation is not None:
            self.conversation = conversation
        elif conversation_store is not None:
            if conversation_id is not None:
                restored = conversation_store.load_state(conversation_id)
                if restored is None:
                    raise ValueError("Persistent conversation does not exist.")
                self.conversation = restored
            else:
                record = conversation_store.create_conversation()
                self.conversation = conversation_store.load_state(record.conversation_id)
        else:
            self.conversation = ConversationState()

    def _persist_state(self):
        if self.conversation_store is None:
            return
        self.conversation_store.save_state(self.conversation.snapshot())

    def ask(self, query: str, provider_name: str | None = None) -> JARVISResponse:
        """Route one user request through conversation, command, or execution paths."""
        if not isinstance(query, str):
            raise TypeError("JARVIS query must be a string.")

        original_query = query
        query = query.strip()
        if not query:
            raise ValueError("JARVIS query cannot be empty.")

        router = (
            self.intelligent_request_router
            if self.intelligent_request_router is not None
            else self.request_router
        )
        route = router.route(query)

        if route.request_type.value == "COMMAND":
            return self._handle_command(route.original_input)

        if route.request_type.value == "TASK" and route.task is not None:
            task = route.task
            realized_metadata = {}
            is_natural_tool = (
                route.metadata.get("intent_kind") == "tool"
                and task.task_type == TaskType.TOOL
                and "tool_name" not in task.metadata
            )

            if is_natural_tool:
                if self.capability_realization_service is None:
                    return self._capability_realization_unavailable_response(task)
                try:
                    realization = self.capability_realization_service.realize(task.content)
                except LookupError:
                    return JARVISResponse(
                        content="I could not find a registered capability that matches that request.",
                        ai_response=None,
                        context=None,
                        metadata={
                            "route": "TASK",
                            "stage": "CAPABILITY_SELECTION",
                            "success": False,
                            "intent_kind": route.metadata.get("intent_kind"),
                            "intent_confidence": route.metadata.get("intent_confidence"),
                        },
                    )
                except CapabilityInvocationError as exc:
                    return JARVISResponse(
                        content=(
                            "I identified a capability, but I could not build a valid invocation.\n\n"
                            f"{exc}"
                        ),
                        ai_response=None,
                        context=None,
                        metadata={
                            "route": "TASK",
                            "stage": "CAPABILITY_INVOCATION",
                            "success": False,
                            "intent_kind": route.metadata.get("intent_kind"),
                            "intent_confidence": route.metadata.get("intent_confidence"),
                            "cognitive_context": cognitive_context,
                        },
                    )
                except (TypeError, ValueError) as exc:
                    return JARVISResponse(
                        content=(
                            "I could not realize that capability request safely.\n\n"
                            f"{exc}"
                        ),
                        ai_response=None,
                        context=None,
                        metadata={
                            "route": "TASK",
                            "stage": "CAPABILITY_REALIZATION",
                            "success": False,
                            "intent_kind": route.metadata.get("intent_kind"),
                            "intent_confidence": route.metadata.get("intent_confidence"),
                            "cognitive_context": cognitive_context,
                        },
                    )

                task = TaskRequest(
                    content=task.content,
                    task_type=TaskType.TOOL,
                    metadata={
                        **task.metadata,
                        "tool_name": realization.request.tool_name,
                        "arguments": dict(realization.request.arguments),
                        **(
                            {"invocation_id": realization.request.invocation_id}
                            if realization.request.invocation_id is not None
                            else {}
                        ),
                    },
                )
                realized_metadata = {
                    "capability": realization.request.tool_name,
                    "capability_score": realization.candidate.score,
                    "capability_reason": realization.candidate.reason,
                    "capability_realized": True,
                }

            response = self._handle_task(task)
            response.metadata.update(
                {
                    "intent_kind": route.metadata.get("intent_kind"),
                    "intent_confidence": route.metadata.get("intent_confidence"),
                    **realized_metadata,
                }
            )
            return response

        return self._handle_conversation(
            query,
            provider_name=provider_name,
            original_input=original_query,
        )

    def _build_cognitive_task_context(
        self,
        query: str,
        route_metadata: dict[str, object],
        *,
        working_context: WorkingContext | None = None,
    ) -> dict[str, object]:
        context_ids: tuple[str, ...] = ()
        memory_ids: tuple[str, ...] = ()
        working_context_payload = None
        if working_context is not None:
            working_context_payload = working_context.to_context()
            if working_context.source_selection is not None:
                context_ids = tuple(working_context.source_selection.selected_source_ids)
            ordered_memory_ids = []
            seen_memory_ids = set()
            for item in working_context.context_package.items:
                memory_id = item.provenance.get("memory_id")
                if memory_id is None:
                    continue
                normalized = str(memory_id)
                if normalized in seen_memory_ids:
                    continue
                seen_memory_ids.add(normalized)
                ordered_memory_ids.append(normalized)
            memory_ids = tuple(ordered_memory_ids)

        operational_learning_context = self.operational_learning_runtime.context_for(query)
        try:
            result = self.cognitive_runtime.run(
                query,
                context_ids=context_ids,
                memory_ids=memory_ids,
                metadata={
                    "intent_kind": route_metadata.get("intent_kind"),
                    "intent_confidence": route_metadata.get("intent_confidence"),
                    "intent_reasoning": route_metadata.get("intent_reasoning"),
                    "working_context": working_context_payload,
                    "operational_learning": operational_learning_context,
                },
            )
        except Exception as exc:
            return {
                "status": "UNAVAILABLE",
                "error_type": type(exc).__name__,
                "error": str(exc),
                "authority_granted": False,
                "authorization_granted": False,
                "execution_requested": False,
                "execution_performed": False,
            }

        context = result.to_context()
        context["status"] = "COMPLETED"
        context["intent_kind"] = route_metadata.get("intent_kind")
        context["intent_confidence"] = route_metadata.get("intent_confidence")
        context["contextualization_status"] = (
            "COMPLETED"
            if working_context is not None
            else (
                "UNAVAILABLE"
                if self._last_working_context_error is not None
                else "NOT_ATTACHED"
            )
        )
        context["contextualization_error"] = self._last_working_context_error
        context["context_ids"] = context_ids
        context["memory_ids"] = memory_ids
        context["working_context"] = working_context_payload
        context["operational_learning"] = operational_learning_context
        context["goal"] = result.planning.context.goal.to_context()

        selected_plan_id = result.planning.ranking.advisory_selected_plan_id
        selected_plan = next(
            (
                candidate
                for candidate in (
                    getattr(result.initiative.context, "selected_plan", None),
                )
                if candidate is not None
            ),
            None,
        )
        if selected_plan is not None:
            context["selected_plan"] = selected_plan.to_context()
        else:
            context["selected_plan"] = None

        selected_evaluation = next(
            (
                evaluation
                for evaluation in result.planning.evaluations
                if evaluation.plan_id == selected_plan_id
            ),
            None,
        )
        context["selected_evaluation"] = (
            None if selected_evaluation is None else selected_evaluation.to_context()
        )
        proposal = result.initiative.proposal
        context["proposal"] = None if proposal is None else proposal.to_dict()
        return context

    def _build_task_working_context(self, task: TaskRequest) -> WorkingContext | None:
        self._last_working_context_error = None
        if self.conversation_store is None:
            return None

        try:
            return self.working_context_runtime.compose(
                task.content,
                options=self.context_options,
                conversation_state=self.conversation.snapshot(),
                task=task,
            )
        except Exception as exc:
            self._last_working_context_error = {
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
            return None

    def ask_task(self, task: TaskRequest) -> JARVISResponse:
        route = self.request_router.route_task(task)
        return self._handle_task(route.task)

    def _handle_command(self, text: str) -> JARVISResponse:
        parsed = self.command_service.parser.parse(text)
        if parsed is not None and parsed.name == "CONFIRM" and self.execution_confirmation_service.get_pending() is not None:
            return self._confirm_execution(parsed.arguments)
        if parsed is not None and parsed.name == "CANCEL" and self.execution_confirmation_service.get_pending() is not None:
            return self._cancel_execution(parsed.arguments)

        result = self.command_service.execute_text(text)
        if result is None:
            return JARVISResponse(
                content="Input is not a command.",
                ai_response=None,
                context=None,
                metadata={"route": "COMMAND", "success": False},
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

    def _handle_task(self, task: TaskRequest) -> JARVISResponse:
        working_context = self._build_task_working_context(task)
        cognitive_context = task.metadata.get("cognitive_context")
        if cognitive_context is None:
            cognitive_context = self._build_cognitive_task_context(
                task.content,
                {},
                working_context=working_context,
            )

        capability_metadata = {}
        if (
            task.task_type == TaskType.ACTION
            and self.capability_realization_service is not None
            and not task.metadata.get("tool_name")
        ):
            capability_query = task.content
            if isinstance(cognitive_context, dict):
                goal = cognitive_context.get("goal")
                if isinstance(goal, dict):
                    desired_outcome = goal.get("desired_outcome")
                    if isinstance(desired_outcome, str) and desired_outcome.strip():
                        capability_query = desired_outcome.strip()

            try:
                realization = self.capability_realization_service.realize(
                    capability_query,
                )
            except LookupError:
                return JARVISResponse(
                    content="I could not find a registered capability that matches the planned action.",
                    ai_response=None,
                    context=None,
                    metadata={
                        "route": "TASK",
                        "stage": "CAPABILITY_SELECTION",
                        "success": False,
                        "cognitive_context": cognitive_context,
                        "capability_query": capability_query,
                    },
                )
            except CapabilityInvocationError as exc:
                return JARVISResponse(
                    content=(
                        "I identified a capability for the planned action, "
                        "but I could not build a valid invocation.\n\n"
                        f"{exc}"
                    ),
                    ai_response=None,
                    context=None,
                    metadata={
                        "route": "TASK",
                        "stage": "CAPABILITY_INVOCATION",
                        "success": False,
                        "cognitive_context": cognitive_context,
                        "capability_query": capability_query,
                    },
                )
            except (TypeError, ValueError) as exc:
                return JARVISResponse(
                    content=(
                        "I could not safely realize a capability for the planned action.\n\n"
                        f"{exc}"
                    ),
                    ai_response=None,
                    context=None,
                    metadata={
                        "route": "TASK",
                        "stage": "CAPABILITY_REALIZATION",
                        "success": False,
                        "cognitive_context": cognitive_context,
                        "capability_query": capability_query,
                    },
                )

            task = TaskRequest(
                content=task.content,
                task_type=TaskType.TOOL,
                metadata={
                    **task.metadata,
                    "tool_name": realization.request.tool_name,
                    "arguments": dict(realization.request.arguments),
                    **(
                        {"invocation_id": realization.request.invocation_id}
                        if realization.request.invocation_id is not None
                        else {}
                    ),
                },
            )
            capability_metadata = {
                "capability": realization.request.tool_name,
                "capability_score": realization.candidate.score,
                "capability_reason": realization.candidate.reason,
                "capability_query": capability_query,
                "capability_realized": True,
            }

        plan = self.execution_planner.plan(task)
        if not isinstance(cognitive_context, dict):
            raise TypeError("cognitive_context must be mapping-compatible")
        plan.metadata["cognitive_context"] = dict(cognitive_context)
        selected_plan = cognitive_context.get("selected_plan")
        if isinstance(selected_plan, dict):
            planned_steps = selected_plan.get("steps")
            if isinstance(planned_steps, (tuple, list)) and planned_steps:
                first_step = planned_steps[0]
                if isinstance(first_step, dict):
                    description = first_step.get("description")
                    if isinstance(description, str) and description.strip():
                        plan.metadata["cognitive_advisory_step"] = description
                        for step in plan.steps:
                            step.metadata["cognitive_advisory_step"] = description
                            step.metadata["cognitive_context"] = dict(cognitive_context)
        validation = self.plan_validator.validate(plan)
        if not validation.valid:
            response = self._validation_response(validation)
            response.metadata["cognitive_context"] = cognitive_context
            return response

        policy = self.execution_policy.evaluate(plan)
        if policy.decision == PolicyDecision.DENY:
            response = self._policy_response(policy)
            response.metadata["cognitive_context"] = cognitive_context
            return response

        if policy.decision == PolicyDecision.REQUIRE_CONFIRMATION:
            pending = self.execution_confirmation_service.stage(
                plan,
                metadata={
                    "policy_decision": policy.decision.value,
                    "plan_fingerprint": execution_plan_fingerprint(plan),
                },
            )
            return JARVISResponse(
                content=(
                    "The task is ready for execution, but confirmation is required.\n\n"
                    f"Operation ID: {pending.operation_id}\n"
                    f"Task: {plan.task_description}\n\n"
                    "Use /CONFIRM to authorize it or /CANCEL to discard it."
                ),
                ai_response=None,
                context=None,
                metadata={
                    "route": "TASK",
                    "stage": "CONFIRMATION",
                    "plan_id": plan.plan_id,
                    "operation_id": pending.operation_id,
                    "plan_fingerprint": pending.metadata["plan_fingerprint"],
                    "policy_decision": policy.decision.value,
                    "cognitive_context": cognitive_context,
                    "execution_plan_cognitive_context": plan.metadata.get("cognitive_context"),
                    **capability_metadata,
                },
            )

        execution = self.plan_executor.execute(plan, policy)
        response = self._execution_response(execution, plan, policy)
        response = self._attach_operational_learning(
            response,
            execution,
            plan,
            capability=capability_metadata.get("capability"),
        )
        response.metadata["cognitive_context"] = cognitive_context
        response.metadata.update(capability_metadata)
        return response

    def _handle_conversation(
        self,
        query: str,
        provider_name: str | None = None,
        original_input: str | None = None,
    ) -> JARVISResponse:
        self.conversation.add_turn("user", query)
        user_snapshot = self.conversation.snapshot()
        source_created_at = user_snapshot.turns[-1].timestamp if user_snapshot.turns else None
        user_message_id = None

        if self.conversation_store is not None:
            previous_message_id = self._get_last_persistent_message_id()
            stored_user_message = self.conversation_store.append_message(
                conversation_id=self.conversation.conversation_id,
                role="user",
                content=query,
                parent_id=previous_message_id,
                created_at=source_created_at,
            )
            user_message_id = stored_user_message["message_id"]

        self._persist_state()
        working_context = self.working_context_runtime.compose(
            query,
            options=self.context_options,
            conversation_state=user_snapshot if self.context_options.include_state else None,
        )
        request = self.working_context_consumption_boundary.consume(working_context)
        ai_response = self.ai_service.generate_for_role(
            request,
            role=ModelRole.GENERAL,
            provider_name=provider_name,
        )
        response_content = str(ai_response.content)
        self.conversation.add_turn("assistant", response_content)
        assistant_snapshot = self.conversation.snapshot()
        assistant_created_at = assistant_snapshot.turns[-1].timestamp if assistant_snapshot.turns else None

        if self.conversation_store is not None:
            self.conversation_store.append_message(
                conversation_id=self.conversation.conversation_id,
                role="assistant",
                content=response_content,
                parent_id=user_message_id,
                created_at=assistant_created_at,
            )

        self._persist_state()
        formation_result = None
        if self._enable_memory_formation:
            formation_result = process_turn(
                user_query=query,
                assistant_response=response_content,
                conversation_id=self.conversation.conversation_id if self.conversation_store is not None else None,
                message_id=user_message_id,
                source_created_at=source_created_at,
            )

        metadata = {
            "route": "CONVERSATION",
            "context_items": len(working_context.context_package.items),
            "working_context_items": len(working_context.context_package.items),
            "working_context_runtime": "v1",
            "source_selection": (
                None
                if working_context.source_selection is None
                else working_context.source_selection.selected_source_ids
            ),
            "provider": ai_response.provider,
            "model": ai_response.model,
            "conversation_id": self.conversation.conversation_id,
            "persistent": self.conversation_store is not None,
        }
        if formation_result is not None:
            metadata["memory_formation"] = {
                "candidates_extracted": formation_result.candidates_extracted,
                "memories_created": formation_result.memories_created,
                "memories_deduplicated": formation_result.memories_deduplicated,
                "evidence_added": formation_result.evidence_added,
                "errors": formation_result.errors,
            }

        return JARVISResponse(
            content=response_content,
            ai_response=ai_response,
            context=working_context.context_package,
            metadata=metadata,
        )

    @staticmethod
    def _validation_response(validation) -> JARVISResponse:
        reasons = "\n".join(f"- {issue.message}" for issue in validation.issues)
        return JARVISResponse(
            content=("I could not produce a valid execution plan.\n\n" f"{reasons}"),
            ai_response=None,
            context=None,
            metadata={
                "route": "TASK",
                "stage": "VALIDATION",
                "valid": False,
                "plan_id": validation.plan.plan_id,
                "issues": tuple(issue.code for issue in validation.issues),
                "execution_plan_cognitive_context": validation.plan.metadata.get("cognitive_context"),
            },
        )

    @staticmethod
    def _policy_response(policy: ExecutionPolicyResult) -> JARVISResponse:
        if policy.decision == PolicyDecision.DENY:
            prefix = "I cannot execute that task."
        else:
            prefix = "The task is ready, but confirmation is required before execution."
        reason_text = "\n".join(f"- {issue.message}" for issue in policy.issues)
        content = prefix if not reason_text else f"{prefix}\n\n{reason_text}"
        return JARVISResponse(
            content=content,
            ai_response=None,
            context=None,
            metadata={
                "route": "TASK",
                "stage": "POLICY",
                "plan_id": policy.plan.plan_id,
                "policy_decision": policy.decision.value,
                "issues": tuple(issue.code for issue in policy.issues),
                "execution_plan_cognitive_context": policy.plan.metadata.get("cognitive_context"),
            },
        )

    def _attach_operational_learning(
        self,
        response: JARVISResponse,
        execution: PlanExecutionResult,
        plan: ExecutionPlan,
        *,
        capability: str | None = None,
    ) -> JARVISResponse:
        """Record one execution result as bounded experience for future cognition."""
        try:
            record = self.operational_learning_runtime.record_execution(
                execution,
                plan,
                capability=capability,
            )
        except Exception as exc:
            response.metadata["operational_learning_status"] = "UNAVAILABLE"
            response.metadata["operational_learning_error"] = {
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
            return response

        response.metadata["operational_learning_status"] = "RECORDED"
        response.metadata["operational_learning"] = {
            "experience_id": record.experience.experience_id,
            "evaluation_id": record.evaluation.evaluation_id,
            "evaluation_status": record.evaluation.status.value,
            "adaptation_hint_id": record.adaptation_hint.hint_id,
            "adaptation_hint_status": record.adaptation_hint.status.value,
            "guidance": record.adaptation_hint.guidance,
            "authority_granted": False,
            "execution_requested": False,
            "authorizes_retry": False,
            "mutates_policy": False,
        }
        return response

    @staticmethod
    def _execution_response(
        execution: PlanExecutionResult,
        plan: ExecutionPlan,
        policy: ExecutionPolicyResult,
    ) -> JARVISResponse:
        outputs = tuple(
            step.output
            for step in execution.steps
            if step.status.value == "COMPLETED" and step.output is not None
        )
        if execution.status == PlanExecutionStatus.COMPLETED:
            content = "Task completed successfully.\n\n" f"Completed {execution.step_count} step(s)."
            if outputs:
                if len(outputs) == 1:
                    content += "\n\nResult:\n" + str(outputs[0])
                else:
                    content += "\n\nResults:\n" + "\n\n".join(str(output) for output in outputs)
        else:
            content = "The task could not be completed.\n\n" + (execution.error or "Execution failed.")

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
                "failed_steps": tuple(step.step_id for step in execution.failed_steps),
                "execution_outputs": outputs,
                "execution_plan_cognitive_context": plan.metadata.get("cognitive_context"),
            },
        )

    def _get_last_persistent_message_id(self):
        if self.conversation_store is None:
            return None
        rows = self.conversation_store.get_messages(self.conversation.conversation_id)
        if not rows:
            return None
        return rows[-1][0]

    def confirm_operation(self, operation_id: str | None = None) -> JARVISResponse:
        """Confirm one staged execution through the existing deterministic boundary."""
        arguments = () if operation_id is None else (operation_id,)
        return self._confirm_execution(arguments)

    def cancel_operation(self, operation_id: str | None = None) -> JARVISResponse:
        """Cancel one staged execution through the existing deterministic boundary."""
        arguments = () if operation_id is None else (operation_id,)
        return self._cancel_execution(arguments)

    def _cancel_execution(self, arguments: tuple[str, ...]) -> JARVISResponse:
        if len(arguments) > 1:
            return JARVISResponse(
                content="/CANCEL accepts zero or one operation ID.",
                ai_response=None,
                context=None,
                metadata={"route": "COMMAND", "command": "CANCEL", "success": False},
            )
        operation_id = arguments[0] if arguments else None
        operation = self.execution_confirmation_service.cancel(operation_id)
        if operation is None:
            return JARVISResponse(
                content="No matching pending execution operation was found.",
                ai_response=None,
                context=None,
                metadata={"route": "COMMAND", "command": "CANCEL", "success": False},
            )
        return JARVISResponse(
            content=f"Execution cancelled.\n\nOperation ID: {operation.operation_id}",
            ai_response=None,
            context=None,
            metadata={
                "route": "COMMAND",
                "command": "CANCEL",
                "success": True,
                "operation_id": operation.operation_id,
                "operation_status": operation.status.value,
            },
        )

    def _confirm_execution(self, arguments: tuple[str, ...]) -> JARVISResponse:
        if len(arguments) > 1:
            return JARVISResponse(
                content="/CONFIRM accepts zero or one operation ID.",
                ai_response=None,
                context=None,
                metadata={"route": "COMMAND", "command": "CONFIRM", "success": False},
            )
        operation_id = arguments[0] if arguments else None
        operation = (
            self.execution_confirmation_service.get_pending()
            if operation_id is None
            else self.execution_confirmation_service.get(operation_id)
        )
        if operation is None:
            return JARVISResponse(
                content="No matching pending execution operation was found.",
                ai_response=None,
                context=None,
                metadata={"route": "COMMAND", "command": "CONFIRM", "success": False},
            )

        expected_fingerprint = operation.metadata.get("plan_fingerprint")
        actual_fingerprint = execution_plan_fingerprint(operation.plan)
        if expected_fingerprint != actual_fingerprint:
            return JARVISResponse(
                content="Execution blocked: the staged plan no longer matches its original fingerprint.",
                ai_response=None,
                context=None,
                metadata={
                    "route": "COMMAND",
                    "command": "CONFIRM",
                    "success": False,
                    "stage": "FINGERPRINT",
                    "operation_id": operation.operation_id,
                },
            )

        validation = self.plan_validator.validate(operation.plan)
        if not validation.valid:
            return self._validation_response(validation)
        policy = self.execution_policy.authorize_confirmed(operation.plan)
        if policy.decision != PolicyDecision.ALLOW:
            return self._policy_response(policy)
        confirmed = self.execution_confirmation_service.confirm(operation.operation_id)
        if confirmed is None:
            return JARVISResponse(
                content="The execution operation could not be confirmed.",
                ai_response=None,
                context=None,
                metadata={"route": "COMMAND", "command": "CONFIRM", "success": False},
            )
        execution = self.plan_executor.execute(confirmed.plan, policy)
        response = self._execution_response(execution, confirmed.plan, policy)
        response = self._attach_operational_learning(
            response,
            execution,
            confirmed.plan,
        )
        response.metadata.update({"confirmation": True, "operation_id": confirmed.operation_id})
        return response

    def _capability_realization_unavailable_response(self, task: TaskRequest) -> JARVISResponse:
        return JARVISResponse(
            content="No capability realization service is configured for natural-language tool requests.",
            ai_response=None,
            context=None,
            metadata={
                "route": "TASK",
                "stage": "CAPABILITY_REALIZATION",
                "success": False,
                "task_type": task.task_type.value,
                "cognitive_context": task.metadata.get("cognitive_context"),
            },
        )
