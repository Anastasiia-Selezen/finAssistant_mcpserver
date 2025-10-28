import logging

import opik
from fastmcp import FastMCP
from servers.agent_scope_server import agent_scope_mcp
from servers.alphavantage_server import alphavantage_mcp
from servers.sec_server import sec_mcp

log = logging.getLogger(__name__)


class McpServersRegistry:
    def __init__(self):
        self.registry = FastMCP("tool_registry")
        self.all_tags: set[str] = set()
        self._is_initialized = False

    @opik.track(name="tool-registry-initialize", type="general")
    async def initialize(self):
        if self._is_initialized:
            return

        log.info("Initializing McpServersRegistry...")
        await self.registry.import_server(alphavantage_mcp, prefix="alphavantage")
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
