from fastmcp import FastMCP

mcp = FastMCP("BigQueryGeminiAssistant")

@mcp.tool()
def ping() -> str:
    """A simple tool to check if the server is responsive."""
    return "pong"