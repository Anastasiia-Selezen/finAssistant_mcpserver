import logging
from contextlib import AsyncExitStack

import opik
import utils.opik_utils as opik_utils
from config import settings
from fastmcp import FastMCP
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

opik_utils.configure()
logger = logging.getLogger("alphavantage_server")
logging.basicConfig(level=logging.INFO)

ALPHAVANTAGE_MCP_URL = f"https://mcp.alphavantage.co/mcp?apikey={settings.ALPHA_VANTAGE_API_KEY}"
SERVER_CONFIG = {
    "type": "http",
    "url": ALPHAVANTAGE_MCP_URL,
}

alphavantage_mcp = FastMCP("alphavantage_proxy")


# TIME_SERIES_INTRADAY
@alphavantage_mcp.tool(
    description="Get intraday time series data",
    tags={"alphavantage", "time_series", "intraday"},
    annotations={"title": "Get Intraday Time Series", "readOnlyHint": True, "openWorldHint": True},
)
@opik.track(name="alphavantage-TIME_SERIES_INTRADAY", type="tool")
async def get_intraday(symbol: str, interval: str):
    context = streamablehttp_client(SERVER_CONFIG.get("url"))
    async with AsyncExitStack() as exit_stack:
        read_stream, write_stream, get_session_id = await exit_stack.enter_async_context(context)
        session = await exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        await session.initialize()
        logger.info(f"Fetching intraday time series data for {symbol} with interval {interval}")
        result = await session.call_tool("TIME_SERIES_INTRADAY", {"symbol": symbol, "interval": interval})
        return result


# NEWS_SENTIMENT
@alphavantage_mcp.tool(
    description="Get news sentiment data",
    tags={"alphavantage", "news", "sentiment"},
    annotations={"title": "Get News Sentiment", "readOnlyHint": True, "openWorldHint": True},
)
@opik.track(name="alphavantage-NEWS_SENTIMENT", type="tool")
async def get_news_sentiment(tickers: str, topics: str = None, time_from: str = None, time_to: str = None):
    context = streamablehttp_client(SERVER_CONFIG.get("url"))
    async with AsyncExitStack() as exit_stack:
        read_stream, write_stream, get_session_id = await exit_stack.enter_async_context(context)
        session = await exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        await session.initialize()
        if tickers:
            logger.info(f"Fetching news sentiment data for tickers: {tickers}")
        if topics:
            logger.info(f"Filtering news sentiment data for topics: {topics}")
        params = {"tickers": tickers, "topics": topics}
        if time_from:
            params["time_from"] = time_from
        if time_to:
            params["time_to"] = time_to
        result = await session.call_tool("NEWS_SENTIMENT", params)
        return result


# SYMBOL_SEARCH
@alphavantage_mcp.tool(
    description="Search for a stock symbol",
    tags={"alphavantage", "symbol", "search"},
    annotations={"title": "Search Stock Symbol", "readOnlyHint": True, "openWorldHint": True},
)
@opik.track(name="alphavantage-SYMBOL_SEARCH", type="tool")
async def search_symbol(keywords: str):
    context = streamablehttp_client(SERVER_CONFIG.get("url"))
    async with AsyncExitStack() as exit_stack:
        read_stream, write_stream, get_session_id = await exit_stack.enter_async_context(context)
        session = await exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        await session.initialize()
        logger.info(f"Searching for stock symbol with keywords: {keywords}")
        result = await session.call_tool("SYMBOL_SEARCH", {"keywords": keywords})
        return result
