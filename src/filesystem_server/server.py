"""
Filesystem MCP Server

This server provides tools for interacting with the local filesystem through the Model Context Protocol.
It exposes capabilities for reading files, listing directories, searching files, and monitoring file changes.
"""

import os
import re
import logging
import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Optional, Any
import json

from mcp.server.fastmcp import FastMCP
from mcp import McpError
from mcp.server.stdio import stdio_server

# Configure logging
logging.basicConfig(
    level=logging.getLevelName(os.getenv("LOG_LEVEL", "INFO").upper()),
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

# Create the MCP server
mcp = FastMCP("Filesystem Server")

# Set up security measures
WORKSPACE_ROOT = os.path.abspath(os.getcwd())
EXCLUDED_PATTERNS = ['.git', '__pycache__', '*.pyc', '*.pyo', '*.pyd', '.DS_Store', '.env']

def is_safe_path(path: str) -> bool:
    """Check if a path is safe to access.
    
    Args:
        path: The path to check
        
    Returns:
        bool: True if the path is safe to access, False otherwise
    """
    abs_path = os.path.abspath(path)
    logger.debug(f"Checking if path is safe: {abs_path}")
    
    # Check if the path is within the workspace
    if not abs_path.startswith(WORKSPACE_ROOT):
        logger.warning(f"Path {abs_path} is outside workspace root {WORKSPACE_ROOT}")
        return False
    
    # Check if the path matches any excluded patterns
    rel_path = os.path.relpath(abs_path, WORKSPACE_ROOT)
    for pattern in EXCLUDED_PATTERNS:
        if re.search(pattern, rel_path):
            logger.warning(f"Path {rel_path} matches excluded pattern {pattern}")
            return False
            
    return True

@mcp.tool()
def read_file(path: str) -> str:
    """Read the contents of a file and return it as a string.
    
    This tool allows reading the contents of text files located within the workspace.
    It's useful when you need to examine file contents, access configuration files,
    or process text data stored in files.
    
    Safety: Only files within the workspace directory can be accessed.
    Files matching certain patterns (like .git, __pycache__) are excluded.
    
    Args:
        path: Relative or absolute path to the file to read
        
    Returns:
        The contents of the file as a string
        
    Errors:
        - If the file does not exist
        - If the file cannot be read
        - If the path is outside the workspace
        - If the file matches an excluded pattern
    """
    logger.debug(f"Attempting to read file at path: {path}")
    
    if not is_safe_path(path):
        logger.error(f"Access denied to file: {path}")
        raise McpError(
            "INVALID_PARAMS",
            f"Access denied to file: {path}. Only files within the workspace can be accessed."
        )
    
    try:
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        logger.debug(f"Successfully read file: {path}")
        return content
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise McpError("NOT_FOUND", f"File not found: {path}")
    except UnicodeDecodeError:
        logger.error(f"Cannot read file as text: {path}")
        raise McpError("INTERNAL_ERROR", f"Cannot read file as text: {path}. The file might be binary.")
    except Exception as e:
        logger.error(f"Error reading file: {path} - {e}")
        raise McpError("INTERNAL_ERROR", f"Error reading file: {path} - {str(e)}")

@mcp.tool()
def list_directory(path: str = ".") -> List[Dict[str, Any]]:
    """List the contents of a directory.
    
    This tool provides information about files and directories within a specified path.
    It's useful for exploring the file structure, finding files to read, or understanding
    the organization of a project.
    
    Safety: Only directories within the workspace can be accessed.
    Directories matching certain patterns (like .git, __pycache__) are excluded.
    
    Args:
        path: Relative or absolute path to the directory to list (defaults to current directory)
        
    Returns:
        A list of dictionaries containing information about each item in the directory.
        Each dictionary contains:
        - name: The name of the file or directory
        - type: "file" or "directory"
        - size: Size in bytes (for files only)
        - is_hidden: Whether the file/directory is hidden
        
    Errors:
        - If the directory does not exist
        - If the path is outside the workspace
        - If the directory matches an excluded pattern
    """
    logger.debug(f"Attempting to list directory: {path}")
    
    if not is_safe_path(path):
        logger.error(f"Access denied to directory: {path}")
        raise McpError(
            "INVALID_PARAMS", 
            f"Access denied to directory: {path}. Only directories within the workspace can be accessed."
        )
    
    try:
        entries = []
        for entry in os.scandir(path):
            # Skip excluded patterns
            if any(re.search(pattern, entry.name) for pattern in EXCLUDED_PATTERNS):
                continue
                
            entry_info = {
                "name": entry.name,
                "type": "directory" if entry.is_dir() else "file",
                "is_hidden": entry.name.startswith('.')
            }
            
            if entry.is_file():
                entry_info["size"] = entry.stat().st_size
                
            entries.append(entry_info)
            
        logger.debug(f"Successfully listed directory: {path}")
        return entries
    except FileNotFoundError:
        logger.error(f"Directory not found: {path}")
        raise McpError("NOT_FOUND", f"Directory not found: {path}")
    except Exception as e:
        logger.error(f"Error listing directory: {path} - {e}")
        raise McpError("INTERNAL_ERROR", f"Error listing directory: {path} - {str(e)}")

@mcp.tool()
def search_files(
    pattern: str,
    path: str = ".",
    max_results: int = 100,
    include_content: bool = False
) -> List[Dict[str, Any]]:
    """Search for files matching a regex pattern.
    
    This tool allows searching for files whose content matches a specified regex pattern.
    It's useful for finding code, configuration entries, or text across multiple files.
    
    Safety: Only files within the workspace directory can be searched.
    Files matching certain patterns (like .git, __pycache__) are excluded.
    
    Args:
        pattern: Regular expression pattern to search for in files
        path: Directory to search in (defaults to current directory)
        max_results: Maximum number of results to return (defaults to 100)
        include_content: Whether to include the matching line content (defaults to False)
        
    Returns:
        A list of dictionaries containing search results. Each dictionary contains:
        - file: Path to the file containing the match
        - line: Line number where the match was found
        - content: The matching line (only if include_content is True)
        
    Errors:
        - If the directory does not exist
        - If the path is outside the workspace
        - If the regex pattern is invalid
    """
    logger.debug(f"Searching for pattern '{pattern}' in directory: {path}")
    
    if not is_safe_path(path):
        logger.error(f"Access denied to directory: {path}")
        raise McpError(
            "INVALID_PARAMS", 
            f"Access denied to directory: {path}. Only directories within the workspace can be accessed."
        )
    
    try:
        compiled_pattern = re.compile(pattern)
    except re.error:
        logger.error(f"Invalid regex pattern: {pattern}")
        raise McpError("INVALID_PARAMS", f"Invalid regex pattern: {pattern}")
    
    results = []
    count = 0
    
    try:
        for root, dirs, files in os.walk(path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(re.search(p, d) for p in EXCLUDED_PATTERNS)]
            
            for file in files:
                # Skip excluded files
                if any(re.search(p, file) for p in EXCLUDED_PATTERNS):
                    continue
                    
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f, 1):
                            if compiled_pattern.search(line):
                                result = {
                                    "file": file_path,
                                    "line": i
                                }
                                
                                if include_content:
                                    result["content"] = line.strip()
                                    
                                results.append(result)
                                count += 1
                                
                                if count >= max_results:
                                    logger.debug(f"Max results ({max_results}) reached")
                                    return results
                except (UnicodeDecodeError, IOError):
                    # Skip binary files or files that can't be read
                    pass
                    
        logger.debug(f"Found {len(results)} matches for pattern '{pattern}'")
        return results
    except Exception as e:
        logger.error(f"Error searching files: {e}")
        raise McpError("INTERNAL_ERROR", f"Error searching files: {str(e)}")

# Resource handler for file monitoring
@mcp.resource("resource://file-monitor/{path}")
async def file_monitor_handler(path: str):
    """Monitor a file for changes.
    
    This resource allows monitoring a file for changes and receiving updates
    when the file is modified. It's useful for tracking log files, configuration
    changes, or any file that's being actively edited.
    
    Safety: Only files within the workspace directory can be monitored.
    Files matching certain patterns (like .git, __pycache__) are excluded.
    
    Args:
        path: Path to the file to monitor
        
    Returns:
        A stream of updates containing the file path and content when changes occur
        
    Errors:
        - If the file does not exist
        - If the path is outside the workspace
        - If the file matches an excluded pattern
    """
    logger.debug(f"Resource handler for file monitoring called with path: {path}")
    
    if not is_safe_path(path):
        raise McpError("INVALID_PARAMS", f"Access denied to file: {path}")
        
    try:
        # First, check if the file exists
        if not os.path.exists(path):
            raise McpError("NOT_FOUND", f"File not found: {path}")
            
        # Read initial content
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Yield initial content
        yield {
            "path": path,
            "content": content,
            "event": "initial"
        }
        
        # Set up monitoring
        last_mtime = os.path.getmtime(path)
        
        while True:
            await asyncio.sleep(1)  # Check every second
            try:
                current_mtime = os.path.getmtime(path)
                if current_mtime > last_mtime:
                    logger.debug(f"File changed: {path}")
                    last_mtime = current_mtime
                    
                    # Read the file contents
                    with open(path, 'r', encoding='utf-8') as file:
                        content = file.read()
                    
                    # Yield the updated content
                    yield {
                        "path": path,
                        "content": content,
                        "event": "update"
                    }
            except FileNotFoundError:
                logger.warning(f"File no longer exists: {path}")
                yield {
                    "path": path,
                    "event": "deleted"
                }
                break
            except Exception as e:
                logger.error(f"Error monitoring file: {path} - {e}")
                yield {
                    "path": path,
                    "event": "error",
                    "error": str(e)
                }
                break
    except Exception as e:
        logger.error(f"Error setting up file monitor: {path} - {e}")
        raise McpError("INTERNAL_ERROR", f"Error setting up file monitor: {str(e)}")

def main():
    """Main entry point for the server."""
    logger.info("Starting Filesystem MCP Server")
    logger.info(f"Workspace root: {WORKSPACE_ROOT}")
    logger.info("Available tools:")
    logger.info("  - read_file: Read the contents of a file")
    logger.info("  - list_directory: List the contents of a directory")
    logger.info("  - search_files: Search for files matching a regex pattern")
    logger.info("  - file-monitor/{path}: Monitor a file for changes (resource)")
    
    try:
        # Run the server using FastMCP's run method
        # This automatically sets up the stdio server
        mcp.run()
    except Exception as e:
        logger.error(f"Error running MCP server: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    # Use sync version since FastMCP.run() handles asyncio internally
    main()
