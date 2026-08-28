import re

from src.memory.memory_decision_models import (
    CREATE,
    CONFIRM,
    CONTRADICT,
    IGNORE,
    UPDATE,
    MemoryDecision,
    MemoryDecisionContext,
)

from src.memory.memory_decision_provider import (
    MemoryDecisionProvider,
)


class DeterministicMemoryDecisionProvider(
    MemoryDecisionProvider
):
    """
    Conservative deterministic memory decision provider.

    V1 deliberately prefers IGNORE over uncertain mutation.

    It uses:
        - candidate validity
        - exact/strong semantic overlap
        - explicit negation language
        - conservative token comparison

    It does not use AI or external services.
    """

    STOP_WORDS = {
        "a",
        "an",
        "and",
        "are",
        "be",
        "for",
        "i",
        "in",
        "is",
        "it",
        "my",
        "of",
        "on",
        "or",
        "still",
        "the",
        "to",
        "user",
        "with",
        "actively",
    }

    CONTRADICTION_PREFIXES = (
        "no longer ",
        "not anymore ",
        "don't ",
        "do not ",
        "isn't ",
        "is no longer ",
        "wasn't ",
        "never ",
    )

    def provider_name(
        self,
    ) -> str:

        return "deterministic"

    def decide(
        self,
        context: MemoryDecisionContext,
    ) -> MemoryDecision:

        candidate = context.candidate
        existing = context.existing_memory

        # ---------------------------------------------------------
        # Basic candidate safety checks
        # ---------------------------------------------------------

        if not candidate.content.strip():

            return self._decision(
                action=IGNORE,
                context=context,
                reason=(
                    "Candidate content is empty."
                ),
                confidence=1.0,
            )

        if (
            not candidate.memory_key
            or not candidate.subject.strip()
        ):

            return self._decision(
                action=IGNORE,
                context=context,
                reason=(
                    "Candidate does not have "
                    "a usable identity."
                ),
                confidence=0.98,
            )

        # ---------------------------------------------------------
        # No existing memory -> CREATE
        # ---------------------------------------------------------

        if existing is None:

            return self._decision(
                action=CREATE,
                context=context,
                reason=(
                    "No active memory matching "
                    "the candidate was supplied."
                ),
                confidence=0.90,
            )

        # ---------------------------------------------------------
        # Build meaningful token sets
        # ---------------------------------------------------------

        candidate_tokens = (
            self._meaningful_tokens(
                candidate.content
            )
        )

        existing_tokens = (
            self._meaningful_tokens(
                existing.content
            )
        )

        if not candidate_tokens:

            return self._decision(
                action=IGNORE,
                context=context,
                reason=(
                    "Candidate does not contain "
                    "enough meaningful information."
                ),
                confidence=0.95,
            )

        if not existing_tokens:

            return self._decision(
                action=IGNORE,
                context=context,
                reason=(
                    "Existing memory could not "
                    "be compared reliably."
                ),
                confidence=0.90,
            )

        # ---------------------------------------------------------
        # Explicit contradiction takes priority
        # ---------------------------------------------------------

        if self._explicitly_contradicts(
            candidate.content,
            existing.content,
        ):

            return self._decision(
                action=CONTRADICT,
                context=context,
                reason=(
                    "Candidate contains explicit "
                    "negation of the existing memory."
                ),
                confidence=0.93,
            )

        # ---------------------------------------------------------
        # Calculate both directions of coverage
        #
        # candidate_coverage:
        #   How much of the candidate is represented
        #   by the existing memory?
        #
        # existing_coverage:
        #   How much of the existing memory is represented
        #   by the candidate?
        #
        # This distinction is what lets us identify:
        #
        #   existing subset of candidate -> UPDATE
        #
        # ---------------------------------------------------------

        shared_tokens = (
            candidate_tokens
            & existing_tokens
        )

        candidate_coverage = (
            len(shared_tokens)
            / len(candidate_tokens)
        )

        existing_coverage = (
            len(shared_tokens)
            / len(existing_tokens)
        )

        # ---------------------------------------------------------
        # Exact semantic equivalence -> CONFIRM
        # ---------------------------------------------------------

        if (
            candidate_tokens
            == existing_tokens
        ):

            return self._decision(
                action=CONFIRM,
                context=context,
                reason=(
                    "Candidate and existing memory "
                    "represent the same claim."
                ),
                confidence=0.96,
            )

        # ---------------------------------------------------------
        # Existing memory fully contained in candidate
        # and candidate contains additional information -> UPDATE
        #
        # Example:
        #
        # Existing:
        #   User is learning PCVUE.
        #
        # Candidate:
        #   User is learning PCVUE v17.
        # ---------------------------------------------------------

        if (
            existing_coverage >= 0.90
            and len(candidate_tokens)
            > len(existing_tokens)
        ):

            return self._decision(
                action=UPDATE,
                context=context,
                reason=(
                    "Candidate contains the existing "
                    "claim plus additional information."
                ),
                confidence=0.88,
            )

        # ---------------------------------------------------------
        # Strong overall similarity -> CONFIRM
        # ---------------------------------------------------------

        if (
            candidate_coverage >= 0.80
            and existing_coverage >= 0.80
        ):

            return self._decision(
                action=CONFIRM,
                context=context,
                reason=(
                    "Candidate strongly overlaps "
                    "the existing memory."
                ),
                confidence=0.82,
            )

        # ---------------------------------------------------------
        # Anything uncertain -> IGNORE
        # ---------------------------------------------------------

        return self._decision(
            action=IGNORE,
            context=context,
            reason=(
                "Similarity is insufficient to "
                "safely modify the existing memory."
            ),
            confidence=0.80,
        )

    def _decision(
        self,
        action,
        context,
        reason,
        confidence,
    ):
        memory_id = None

        if context.existing_memory is not None:

            memory_id = (
                context
                .existing_memory
                .memory_id
            )

        return MemoryDecision(
            action=action,
            candidate=context.candidate,
            memory_id=memory_id,
            reason=reason,
            confidence=confidence,
            metadata={
                "provider": self.provider_name(),
            },
        )

    @classmethod
    def _meaningful_tokens(
        cls,
        text,
    ):

        tokens = re.findall(
            r"\b[a-zA-Z0-9][a-zA-Z0-9_-]*\b",
            text.casefold(),
        )

        return {
            token
            for token in tokens
            if token not in cls.STOP_WORDS
        }

    @classmethod
    def _explicitly_contradicts(
        cls,
        candidate_content,
        existing_content,
    ):
        candidate = (
            candidate_content
            .casefold()
            .strip()
        )

        existing = (
            existing_content
            .casefold()
            .strip()
        )

        candidate_tokens = (
            cls._meaningful_tokens(
                candidate
            )
        )

        existing_tokens = (
            cls._meaningful_tokens(
                existing
            )
        )

        shared_tokens = (
            candidate_tokens
            & existing_tokens
        )

        if not shared_tokens:
            return False

        for prefix in cls.CONTRADICTION_PREFIXES:

            if candidate.startswith(
                prefix
            ):

                return True

        patterns = (
            r"\bno longer\b",
            r"\bnot anymore\b",
            r"\bdoesn't\b",
            r"\bdo not\b",
            r"\bdon't\b",
            r"\bisn't\b",
            r"\bnever\b",
        )

        return any(
            re.search(
                pattern,
                candidate,
            )
            for pattern in patterns
        )