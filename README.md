# Filesystem MCP Server

A Python implementation of a Model Context Protocol (MCP) server for interacting with the local filesystem. This server exposes tools for reading files, listing directories, searching files, and monitoring file changes.

## Features

- **File Reading**: Read file contents with path validation for security
- **Directory Listing**: List contents of directories with metadata
- **File Searching**: Search files using regex patterns
- **File Monitoring**: Monitor files for changes and get notified (resource)
- **Security**: Path validation to prevent directory traversal attacks
- **Logging**: Comprehensive logging with configurable log levels

## Installation

### Prerequisites

- Python 3.9 or higher
- `mcp` Python package

### Installation Steps

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd filesystem-mcp-server
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

## Usage

### Running the Server

You can run the server directly using:

```bash
python -m src.filesystem_server.server
```

Or, if you installed the package:

```bash
filesystem-mcp
```

### Connecting to Claude Desktop

1. Open Claude Desktop
2. From the settings menu, enable the MCP extension
3. Connect to the filesystem server by clicking "Add Server" and entering the path to the server script

### Connecting to Cursor

1. Edit `~/.cursor/mcp.json` to include:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "/path/to/python",
      "args": [
        "/absolute/path/to/src/filesystem_server/server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

2. Restart Cursor to apply the new configuration.

## Available Tools and Resources

### Tools

1. **read_file(path: str) -> str**
   - Read the contents of a file and return it as a string
   - Only files within the workspace directory can be accessed

2. **list_directory(path: str = ".") -> List[Dict[str, Any]]**
   - List the contents of a directory
   - Returns metadata including file type, size, and whether it's hidden
   
3. **search_files(pattern: str, path: str = ".", max_results: int = 100, include_content: bool = False) -> List[Dict[str, Any]]**
   - Search for files matching a regex pattern
   - Can include matching line content in results

### Resources

1. **file-monitor**
   - Monitor a file for changes and receive updates
   - Parameters: `path` - Path to the file to monitor

## Security Considerations

- The server implements path validation to ensure only files within the workspace directory can be accessed
- Excluded patterns prevent access to sensitive files (e.g., `.git`, `.env`)
- All file operations are logged for audit purposes

## Environment Variables

- `LOG_LEVEL`: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `PYTHONUNBUFFERED`: Set to 1 to ensure unbuffered output (recommended for logging)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
