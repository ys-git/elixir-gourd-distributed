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
    "You are a code diagnostic engine.\n"
    "Analyze the pytest failure output and determine the root cause.\n"
    "Return a concise technical diagnosis:\n"
    "1. Nature of the failure (assertion mismatch, exception type, etc).\n"
    "2. Identified function and line.\n"
    "3. Required logical or algorithmic correction."
)

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
)


def diagnose(params: dict[str, Any]) -> dict[str, Any]:
    target_file = params["target_file"]
    test_output = params["test_output"]
    iteration = params.get("iteration", 0)

    user_content = (
        f"TARGET FILE: {target_file}\n"
        f"ITERATION: {iteration}\n\n"
        f"PYTEST OUTPUT:\n```\n{test_output}\n```"
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.1,
    )

    diagnosis = response.choices[0].message.content or "No diagnosis generated."
    log.info("[Triage] Diagnosis complete")
    return {"diagnosis": diagnosis}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001

    card = AgentCard(
        name="TriageAgent",
        description="Diagnoses pytest failure traces and identifies root causes.",
        supported_methods=["diagnose"],
        supported_interfaces=[
            AgentInterface(url=f"http://localhost:{port}/rpc"),
        ],
    )

    server = AgentServer("0.0.0.0", port, card)
    server.register_method("diagnose", diagnose)
    server.start()


if __name__ == "__main__":
    main()

