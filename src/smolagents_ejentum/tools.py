"""smolagents Tool subclasses for the Ejentum Reasoning Harness.

Each tool is a :class:`smolagents.Tool` subclass an agent calls before
generating. Pick the tool that matches what the agent is about to do
(or pass all four via :func:`ejentum_tools` and let the agent route).

The bracketed labels in the returned scaffold (``[NEGATIVE GATE]``,
``[PROCEDURE]``, ``[REASONING TOPOLOGY]``, ``[FALSIFICATION TEST]``, etc.)
are instructions to the agent, not content to display.
"""

from __future__ import annotations

from typing import ClassVar, List, Optional

from smolagents import Tool

from smolagents_ejentum._api import (
    DEFAULT_API_URL,
    DEFAULT_TIMEOUT_SECONDS,
    call_logic_api,
)


_QUERY_INPUT = {
    "type": "string",
    "description": (
        "A 1-2 sentence description of the task the agent is about to "
        "work on. Be specific about the failure mode to avoid. For the "
        "memory tool, format as: 'I noticed [X]. This might mean [Y]. "
        "Sharpen: [Z].'"
    ),
}


class _EjentumBaseTool(Tool):
    """Internal base. Concrete subclasses fix ``mode`` via a class attribute.

    Note: smolagents' Hub-shareable tool convention requires ``__init__``
    to take only ``self``. We don't share these tools to the HF Hub
    (they're distributed via PyPI), so we take constructor args freely
    for ergonomic config.
    """

    inputs: ClassVar[dict] = {"query": _QUERY_INPUT}
    output_type: ClassVar[str] = "string"

    # Subclasses set ``mode`` to one of the four valid modes.
    mode: ClassVar[str] = ""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: str = DEFAULT_API_URL,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        super().__init__()
        self.api_key = api_key
        self.api_url = api_url
        self.timeout_seconds = timeout_seconds

    def forward(self, query: str) -> str:
        return call_logic_api(
            mode=self.mode,
            query=query,
            api_key=self.api_key,
            api_url=self.api_url,
            timeout_seconds=self.timeout_seconds,
        )


class EjentumReasoningTool(_EjentumBaseTool):
    """Retrieve a reasoning-mode scaffold before an analytical or planning step.

    Call BEFORE the agent performs analysis, diagnosis, planning, or any
    multi-step task. The Ejentum reasoning harness contains 311 operations
    spanning abstraction, time, causality, simulation, spatial, and
    metacognition. The returned scaffold is engineered in two layers: a
    natural-language procedure (named failure pattern, executable steps,
    suppression vectors, falsification test) and an executable reasoning
    topology (graph DAG with decision gates, parallel branches, bounded
    loops, and meta-cognitive exit nodes). Read both before generating.
    """

    name: ClassVar[str] = "ejentum_harness_reasoning"
    description: ClassVar[str] = (
        "Retrieve a reasoning scaffold before any analytical, diagnostic, "
        "planning, or multi-step task. Returns a structured scaffold with "
        "a named failure pattern, an executable procedure, a reasoning "
        "topology (graph DAG), and a falsification test from a library of "
        "311 reasoning operations. Use 'query' to describe what the agent "
        "is about to work on in 1-2 sentences."
    )
    mode: ClassVar[str] = "reasoning"


class EjentumCodeTool(_EjentumBaseTool):
    """Retrieve a code-mode scaffold before generating, refactoring, or reviewing code.

    Call BEFORE the agent produces or reviews code. The Ejentum code
    harness contains 128 operations in the software-engineering layer
    (correctness, refactor safety, contract preservation, edge case
    coverage, error path discipline).
    """

    name: ClassVar[str] = "ejentum_harness_code"
    description: ClassVar[str] = (
        "Retrieve a code scaffold before any code generation, refactoring, "
        "review, or debugging task. Returns a structured scaffold with a "
        "named code-failure pattern, an engineering procedure, a reasoning "
        "topology (graph DAG), and a verification step from a library of "
        "128 code operations. Use 'query' to describe what the agent is "
        "coding or reviewing in 1-2 sentences; include the failure risk "
        "to avoid where possible."
    )
    mode: ClassVar[str] = "code"


class EjentumAntiDeceptionTool(_EjentumBaseTool):
    """Retrieve an anti-deception scaffold when the prompt pressures the agent to soften an honest assessment.

    Call BEFORE the agent responds to prompts that pressure validation,
    manufactured agreement, authority appeals, fabricated commitments,
    or any setup where the obvious helpful answer would compromise
    honesty. The Ejentum anti-deception harness contains 139 operations
    spanning sycophancy, hallucination, deception, adversarial framing,
    judgment, and executive control.
    """

    name: ClassVar[str] = "ejentum_harness_anti_deception"
    description: ClassVar[str] = (
        "Retrieve an anti-deception scaffold before responding to any "
        "prompt that pressures the agent to validate, certify, or soften "
        "an honest assessment. Returns a structured scaffold with a named "
        "deception pattern, an integrity procedure, a detection topology "
        "(graph DAG with omission-bias gates), and an integrity check. "
        "Use 'query' to describe the integrity dynamic at play in 1-2 "
        "sentences."
    )
    mode: ClassVar[str] = "anti-deception"


class EjentumMemoryTool(_EjentumBaseTool):
    """Retrieve a memory-mode scaffold to sharpen a cross-turn observation already formed.

    Call ONLY when sharpening an observation the agent has already
    formed about conversation state, drift, or cross-turn pattern. The
    Ejentum memory harness is filter-oriented (101 perception
    operations), NOT write-oriented; do not call for fact extraction,
    summarization, or storing structured data, those produce scaffold
    paralysis.

    The query MUST be in the format: "I noticed [observation]. This
    might mean [tentative interpretation]. Sharpen: [what to see deeper
    into]." Calling with an empty mind defeats the harness.
    """

    name: ClassVar[str] = "ejentum_harness_memory"
    description: ClassVar[str] = (
        "Retrieve a memory-mode scaffold ONLY when sharpening an "
        "observation the agent has already formed about cross-turn drift "
        "or pattern. Filter-oriented, not write-oriented; do not call "
        "for fact extraction. Format 'query' as: 'I noticed [X]. This "
        "might mean [Y]. Sharpen: [Z].' Calling with an empty mind "
        "defeats the harness."
    )
    mode: ClassVar[str] = "memory"


def ejentum_tools(
    api_key: Optional[str] = None,
    api_url: str = DEFAULT_API_URL,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> List[Tool]:
    """Return all four Ejentum harness tools as a list with shared config.

    Convenience for the common case of passing every harness to a
    smolagents agent::

        from smolagents import CodeAgent
        from smolagents_ejentum import ejentum_tools

        agent = CodeAgent(tools=ejentum_tools(), model=model)
    """
    kwargs = dict(api_key=api_key, api_url=api_url, timeout_seconds=timeout_seconds)
    return [
        EjentumReasoningTool(**kwargs),
        EjentumCodeTool(**kwargs),
        EjentumAntiDeceptionTool(**kwargs),
        EjentumMemoryTool(**kwargs),
    ]
