import json
import urllib.error
import urllib.request
from typing import Any

from common.agent_card import AgentCard
from common.jsonrpc import JsonRpcRequest, JsonRpcResponse

class AgentRpcClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.rpc_url = f"{self.base_url}/rpc"
        self._request_counter = 0

    def get_agent_card(self) -> AgentCard:
        url = f"{self.base_url}/.well-known/agent-card.json"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return AgentCard(**data)

    def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self._request_counter += 1
        req_obj = JsonRpcRequest(
            method=method,
            params=params or {},
            id=f"req-{self._request_counter}"
        )
        body = json.dumps(req_obj.model_dump()).encode("utf-8")
        req = urllib.request.Request(
            self.rpc_url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                rpc_resp = JsonRpcResponse(**data)
                if rpc_resp.error:
                    raise RuntimeError(f"RPC Error [{rpc_resp.error.code}]: {rpc_resp.error.message}")
                return rpc_resp.result or {}
        except urllib.error.URLError as e:
            raise ConnectionError(f"Failed to connect to agent at {self.rpc_url}: {e}")

