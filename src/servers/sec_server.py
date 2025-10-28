import asyncio
import logging
from collections.abc import Iterable

import opik
import utils.opik_utils as opik_utils
from clients.sec_client import SECClient
from fastmcp import FastMCP

opik_utils.configure()
logger = logging.getLogger(__name__)

sec_mcp = FastMCP("sec_tools")
sec_client = SECClient()


@sec_mcp.tool(
    description="Map a stock ticker symbol to its Central Index Key (CIK).",
    tags={"sec", "mapping", "ticker", "cik"},
    annotations={"title": "Map Ticker to CIK", "readOnlyHint": True, "openWorldHint": True},
)
@opik.track(name="sec-map-ticker", type="tool")
async def map_ticker_to_cik(ticker: str):
    try:
        cik = await asyncio.to_thread(sec_client.map_ticker_to_cik, ticker)
        return {"ticker": ticker.strip().upper(), "cik": cik}
    except Exception as exc:
        logger.exception("Failed to map ticker %s", ticker)
        return {"error": str(exc)}


@sec_mcp.tool(
    description="Fetch metadata for the latest 10-K filing of a ticker symbol.",
    tags={"sec", "filing", "10-K", "metadata"},
    annotations={"title": "Get Latest 10-K Metadata", "readOnlyHint": True, "openWorldHint": True},
)
@opik.track(name="sec-latest-10k", type="tool")
async def get_latest_10k_metadata(ticker: str):
    try:
        cik = await asyncio.to_thread(sec_client.map_ticker_to_cik, ticker)
        filing = await asyncio.to_thread(sec_client.get_latest_10k_filing, cik)
        if not filing:
            return {"ticker": ticker.strip().upper(), "cik": cik, "filing": None}
        return {"ticker": ticker.strip().upper(), "cik": cik, "filing": filing}
    except Exception as exc:
        logger.exception("Failed to fetch 10-K metadata for %s", ticker)
        return {"error": str(exc)}


@sec_mcp.tool(
    description="Extract text from the latest 10-K filing of a ticker symbol. Optionally limit to specific sections.",
    tags={"sec", "filing", "10-K", "text"},
    annotations={"title": "Get Latest 10-K Text", "readOnlyHint": True, "openWorldHint": True},
)
@opik.track(name="sec-latest-10k-text", type="tool")
async def get_latest_10k_text(ticker: str, sections: str | None = None):
    try:
        section_list = _parse_sections(sections)
        cik = await asyncio.to_thread(sec_client.map_ticker_to_cik, ticker)
        filing = await asyncio.to_thread(sec_client.get_latest_10k_filing, cik)
        if not filing:
            return {"ticker": ticker.strip().upper(), "cik": cik, "text": None}
        text = await asyncio.to_thread(
            sec_client.extract_filing_text,
            filing,
            sections=section_list,
        )
        return {
            "ticker": ticker.strip().upper(),
            "cik": cik,
            "accessionNumber": filing.get("accessionNumber"),
            "text": text,
        }
    except Exception as exc:
        logger.exception("Failed to extract 10-K text for %s", ticker)
        return {"error": str(exc)}


def _parse_sections(sections: str | None) -> Iterable[str] | None:
    if sections is None:
        return None
    if isinstance(sections, str):
        parsed = [section.strip() for section in sections.split(",") if section.strip()]
        return parsed or None
    return sections
