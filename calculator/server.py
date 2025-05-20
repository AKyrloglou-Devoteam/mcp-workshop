from fastmcp import FastMCP, Context
from typing import Union

# --- fastMCP Server Setup ---
mcp = FastMCP(name="CalculatorWorkshopAgent")

# --- fastMCP Tool Definitions ---
@mcp.tool()
def calculate(number1: float, number2: float, operation: str, ctx: Context) -> dict[str, Union[float, str]]:
    """
    Performs a calculation based on two numbers and an operation.
    Supported operations: 'add', 'subtract', 'multiply', 'divide'.
    Returns a dictionary with the result or an error message.
    """
    ctx.info(f"Tool 'calculate' received: num1={number1}, num2={number2}, op='{operation}'")
    
    result = None
    error_message = None

    if operation == 'add':
        result = number1 + number2
    elif operation == 'subtract':
        result = number1 - number2
    elif operation == 'multiply':
        result = number1 * number2
    elif operation == 'divide':
        if number2 == 0:
            error_message = "Error: Cannot divide by zero."
            ctx.error(error_message)
        else:
            result = number1 / number2
    else:
        error_message = "Error: Invalid operation specified. Choose 'add', 'subtract', 'multiply', or 'divide'."
        ctx.error(error_message)

    if error_message:
        return {"error": error_message}
    else:
        ctx.info(f"Calculation result: {result}")
        return {"result": result}


@mcp.tool()
def ping(ctx: Context) -> str:
    """A simple tool to check server responsiveness."""
    ctx.info("Ping tool called.")
    return "pong"

# # --- CORS Middleware and ASGI App Setup ---
# cors_middleware = Middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Restrict in production!
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# http_app = mcp.http_app(middleware=[cors_middleware])

# # --- Run with Uvicorn (for local development) ---
# if __name__ == "__main__":
#     import uvicorn
#     port = int(os.environ.get("PORT", 8000)) # Changed default to 8000 for clarity
#     print(f"Starting Calculator fastMCP server with Uvicorn on http://0.0.0.0:{port}")
#     uvicorn.run(http_app, host="0.0.0.0", port=port, log_level="info")