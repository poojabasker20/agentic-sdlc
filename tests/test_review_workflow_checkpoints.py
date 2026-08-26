import os
import unittest


class TestReviewWorkflowCheckpoints(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.workflow_path = os.path.join(self.root_dir, "workflows", "SDLC_REVIEW_WORKFLOW.md")

    def get_section(self, content, header):
        idx = content.find(header)
        if idx == -1:
            return ""
        next_idx = content.find("\n## ", idx + len(header))
        if next_idx == -1:
            return content[idx:]
        return content[idx:next_idx]

    def test_workflow_file_exists(self):
        self.assertTrue(os.path.exists(self.workflow_path), f"File not found: {self.workflow_path}")

    def test_section_0_initializes_sdlc_state(self):
        with open(self.workflow_path, "r", encoding="utf-8") as f:
            content = f.read()
        section_0 = self.get_section(content, "## 0. Prerequisite Check & Configuration Loading")
        self.assertIn(".agent_artifacts/SDLC_STATE.md", section_0)
        self.assertTrue(
            "initialize" in section_0.lower() or "load" in section_0.lower(),
            "Section 0 must instruct to Initialize/Load SDLC_STATE.md"
        )

    def test_section_2_tracks_iteration_and_circuit_breaker_in_sdlc_state(self):
        with open(self.workflow_path, "r", encoding="utf-8") as f:
            content = f.read()
        section_2 = self.get_section(content, "## 2. Circuit Breaker & Logging Protocol")
        self.assertIn(".agent_artifacts/SDLC_STATE.md", section_2)
        self.assertIn("Iteration N/3", section_2)
        self.assertIn("circuit breaker status", section_2.lower())

    def test_section_3_tracks_active_review_findings_in_sdlc_state(self):
        with open(self.workflow_path, "r", encoding="utf-8") as f:
            content = f.read()
        section_3 = self.get_section(content, "## 3. The 5-Step Remediation Loop")
        self.assertIn(".agent_artifacts/SDLC_STATE.md", section_3)
        self.assertIn("active review findings table", section_3.lower())

    def test_section_5_completes_and_retains_sdlc_state(self):
        with open(self.workflow_path, "r", encoding="utf-8") as f:
            content = f.read()
        section_5 = self.get_section(content, "## 5. Pre-Merge Automated Bot Triage Gate & Clean Termination")
        self.assertIn(".agent_artifacts/SDLC_STATE.md", section_5)
        self.assertIn("COMPLETED", section_5)
        self.assertTrue(
            "retain" in section_5.lower() or "retained" in section_5.lower(),
            "Section 5 must specify retaining SDLC_STATE.md"
        )


if __name__ == "__main__":
    unittest.main()
