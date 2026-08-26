import json
import os
import unittest

try:
    import jsonschema
except ImportError:
    jsonschema = None


class TestSDLCStateSchema(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.schema_path = os.path.join(self.root_dir, "schemas", "sdlc-state.schema.json")
        self.md_path = os.path.join(self.root_dir, "schemas", "SDLC_STATE.md")

    def test_schema_loads_and_has_required_properties(self):
        self.assertTrue(os.path.exists(self.schema_path), f"Schema file not found at {self.schema_path}")
        with open(self.schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        self.assertEqual(schema.get("type"), "object")
        properties = schema.get("properties", {})
        expected_properties = [
            "current_phase",
            "status",
            "hitl_mode",
            "tracking_mode",
            "active_issue_id",
            "checkpoints",
        ]
        for prop in expected_properties:
            self.assertIn(prop, properties, f"Missing property '{prop}' in schema")

        required = schema.get("required", [])
        expected_required = ["current_phase", "status", "hitl_mode", "tracking_mode"]
        for req in expected_required:
            self.assertIn(req, required, f"Missing required property '{req}' in schema")

    def validate_instance_manual(self, instance, schema):
        if not isinstance(instance, dict):
            raise ValueError("Instance must be a dictionary")
        for req in schema.get("required", []):
            if req not in instance:
                raise ValueError(f"Missing required key: {req}")

        properties = schema.get("properties", {})
        for key, val in instance.items():
            if key in properties:
                prop_schema = properties[key]
                if "enum" in prop_schema and val not in prop_schema["enum"]:
                    raise ValueError(f"Value '{val}' for key '{key}' not in enum {prop_schema['enum']}")
                if key == "checkpoints" and val is not None:
                    if not isinstance(val, dict):
                        raise ValueError("checkpoints must be an object/dict")
                    cp_props = prop_schema.get("properties", {})
                    if "active_tasks" in val:
                        if not isinstance(val["active_tasks"], list):
                            raise ValueError("active_tasks must be a list")
                    if "review_remediation" in val:
                        rr = val["review_remediation"]
                        if not isinstance(rr, dict):
                            raise ValueError("review_remediation must be a dict")
                        rr_props = cp_props.get("review_remediation", {}).get("properties", {})
                        if "circuit_breaker_status" in rr and "enum" in rr_props.get("circuit_breaker_status", {}):
                            if rr["circuit_breaker_status"] not in rr_props["circuit_breaker_status"]["enum"]:
                                raise ValueError(f"Invalid circuit_breaker_status: {rr['circuit_breaker_status']}")

    def test_sample_valid_state_validation(self):
        self.assertTrue(os.path.exists(self.schema_path), f"Schema file not found at {self.schema_path}")
        with open(self.schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        valid_sample = {
            "current_phase": "Step 1",
            "status": "IN_PROGRESS",
            "hitl_mode": "strict",
            "tracking_mode": "local",
            "active_issue_id": "#27",
            "checkpoints": {
                "active_tasks": [
                    {
                        "task_id": "T-001",
                        "title": "Implement Schemas",
                        "status": "IN_PROGRESS",
                        "assignee": "sdlc-coding-agent"
                    }
                ],
                "review_remediation": {
                    "iteration_counter": "Iteration 1/3",
                    "circuit_breaker_status": "ACTIVE",
                    "active_findings": [
                        {
                            "finding_id": "REV-001",
                            "pillar": "Security",
                            "description": "Check permissions",
                            "remediation_status": "OPEN"
                        }
                    ]
                }
            }
        }

        if jsonschema:
            jsonschema.validate(instance=valid_sample, schema=schema)

        # Always run manual check as fallback/verification
        self.validate_instance_manual(valid_sample, schema)

        invalid_sample_missing_req = {
            "current_phase": "Step 1",
            "hitl_mode": "strict"
        }
        if jsonschema:
            with self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate(instance=invalid_sample_missing_req, schema=schema)
        with self.assertRaises(ValueError):
            self.validate_instance_manual(invalid_sample_missing_req, schema)

        invalid_sample_bad_enum = {
            "current_phase": "Step 1",
            "status": "NOT_A_VALID_STATUS",
            "hitl_mode": "strict",
            "tracking_mode": "local"
        }
        if jsonschema:
            with self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate(instance=invalid_sample_bad_enum, schema=schema)
        with self.assertRaises(ValueError):
            self.validate_instance_manual(invalid_sample_bad_enum, schema)

    def test_sdlc_state_md_exists_and_headers(self):
        self.assertTrue(os.path.exists(self.md_path), f"Markdown file not found at {self.md_path}")
        with open(self.md_path, "r", encoding="utf-8") as f:
            content = f.read()

        required_headers = [
            "# SDLC Runtime State Checkpoint",
            "## Metadata",
            "## Active Tasks Checkpoint",
            "## Review & Remediation Checkpoint",
        ]
        for header in required_headers:
            self.assertIn(header, content, f"Header '{header}' missing in {self.md_path}")


if __name__ == "__main__":
    unittest.main()
