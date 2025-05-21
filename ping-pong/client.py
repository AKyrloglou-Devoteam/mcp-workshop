import asyncio
from fastmcp import Client
from server import mcp 

async def main():
    # In-memory client for testing the 'mcp' object directly
    while True:
        async with Client(mcp) as client:
            print("ping")
            response = await client.call_tool("ping")
            print(f"{response[0].text}")
            assert response[0].text == "pong"

if __name__ == "__main__":
    asyncio.run(main())