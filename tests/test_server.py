"""
Tests for the MCP Filesystem Server.
"""

import os
import tempfile
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.filesystem_server.server import (
    read_file,
    list_directory,
    search_files,
    file_monitor_handler,
    is_safe_path,
    WORKSPACE_ROOT,
)
from mcp import McpError

# Test fixtures
@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        f.write("Test content\nAnother line\nThird line with pattern123")
        path = f.name
    
    yield path
    
    # Cleanup
    if os.path.exists(path):
        os.unlink(path)

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as dir_path:
        # Create a few files in the directory
        with open(os.path.join(dir_path, "file1.txt"), "w") as f:
            f.write("Content of file1")
            
        with open(os.path.join(dir_path, "file2.txt"), "w") as f:
            f.write("Content of file2")
            
        os.mkdir(os.path.join(dir_path, "subdir"))
        with open(os.path.join(dir_path, "subdir", "file3.txt"), "w") as f:
            f.write("Content of file3")
            
        yield dir_path

# Tests for is_safe_path
def test_is_safe_path_valid():
    """Test is_safe_path with a valid path."""
    # Path within workspace
    assert is_safe_path(os.path.join(WORKSPACE_ROOT, "valid_file.txt"))

def test_is_safe_path_outside_workspace():
    """Test is_safe_path with a path outside the workspace."""
    # Path outside workspace
    assert not is_safe_path("/etc/passwd")

def test_is_safe_path_excluded_pattern():
    """Test is_safe_path with an excluded pattern."""
    # Path with excluded pattern
    assert not is_safe_path(os.path.join(WORKSPACE_ROOT, ".git", "config"))

# Tests for read_file
def test_read_file_success(temp_file, monkeypatch):
    """Test successful file reading."""
    # Mock is_safe_path to return True
    monkeypatch.setattr("src.filesystem_server.server.is_safe_path", lambda path: True)
    
    content = read_file(temp_file)
    assert "Test content" in content
    assert "pattern123" in content

def test_read_file_not_found(monkeypatch):
    """Test reading a non-existent file."""
    # Mock is_safe_path to return True
    monkeypatch.setattr("src.filesystem_server.server.is_safe_path", lambda path: True)
    
    with pytest.raises(McpError) as excinfo:
        read_file("non_existent_file.txt")
    
    assert "File not found" in str(excinfo.value)

def test_read_file_unsafe_path(monkeypatch):
    """Test reading a file with unsafe path."""
    # Mock is_safe_path to return False
    monkeypatch.setattr("src.filesystem_server.server.is_safe_path", lambda path: False)
    
    with pytest.raises(McpError) as excinfo:
        read_file("/etc/passwd")
    
    assert "Access denied" in str(excinfo.value)

# Tests for list_directory
def test_list_directory_success(temp_dir, monkeypatch):
    """Test successful directory listing."""
    # Mock is_safe_path to return True
    monkeypatch.setattr("src.filesystem_server.server.is_safe_path", lambda path: True)
    
    entries = list_directory(temp_dir)
    
    # Verify entries
    file_names = [entry["name"] for entry in entries]
    assert "file1.txt" in file_names
    assert "file2.txt" in file_names
    assert "subdir" in file_names
    
    # Verify types
    file_entries = [entry for entry in entries if entry["name"] == "file1.txt"]
    dir_entries = [entry for entry in entries if entry["name"] == "subdir"]
    
    assert file_entries[0]["type"] == "file"
    assert dir_entries[0]["type"] == "directory"

def test_list_directory_not_found(monkeypatch):
    """Test listing a non-existent directory."""
    # Mock is_safe_path to return True
    monkeypatch.setattr("src.filesystem_server.server.is_safe_path", lambda path: True)
    
    with pytest.raises(McpError) as excinfo:
        list_directory("non_existent_directory")
    
    assert "Directory not found" in str(excinfo.value)

def test_list_directory_unsafe_path(monkeypatch):
    """Test listing a directory with unsafe path."""
    # Mock is_safe_path to return False
    monkeypatch.setattr("src.filesystem_server.server.is_safe_path", lambda path: False)
    
    with pytest.raises(McpError) as excinfo:
        list_directory("/etc")
    
    assert "Access denied" in str(excinfo.value)

# Tests for search_files
def test_search_files_success(temp_dir, monkeypatch):
    """Test successful file searching."""
    # Mock is_safe_path to return True
    monkeypatch.setattr("src.filesystem_server.server.is_safe_path", lambda path: True)
    
    # Create a file with specific content
    test_file_path = os.path.join(temp_dir, "searchable.txt")
    with open(test_file_path, "w") as f:
        f.write("Line with pattern123\nAnother line\nThird line with pattern123 again")
    
    # Search for pattern
    results = search_files("pattern123", temp_dir, include_content=True)
    
    # Verify results
    assert len(results) == 2  # Two lines match
    assert results[0]["file"] == test_file_path
    assert "pattern123" in results[0]["content"]

def test_search_files_invalid_pattern(temp_dir, monkeypatch):
    """Test searching with an invalid regex pattern."""
    # Mock is_safe_path to return True
    monkeypatch.setattr("src.filesystem_server.server.is_safe_path", lambda path: True)
    
    with pytest.raises(McpError) as excinfo:
        search_files("[invalid regex", temp_dir)
    
    assert "Invalid regex pattern" in str(excinfo.value)

def test_search_files_unsafe_path(monkeypatch):
    """Test searching files with unsafe path."""
    # Mock is_safe_path to return False
    monkeypatch.setattr("src.filesystem_server.server.is_safe_path", lambda path: False)
    
    with pytest.raises(McpError) as excinfo:
        search_files("pattern", "/etc")
    
    assert "Access denied" in str(excinfo.value)

# Tests for file_monitor resource
@pytest.mark.asyncio
async def test_file_monitor_handler_success(temp_file):
    """Test successful file monitor handler."""
    # Mock is_safe_path to return True
    with patch("src.filesystem_server.server.is_safe_path", return_value=True):
        # Call the resource handler
        result = await file_monitor_handler(temp_file)
        
        # Verify result
        assert result["path"] == temp_file
        assert "size" in result
        assert "last_modified" in result

@pytest.mark.asyncio
async def test_file_monitor_handler_not_found():
    """Test file monitor handler with non-existent file."""
    # Mock is_safe_path to return True
    with patch("src.filesystem_server.server.is_safe_path", return_value=True):
        with pytest.raises(McpError) as excinfo:
            await file_monitor_handler("non_existent_file.txt")
        
        assert "File not found" in str(excinfo.value)

@pytest.mark.asyncio
async def test_file_monitor_handler_unsafe_path():
    """Test file monitor handler with an unsafe path."""
    # Mock is_safe_path to return False
    with patch("src.filesystem_server.server.is_safe_path", return_value=False):
        with pytest.raises(McpError) as excinfo:
            await file_monitor_handler("/etc/passwd")
        
        assert "Access denied" in str(excinfo.value) 