import asyncio
from fastmcp import Client

ws_url = "http://localhost:9003/mcp"
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

        user_question = "What is the most expencive item available?"#"What can you tell me about the items in the knowledge base?"
        # For a more specific question, it would depend on the content of BIGQUERY_TABLE_ID
        # e.g., if it's Shakespeare data: "What are the themes in Hamlet's speeches?"

        print(f"\nAsking question: '{user_question}'")
        
        try:
            # Tool name is derived from the function name by default
            # e.g., answer_question_with_bigquery_context
            response = await client.call_tool(tools[0].name, arguments={"user_question": user_question})
            
            # The response from client.tools.tool_name(...) is directly the tool's return value
            # if it's a simple string. If it's a complex MCPMessage, you might need response.text
            print("\n--- Gemini's Answer ---")
            print(response[0].text) # Assuming the tool returns a string
            print("----------------------")

        except AttributeError:
            print("Error: Tool 'answer_question_with_bigquery_context' not found or client structure incorrect.")
            print("Ensure the tool name matches the method name in client.tools.TOOL_NAME(...)")
        except Exception as e:
            print(f"An error occurred while calling the tool: {e}")

if __name__ == "__main__":
    asyncio.run(main())