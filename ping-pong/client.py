import asyncio
from fastmcp import Client
from server import mcp 

async def main():
    # In-memory client for testing the 'mcp' object directly
    async with Client(mcp) as client:
        response = await client.call_tool("ping")
        print(f"Ping tool response: {response[0].text}")
        assert response[0].text == "pong"

if __name__ == "__main__":
    asyncio.run(main())