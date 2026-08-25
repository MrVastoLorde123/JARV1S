# ADR-002: Separate Memory from Evidence

## Status

Accepted

## Decision

Structured memories and their supporting evidence will be stored separately.

## Reason

A memory is a claim or structured representation.

Evidence is the information supporting that claim.

Separating them allows JARVIS to preserve provenance and eventually support verification, contradiction handling, and memory revision.