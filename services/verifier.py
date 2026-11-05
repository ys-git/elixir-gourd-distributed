import logging
import os
import subprocess
import sys
from typing import Any

from common.agent_card import AgentCard, AgentInterface
from services.base import AgentServer

log = logging.getLogger(__name__)


def verify(params: dict[str, Any]) -> dict[str, Any]:
    test_file = params["test_file"]

    venv_pytest = os.path.join(os.getcwd(), ".venv", "bin", "pytest")
    pytest_bin = venv_pytest if os.path.exists(venv_pytest) else "pytest"

    try:
        result = subprocess.run(
            [pytest_bin, test_file, "-v", "--no-header"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = (result.stdout + result.stderr).strip()
        passed = result.returncode == 0
    except subprocess.TimeoutExpired:
        output = "pytest timed out after 30 seconds."
        passed = False
    except Exception as e:
        output = f"pytest execution error: {str(e)}"
        passed = False

    log.info("[Verifier] passed=%s", passed)
    return {"passed": passed, "output": output}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8003

    card = AgentCard(
        name="VerifierAgent",
        description="Runs pytest in a subprocess and returns pass/fail status.",
        supported_methods=["verify"],
        supported_interfaces=[
            AgentInterface(url=f"http://localhost:{port}/rpc"),
        ],
    )

    server = AgentServer("0.0.0.0", port, card)
    server.register_method("verify", verify)
    server.start()


if __name__ == "__main__":
    main()

