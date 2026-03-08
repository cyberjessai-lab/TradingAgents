"""
Nemo Boost CFD Trading Configuration
Customized for: Gold, Silver, Oil, Natural Gas, Copper, BTC, ETH
Platform: Nemo Money app (nemo.money/boost)
"""

import os
from tradingagents.default_config import DEFAULT_CONFIG

# Nemo Boost asset mapping to yfinance tickers
NEMO_ASSETS = {
    "GOLD":   {"ticker": "GC=F",    "name": "Gold Futures",          "category": "commodity", "priority": 1},
    "SILVER": {"ticker": "SI=F",    "name": "Silver Futures",        "category": "commodity", "priority": 2},
    "OIL":    {"ticker": "CL=F",    "name": "Crude Oil WTI Futures", "category": "commodity", "priority": 3},
    "NATGAS": {"ticker": "NG=F",    "name": "Natural Gas Futures",   "category": "commodity", "priority": 4},
    "COPPER": {"ticker": "HG=F",    "name": "Copper Futures",        "category": "commodity", "priority": 5},
    "BTC":    {"ticker": "BTC-USD",  "name": "Bitcoin",              "category": "crypto",    "priority": 6},
    "ETH":    {"ticker": "ETH-USD",  "name": "Ethereum",             "category": "crypto",    "priority": 7},
}

# Build Nemo config on top of defaults
NEMO_CONFIG = DEFAULT_CONFIG.copy()
NEMO_CONFIG.update({
    # Use Google Gemini (free tier)
    "llm_provider": "google",
    "deep_think_llm": "gemini-2.5-flash",
    "quick_think_llm": "gemini-2.5-flash-lite",
    "backend_url": None,  # Not needed for Google

    # Enable thinking for deeper analysis
    "google_thinking_level": "high",

    # Debate settings — 1 round for fast commodity signals
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,

    # Data vendors — yfinance works for commodities and crypto
    "data_vendors": {
        "core_stock_apis": "yfinance",
        "technical_indicators": "yfinance",
        "fundamental_data": "yfinance",
        "news_data": "yfinance",
    },

    # Results go to our project
    "results_dir": "/home/cylon/TradingAgents/nemo_results",
})

# Analyst selection for commodities/crypto
# Skip fundamentals (no balance sheets for commodities)
# Use market (technicals) + news (macro events)
NEMO_ANALYSTS = ["market", "news"]

def get_ticker(asset_name: str) -> str:
    """Convert Nemo asset name to yfinance ticker."""
    asset = NEMO_ASSETS.get(asset_name.upper())
    if not asset:
        raise ValueError(f"Unknown asset: {asset_name}. Valid: {list(NEMO_ASSETS.keys())}")
    return asset["ticker"]

def get_all_tickers() -> dict:
    """Return all Nemo assets with their tickers."""
    return {name: info["ticker"] for name, info in NEMO_ASSETS.items()}
