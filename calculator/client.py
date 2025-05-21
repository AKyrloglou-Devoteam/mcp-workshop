import asyncio
from fastmcp import Client
from server import mcp 

# Configuration - should match where the server is running
ws_url = "http://localhost:8000/mcp"
client = Client(ws_url)

async def main():

    async with Client(ws_url) as client:
        
        # Test calculate tool - Addition
        print("\nTesting ADDITION:")
        try:
            calc_input_add = {"number1": 10, "number2": 5, "operation": "add"}
            response_add = await client.call_tool("calculate",arguments=calc_input_add)
            response_text = response_add[0].text
            print(f"Calculate(10 + 5): {response_text}")
        except Exception as e:
            print(f"Error during addition: {e}")

        # Test calculate tool - Subtraction
        print("\nTesting SUBTRACTION:")
        try:
            calc_input_subtract = {"number1": 10, "number2": 5, "operation": "subtract"}
            response_subtract = await client.call_tool("calculate",arguments=calc_input_subtract)
            response_text = response_subtract[0].text
            print(f"Calculate(10 - 5): {response_text}")
        except Exception as e:
            print(f"Error during subtraction: {e}")

        # Test calculate tool - Multiplication
        print("\nTesting MULTIPLICATION:")
        try:
            calc_input_multiply = {"number1": 10, "number2": 5, "operation": "multiply"}
            response_multiply = await client.call_tool("calculate",arguments=calc_input_multiply)
            response_text = response_multiply[0].text
            print(f"Calculate(10 * 5): {response_text}")
        except Exception as e:
            print(f"Error during multiplication: {e}")

        # Test calculate tool - Division
        print("\nTesting DIVISION:")
        try:
            calc_input_divide = {"number1": 10, "number2": 5, "operation": "divide"}
            response_divide = await client.call_tool("calculate",arguments=calc_input_divide)
            response_text = response_divide[0].text
            print(f"Calculate(10 / 5): {response_text}")
        except Exception as e:
            print(f"Error during division: {e}")

        # Test calculate tool - Division by zero
        print("\nTesting DIVISION BY ZERO:")
        try:
            calc_input_div_zero = {"number1": 10, "number2": 0, "operation": "divide"}
            response_div_zero = await client.call_tool("calculate",arguments=calc_input_div_zero)
            response_text = response_div_zero[0].text
            print(f"Calculate(10 / 0): {response_text}")
        except Exception as e:
            print(f"Error during division by zero (expected): {e}")
            # If the server returns an error in the JSON, the client might raise an MCPError
            # or you might get the error dictionary back, depending on fastmcp client behavior.
            # The provided server code returns {"error": "message"}, so it should print that.


if __name__ == "__main__":
    asyncio.run(main())