import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Callable

from common.agent_card import AgentCard
from common.jsonrpc import JsonRpcRequest, make_success, make_error

log = logging.getLogger(__name__)


class JsonRpcHandler(BaseHTTPRequestHandler):

    def do_GET(self) -> None:
        if self.path == "/.well-known/agent-card.json":
            card: AgentCard = self.server.agent_card
            body = json.dumps(card.model_dump(), indent=2).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:
        if self.path != "/rpc":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length)

        try:
            payload = json.loads(raw_body)
            request = JsonRpcRequest(**payload)
        except Exception:
            response = make_error(0, -32700, "Parse error: invalid JSON-RPC request")
            self._send_json(response)
            return

        method_name = request.method
        registry: dict[str, Callable] = self.server.method_registry

        if method_name not in registry:
            response = make_error(request.id, -32601, f"Method not found: {method_name}")
            self._send_json(response)
            return

        try:
            result = registry[method_name](request.params)
            response = make_success(request.id, result)
        except Exception as e:
            log.exception("Method execution failed: %s", method_name)
            response = make_error(request.id, -32000, f"Internal error: {str(e)}")

        self._send_json(response)

    def _send_json(self, data: dict[str, Any]) -> None:
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: Any) -> None:
        log.info("[%s] %s", self.server.agent_card.name, fmt % args)


class AgentServer(HTTPServer):

    def __init__(self, host: str, port: int, card: AgentCard) -> None:
        super().__init__((host, port), JsonRpcHandler)
        self.agent_card = card
        self.method_registry: dict[str, Callable] = {}

    def register_method(self, name: str, handler: Callable) -> None:
        self.method_registry[name] = handler

    def start(self) -> None:
        addr = f"{self.server_address[0]}:{self.server_address[1]}"
        log.info("[%s] Listening on %s", self.agent_card.name, addr)
        self.serve_forever()

