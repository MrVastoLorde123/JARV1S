"""M17 Human Operating Layer with M18 personal continuity.

Provides the human-facing control loop around the canonical JARVIS runtime.
It owns interaction mechanics only: command parsing, session identity,
request sequencing, and presentation. It does not interpret intent, grant
authority, authorize execution, mutate policy, or execute capabilities.

M18 adds a persistence seam for the human-facing session identifier. The
identifier is continuity metadata only; it is never treated as authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Protocol
from uuid import uuid4

from src.interface.boundary import InterfaceBoundary, InterfaceChannel

if TYPE_CHECKING:
    from src.core.jarvis_runtime import JARVISRuntime


class HumanRuntime(Protocol):
    """Minimal runtime contract consumed by the human operating layer."""

    def process(self, request): ...
    def respond(self, result): ...


class SessionIdentityRuntime(Protocol):
    """Persistence contract for the active human-facing session identity."""

    def get_or_create(self, requested_session_id: str | None = None) -> str: ...

    def new_session(self) -> str: ...


@dataclass(frozen=True)
class HumanCommand:
    name: str
    argument: str = ""


@dataclass(frozen=True)
class HumanTurn:
    request_id: str
    session_id: str
    content: str
    response: str


class HumanOperatingLayer:
    """Persistent text operator for one canonical JARVIS runtime."""

    HELP_TEXT = (
        "Commands:\n"
        ":help          show this help\n"
        ":session       show the active session ID\n"
        ":new           start a new session\n"
        ":quit          end the JARVIS session\n"
        "\n"
        "Anything else is sent to JARVIS as a normal request."
    )

    def __init__(
        self,
        runtime: "JARVISRuntime | HumanRuntime",
        *,
        session_id: str | None = None,
        session_identity: SessionIdentityRuntime | None = None,
        channel: InterfaceChannel = InterfaceChannel.TEXT,
        request_id_factory: Callable[[], str] | None = None,
    ) -> None:
        if not callable(getattr(runtime, "process", None)) or not callable(
            getattr(runtime, "respond", None)
        ):
            raise TypeError("runtime must provide process(request) and respond(result) methods")
        if session_identity is not None and not callable(
            getattr(session_identity, "get_or_create", None)
        ):
            raise TypeError("session_identity must provide get_or_create()")
        if session_identity is not None and not callable(
            getattr(session_identity, "new_session", None)
        ):
            raise TypeError("session_identity must provide new_session()")
        if not isinstance(channel, InterfaceChannel):
            raise TypeError("channel must be an InterfaceChannel")

        self.runtime = runtime
        self.boundary = InterfaceBoundary()
        self.channel = channel
        self._session_identity = session_identity
        self._session_id = self._resolve_initial_session_id(session_id)
        self._request_id_factory = request_id_factory or (lambda: self._new_id("request"))

    @property
    def session_id(self) -> str:
        return self._session_id

    def parse_command(self, content: str) -> HumanCommand | None:
        if not isinstance(content, str):
            raise TypeError("content must be a string")
        text = content.strip()
        if not text.startswith(":"):
            return None
        name, _, argument = text[1:].partition(" ")
        return HumanCommand(name=name.lower().strip(), argument=argument.strip())

    def handle(self, content: str) -> str | HumanTurn:
        """Handle one operator input; return a presentation-ready response or turn."""
        if not isinstance(content, str):
            raise TypeError("content must be a string")
        normalized = content.strip()
        if not normalized:
            return "Please enter a request."

        command = self.parse_command(normalized)
        if command is not None:
            return self._handle_command(command)

        request_id = self._request_id_factory()
        if not isinstance(request_id, str) or not request_id.strip():
            raise ValueError("request_id_factory must return a non-empty string")

        request = self.boundary.request(
            request_id=request_id,
            channel=self.channel,
            content=normalized,
            session_id=self._session_id,
            metadata={
                "human_operating_layer": "m17",
                "personal_continuity": "m18",
            },
        )
        result = self.runtime.process(request)
        response = self.runtime.respond(result)
        return HumanTurn(
            request_id=response.request_id,
            session_id=self._session_id,
            content=normalized,
            response=response.content,
        )

    def run(
        self,
        *,
        input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], object] = print,
        prompt: str = "You > ",
    ) -> None:
        """Run the persistent operator loop until :quit or EOF."""
        output_fn("JARVIS Human Operating Layer")
        output_fn(self.HELP_TEXT)
        output_fn(f"Session: {self._session_id}")

        while True:
            try:
                content = input_fn(prompt)
            except (EOFError, KeyboardInterrupt):
                output_fn("\nJARVIS session ended.")
                return

            result = self.handle(content)
            if result == "__QUIT__":
                output_fn("JARVIS session ended.")
                return
            if isinstance(result, HumanTurn):
                output_fn(f"\nJARVIS > {result.response}\n")
            else:
                output_fn(result)

    def _handle_command(self, command: HumanCommand) -> str:
        if command.name == "help":
            return self.HELP_TEXT
        if command.name == "session":
            return f"Active session: {self._session_id}"
        if command.name == "new":
            if self._session_identity is None:
                self._session_id = self._new_id("local")
            else:
                self._session_id = self._session_identity.new_session()
            return f"Started new session: {self._session_id}"
        if command.name in {"quit", "exit"}:
            return "__QUIT__"
        return f"Unknown command: :{command.name}. Use :help."

    def _resolve_initial_session_id(self, requested_session_id: str | None) -> str:
        if self._session_identity is not None:
            return self._session_identity.get_or_create(requested_session_id)
        if requested_session_id:
            return self._normalize_session_id(requested_session_id)
        return self._new_id("local")

    @staticmethod
    def _new_id(prefix: str) -> str:
        return f"{prefix}-{uuid4().hex}"

    @staticmethod
    def _normalize_session_id(session_id: str) -> str:
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("session_id must be a non-empty string")
        return session_id.strip()


__all__ = [
    "HumanCommand",
    "HumanTurn",
    "HumanOperatingLayer",
    "SessionIdentityRuntime",
]
