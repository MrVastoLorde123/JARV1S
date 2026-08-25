import json
from urllib import error, request
from src.context.models import ContextPackage

from src.ai.errors import (
    AuthenticationError,
    GenerationError,
    InvalidRequestError,
    ProviderUnavailableError,
    TimeoutError,
)

from src.ai.models import (
    AIRequest,
    AIResponse,
    AICapabilities,
)

from src.ai.provider import AIProvider


class LocalProvider(AIProvider):
    """
    JARVIS provider for a local llama.cpp server.

    The provider communicates with llama-server over localhost HTTP.
    """

    def __init__(
        self,
        base_url="http://127.0.0.1:8080",
        model="qwen3-4b-local",
        timeout=120,
        api_key="no-key-required",
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.api_key = api_key

    def provider_name(self):
        return "local"

    def capabilities(self):

        return AICapabilities(
            text_generation=True,
            streaming=False,
            structured_output=True,
            tool_calling=False,
            vision=False,
            embeddings=False,
        )

    def _build_context_text(self, context):

        if context is None:
            return ""

        if not isinstance(context, ContextPackage):
            raise InvalidRequestError(
                "LocalProvider requires a ContextPackage "
                "when context is provided."
            )

        sections = []

        if getattr(context, "instructions", None):

            instructions = "\n".join(
                f"- {instruction}"
                for instruction in context.instructions
            )

            sections.append(
                "JARVIS INSTRUCTIONS:\n"
                f"{instructions}"
            )

        items = getattr(context, "items", ())

        if items:

            context_lines = []

            for item in items:

                provenance = ""

                if item.provenance:
                    provenance = (
                        f"\nProvenance: "
                        f"{item.provenance}"
                    )

                context_lines.append(
                    f"[{item.source_type}] "
                    f"{item.content}\n"
                    f"Confidence: {item.confidence}\n"
                    f"Relevance: {item.relevance_score}\n"
                    f"Importance: {item.importance}"
                    f"{provenance}"
                )

            sections.append(
                "JARVIS CONTEXT:\n"
                + "\n\n".join(context_lines)
            )

        return "\n\n".join(sections)

    def _build_messages(self, request):

        context_text = self._build_context_text(
            request.context
        )

        system_parts = [
            "You are the intelligence component "
            "of JARVIS.",
        ]

        if context_text:
            system_parts.append(
                context_text
            )

        messages = [
            {
                "role": "system",
                "content": "\n\n".join(system_parts),
            },
            {
                "role": "user",
                "content": request.task,
            },
        ]

        return messages

    def _build_payload(self, request):

        payload = {
            "model": (
                request.model
                or self.model
            ),
            "messages": self._build_messages(
                request
            ),
            "stream": False,
        }

        options = request.generation_options

        if "temperature" in options:
            payload["temperature"] = (
                options["temperature"]
            )

        if "top_p" in options:
            payload["top_p"] = options["top_p"]

        if "max_output_tokens" in options:
            payload["max_tokens"] = (
                options["max_output_tokens"]
            )

        elif "max_tokens" in options:
            payload["max_tokens"] = (
                options["max_tokens"]
            )

        if "seed" in options:
            payload["seed"] = options["seed"]

        if "response_format" in options:
            payload["response_format"] = (
                options["response_format"]
            )

        return payload

    def generate(self, request_object):

        if not isinstance(
            request_object,
            AIRequest
        ):
            raise InvalidRequestError(
                "LocalProvider requires an AIRequest."
            )

        if not request_object.task.strip():
            raise InvalidRequestError(
                "AIRequest task cannot be empty."
            )

        payload = self._build_payload(
            request_object
        )

        body = json.dumps(
            payload
        ).encode("utf-8")

        endpoint = (
            f"{self.base_url}"
            "/v1/chat/completions"
        )

        http_request = request.Request(
            endpoint,
            data=body,
            headers={
                "Content-Type":
                    "application/json",
                "Authorization":
                    f"Bearer {self.api_key}",
            },
            method="POST",
        )

        try:

            with request.urlopen(
                http_request,
                timeout=self.timeout,
            ) as response:

                response_body = (
                    response.read()
                    .decode("utf-8")
                )

        except error.HTTPError as exc:

            if exc.code in (401, 403):
                raise AuthenticationError(
                    "Local AI server rejected "
                    "the request."
                ) from exc

            try:
                error_body = (
                    exc.read()
                    .decode("utf-8")
                )
            except Exception:
                error_body = str(exc)

            raise GenerationError(
                f"Local AI server returned "
                f"HTTP {exc.code}: "
                f"{error_body}"
            ) from exc

        except error.URLError as exc:

            raise ProviderUnavailableError(
                "Unable to connect to "
                "llama-server."
            ) from exc

        except TimeoutError as exc:

            raise TimeoutError(
                "Local AI request timed out."
            ) from exc

        except OSError as exc:

            raise ProviderUnavailableError(
                "Local AI server connection failed."
            ) from exc

        try:

            data = json.loads(
                response_body
            )

            choice = data["choices"][0]

            message = choice["message"]

            content = message.get(
                "content",
                ""
            )

            usage_data = data.get(
                "usage"
            )

            usage = None

            if usage_data:

                from src.ai.models import AIUsage

                usage = AIUsage(
                    input_tokens=usage_data.get(
                        "prompt_tokens"
                    ),
                    output_tokens=usage_data.get(
                        "completion_tokens"
                    ),
                    total_tokens=usage_data.get(
                        "total_tokens"
                    ),
                )

            return AIResponse(
                content=content,
                provider=self.provider_name(),
                model=data.get(
                    "model",
                    request_object.model
                    or self.model,
                ),
                finish_reason=choice.get(
                    "finish_reason"
                ),
                usage=usage,
                metadata={
                    "endpoint": endpoint,
                    "local": True,
                },
            )

        except (
            KeyError,
            IndexError,
            TypeError,
            json.JSONDecodeError,
        ) as exc:

            raise GenerationError(
                "Local AI server returned "
                "an unexpected response."
            ) from exc