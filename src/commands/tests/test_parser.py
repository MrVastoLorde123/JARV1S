import unittest

from src.commands.models import (
    CommandRequest,
)

from src.commands.parser import (
    CommandParser,
)


class CommandParserTests(
    unittest.TestCase
):

    def setUp(
        self,
    ):
        self.parser = CommandParser()

    def test_normal_text_is_not_a_command(
        self,
    ):
        result = self.parser.parse(
            "Tell me about PCVUE."
        )

        self.assertIsNone(
            result
        )

    def test_command_name_is_normalized(
        self,
    ):
        result = self.parser.parse(
            "/remember"
        )

        self.assertIsInstance(
            result,
            CommandRequest,
        )

        self.assertEqual(
            result.name,
            "REMEMBER",
        )

    def test_arguments_are_parsed(
        self,
    ):
        result = self.parser.parse(
            "/DELETE pcvue_skill"
        )

        self.assertEqual(
            result.name,
            "DELETE",
        )

        self.assertEqual(
            result.arguments,
            ("pcvue_skill",),
        )

    def test_multiple_arguments_are_supported(
        self,
    ):
        result = self.parser.parse(
            "/TEST one two three"
        )

        self.assertEqual(
            result.arguments,
            (
                "one",
                "two",
                "three",
            ),
        )

    def test_quoted_arguments_are_preserved(
        self,
    ):
        result = self.parser.parse(
            '/REMEMBER "local AI is preferred"'
        )

        self.assertEqual(
            result.arguments,
            ("local AI is preferred",),
        )

    def test_raw_text_is_preserved(
        self,
    ):
        text = (
            "/DELETE pcvue_skill"
        )

        result = self.parser.parse(
            text
        )

        self.assertEqual(
            result.raw_text,
            text,
        )

    def test_whitespace_is_ignored_around_command(
        self,
    ):
        result = self.parser.parse(
            "   /HELP   "
        )

        self.assertEqual(
            result.name,
            "HELP",
        )

    def test_bare_slash_is_rejected(
        self,
    ):
        with self.assertRaises(
            ValueError
        ):
            self.parser.parse(
                "/"
            )

    def test_non_string_input_is_rejected(
        self,
    ):
        with self.assertRaises(
            TypeError
        ):
            self.parser.parse(
                123
            )

    def test_invalid_quotes_are_rejected(
        self,
    ):
        with self.assertRaises(
            ValueError
        ):
            self.parser.parse(
                '/REMEMBER "unfinished'
            )


if __name__ == "__main__":
    unittest.main(
        verbosity=2
    )