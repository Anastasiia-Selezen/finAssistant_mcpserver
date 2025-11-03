import logging

from config import settings
from fastmcp import FastMCP
from fastmcp.tools import Tool

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)



ALPHAVANTAGE_MCP_CONFIG = {
    "mcpServers": {
        "alphavantage_proxy": {
            "url": f"https://mcp.alphavantage.co/mcp?apikey={settings.ALPHA_VANTAGE_API_KEY}",
            "transport": "streamable-http",
            "headers": {"Accept-Encoding": "gzip, deflate, br, zstd"},
        }
    }
}

alphavantage_proxy = FastMCP.as_proxy(
    ALPHAVANTAGE_MCP_CONFIG,
    name="alphavantage_proxy",
)

alphavantage_mcp = FastMCP("alphavantage_tools")

_SELECTED_TOOLS = {
    "TIME_SERIES_INTRADAY": "get_intraday",
    "NEWS_SENTIMENT": "get_news_sentiment",
    "SYMBOL_SEARCH": "search_symbol",
}

_tools_loaded = False


async def load_alpha_vantage_tools() -> None:
    """Populate alphavantage_mcp with the three mirrored tools (idempotent)."""
    global _tools_loaded
    if _tools_loaded:
        return

    log.info("Loading Alpha Vantage tools via FastMCP proxy...")
    mirrored = await alphavantage_proxy.get_tools()

    for remote_name, local_name in _SELECTED_TOOLS.items():
        try:
            proxy_tool = mirrored[remote_name]
        except KeyError as exc:
            raise RuntimeError(
                f"Alpha Vantage tool {remote_name} not found in proxy inventory"
            ) from exc

        # Use a transformed copy so the local alias preserves the remote call target.
        local_tool = Tool.from_tool(proxy_tool, name=local_name)
        alphavantage_mcp.add_tool(local_tool)

    _tools_loaded = True
    log.info("Alpha Vantage tools ready.")


__all__ = ("alphavantage_mcp", "load_alpha_vantage_tools")
