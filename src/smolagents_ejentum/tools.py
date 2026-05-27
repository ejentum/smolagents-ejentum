"""smolagents Tool subclasses for the Ejentum Reasoning Harness.

Eight tools total: four dynamic (`reasoning`, `code`, `anti-deception`,
`memory`) and four adaptive (`adaptive-reasoning`, `adaptive-code`,
`adaptive-anti-deception`, `adaptive-memory`) that pre-fit the cognitive
operation to the caller's task via an adapter LLM. Adaptive tools require
the Go or Super tier.

Tool ``name`` (the LLM-facing string) equals the API mode string.

The bracketed labels in the returned injection (``[NEGATIVE GATE]``,
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
        "memory and adaptive-memory tools, format as: 'I noticed [X]. "
        "This might mean [Y]. Sharpen: [Z].'"
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

    # Subclasses set ``mode`` to one of the eight valid modes.
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


# ---------------------------------------------------------------------------
# Dynamic tools (single retrieval, all tiers including the 30-day free trial)
# ---------------------------------------------------------------------------


class EjentumReasoningTool(_EjentumBaseTool):
    """Retrieve a reasoning injection before an analytical or planning step.

    Call BEFORE the agent performs analysis, diagnosis, planning, or any
    multi-step task. 311 operations spanning abstraction, time, causality,
    simulation, spatial, and metacognition.
    """

    name: ClassVar[str] = "reasoning"
    description: ClassVar[str] = (
        "Retrieve a reasoning injection before any analytical, diagnostic, "
        "planning, or multi-step task. Returns a structured injection with "
        "a named failure pattern, an executable procedure, a reasoning "
        "topology (graph DAG), and a falsification test from a library of "
        "311 reasoning operations."
    )
    mode: ClassVar[str] = "reasoning"


class EjentumCodeTool(_EjentumBaseTool):
    """Retrieve a code injection before generating, refactoring, or reviewing code.

    Call BEFORE the agent produces or reviews code. 128 operations in the
    software-engineering layer.
    """

    name: ClassVar[str] = "code"
    description: ClassVar[str] = (
        "Retrieve a code injection before any code generation, refactoring, "
        "review, or debugging task. Returns a structured injection with a "
        "named code-failure pattern, an engineering procedure, a reasoning "
        "topology (graph DAG), and a verification step from a library of "
        "128 code operations."
    )
    mode: ClassVar[str] = "code"


class EjentumAntiDeceptionTool(_EjentumBaseTool):
    """Retrieve an anti-deception injection when the prompt pressures the agent.

    Call BEFORE responding to prompts that pressure validation, manufactured
    agreement, authority appeals, or any setup where the obvious helpful
    answer would compromise honesty. 139 operations spanning sycophancy,
    hallucination, deception, adversarial framing, judgment, executive control.
    """

    name: ClassVar[str] = "anti-deception"
    description: ClassVar[str] = (
        "Retrieve an anti-deception injection before responding to any "
        "prompt that pressures the agent to validate, certify, or soften "
        "an honest assessment. Returns a structured injection with a named "
        "deception pattern, an integrity procedure, a detection topology "
        "(graph DAG with omission-bias gates), and an integrity check from "
        "a library of 139 operations."
    )
    mode: ClassVar[str] = "anti-deception"


class EjentumMemoryTool(_EjentumBaseTool):
    """Retrieve a memory injection to sharpen a cross-turn observation already formed.

    Filter-oriented (101 perception operations), NOT write-oriented. The
    query MUST be in the format: "I noticed [observation]. This might mean
    [interpretation]. Sharpen: [what to see deeper into]."
    """

    name: ClassVar[str] = "memory"
    description: ClassVar[str] = (
        "Retrieve a memory injection ONLY when sharpening an observation "
        "the agent has already formed about cross-turn drift or pattern. "
        "Filter-oriented, not write-oriented. Format 'query' as: 'I "
        "noticed [X]. This might mean [Y]. Sharpen: [Z].' Library of 101 "
        "perception operations."
    )
    mode: ClassVar[str] = "memory"


# ---------------------------------------------------------------------------
# Adaptive tools (top-k retrieval + LLM adapter rewrites operation to fit
# the specific task; requires Go or Super tier)
# ---------------------------------------------------------------------------


class EjentumAdaptiveReasoningTool(_EjentumBaseTool):
    """Same triggers as :class:`EjentumReasoningTool`, but the operation is rewritten by an adapter LLM.

    Procedure steps and topology DAG nodes are concretized with task-specific
    language. Requires Go or Super tier. Cost ~2-3 seconds.
    """

    name: ClassVar[str] = "adaptive-reasoning"
    description: ClassVar[str] = (
        "Same triggers as `reasoning`, but the returned operation is "
        "REWRITTEN by an adapter LLM to fit the specific task. Procedure "
        "steps and topology DAG nodes are concretized with task-specific "
        "language. Use when the dynamic tool is too generic. Requires Go "
        "or Super tier."
    )
    mode: ClassVar[str] = "adaptive-reasoning"


class EjentumAdaptiveCodeTool(_EjentumBaseTool):
    """Same triggers as :class:`EjentumCodeTool`, but the operation is rewritten by an adapter LLM.

    Language, framework, and failure modes are concretized in every step.
    Requires Go or Super tier.
    """

    name: ClassVar[str] = "adaptive-code"
    description: ClassVar[str] = (
        "Same triggers as `code`, but the returned operation is REWRITTEN "
        "by an adapter LLM to fit the specific code task: language, "
        "framework, and failure modes are concretized in every step. "
        "Requires Go or Super tier."
    )
    mode: ClassVar[str] = "adaptive-code"


class EjentumAdaptiveAntiDeceptionTool(_EjentumBaseTool):
    """Same triggers as :class:`EjentumAntiDeceptionTool`, but the operation is rewritten by an adapter LLM.

    Detection topology gates are concretized to the exact pressure at play.
    Requires Go or Super tier.
    """

    name: ClassVar[str] = "adaptive-anti-deception"
    description: ClassVar[str] = (
        "Same triggers as `anti-deception`, but the returned operation is "
        "REWRITTEN by an adapter LLM to fit the specific integrity dynamic. "
        "Detection topology gates are concretized to the exact pressure at "
        "play. Requires Go or Super tier."
    )
    mode: ClassVar[str] = "adaptive-anti-deception"


class EjentumAdaptiveMemoryTool(_EjentumBaseTool):
    """Same triggers as :class:`EjentumMemoryTool`, but the operation is rewritten by an adapter LLM.

    Perception topology nodes are concretized to the specific signal.
    Observe FIRST, then call. Requires Go or Super tier.
    """

    name: ClassVar[str] = "adaptive-memory"
    description: ClassVar[str] = (
        "Same triggers as `memory`, but the returned operation is REWRITTEN "
        "by an adapter LLM to fit the specific observation. Perception "
        "topology nodes are concretized to the specific signal. Observe "
        "FIRST, then call. Requires Go or Super tier."
    )
    mode: ClassVar[str] = "adaptive-memory"


def ejentum_tools(
    api_key: Optional[str] = None,
    api_url: str = DEFAULT_API_URL,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> List[Tool]:
    """Return all eight Ejentum harness tools as a list with shared config.

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
        EjentumAdaptiveReasoningTool(**kwargs),
        EjentumAdaptiveCodeTool(**kwargs),
        EjentumAdaptiveAntiDeceptionTool(**kwargs),
        EjentumAdaptiveMemoryTool(**kwargs),
    ]
