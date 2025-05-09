"""
Simple test client for the MCP server
"""

import asyncio
import subprocess
import json
import sys
import time
import os

async def main():
    print("Starting test client for MCP server")
    
    # Start the server as a subprocess
    server_process = subprocess.Popen(
        [sys.executable, "src/filesystem_server/server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "PYTHONUNBUFFERED": "1"}
    )
    
    # Wait a moment for the server to start
    await asyncio.sleep(1)
    
    try:
        # Send a ListTools request
        list_tools_request = {
            "id": "1",
            "jsonrpc": "2.0",
            "method": "listTools",
            "params": {}
        }
        
        # Encode the request as JSON and send it to the server
        request_str = json.dumps(list_tools_request) + "\n"
        print(f"Sending request: {request_str}")
        server_process.stdin.write(request_str)
        server_process.stdin.flush()
        
        # Wait for the response
        response_line = server_process.stdout.readline().strip()
        if response_line:
            print(f"Received response: {response_line}")
            response = json.loads(response_line)
            
            # Check if the response contains tools
            if "result" in response and "tools" in response["result"]:
                print("\nAvailable tools:")
                for tool in response["result"]["tools"]:
                    print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
                    
            # Try to use the list_directory tool
            list_dir_request = {
                "id": "2",
                "jsonrpc": "2.0",
                "method": "callTool",
                "params": {
                    "name": "list_directory",
                    "parameters": {"path": "."}
                }
            }
            
            print(f"\nSending list_directory request...")
            server_process.stdin.write(json.dumps(list_dir_request) + "\n")
            server_process.stdin.flush()
            
            # Wait for the response
            await asyncio.sleep(0.5)
            response_line = server_process.stdout.readline().strip()
            if response_line:
                print(f"Received list_directory response:")
                response = json.loads(response_line)
                if "result" in response:
                    print(json.dumps(response["result"], indent=2))
        else:
            print("No response received from the server")
            
    finally:
        # Terminate the server
        print("\nTerminating the server")
        server_process.terminate()
        await asyncio.sleep(0.5)
        
        # Check if the server had any error output
        stderr_output = server_process.stderr.read()
        if stderr_output:
            print("\nServer error output:")
            print(stderr_output)
            
    print("Test complete")

if __name__ == "__main__":
    asyncio.run(main()) 