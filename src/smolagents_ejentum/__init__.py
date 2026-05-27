"""smolagents-ejentum: smolagents Tool subclasses for the Ejentum Reasoning Harness.

Eight agent-callable :class:`smolagents.Tool` subclasses.

Dynamic (single retrieval, all tiers including the 30-day free trial):

- :class:`EjentumReasoningTool` (311 operations: abstraction, time,
  causality, simulation, spatial, metacognition)
- :class:`EjentumCodeTool` (128 operations: software-engineering layer)
- :class:`EjentumAntiDeceptionTool` (139 operations: sycophancy,
  hallucination, deception, adversarial framing, judgment, executive
  control)
- :class:`EjentumMemoryTool` (101 operations: perception layer;
  filter-oriented)

Adaptive (top-k retrieval + adapter LLM rewrites the operation to fit
the specific task; requires Go or Super tier):

- :class:`EjentumAdaptiveReasoningTool`
- :class:`EjentumAdaptiveCodeTool`
- :class:`EjentumAdaptiveAntiDeceptionTool`
- :class:`EjentumAdaptiveMemoryTool`

Plus :func:`ejentum_tools`, a factory that returns all eight with shared
config as a Python list.

Pricing at https://ejentum.com/pricing.
"""

from smolagents_ejentum.tools import (
    EjentumAdaptiveAntiDeceptionTool,
    EjentumAdaptiveCodeTool,
    EjentumAdaptiveMemoryTool,
    EjentumAdaptiveReasoningTool,
    EjentumAntiDeceptionTool,
    EjentumCodeTool,
    EjentumMemoryTool,
    EjentumReasoningTool,
    ejentum_tools,
)
from smolagents_ejentum._api import (
    DEFAULT_API_URL,
    DEFAULT_TIMEOUT_SECONDS,
    VALID_MODES,
)

__all__ = [
    "EjentumReasoningTool",
    "EjentumCodeTool",
    "EjentumAntiDeceptionTool",
    "EjentumMemoryTool",
    "EjentumAdaptiveReasoningTool",
    "EjentumAdaptiveCodeTool",
    "EjentumAdaptiveAntiDeceptionTool",
    "EjentumAdaptiveMemoryTool",
    "ejentum_tools",
    "DEFAULT_API_URL",
    "DEFAULT_TIMEOUT_SECONDS",
    "VALID_MODES",
]
__version__ = "0.2.0"
