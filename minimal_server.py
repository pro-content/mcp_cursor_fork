"""
Minimal MCP server for testing
"""

import logging
import sys
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

# Create the MCP server
mcp = FastMCP("Minimal Test Server")

@mcp.tool()
def hello(name: str = "World") -> str:
    """Say hello to someone.
    
    Args:
        name: The name to greet (defaults to "World")
        
    Returns:
        A greeting message
    """
    logger.info(f"Greeting {name}")
    return f"Hello, {name}!"

if __name__ == "__main__":
    logger.info("Starting Minimal MCP Server")
    
    try:
        # Run the MCP server
        mcp.run()
    except Exception as e:
        logger.error(f"Error running MCP server: {e}", exc_info=True)
        sys.exit(1) 