
from mcp.server import MCPServer

# Initialize the MCP server.
# This gives our server a recognizable name.
mcp = MCPServer("Calculator Server")


@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """
    Add two integers and return their sum.

    The type hints describe the expected inputs and output.
    The SDK derives the tool's input schema from these hints.
    """
    print(f"Executing add_numbers: a={a}, b={b}")

    # Actual business logic executes in Python.
    result = a + b

    print(f"Tool result: {result}")
    return result
