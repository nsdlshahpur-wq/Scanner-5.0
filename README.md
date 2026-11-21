# Scanner 5.0

A modular market-analysis toolkit for US and Indian stock research. Existing US Scanner modules are preserved; the NSE scanner is being added as an independent engine with separate data handling and conservative paper-trading controls.

## Project structure

- [scanner-core/](scanner-core/) — Python tools, modules, documentation and offline tests.
- [scanner-core/trader-india/](scanner-core/trader-india/) — NSE scanner and paper-only sizing.
- [.github/workflows/scanner-tests.yml](.github/workflows/scanner-tests.yml) — automated Python test workflow.

## Current capabilities

- Existing US market scanning, news, entry/exit, risk, budget, alerts and historical simulation.
- NSE daily technical scanner: 20-session closing breakout, bull flag, MA20 reclaim, RSI-14 oversold and oversold bounce.
- Conservative paper position sizing and local paper ledger.

The NSE universe supplied in the repository is a curated starter watchlist, not the complete NSE listing. Yahoo Finance data is unofficial and may be delayed or incomplete. NSE F&O and broader market modules are planned, not yet implemented.

## Important

Research and decision-support software only. No live broker orders are sent by the NSE module. Paper mode is the default development mode. Never treat a signal as a buy recommendation.
