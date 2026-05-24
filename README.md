# smolagents-ejentum

[smolagents](https://github.com/huggingface/smolagents) integration for the [Ejentum](https://ejentum.com) Reasoning Harness. Four `Tool` subclasses an agent calls before generating, plus an `ejentum_tools()` factory that returns all four with shared config.

Each operation in the Ejentum library (679 of them, organized across four harnesses) is engineered in **two layers**:

- a **natural-language procedure** the model can read, naming the steps to take and the failure pattern to refuse, and
- an **executable reasoning topology**: a graph-shaped plan over those steps. The plan names explicit decision points where the model branches, parallel branches that run and rejoin, bounded loops that run until convergence, named meta-cognitive moments where the model is asked to stop, look at its own working, and re-enter at a specific step, plus escape paths for when the prescribed plan stops fitting the task at hand.

The natural-language layer tells the model *what* to do. The topology layer pins down *how* those steps connect: where to decide, where to loop, where to stop and look at itself. Together they act as a persistent attention anchor that survives long context windows and multi-turn execution chains, which is precisely where a model's own reasoning template typically decays.

## Installation

```bash
pip install smolagents-ejentum
```

## Configuration

Get an Ejentum API key at <https://ejentum.com/pricing> (free and paid tiers) and set it in your environment:

```bash
export EJENTUM_API_KEY="zpka_..."
```

## Usage

### Drop-in: all four tools

```python
from smolagents import CodeAgent, InferenceClientModel
from smolagents_ejentum import ejentum_tools

model = InferenceClientModel(model_id="meta-llama/Llama-3.3-70B-Instruct")
agent = CodeAgent(tools=ejentum_tools(), model=model)  # reads EJENTUM_API_KEY from env

agent.run(
    "We've spent three months on the GraphQL gateway. "
    "Should we keep going or pivot to REST?"
)
```

The agent reads each tool's `description` and picks `ejentum_harness_anti_deception` on the sunk-cost framing, `ejentum_harness_reasoning` on a clean analytical question, etc.

### Pick one tool

```python
from smolagents import CodeAgent, InferenceClientModel
from smolagents_ejentum import EjentumAntiDeceptionTool

tool = EjentumAntiDeceptionTool()  # reads EJENTUM_API_KEY from env

agent = CodeAgent(tools=[tool], model=InferenceClientModel("..."))
```

### Explicit API key

```python
from smolagents_ejentum import ejentum_tools

tools = ejentum_tools(api_key="zpka_...")
```

## The four tools

| Class | Tool name | Best for | Library size |
|---|---|---|---|
| `EjentumReasoningTool` | `ejentum_harness_reasoning` | Analytical, diagnostic, planning, multi-step tasks spanning abstraction, time, causality, simulation, spatial, and metacognition | 311 operations |
| `EjentumCodeTool` | `ejentum_harness_code` | Code generation, refactoring, review, and debugging across the software-engineering layer | 128 operations |
| `EjentumAntiDeceptionTool` | `ejentum_harness_anti_deception` | Prompts that pressure the agent to validate, certify, or soften an honest assessment | 139 operations |
| `EjentumMemoryTool` | `ejentum_harness_memory` | Sharpening an observation already formed about cross-turn drift. Filter-oriented, not write-oriented. Format query as `"I noticed X. This might mean Y. Sharpen: Z."` | 101 operations |

## What an injection looks like

A real `reasoning` mode response on the query `investigate why our nightly ETL job has started failing intermittently over the past two weeks; nothing in the code or schema has changed`:

```
[NEGATIVE GATE]
The server's response time was accepted as average, despite a suspicious
rhythm break in its timing pattern.

[PROCEDURE]
Step 1: Establish baseline timing profiles by extracting historical
durations and intervals for each event type. Step 2: Compare each observed
timing against its baseline and compute deviation magnitude. Step 3:
Classify anomalies as too fast, too slow, too early, or too late, and rank
by severity. ... Step 5: If deviation exceeds two standard deviations,
probe root cause by tracing upstream dependencies. ...

[REASONING TOPOLOGY]
S1:durations -> FIXED_POINT[baselines] -> N{dismiss_timing_deviations_
without_investigation} -> for_each: S2:compare -> S3:deviation ->
G1{>2sigma?} --yes-> S4:classify -> S5:probe_cause -> FLAG -> continue --no->
S6:validate -> continue -> all_checked -> OUT:anomaly_report

[TARGET PATTERN]
Establish timing baselines by extracting historical response intervals.
Compare current server response time to this baseline. ...

[FALSIFICATION TEST]
If no event timing is flagged as suspiciously fast or slow relative to
baseline, temporal anomaly detection was not active.

Amplify: timing baseline comparison; anomaly classification; security
context elevation
Suppress: average timing acceptance; outlier normalization
```

The agent reads both the natural-language `[PROCEDURE]` and the graph-logic `[REASONING TOPOLOGY]` before generating its user-facing answer. The bracketed labels are instructions to the agent, not content to display.

## API reference

```python
# Per-tool
EjentumReasoningTool(
    api_key: str | None = None,
    api_url: str = "https://ejentum-main-ab125c3.zuplo.app/logicv1/",
    timeout_seconds: float = 10.0,
)
# (same constructor on EjentumCodeTool, EjentumAntiDeceptionTool, EjentumMemoryTool)

# Factory
ejentum_tools(
    api_key: str | None = None,
    api_url: str = "https://ejentum-main-ab125c3.zuplo.app/logicv1/",
    timeout_seconds: float = 10.0,
) -> list[Tool]
```

Every tool exposes `name`, `description`, `inputs={"query": {...}}`, `output_type="string"`. Errors are returned as human-readable strings from `forward` (no exceptions cross the tool boundary, so an agent step never crashes the run).

> **MCP alternative.** This package wraps the Logic API REST gateway. smolagents also has a first-class MCP client (`MCPClient`, `ToolCollection.from_mcp`) that can consume the hosted Ejentum MCP endpoint at `https://api.ejentum.com/mcp` with Bearer auth. The PyPI package skips MCP setup and keeps the import surface tiny.

> **Hub-shareable tools constraint.** smolagents' Hub-share convention requires `__init__` to take only `self`. These tools are distributed via PyPI, not the Hub, so they take constructor args freely. If you fork and `push_to_hub`, refactor to hard-code config as class attributes.

## Compatibility

- Python 3.10+
- `smolagents>=1.0.0`
- `requests>=2.31.0`

## Resources

- Ejentum homepage: <https://ejentum.com>
- Pricing: <https://ejentum.com/pricing>
- API reference: <https://ejentum.com/docs/api_reference>
- "Why LLM Agents Fail" essay: <https://ejentum.com/blog/why-llm-agents-fail>
- "Under Pressure" research paper: <https://doi.org/10.5281/zenodo.19392715>
- smolagents documentation: <https://huggingface.co/docs/smolagents>

## License

[MIT](./LICENSE)


## Measured effects

The Ejentum harness is benchmarked publicly under CC BY 4.0 at [github.com/ejentum/benchmarks](https://github.com/ejentum/benchmarks):

- **ELEPHANT** sycophancy: 5.8% composite on GPT-4o (40 real Reddit scenarios)
- **LiveCodeBench Hard**: 85.7% to 100% on Claude Opus (28 competitive programming tasks)
- **Memory retention**: 50% fewer stale facts served (20-turn implicit state changes)
- Plus per-harness numbers across BBH/CausalBench/MuSR, ARC-AGI-3, SciCode, and perception tasks

Methodology, scenarios, run scripts, and raw outputs are all in-repo.
