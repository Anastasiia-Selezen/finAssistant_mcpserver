import logging

from fastmcp import FastMCP
from server.agent_scope import agent_scope_mcp
from server.alpha_vantage import alphavantage_mcp, load_alpha_vantage_tools
from server.sec import sec_mcp

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class McpServersRegistry:
    def __init__(self):
        self.registry = FastMCP("tool_registry")
        self.all_tags: set[str] = set()
        self._is_initialized = False

    async def initialize(self):
        if self._is_initialized:
            return

        log.info("Initializing McpServersRegistry...")

        await load_alpha_vantage_tools()
        self.registry.mount(alphavantage_mcp, prefix="alphavantage")
        await self.registry.import_server(agent_scope_mcp, prefix="scope")
        await self.registry.import_server(sec_mcp, prefix="sec")

        all_tools = await self.registry.get_tools()
        for tool in all_tools.values():
            if tool.tags:
                self.all_tags.update(tool.tags)

        log.info(f"Registry initialization complete. Found tags: {self.all_tags}")
        self._is_initialized = True

    def get_registry(self) -> FastMCP:
        """returns the initialized tool registry."""
        return self.registry

    def get_all_tags(self) -> set[str]:
        """returns the pre-calculated set of all tool tags."""
        return self.all_tags
