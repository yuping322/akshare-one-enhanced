"""MCP (Model Context Protocol) server for akshare-one.

This module provides MCP server functionality to expose akshare-one data
through the Model Context Protocol, enabling integration with AI assistants.
"""

from .server import mcp, run_server

__all__ = ["mcp", "run_server"]
