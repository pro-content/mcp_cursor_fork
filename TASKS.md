# Project Tasks

## 1. Environment Setup

- [x] Install Python 3.10 or higher.
- [x] Set up a virtual environment using `uv` or `venv`.
- [x] Install the MCP Python SDK:
  ```bash
  uv add "mcp[cli]"
  ```

## 2. Project Initialization

- [x] Create the project directory structure.
- [x] Initialize a Git repository.
- [x] Set up `.gitignore` to exclude unnecessary files.

## 3. Basic MCP Server Implementation

- [x] Create a Python script (e.g., `server.py`) and initialize the `FastMCP` server.
- [x] Define a simple tool (e.g., addition function) to test server functionality.
- [x] Run the server and verify it starts without errors.

## 4. Filesystem Tools Development

- [x] Implement a tool to read file contents given a relative path.
- [x] Implement a tool to list directory contents.
- [x] Implement a tool to search files using regex patterns.
- [x] Implement a resource to monitor file changes (optional).

## 5. Security Enhancements

- [x] Implement directory access restrictions to prevent traversal attacks.
- [x] Integrate `.gitignore` pattern recognition to exclude specific files.
- [ ] Set up API key authentication for accessing tools and resources.

## 6. Client Integration

- [ ] Configure Claude Desktop to connect with the MCP server.
- [ ] Test server functionalities through the client interface.
- [ ] Handle client requests and ensure appropriate responses.

## 7. Testing and Validation

- [x] Write unit tests for each tool and resource.
- [ ] Perform integration testing with clients.
- [ ] Validate security measures against potential threats.

## 8. Documentation

- [x] Document the setup process and usage instructions.
- [x] Provide examples for each tool and resource.
- [x] Include security guidelines and best practices.

## 9. Integrate MCP Server with Cascade

- [ ] Update Cascade MCP Configuration:

  - Edit `~/.codeium/windsurf/mcp_config.json` to include:

    ```json
    {
      "mcpServers": {
        "filesystem": {
          "command": "/usr/bin/python3",
          "args": [
            "/home/yourusername/path/to/server.py"
          ],
          "env": {
            "PYTHONUNBUFFERED": "1",
            "LOG_LEVEL": "DEBUG"
          }
        }
      }
    }
    ```

- [x] Implement extensive debug logging in `server.py`:

  ```python
  import logging
  import os

  log_level = os.getenv("LOG_LEVEL", "INFO").upper()
  logging.basicConfig(
      level=log_level,
      format='%(asctime)s [%(levelname)s] %(message)s',
      handlers=[logging.StreamHandler()]
  )

  logger = logging.getLogger(__name__)

  @mcp.tool()
  def read_file(path: str) -> str:
      logger.debug(f"Attempting to read file at path: {path}")
      try:
          with open(path, 'r') as file:
              content = file.read()
          logger.debug(f"Successfully read file at path: {path}")
          return content
      except Exception as e:
          logger.error(f"Error reading file at path: {path} - {e}")
          raise
  ```

- [ ] Restart Cascade and verify MCP connection and debug log output.

## 10. Integrate MCP Server with Cursor

- [x] Update Cursor MCP Configuration:

  - Created `.cursor/mcp.json` to include:

    ```json
    {
      "mcpServers": {
        "filesystem": {
          "command": "/usr/bin/python3",
          "args": [
            "/Users/niladribose/code/CONTENT/WINDSURF_VS_CURSOR/MCP_SERVER/mcp_cursor/mcp_cursor_fork/src/filesystem_server/server.py"
          ],
          "env": {
            "PYTHONUNBUFFERED": "1",
            "LOG_LEVEL": "DEBUG"
          }
        }
      }
    }
    ```

- [x] Fixed MCP server compatibility issues with latest MCP SDK.

- [x] Verified that the server starts and works correctly.

- [x] Fixed "Client closed" error by improving resource handler implementation.

- [ ] Restart Cursor to apply the new configuration.

- [ ] Check the logs to ensure that debug messages are being recorded as expected.

## Discovered During Work

- [x] Add proper error handling for binary files in file reading.
- [x] Fixed resource URI syntax to use the required format (resource://).
- [x] Updated server implementation to work with the latest MCP SDK.
- [x] Converted `monitor_file_changes` function into a proper resource streaming handler.
- [x] Fixed asyncio event loop handling to avoid conflicts.
- [ ] Consider adding a configuration file to make workspace root configurable.

