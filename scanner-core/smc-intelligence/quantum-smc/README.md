# Quantum Algo — Smart Money Concepts module

This directory contains the original Pine Script v6 indicator imported as a separate, standalone TradingView module.

## Included features
- Swing and internal market structure: BOS and CHoCH
- Order Blocks and zone lifecycle
- Fair Value Gaps and inversions
- Equal highs/lows and liquidity sweeps
- Premium/Discount mapping
- Confluence score, dashboard and alert conditions

## Source and attribution
- Original repository: https://github.com/quantumalgo-official/smart-money-concepts-indicator
- Original file: https://github.com/quantumalgo-official/smart-money-concepts-indicator/blob/main/smart-money-concepts.pine
- Original author/copyright: Quantum Algo, 2026
- License: MIT (see `LICENSE` in this directory)

The Pine file is kept separate from Scanner 5.0's Python/NSE-BSE scanner engines. It is a TradingView Pine Script indicator and is not yet wired into the Python scanner or the SMC Intelligence Elite web app. Integration into those systems requires a separate port/adaptor and validation.

No profitability or execution behavior is implied. Verify signals and test on historical data before use.
