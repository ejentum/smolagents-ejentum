"""smolagents-ejentum: smolagents Tool subclasses for the Ejentum Reasoning Harness.

Exposes four agent-callable :class:`smolagents.Tool` subclasses, one per
harness:

- :class:`EjentumReasoningTool` (311 operations: abstraction, time,
  causality, simulation, spatial, metacognition)
- :class:`EjentumCodeTool` (128 operations: software-engineering layer)
- :class:`EjentumAntiDeceptionTool` (139 operations: sycophancy,
  hallucination, deception, adversarial framing, judgment, executive
  control)
- :class:`EjentumMemoryTool` (101 operations: perception layer;
  filter-oriented)

Plus :func:`ejentum_tools`, a factory that returns all four with shared
config as a Python list.

Free and paid tiers at https://ejentum.com/pricing.
"""

from smolagents_ejentum.tools import (
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
    "ejentum_tools",
    "DEFAULT_API_URL",
    "DEFAULT_TIMEOUT_SECONDS",
    "VALID_MODES",
]
__version__ = "0.1.0"
