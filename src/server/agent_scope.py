import logging

from fastmcp import FastMCP
from server.prompts import SYSTEM_PROMPT

agent_scope_mcp = FastMCP("agent_scope_prompts")

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@agent_scope_mcp.prompt(
    name="financial_analysis_prompt",
    description="Prompt for analyzing financial data, stocks and market trends.",
    tags={"financial", "analysis", "stocks"},
)
def financial_analysis_prompt(query: str):
    """
    Format the FINANCIAL_ANALYSIS_PROMPT using the provided arguments dict.
    All keys in arguments will be passed as keyword arguments to format().
    """
    log.info(f"Formatting financial analysis prompt with arguments: {query}")
    return SYSTEM_PROMPT.format(query)
