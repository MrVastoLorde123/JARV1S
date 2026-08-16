from pathlib import Path


VALID_CATEGORIES = {
    "PERSONAL",
    "SKILL",
    "PREFERENCE",
    "PROJECT",
    "GOAL",
    "FACT",
    "WORKFLOW",
    "RELATIONSHIP",
    "EXPERIENCE",
    "OTHER",
}

VALID_STATUSES = {
    "CANDIDATE",
    "ACTIVE",
    "SUPERSEDED",
    "ARCHIVED",
    "REJECTED",
}


def validate_memory(memory):
    errors = []

    # Check content
    content = memory.get("content")

    if not content:
        errors.append("Memory content is missing.")

    elif not isinstance(content, str):
        errors.append("Memory content must be a string.")

    elif len(content.strip()) < 5:
        errors.append("Memory content is too short.")

    # Check category
    category = memory.get("category")

    if not category:
        errors.append("Memory category is missing.")

    elif category.upper() not in VALID_CATEGORIES:
        errors.append(
            f"Invalid category: {category}"
        )

    # Check confidence
    confidence = memory.get("confidence")

    if confidence is None:
        errors.append("Memory confidence is missing.")

    elif not isinstance(confidence, (int, float)):
        errors.append(
            "Memory confidence must be a number."
        )

    elif not 0.0 <= confidence <= 1.0:
        errors.append(
            "Memory confidence must be between 0.0 and 1.0."
        )

    # Check importance
    importance = memory.get("importance")

    if importance is None:
        errors.append("Memory importance is missing.")

    elif not isinstance(importance, (int, float)):
        errors.append(
            "Memory importance must be a number."
        )

    elif not 0.0 <= importance <= 1.0:
        errors.append(
            "Memory importance must be between 0.0 and 1.0."
        )

    # Check status
    status = memory.get("status", "CANDIDATE")

    if status.upper() not in VALID_STATUSES:
        errors.append(
            f"Invalid status: {status}"
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


if __name__ == "__main__":

    print("=" * 60)
    print("JARVIS MEMORY VALIDATOR TEST")
    print("=" * 60)

    test_memories = [

        {
            "content": "User is learning PCVUE v17.",
            "category": "SKILL",
            "confidence": 0.95,
            "importance": 0.90,
            "status": "CANDIDATE",
        },

        {
            "content": "User likes pizza.",
            "category": "INVALID_CATEGORY",
            "confidence": 0.8,
            "importance": 0.5,
            "status": "CANDIDATE",
        },

        {
            "content": "",
            "category": "SKILL",
            "confidence": 1.5,
            "importance": -0.2,
            "status": "UNKNOWN",
        },

    ]

    for number, memory in enumerate(test_memories, start=1):

        print()
        print(f"Test Memory #{number}")
        print("-" * 60)

        result = validate_memory(memory)

        if result["valid"]:
            print("VALID")
        else:
            print("INVALID")

            for error in result["errors"]:
                print(f"  - {error}")