import unittest

from src.commands.handlers.memory import (
    ShowMemoryHandler,
)

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


class MemoryCommandIntegrationTests(
    unittest.TestCase
):

    def setUp(
        self,
    ):

        self.registry = CommandRegistry()

        self.registry.register(
            ShowMemoryHandler()
        )

        self.service = CommandService(
            registry=self.registry,
            parser=CommandParser(),
        )

    def test_show_memory_is_routed_to_handler(
        self,
    ):

        result = self.service.execute_text(
            "/SHOW-MEMORY pcvue_skill"
        )

        self.assertIsInstance(
            result,
            CommandResult,
        )

        self.assertEqual(
            result.command,
            "SHOW-MEMORY",
        )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )