import os
import unittest


class TestImplementWorkflowCheckpoints(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.workflow_path = os.path.join(self.root_dir, "workflows", "SDLC_IMPLEMENT_WORKFLOW.md")
        self.assertTrue(os.path.exists(self.workflow_path), f"Workflow file not found at {self.workflow_path}")
        with open(self.workflow_path, "r", encoding="utf-8") as f:
            self.content = f.read()

    def _get_section(self, start_heading, next_heading=None):
        idx = self.content.find(start_heading)
        self.assertNotEqual(idx, -1, f"Could not find heading '{start_heading}'")
        if next_heading:
            end_idx = self.content.find(next_heading, idx + len(start_heading))
            self.assertNotEqual(end_idx, -1, f"Could not find next heading '{next_heading}' after '{start_heading}'")
            return self.content[idx:end_idx]
        return self.content[idx:]

    def test_section_0_initializes_sdlc_state(self):
        section_0 = self._get_section("## 0. Prerequisite Check & Configuration Loading", "## 1.")
        self.assertIn(".agent_artifacts/SDLC_STATE.md", section_0, "Section 0 must reference .agent_artifacts/SDLC_STATE.md")
        has_init_or_load = "initialize" in section_0.lower() or "load" in section_0.lower()
        self.assertTrue(has_init_or_load, "Section 0 must instruct to Initialize/Load SDLC_STATE.md")

    def test_step_1_checkpoint(self):
        step_1 = self._get_section("### Step 1:", "### Step 2:")
        self.assertIn("SDLC_STATE.md", step_1, "Step 1 must reference SDLC_STATE.md checkpoint")

    def test_step_2_checkpoint(self):
        step_2 = self._get_section("### Step 2:", "### Step 3:")
        self.assertIn("SDLC_STATE.md", step_2, "Step 2 must reference SDLC_STATE.md checkpoint")

    def test_step_3_checkpoint(self):
        step_3 = self._get_section("### Step 3:", "### Step 4:")
        self.assertIn("SDLC_STATE.md", step_3, "Step 3 must reference SDLC_STATE.md checkpoint")

    def test_step_4_checkpoint(self):
        step_4 = self._get_section("### Step 4: Fan-Out Task Execution (Implementation Stage)", "### Step 5:")
        self.assertIn("SDLC_STATE.md", step_4, "Step 4 must reference SDLC_STATE.md checkpoint")

    def test_step_5_checkpoint(self):
        step_5 = self._get_section("### Step 5: Pull Request Creation & Automated Review Pipeline", "## 3. Finalization")
        self.assertIn("SDLC_STATE.md", step_5, "Step 5 must reference SDLC_STATE.md checkpoint")

    def test_section_3_finalization(self):
        section_3 = self._get_section("## 3. Finalization")
        self.assertIn("COMPLETED", section_3, "Section 3 must set status to COMPLETED upon clean finalization")
        self.assertIn(".agent_artifacts/SDLC_STATE.md", section_3, "Section 3 must instruct to retain .agent_artifacts/SDLC_STATE.md")


if __name__ == "__main__":
    unittest.main()
