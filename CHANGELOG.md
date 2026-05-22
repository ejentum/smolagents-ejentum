# Changelog

All notable changes to `smolagents-ejentum` are documented here. This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-23

### Added

- Initial release.
- Four `smolagents.Tool` subclasses: `EjentumReasoningTool`, `EjentumCodeTool`, `EjentumAntiDeceptionTool`, `EjentumMemoryTool`. Each is a single-input tool (`query: string`, `output_type: string`) that calls the Ejentum Logic API and returns a structured scaffold.
- `ejentum_tools(api_key=...)` factory returning all four tools as a list, for the common case of passing every harness to a `CodeAgent` or `ToolCallingAgent` with shared configuration.
- Each tool reads from the `EJENTUM_API_KEY` environment variable at call time or accepts an explicit `api_key` constructor arg, plus `api_url` and `timeout_seconds` overrides.
- Construction-time and call-time validation: empty/whitespace query returns an actionable error without spending a paid API call. Missing `EJENTUM_API_KEY` returns an actionable error pointing to https://ejentum.com/pricing.
- Errors returned as human-readable strings from `forward` for every failure path (no exceptions cross the tool boundary so an agent step never crashes the run).
- Unit tests cover the failure surface (missing key, empty/whitespace/non-string query, invalid mode, 401, non-200, invalid JSON, unexpected shape, non-string scaffold, network error) plus per-class identity (each is a `Tool` subclass with the documented class attributes `name`, `description`, `inputs`, `output_type`), parametric per-class mode dispatch, and factory propagation of shared config.
- Published to PyPI with OIDC trusted-publisher provenance attestation via GitHub Actions.

### Background

This package is the standalone-PyPI companion to the open [huggingface/smolagents#2300](https://github.com/huggingface/smolagents/issues/2300) integration proposal. smolagents distributes third-party tools two ways: via `Tool.from_hub`/`load_tool` against Hugging Face Spaces, or via plain PyPI packages users import. PyPI is the lower-friction path for an API-key-protected tool.
