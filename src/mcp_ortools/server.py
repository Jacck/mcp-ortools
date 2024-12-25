import asyncio
import logging
from typing import List, Optional, Any
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from mcp.shared.exceptions import McpError

from .solver_manager import SolverManager, SolverError

logger = logging.getLogger(__name__)

async def serve() -> None:
    """Main server function that handles the MCP protocol"""
    logger.info("Starting OR-Tools MCP server")
    
    server = Server("ortools")
    solver_mgr = SolverManager()

    @server.list_tools()
    async def list_tools() -> List[types.Tool]:
        return [
            types.Tool(
                name="submit_model",
                description="Submit an optimization model in JSON format",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "model": {
                            "type": "string",
                            "description": "Model specification in JSON format"
                        }
                    },
                    "required": ["model"]
                }
            ),
            types.Tool(
                name="solve_model",
                description="Solve the current optimization model",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "timeout": {
                            "type": ["number", "null"],
                            "description": "Optional solve timeout in seconds"
                        }
                    }
                }
            ),
            types.Tool(
                name="get_solution",
                description="Get the current solution if available",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
        """Handle tool calls and map them to solver operations"""
        logger.debug(f"Tool call: {name} with arguments {arguments}")
        
        try:
            match name:
                case "submit_model":
                    model_str = arguments.get("model")
                    if not model_str:
                        raise McpError("Model required", "model parameter is required")
                        
                    valid, message = solver_mgr.parse_model(model_str)
                    if not valid:
                        raise McpError("Invalid model", message)
                    
                    logger.info("Model submitted successfully")
                    return [types.TextContent(type="text", text="Model submitted successfully")]

                case "solve_model":
                    try:
                        timeout = arguments.get("timeout")
                        result = solver_mgr.solve(timeout)
                        logger.info(f"Solve completed with status {result.get('status')}")
                        return [types.TextContent(type="text", text=str(result))]
                    except SolverError as e:
                        raise McpError("Solver error", str(e))

                case "get_solution":
                    solution = solver_mgr.get_current_solution()
                    if solution is None:
                        raise McpError("No solution", "No solution is available")
                    return [types.TextContent(type="text", text=str(solution))]

                case _:
                    raise McpError("Unknown tool", f"Tool {name} not found")

        except McpError:
            raise
        except Exception as e:
            logger.exception(f"Error in {name}")
            raise McpError("Tool execution failed", str(e))

    logger.info("Starting STDIO server")
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("STDIO server started")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ortools",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

def main() -> int:
    """Main entry point"""
    try:
        asyncio.run(serve())
        return 0
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.exception("Server error")
        return 1

if __name__ == "__main__":
    main()