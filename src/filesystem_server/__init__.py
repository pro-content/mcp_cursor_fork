"""
Filesystem MCP Server Package

This package provides a Model Context Protocol (MCP) server for interacting with the local filesystem.
"""

from . import server

def main():
    """Main entry point for the package."""
    server.main()

# Expose important items at package level
__all__ = ['main', 'server']
