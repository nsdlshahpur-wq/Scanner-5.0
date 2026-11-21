# Scanner 5.0 — Market Analysis Toolkit

A collection of modular skills and Python utilities for stock-market research, technical scanning, news monitoring, trade planning, position sizing, risk checks, and historical scenario analysis.

The toolkit reads public market and regulatory data. It does not place orders automatically. Broker tickets require explicit confirmation, and paper mode is the default.

## Modules

| Module | Purpose |
| --- | --- |
| `trader-scanner` | Scans a stock universe for technical setups |
| `trader-news` | Monitors market headlines and company filings |
| `trader-entry` | Tracks setup conditions and entry timing |
| `trader-exit` | Prepares stop-loss and target plans |
| `trader-timemachine` | Simulates historical and potential scenarios |
| `trader-risk` | Checks orders against risk limits |
| `trader-budget` | Calculates position size from account limits |
| `trader-broker` | Prepares broker tickets; paper mode by default |
| `trader-alerts` | Monitors configured price and time alerts |
| `trader-analyst` | Summarizes earnings and company fundamentals |
| `trader-pelosi` | Reads publicly disclosed congressional trades |

## Requirements

- Python 3.8 or newer
- Standard library only; no additional package installation is required for the included tools
- SEC data access requires a valid identifying user-agent string in the relevant configuration or `SEC_USER_AGENT` environment variable

## Run the tests

From this directory:

```bash
python -m unittest discover -s tests -v
```

The test suite uses local fixtures and is designed to run offline. Three binary upstream fixtures were not available when this repository copy was assembled, so tests that depend on those specific files may not pass until the fixtures are restored.

## Safety and limitations

- This software is for research and decision support, not financial, legal, or tax advice.
- Market data providers may change endpoints, delay data, or impose rate limits.
- Simulations describe assumptions and historical observations; they do not predict future results.
- Stop prices are not guaranteed execution prices, especially during fast markets or price gaps.
- Keep broker credentials in environment variables or secure local configuration, never in chat or source control.
- Keep broker tools in approval-required mode. Review every order before confirming it.

## License and attribution

MIT License. Original copyright and attribution are preserved in `LICENSE`.
