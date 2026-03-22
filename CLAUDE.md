# TradingAgents

## Purpose
Multi-agent LLM financial trading framework that mirrors real-world trading firm dynamics — analysts, researchers, traders, and risk managers collaborate to evaluate markets and inform trading decisions.

## Stack
- Python 3.10+ (v0.2.0)
- LangGraph + LangChain (core orchestration)
- Multi-provider LLM support: OpenAI, Google (Gemini), Anthropic (Claude), xAI (Grok), OpenRouter, Ollama
- Data: yfinance, Alpha Vantage, stockstats, pandas
- CLI: Typer + Rich + Questionary
- UI: Chainlit
- Caching: Redis
- GitHub: git@github.com:cyberjessai-lab/TradingAgents.git (fork of TauricResearch/TradingAgents)

## Current State
- Phase: Forked and available for research use
- v0.2.0 with multi-provider LLM support
- CLI interface working (python -m cli.main)
- Python package usage working (TradingAgentsGraph.propagate())
- Original paper: arXiv:2412.20138

## Architecture
- **Analyst Team**: Fundamentals, Sentiment, News, Technical analysts
- **Researcher Team**: Bull and Bear researchers (structured debates)
- **Trader Agent**: Composes reports, makes trade decisions
- **Risk Management**: Aggressive, Conservative, Neutral debaters + Portfolio Manager (final approve/reject)
- **Data flows**: Alpha Vantage (stock/fundamentals/indicators/news), yfinance (backup)
- **Graph**: LangGraph-based with conditional logic, reflection, signal processing

## Key Data
- Not financial advice — research purposes only
- API keys needed: at least one LLM provider + Alpha Vantage for market data
- Config via tradingagents/default_config.py

## Rules
- Never treat output as financial advice — this is a research tool
- Never commit API keys — use .env file (see .env.example)
- Never modify the upstream TauricResearch code without understanding the LangGraph flow
- Keep default_config.py as the single source of config truth
- Redis must be running for caching features
- Test with known historical dates before trusting live analysis
