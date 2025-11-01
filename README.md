# Financial AI Assistant MCP Server

Financial AI Assistant MCP Server combines several financial data sources behind a single [FastMCP](https://github.com/modelcontextprotocol/fastmcp) registry so agents can fetch market data, SEC filings, and reusable prompts through the Model Context Protocol (MCP).

## Features

- Unified MCP registry that exposes Alpha Vantage market data, SEC filings, and a reusable financial-analysis prompt.
- Streamable HTTP transport on `localhost:5555` for integration with MCP-compatible clients.


## Requirements

- Python 3.12+
- API keys for:
  - Alpha Vantage – <https://www.alphavantage.co/support/#api-key>
  - SEC API (sec-api.io) – <https://sec-api.io/>


## Installation

1. Clone the repository and switch into the project directory.
2. Install dependencies: `uv sync`


## Configuration

The server loads settings from environment variables (optionally via a `.env` file). These keys are mandatory and validated on startup:

| Variable | Description |
| --- | --- |
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage REST API key. |
| `SEC_API_KEY` | sec-api.io key used by `SECClient`. |


Rename `.env.example` file to `.env` file in the project root and add your API keys or export them in your shell before running the server.

## Running the MCP Server

Start the registry locally:

```bash
uv run src/main.py
```

By default the FastMCP registry listens on `streamable-http://localhost:5555`.

## Available MCP Tools

### Alpha Vantage (`alphavantage_*`)

- `alphavantage.get_intraday(symbol, interval)` — OHLCV intraday data.
- `alphavantage.get_news_sentiment(tickers, topics?, time_from?, time_to?)` — Headline sentiment feed.
- `alphavantage.search_symbol(keywords)` — Resolve tickers from company names.

All Alpha Vantage calls are proxied to the hosted MCP endpoint with your API key.

### SEC (`sec_*`)

- `sec.map_ticker_to_cik(ticker)` — Convert ticker symbols to CIK identifiers.
- `sec.get_latest_10k_metadata(ticker)` — Metadata for the most recent 10-K filing.
- `sec.get_latest_10k_text(ticker, sections?)` — Extract 10-K text (optionally limited to sections such as `1`, `7`, etc.).

These tools rely on the `sec-api` SDK.

### Agent Scope Prompt (`scope_*`)

- `scope.financial_analysis_prompt(query)` — Formats a structured analysis prompt that nudges downstream agents to plan tool usage before answering.

