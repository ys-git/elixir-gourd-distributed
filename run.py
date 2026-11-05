import argparse
import os
import sys
from dotenv import load_dotenv

from client.orchestrator import DistributedSwarmOrchestrator

def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Elixir Gourd Distributed: A2A JSON-RPC 2.0 Orchestrator"
    )
    parser.add_argument(
        "--target",
        type=str,
        default="benchmarks/sample_math.py",
        help="Target source file to repair."
    )
    parser.add_argument(
        "--test",
        type=str,
        default="benchmarks/test_sample_math.py",
        help="Pytest test file to verify against."
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum repair iterations (default: 3)."
    )
    parser.add_argument(
        "--triage-url",
        type=str,
        default="http://localhost:8001",
        help="URL of Triage Agent."
    )
    parser.add_argument(
        "--coder-url",
        type=str,
        default="http://localhost:8002",
        help="URL of Coder Agent."
    )
    parser.add_argument(
        "--verifier-url",
        type=str,
        default="http://localhost:8003",
        help="URL of Verifier Agent."
    )

    args = parser.parse_args()

    orchestrator = DistributedSwarmOrchestrator(
        triage_url=args.triage_url,
        coder_url=args.coder_url,
        verifier_url=args.verifier_url,
    )

    success = orchestrator.run(
        target_file=args.target,
        test_file=args.test,
        max_iterations=args.max_retries,
    )

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

