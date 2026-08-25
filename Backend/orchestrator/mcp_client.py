import asyncio
from typing import Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import sys

class LocalMCPClient:
    def __init__(self, server_script_path: str):
        self.server_script_path = server_script_path
        self.session: Optional[ClientSession] = None
        self._exit_stack = None

    async def connect(self):
        """Connects to the local MCP server via stdio."""
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[self.server_script_path],
            env=os.environ.copy()
        )
        
        # Need contextlib to manage async context
        from contextlib import AsyncExitStack
        self._exit_stack = AsyncExitStack()
        
        read, write = await self._exit_stack.enter_async_context(stdio_client(server_params))
        self.session = await self._exit_stack.enter_async_context(ClientSession(read, write))
        
        await self.session.initialize()
        print(f"Connected to MCP Server at {self.server_script_path}")

    async def get_tools(self):
        """Returns available tools from the MCP server, auto-connecting if needed."""
        if not self.session:
            await self.connect()
        try:
            response = await self.session.list_tools()
            return response.tools
        except Exception:
            # Retry after re-establishing connection
            await self.disconnect()
            await self.connect()
            response = await self.session.list_tools()
            return response.tools

    async def call_tool(self, name: str, arguments: dict) -> str:
        """Calls a tool on the MCP server."""
        if not self.session:
            print("[MCP Client] Connection lost or not established. Reconnecting...")
            await self.connect()
        
        try:
            response = await self.session.call_tool(name, arguments)
        except Exception as e:
            print(f"[MCP Client] Error calling tool {name}: {e}")
            raise
            
        # Assuming TextContent response type based on our server implementation
        if response.content and hasattr(response.content[0], 'text'):
            return response.content[0].text
        return str(response.content)

    async def disconnect(self):
        """Disconnects from the server cleanly."""
        if self._exit_stack:
            try:
                await self._exit_stack.aclose()
            except Exception:
                pass
            self.session = None
            self._exit_stack = None

