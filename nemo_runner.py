#!/usr/bin/env python3
"""
Nemo Boost Trading Council Runner
Runs the multi-agent trading council for all Nemo Boost assets.
Outputs signals to CyberJessAI's trading-signals.json and sends via Telegram.

Usage:
    python nemo_runner.py                    # Scan all assets
    python nemo_runner.py GOLD               # Scan single asset
    python nemo_runner.py GOLD BTC SILVER    # Scan specific assets
"""

import sys
import os
import json
import time
from datetime import datetime, date
from pathlib import Path

# Load environment
from dotenv import load_dotenv
load_dotenv()

from nemo_config import NEMO_CONFIG, NEMO_ASSETS, NEMO_ANALYSTS, get_ticker
from tradingagents.graph.trading_graph import TradingAgentsGraph

# Paths
SIGNALS_FILE = "/home/cylon/CyberJessAI/trading-signals.json"
COUNCIL_FILE = "/home/cylon/CyberJessAI/council-reports.json"
LOG_FILE = "/home/cylon/TradingAgents/nemo_runner.log"
ACTIVE_TRADES_FILE = "/home/cylon/CyberJessAI/active-trades.json"

# Telegram
TG_BOT_TOKEN = "8558072460:AAGWwj-hLESoCaPq5Qgvd8-Qfc531yJxxl8"
TG_CHAT_ID = "1053322620"


def log(msg):
    line = f"[{datetime.now().isoformat()}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except:
        pass


def read_json(path, fallback=None):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return fallback if fallback is not None else {}


def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


async def send_telegram(text):
    import urllib.request
    try:
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        data = json.dumps({
            "chat_id": TG_CHAT_ID,
            "text": text[:4000],
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        log(f"Telegram error: {e}")


def send_telegram_sync(text):
    import urllib.request
    try:
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        data = json.dumps({
            "chat_id": TG_CHAT_ID,
            "text": text[:4000],
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        log(f"Telegram error: {e}")


def analyze_asset(asset_name: str) -> dict:
    """Run the full trading council analysis for a single asset."""
    ticker = get_ticker(asset_name)
    trade_date = date.today().isoformat()

    log(f"Council analyzing {asset_name} ({ticker})...")

    try:
        ta = TradingAgentsGraph(
            selected_analysts=NEMO_ANALYSTS,
            debug=False,
            config=NEMO_CONFIG,
        )

        start = time.time()
        final_state, decision = ta.propagate(ticker, trade_date)
        elapsed = round(time.time() - start, 1)

        log(f"{asset_name} decision: {decision} ({elapsed}s)")

        # Extract key reports
        result = {
            "asset": asset_name,
            "ticker": ticker,
            "decision": decision,
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": elapsed,
            "market_report": final_state.get("market_report", ""),
            "news_report": final_state.get("news_report", ""),
            "investment_plan": final_state.get("investment_plan", ""),
            "trader_plan": final_state.get("trader_investment_plan", ""),
            "final_decision": final_state.get("final_trade_decision", ""),
            "risk_debate": {
                "aggressive": final_state.get("risk_debate_state", {}).get("aggressive_history", ""),
                "conservative": final_state.get("risk_debate_state", {}).get("conservative_history", ""),
                "neutral": final_state.get("risk_debate_state", {}).get("neutral_history", ""),
                "judge": final_state.get("risk_debate_state", {}).get("judge_decision", ""),
            },
        }

        # Check for active trades to enable learning
        active_data = read_json(ACTIVE_TRADES_FILE, {})
        active_trades = active_data.get("active_trades", []) if isinstance(active_data, dict) else active_data
        for trade in active_trades:
            if isinstance(trade, dict) and trade.get("asset") == asset_name and trade.get("pnl") is not None:
                log(f"Reflecting on {asset_name} P&L: {trade['pnl']}")
                ta.reflect_and_remember(trade["pnl"])
                break

        return result

    except Exception as e:
        log(f"ERROR analyzing {asset_name}: {e}")
        import traceback
        traceback.print_exc()
        return {
            "asset": asset_name,
            "ticker": ticker,
            "decision": "ERROR",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }


def run_council(assets: list = None):
    """Run the trading council for specified assets (or all)."""
    if not assets:
        # Priority order: GOLD first (highest priority)
        assets = sorted(NEMO_ASSETS.keys(), key=lambda a: NEMO_ASSETS[a]["priority"])

    log(f"=== Nemo Boost Trading Council ===")
    log(f"Assets: {', '.join(assets)}")
    log(f"Analysts: {', '.join(NEMO_ANALYSTS)}")
    log(f"LLM: {NEMO_CONFIG['llm_provider']} ({NEMO_CONFIG['deep_think_llm']})")

    signals = read_json(SIGNALS_FILE, [])
    council_reports = read_json(COUNCIL_FILE, [])
    results = []

    for asset in assets:
        if asset.upper() not in NEMO_ASSETS:
            log(f"Skipping unknown asset: {asset}")
            continue

        result = analyze_asset(asset.upper())
        results.append(result)

        if result["decision"] != "ERROR":
            # Update signals file — add council signal to existing structure
            signal = {
                "asset": result["asset"],
                "ticker": result["ticker"],
                "signal": result["decision"],
                "timestamp": result["timestamp"],
                "source": "nemo-council",
                "elapsed": result.get("elapsed_seconds", 0),
            }

            # Handle both array and object formats
            if isinstance(signals, dict):
                council_signals = signals.get("council_signals", [])
                council_signals = [s for s in council_signals if s.get("asset") != result["asset"]]
                council_signals.append(signal)
                signals["council_signals"] = council_signals
            else:
                signals = [s for s in signals if s.get("asset") != result["asset"]]
                signals.append(signal)

            # Add to council reports (keep last 50)
            council_reports.append({
                "asset": result["asset"],
                "decision": result["decision"],
                "timestamp": result["timestamp"],
                "investment_plan": result.get("investment_plan", "")[:500],
                "risk_judge": result.get("risk_debate", {}).get("judge", "")[:500],
            })
            if len(council_reports) > 50:
                council_reports = council_reports[-50:]

    # Save updated signals and reports
    write_json(SIGNALS_FILE, signals)
    write_json(COUNCIL_FILE, council_reports)

    # Build summary for Telegram
    summary = "*NEMO TRADING COUNCIL*\n"
    summary += f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

    for r in results:
        icon = {"BUY": "+", "SELL": "-", "HOLD": "~", "ERROR": "!"}.get(r["decision"], "?")
        summary += f"`{icon} {r['asset']:7s} {r['decision']}`"
        if r.get("elapsed_seconds"):
            summary += f" ({r['elapsed_seconds']}s)"
        summary += "\n"

    summary += f"\nAnalysts: {', '.join(NEMO_ANALYSTS)}"
    summary += f"\nModel: {NEMO_CONFIG['deep_think_llm']}"

    send_telegram_sync(summary)
    log("Council complete. Signals saved.")

    return results


if __name__ == "__main__":
    assets = sys.argv[1:] if len(sys.argv) > 1 else None
    run_council(assets)
