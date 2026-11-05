from pydantic import BaseModel


class AgentInterface(BaseModel):
    url: str
    protocol_binding: str = "JSONRPC"
    protocol_version: str = "2.0"


class AgentCard(BaseModel):
    name: str
    version: str = "1.0"
    description: str = ""
    supported_methods: list[str] = []
    supported_interfaces: list[AgentInterface] = []

