import asyncio
from fastmcp import Client

ws_url = "http://localhost:8003/mcp"
client = Client(ws_url)

async def main():

    client = Client(ws_url)

    async with client:
        print("Successfully connected to the fastMCP server.")
        
        # List available tools (optional, for verification)
        try:
            tools = await client.list_tools()
            print(f"Available tools: {[tool.name for tool in tools]}")
        except Exception as e:
            print(f"Could not list tools: {e}")
            return

        user_question = "What is the cheapest item available?"#"What can you tell me about the items in the knowledge base?"

        print(f"\nAsking question: '{user_question}'")
        
        try:
            response = await client.call_tool(tools[0].name, arguments={"user_question": user_question})
            
            print("\n--- Gemini's Answer ---")
            print(response[0].text)
            print("----------------------")

        except AttributeError:
            print("Error: Tool 'answer_question_with_bigquery_context' not found or client structure incorrect.")
            print("Ensure the tool name matches the method name in client.tools.TOOL_NAME(...)")
        except Exception as e:
            print(f"An error occurred while calling the tool: {e}")

if __name__ == "__main__":
    asyncio.run(main())