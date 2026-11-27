# CSIF CRT-SMC-ICT Fusion Engine

An isolated strategy module for Scanner 5.0's NSE/BSE engine. The existing US
scanner is untouched. Initial execution mode is paper-only.

## Final configuration

- CRT reference windows: previous completed 15-minute and 1-hour candles.
- Intraday execution: completed 5-minute bars.
- Swing execution: completed 1-hour bars resampled from 5-minute source data.
- Directional filter: 1-hour 20/50 SMA alignment and fast-average slope.
- Sequence: CRT sweep and close back into range -> SMC MSS -> displacement ->
  three-candle FVG -> later FVG retest.
- Entry reference: FVG midpoint. Historical simulation attempts a next-bar
  open fill only if that open remains inside the FVG.
- Minimum score: 80/100. The sequence gates are mandatory; a score cannot
  override a missing CRT sweep, MSS, displacement, FVG or retest.
- Minimum reward/risk: 1:2.
- Conservative research defaults: 0.5% capital risk per trade, 20% maximum
  notional, 1% daily realized loss stop, maximum two trades per day.
- Universe: validated NSE/BSE cash-equity symbols. Exclude suspended,
  stale-feed, SME/illiquid and invalid symbols from production scans.

## Python interface

Run from the scanner-core directory with trader-india on PYTHONPATH:

- parse_bars(rows) validates and sorts OHLCV input.
- scan(bars, symbol, exchange, modes) returns signal dictionaries.
- run_backtest(...) returns trades, net P&L, win rate, profit factor and
  drawdown.
- open_paper_position(...), mark_paper_positions(...) and
  close_paper_position(...) manage a local JSON ledger.

Example:

    import csv
    from csif.engine import parse_bars, scan

    with open("trader/RELIANCE-5m.csv", newline="", encoding="utf-8-sig") as f:
        bars = parse_bars(csv.DictReader(f))
    signals = scan(bars, "RELIANCE", "NSE", modes=("intraday", "swing"))
    print(signals)

## CLI examples

Run from the scanner-core/trader-india directory:

    python csif_cli.py --csv data/RELIANCE-5m.csv --symbol RELIANCE --exchange NSE --mode both --action scan --output output/reliance-signals.json

    python csif_cli.py --csv data/RELIANCE-5m.csv --symbol RELIANCE --exchange NSE --mode intraday --action backtest --capital 100000 --risk-pct 0.5 --fee-bps 5 --slippage-bps 5 --output output/reliance-backtest.json

To explicitly open the first qualified signal in the local paper ledger, add
--paper-open-first-signal to a scan command. This does not connect to Dhan or
send an order. CSV columns must include timestamp, open, high, low, close and
volume; timestamps must be timezone-consistent and bars must be 5-minute.

## Backtest protocol

1. Begin with the NIFTY 50 constituent universe and five years of 5-minute
   history where licensed and complete data is available.
2. Run intraday and swing modes separately, then combine only after each has
   independent results.
3. Test NSE and BSE separately with exchange-qualified instrument identifiers.
4. Use chronological train/validation/test periods. Freeze rules before the
   final out-of-sample test.
5. Model brokerage, STT, exchange charges, GST, stamp duty, slippage, gaps,
   corporate actions and delisted constituents. The fixed bps cost in this
   prototype is only a placeholder.
6. Report trade count, win rate, profit factor, expectancy, maximum drawdown,
   average holding time, exposure, symbol concentration, daily loss breaches
   and out-of-sample results.
7. Run parameter sensitivity and ablation tests. Do not optimize only for
   win rate.

## Limitations before production

- This is a deterministic research prototype, not a validated profitable
  strategy.
- Historical replay is computationally heavier than the existing daily
  breakout baseline; begin with a small symbol sample.
- The initial event model uses completed bars and next-bar FVG fills. It does
  not model queue priority, partial fills, market impact or intrabar ticks.
- If stop and target both touch in one OHLC bar, the backtest assumes the
  stop occurs first.
- Resampling assumes regular 5-minute bars anchored to the NSE/BSE 09:15
  session open. Missing bars can invalidate an aggregate candle.
- No WebSocket stream, automatic broker order or live execution is included.
