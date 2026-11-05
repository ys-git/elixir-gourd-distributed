import json
import logging
import os
import sys
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from common.agent_card import AgentCard, AgentInterface
from services.base import AgentServer

load_dotenv()
log = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a code repair engine.\n"
    "Fix the bug in the target file based on the diagnosis.\n"
    "Execution workflow:\n"
    "1. Use `read_file` to inspect the target file content.\n"
    "2. Modify the code and use `write_file` to write the complete updated content.\n"
    "3. Provide a brief summary of changes once written.\n"
    "Preserve existing signatures and structure unless directly related to the fix."
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read file contents from disk.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "File path."}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write updated source code to disk.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path."},
                    "content": {"type": "string", "description": "File content."},
                },
                "required": ["path", "content"],
            },
        },
    },
]

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
)


def _execute_tool(name: str, arguments: dict[str, Any]) -> str:
    if name == "read_file":
        path = arguments["path"]
        if not os.path.exists(path):
            return f"Error: File '{path}' not found."
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    if name == "write_file":
        path = arguments["path"]
        content = arguments["content"]
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Wrote {len(content)} characters to '{path}'."

    return f"Unknown tool: {name}"


def repair(params: dict[str, Any]) -> dict[str, Any]:
    target_file = params["target_file"]
    diagnosis = params["diagnosis"]
    max_turns = 5

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"TARGET FILE: {target_file}\n"
                f"DIAGNOSIS:\n{diagnosis}\n\n"
                "Read the target file, apply the fix, and write the updated file."
            ),
        },
    ]

    patch_summary = ""
    for turn in range(max_turns):
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.2,
        )

        msg = response.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            patch_summary = msg.content or "Repair completed."
            break

        for tool_call in msg.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)
            log.info("[Coder] Tool: %s(%s)", func_name, list(func_args.keys()))
            output = _execute_tool(func_name, func_args)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": output,
            })

    log.info("[Coder] Patch applied")
    return {"patch_summary": patch_summary}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8002

    card = AgentCard(
        name="CoderAgent",
        description="Repairs buggy source files using tool-assisted code editing.",
        supported_methods=["repair"],
        supported_interfaces=[
            AgentInterface(url=f"http://localhost:{port}/rpc"),
        ],
    )

    server = AgentServer("0.0.0.0", port, card)
    server.register_method("repair", repair)
    server.start()


if __name__ == "__main__":
    main()

