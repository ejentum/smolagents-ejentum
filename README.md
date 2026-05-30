# smolagents-ejentum

[smolagents](https://github.com/huggingface/smolagents) integration for the Ejentum Reasoning Harness. Exposes eight `Tool` subclasses (one per mode) plus an `ejentum_tools()` factory that returns all eight as a list.

Use the harness before the agent generates on complex, multi-step, or multi-constraint tasks where the model's default reasoning template would miss a constraint, take a shortcut, or drift across turns. Each call returns a *cognitive operation*: a structured procedure (numbered steps with a failure pattern to refuse and a falsification test) paired with an executable reasoning topology (a DAG of those steps with decision gates, parallel branches, bounded loops, and meta-cognitive exit nodes). The agent reads both layers before producing its response.

Four dynamic tools (`reasoning`, `code`, `anti_deception`, `memory`) are available on all tiers including the 30-day free trial. Four adaptive tools (`adaptive_reasoning`, `adaptive_code`, `adaptive_anti_deception`, `adaptive_memory`) additionally run an adapter LLM that rewrites the matched operation with task-specific identifiers; they require the Go or Super tier.

smolagents validates the `Tool.name` class attribute against a Python-identifier regex at `__init_subclass__`. Tool names here use underscores; the on-wire API mode strings (sent in the POST body) stay hyphenated. The split between LLM-facing name and on-wire mode lives in each tool's `name` vs `mode` class attributes.

## Install

```bash
pip install smolagents-ejentum
```

## Configuration

```bash
export EJENTUM_API_KEY="ej_..."
```

Or pass `api_key=` to any tool constructor. Get a key at [ejentum.com/pricing](https://ejentum.com/pricing).

## Usage

### All eight tools

```python
from smolagents import CodeAgent, InferenceClientModel
from smolagents_ejentum import ejentum_tools

model = InferenceClientModel(model_id="meta-llama/Llama-3.3-70B-Instruct")
agent = CodeAgent(tools=ejentum_tools(), model=model)

agent.run(
    "We have spent three months on the GraphQL gateway. "
    "Should we keep going or pivot to REST?"
)
```

### One tool

```python
from smolagents import CodeAgent, InferenceClientModel
from smolagents_ejentum import EjentumAntiDeceptionTool

tool = EjentumAntiDeceptionTool()
agent = CodeAgent(tools=[tool], model=InferenceClientModel("..."))
```

### Explicit API key

```python
tools = ejentum_tools(api_key="ej_...")
```

## Tool inventory

### Dynamic (all tiers)

| Class | Tool `name` (LLM-visible) | Mode string (on wire) | Library size |
|---|---|---|---:|
| `EjentumReasoningTool` | `reasoning` | `reasoning` | 311 |
| `EjentumCodeTool` | `code` | `code` | 128 |
| `EjentumAntiDeceptionTool` | `anti_deception` | `anti-deception` | 139 |
| `EjentumMemoryTool` | `memory` | `memory` | 101 |

### Adaptive (Go or Super tier)

| Class | Tool `name` | Mode string (on wire) |
|---|---|---|
| `EjentumAdaptiveReasoningTool` | `adaptive_reasoning` | `adaptive-reasoning` |
| `EjentumAdaptiveCodeTool` | `adaptive_code` | `adaptive-code` |
| `EjentumAdaptiveAntiDeceptionTool` | `adaptive_anti_deception` | `adaptive-anti-deception` |
| `EjentumAdaptiveMemoryTool` | `adaptive_memory` | `adaptive-memory` |

Every tool defines `name`, `description`, `inputs={"query": {...}}`, `output_type="string"`. Returns the injection from `forward(query)` as a string. Errors return as strings; `forward` does not raise.

## API reference

```python
# Per-tool (same constructor on every Ejentum*Tool class)
EjentumReasoningTool(
    api_key: str | None = None,
    api_url: str = "https://api.ejentum.com/harness/",
    timeout_seconds: float = 10.0,
)

# Factory
ejentum_tools(
    api_key: str | None = None,
    api_url: str = "https://api.ejentum.com/harness/",
    timeout_seconds: float = 10.0,
) -> list[Tool]
```

## Wire contract

```
POST https://api.ejentum.com/harness/
Headers: Authorization: Bearer <key>, Content-Type: application/json
Body:    { "query": <string>, "mode": <one of 8 mode strings> }
Response (200): [ { "<mode>": "<injection string>" } ]
Response (401|403|429): { "error": "..." }
```

Full wire contract, field structure of an injection, DAG syntax, and a canonical dynamic-vs-adaptive comparison on the same query are documented in the [ejentum-mcp README](https://github.com/ejentum/ejentum-mcp#wire-contract).

## ejentum-mcp alternative

The same eight tools are hosted as an MCP server at `https://api.ejentum.com/mcp`. smolagents has a first-class MCP client (`MCPClient`, `ToolCollection.from_mcp`) that consumes the endpoint with Bearer auth.

## Hub-shareable tools constraint

smolagents' Hub-share convention requires `__init__` to take only `self`. The tools here are distributed via PyPI, not the Hub, so they take constructor args (`api_key`, `api_url`, `timeout_seconds`). If you fork and `push_to_hub`, refactor to hard-code config as class attributes first.

## Compatibility

- Python 3.10+
- `smolagents>=1.0.0`
- `requests>=2.31.0`

## License

[MIT](./LICENSE)


## Measured effects

The Ejentum harness is benchmarked publicly under CC BY 4.0 at [github.com/ejentum/benchmarks](https://github.com/ejentum/benchmarks):

- **ELEPHANT** sycophancy: 5.8% composite on GPT-4o (40 real Reddit scenarios)
- **LiveCodeBench Hard**: 85.7% to 100% on Claude Opus (28 competitive programming tasks)
- **Memory retention**: 50% fewer stale facts served (20-turn implicit state changes)
- Plus per-harness numbers across BBH/CausalBench/MuSR, ARC-AGI-3, SciCode, and perception tasks

Methodology, scenarios, run scripts, and raw outputs are all in-repo.
