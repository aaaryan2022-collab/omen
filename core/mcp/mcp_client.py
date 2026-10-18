# ============================================
"""
Model Context Protocol (MCP) Client for OMEN.
Supports connecting to external MCP servers via stdio or HTTP/SSE, discovering tools, and executing them.
"""

import subprocess
import json
import os
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from app.logging_config import logger
from tools.base import BaseTool, ToolResult
from app.constants import RiskLevel


class MCPToolDefinition(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]


class MCPClient:
    """Client for Model Context Protocol servers."""

    def __init__(self, server_name: str, command: str, args: Optional[List[str]] = None, env: Optional[Dict[str, str]] = None):
        self.server_name = server_name
        self.command = command
        self.args = args or []
        self.env = env or {}
        self._proc: Optional[subprocess.Popen] = None
        self._tools: Dict[str, MCPToolDefinition] = {}
        self._connected = False

    def connect(self) -> bool:
        """Starts the MCP server process over stdio."""
        try:
            full_env = os.environ.copy()
            full_env.update(self.env)
            self._proc = subprocess.Popen(
                [self.command] + self.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=full_env,
                bufsize=1
            )
            self._connected = True
            logger.info(f"Connected to MCP server: {self.server_name}")
            self._discover_tools()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {self.server_name}: {e}")
            self._connected = False
            return False

    def _send_rpc(self, method: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        if not self._proc or not self._proc.stdin or not self._proc.stdout:
            return None
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        try:
            line = json.dumps(req) + "\n"
            self._proc.stdin.write(line)
            self._proc.stdin.flush()
            resp_line = self._proc.stdout.readline()
            if resp_line:
                return json.loads(resp_line)
        except Exception as e:
            logger.error(f"RPC communication failed with {self.server_name}: {e}")
        return None

    def _discover_tools(self) -> None:
        """Discovers tools exposed by the MCP server."""
        resp = self._send_rpc("tools/list")
        if resp and "result" in resp and "tools" in resp["result"]:
            for t in resp["result"]["tools"]:
                tool_def = MCPToolDefinition(
                    name=t.get("name", ""),
                    description=t.get("description", ""),
                    inputSchema=t.get("inputSchema", {})
                )
                self._tools[tool_def.name] = tool_def
            logger.info(f"Discovered {len(self._tools)} tools from MCP server {self.server_name}")

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Invokes a tool on the external MCP server."""
        if not self._connected:
            return ToolResult(success=False, error=f"MCP server {self.server_name} is not connected.")
        resp = self._send_rpc("tools/call", {"name": tool_name, "arguments": arguments})
        if not resp:
            return ToolResult(success=False, error="Empty response from MCP server.")
        if "error" in resp:
            return ToolResult(success=False, error=str(resp["error"]))
        content = resp.get("result", {}).get("content", [])
        text_out = "\n".join([c.get("text", "") for c in content if isinstance(c, dict) and "text" in c])
        return ToolResult(success=True, data=resp.get("result"), message=text_out or "Tool executed.")

    def disconnect(self) -> None:
        if self._proc:
            try:
                self._proc.terminate()
            except Exception:
                pass
            self._proc = None
        self._connected = False


class MCPManager:
    """Manages active MCP servers."""

    def __init__(self):
        self._clients: Dict[str, MCPClient] = {}

    def register_server(self, name: str, command: str, args: Optional[List[str]] = None) -> MCPClient:
        client = MCPClient(name, command, args)
        self._clients[name] = client
        return client

    def get_server(self, name: str) -> Optional[MCPClient]:
        return self._clients.get(name)

    def list_servers(self) -> List[str]:
        return list(self._clients.keys())


mcp_manager = MCPManager()
