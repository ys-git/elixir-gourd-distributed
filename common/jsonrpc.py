from typing import Any
from pydantic import BaseModel, Field


class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: dict[str, Any] = Field(default_factory=dict)
    id: str | int


class JsonRpcError(BaseModel):
    code: int
    message: str
    data: Any = None


class JsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: dict[str, Any] | None = None
    error: JsonRpcError | None = None
    id: str | int


def make_success(request_id: str | int, result: dict[str, Any]) -> dict[str, Any]:
    return JsonRpcResponse(result=result, id=request_id).model_dump(exclude_none=True)


def make_error(request_id: str | int, code: int, message: str) -> dict[str, Any]:
    return JsonRpcResponse(
        error=JsonRpcError(code=code, message=message),
        id=request_id,
    ).model_dump()

