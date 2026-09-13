"""Structured communication contract between agents and JARVIS.

Agents are capable of reasoning, but they are not the authority. This module
provides the language an agent uses to communicate with JARVIS about state,
questions, blockers, capability needs, tool needs, escalation, and completion.

The protocol deliberately does not grant permission. An agent can describe
what it needs and why; JARVIS decides whether anything is granted.
"""
