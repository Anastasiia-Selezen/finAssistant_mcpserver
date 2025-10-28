import anyio
import utils.opik_utils as opik_utils
from servers.tool_registry import McpServersRegistry


def main():
    mcp_tool_manager = McpServersRegistry()
    anyio.run(mcp_tool_manager.initialize)

    mcp_tool_manager.get_registry().run(transport="streamable-http", host="localhost", port=5555)


if __name__ == "__main__":
    opik_utils.configure()
    main()
