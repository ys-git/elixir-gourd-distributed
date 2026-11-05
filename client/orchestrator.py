from client.rpc_client import AgentRpcClient

class DistributedSwarmOrchestrator:
    def __init__(
        self,
        triage_url: str = "http://localhost:8001",
        coder_url: str = "http://localhost:8002",
        verifier_url: str = "http://localhost:8003",
    ) -> None:
        self.triage_client = AgentRpcClient(triage_url)
        self.coder_client = AgentRpcClient(coder_url)
        self.verifier_client = AgentRpcClient(verifier_url)

    def ping_all(self) -> None:
        for name, client in [
            ("TriageAgent", self.triage_client),
            ("CoderAgent", self.coder_client),
            ("VerifierAgent", self.verifier_client),
        ]:
            card = client.get_agent_card()
            print(f"[DISCOVERY] Found {card.name} v{card.version} at {client.base_url}")

    def run(self, target_file: str, test_file: str, max_iterations: int = 3) -> bool:
        print("-" * 60)
        print("ELIXIR GOURD DISTRIBUTED: A2A JSON-RPC 2.0 Orchestrator")
        print(f"Target: {target_file}")
        print(f"Test  : {test_file}")
        print(f"Limit : {max_iterations} iterations")
        print("-" * 60)

        print("[INFO] Verifying agent availability...")
        self.ping_all()

        print("\n[INFO] Running baseline verification...")
        verify_res = self.verifier_client.call("verify", {"test_file": test_file})
        if verify_res.get("passed"):
            print("[INFO] All tests already pass. No repair needed.")
            return True

        iteration = 0
        last_test_output = verify_res.get("output", "")

        while iteration < max_iterations:
            iteration += 1
            print(f"\n[ITERATION {iteration}/{max_iterations}]")

            print("[RPC -> TriageAgent] Requesting diagnosis...")
            triage_res = self.triage_client.call(
                "diagnose",
                {
                    "target_file": target_file,
                    "test_output": last_test_output,
                    "iteration": iteration,
                }
            )
            diagnosis = triage_res.get("diagnosis", "")
            print(f"[DIAGNOSIS]\n{diagnosis}\n")

            print("[RPC -> CoderAgent] Requesting code repair...")
            coder_res = self.coder_client.call(
                "repair",
                {
                    "target_file": target_file,
                    "diagnosis": diagnosis,
                }
            )
            summary = coder_res.get("patch_summary", "")
            print(f"[SUMMARY]\n{summary}\n")

            print("[RPC -> VerifierAgent] Verifying repair...")
            verify_res = self.verifier_client.call("verify", {"test_file": test_file})
            if verify_res.get("passed"):
                print("-" * 60)
                print(f"[SUCCESS] Repaired in {iteration} iteration(s) via distributed agents.")
                print("-" * 60)
                return True

            last_test_output = verify_res.get("output", "")
            print("[WARN] Verification failed. Continuing loop.")

        print("-" * 60)
        print(f"[ERROR] Max iterations reached ({max_iterations}). Repair aborted.")
        print("-" * 60)
        return False

