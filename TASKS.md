# Project Tasks

## 1. Environment Setup

- [ ] Install Python 3.10 or higher.
- [ ] Set up a virtual environment using `uv` or `venv`.
- [ ] Install the MCP Python SDK:
  ```bash
  uv add "mcp[cli]"
  ```

## 2. Project Initialization

- [ ] Create the project directory structure.
- [ ] Initialize a Git repository.
- [ ] Set up `.gitignore` to exclude unnecessary files.

## 3. Basic MCP Server Implementation

- [ ] Create a Python script (e.g., `server.py`) and initialize the `FastMCP` server.
- [ ] Define a simple tool (e.g., addition function) to test server functionality.
- [ ] Run the server and verify it starts without errors.

## 4. Filesystem Tools Development

- [ ] Implement a tool to read file contents given a relative path.
- [ ] Implement a tool to list directory contents.
- [ ] Implement a tool to search files using regex patterns.
- [ ] Implement a resource to monitor file changes (optional).

## 5. Security Enhancements

- [ ] Implement directory access restrictions to prevent traversal attacks.
- [ ] Integrate `.gitignore` pattern recognition to exclude specific files.
- [ ] Set up API key authentication for accessing tools and resources.

## 6. Client Integration

- [ ] Configure Claude Desktop to connect with the MCP server.
- [ ] Test server functionalities through the client interface.
- [ ] Handle client requests and ensure appropriate responses.

## 7. Testing and Validation

- [ ] Write unit tests for each tool and resource.
- [ ] Perform integration testing with clients.
- [ ] Validate security measures against potential threats.

## 8. Documentation

- [ ] Document the setup process and usage instructions.
- [ ] Provide examples for each tool and resource.
- [ ] Include security guidelines and best practices.

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

- [ ] Implement extensive debug logging in `server.py`:

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

- [ ] Update Cursor MCP Configuration:

  - Edit `~/.cursor/mcp.json` to include:

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

    **Notes:**
    - Replace `/usr/bin/python3` with the path to your Python interpreter.
    - Replace `/home/yourusername/path/to/server.py` with the absolute path to your MCP server script.
    - The `PYTHONUNBUFFERED` environment variable ensures that output is unbuffered, which is helpful for real-time logging.
    - The `LOG_LEVEL` environment variable sets the logging level to `DEBUG`.

    This configuration tells Cursor to launch your MCP server using the STDIO transport, which is suitable for local integrations and command-line tools.

- [ ] Restart Cursor to apply the new configuration.

- [ ] Verify that your MCP server starts correctly and that Cursor can communicate with it.

- [ ] Check the logs to ensure that debug messages are being recorded as expected.

**Note:** For project-specific configurations, you can create a `.cursor/mcp.json` file within your project directory. This allows you to define MCP servers that are only available within that specific project.

