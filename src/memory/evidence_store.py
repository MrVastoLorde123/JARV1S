from src.database import get_connection
from datetime import datetime
import sqlite3


VALID_EVIDENCE_TYPES = {
    "DIRECT",
    "INFERRED",
    "REPEATED",
    "CORROBORATING",
    "CONTRADICTING",
}


def validate_evidence(
    memory_id,
    evidence_text,
    evidence_type,
    confidence
):
    errors = []

    if not memory_id:
        errors.append("Memory ID is required.")

    if not evidence_text or not evidence_text.strip():
        errors.append("Evidence text is missing.")

    if evidence_type.upper() not in VALID_EVIDENCE_TYPES:
        errors.append(
            f"Invalid evidence type: {evidence_type}"
        )

    if not 0.0 <= confidence <= 1.0:
        errors.append(
            "Evidence confidence must be between 0.0 and 1.0."
        )

    return errors


def add_evidence(
    memory_id,
    evidence_text,
    evidence_type,
    confidence,
    conversation_id=None,
    message_id=None,
    source_created_at=None
):
    """
    Add a piece of evidence to an existing memory.
    """

    errors = validate_evidence(
        memory_id=memory_id,
        evidence_text=evidence_text,
        evidence_type=evidence_type,
        confidence=confidence
    )

    if errors:
        print("Evidence rejected.")

        for error in errors:
            print(f"  - {error}")

        return None

    evidence_type = evidence_type.upper()

    connection = get_connection()

    connection.execute("PRAGMA foreign_keys = ON")

    cursor = connection.cursor()

    timestamp = datetime.now().isoformat()

    try:

        cursor.execute("""
            INSERT INTO memory_evidence (
                memory_id,
                conversation_id,
                message_id,
                evidence_text,
                evidence_type,
                confidence,
                source_created_at,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory_id,
            conversation_id,
            message_id,
            evidence_text.strip(),
            evidence_type,
            confidence,
            source_created_at,
            timestamp
        ))

        connection.commit()

        evidence_id = cursor.lastrowid

    except sqlite3.IntegrityError as error:

        connection.rollback()

        print("Evidence rejected.")
        print(f"  - Database integrity error: {error}")

        return None

    finally:

        connection.close()

    return evidence_id


def get_evidence_for_memory(memory_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            memory_id,
            conversation_id,
            message_id,
            evidence_text,
            evidence_type,
            confidence,
            source_created_at,
            created_at
        FROM memory_evidence
        WHERE memory_id = ?
        ORDER BY created_at
    """, (memory_id,))

    evidence = cursor.fetchall()

    connection.close()

    return evidence


def get_evidence_for_conversation(conversation_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            memory_id,
            conversation_id,
            message_id,
            evidence_text,
            evidence_type,
            confidence,
            source_created_at,
            created_at
        FROM memory_evidence
        WHERE conversation_id = ?
        ORDER BY created_at
    """, (conversation_id,))

    evidence = cursor.fetchall()

    connection.close()

    return evidence