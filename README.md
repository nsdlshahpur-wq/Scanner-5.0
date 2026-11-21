# Scanner 5.0

A modular market-analysis toolkit for researching stocks, monitoring market news, identifying technical setups, planning entries and exits, sizing positions, applying risk controls, and reviewing historical scenarios.

## Project structure

- [scanner-core/](scanner-core/) — Python tools, skill instructions, plugin metadata, documentation, and offline tests.
- [.github/workflows/scanner-tests.yml](.github/workflows/scanner-tests.yml) — automated Python test workflow.

## Included capabilities

- Market scanning and technical setup detection
- News and company-filing monitoring
- Entry timing and exit planning
- Historical scenario simulation
- Position sizing and risk checks
- Broker ticket preparation with paper mode as the default
- Price alerts, earnings analysis, and public congressional-trade disclosures

## Important

The tools are research and decision-support software, not financial advice or a guarantee of results. Market data may be delayed or incomplete. Broker actions require explicit user approval; paper trading should be used while testing.

The imported source retains its MIT license and original attribution in `scanner-core/LICENSE`.

Three upstream binary test fixtures were unavailable through the connected repository interface and are not included: `2026FD.zip`, `wall5m-2026-10-19.json.gz`, and `TSLA-60d5m.json.gz`. The available source files and text-based fixtures are retained.

See [scanner-core/README.md](scanner-core/README.md) for setup and usage.
