"""MCP server for akshare-one.

This package provides MCP (Model Context Protocol) tools for accessing
Chinese stock market data through the akshare-one library.

Usage:
    akshare-one-mcp

Or programmatically:
    from akshare_one_mcp import run_server
    run_server()
"""

from .server import mcp, run_server

__all__ = ["mcp", "run_server"]
