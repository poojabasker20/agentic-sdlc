"""Pydantic schema definition for SDLC Plan Verifier Agent."""

from typing import List, Optional
from pydantic import BaseModel, Field


class PlanAuditFinding(BaseModel):
    finding_id: str = Field(description="Unique finding code (e.g. CHK-001)")
    severity: str = Field(
        default="Medium",
        description="Severity level: 'High' (blocking), 'Medium', or 'Low'",
    )
    category: str = Field(
        description="Category (e.g. Scope Exceeded, Missing BDD Test, Invalid Path, DAG Cycle)"
    )
    target_component_or_step: str = Field(
        description="Target step or component (e.g. Step 3.1, Testing Strategy)"
    )
    description: str = Field(
        description="Detailed description of defect or non-compliance"
    )
    remediation_instruction: str = Field(
        description="Actionable, prescriptive remediation instruction"
    )


class ChecklistItem(BaseModel):
    name: str = Field(description="Name of the checklist rule")
    passed: bool = Field(default=True, description="True if compliant, False otherwise")


class PlanVerifierPayload(BaseModel):
    plan_id: str = Field(description="Implementation Plan identifier, e.g. SUBTASK-STORY-101-1-PLAN")
    target_subtask: str = Field(description="Target Subtask ID, e.g. SUBTASK-STORY-101-1")
    parent_story_id: str = Field(description="Parent User Story ID, e.g. STORY-101")
    target_repository: str = Field(
        default="poojabasker20/springboot-hello-world",
        description="Target codebase repository",
    )
    audit_timestamp: str = Field(
        default="2026-08-30 00:00:00 UTC",
        description="Timestamp of audit execution",
    )
    overall_verdict: str = Field(
        description="Final verdict: 'PASSED' or 'REJECTED - REVISION REQUIRED'"
    )
    verification_score: int = Field(
        default=90, description="Verification score out of 100"
    )
    executive_summary: str = Field(
        description="Concise summary of adversarial assessment, DAG health, and readiness"
    )
    surgical_editing_compliant: bool = Field(
        default=True,
        description="True if file count <= 10 and estimated LOC <= 400",
    )
    dependency_dag_valid: bool = Field(
        default=True,
        description="True if dependency ordering has no cycles or missing prerequisites",
    )
    rollback_handling_valid: bool = Field(
        default=True,
        description="True if rollback/failure states are accounted for",
    )
    ast_integrity_confirmed: bool = Field(
        default=True,
        description="True if target symbols and file paths match AST code map",
    )
    bdd_coverage_complete: bool = Field(
        default=True,
        description="True if 100% of BDD Acceptance Criteria are tested",
    )
    findings: List[PlanAuditFinding] = Field(
        default_factory=list,
        description="Detailed findings and critique items",
    )
    remediation_action_plan: List[str] = Field(
        default_factory=list,
        description="Prioritized, actionable remediation items if REJECTED",
    )
    verifier_assumptions: List[str] = Field(
        default_factory=list,
        description="Assumptions made by the verifier during analysis",
    )

    @property
    def rendered_markdown(self) -> str:
        """Renders the audit report into the standard SKILL.md Markdown format."""
        lines = [
            f"# Plan Verification Audit Report: {self.target_subtask}\n",
            f"**Plan ID:** `{self.plan_id}`  ",
            f"**Target Subtask:** `{self.target_subtask}`  ",
            f"**Parent Story ID:** `{self.parent_story_id}`  ",
            f"**Target Repository:** `{self.target_repository}`  ",
            f"**Audit Timestamp:** `{self.audit_timestamp}`  ",
            f"**Overall Verdict:** **`{self.overall_verdict}`**  ",
            f"**Verification Score:** `{self.verification_score}/100`\n",
            "## 1. Executive Summary & Adversarial Assessment\n",
            f"{self.executive_summary.strip()}\n",
            "## 2. Plan Verification Checklist Summary\n",
            f"- [{'x' if self.surgical_editing_compliant else ' '}] Surgical Editing Limits (<10 files, <400 LOC per plan)",
            f"- [{'x' if self.dependency_dag_valid else ' '}] Dependency DAG & Execution Sequence Validated",
            f"- [{'x' if self.rollback_handling_valid else ' '}] Rollback & Failure States Accounted For",
            f"- [{'x' if self.ast_integrity_confirmed else ' '}] AST Code Map Symbol & File Path Integrity Confirmed",
            f"- [{'x' if self.bdd_coverage_complete else ' '}] Complete Coverage of User Story BDD Acceptance Criteria\n",
            "## 3. Detailed Critique & Findings Table\n",
            "| Finding ID | Severity | Category | Target Component / Step | Description | Remediation & Restructuring Instruction |",
            "| ---------- | -------- | -------- | ----------------------- | ----------- | --------------------------------------- |",
        ]

        if self.findings:
            for f in self.findings:
                lines.append(
                    f"| `{f.finding_id}` | **{f.severity}** | {f.category} | {f.target_component_or_step} | {f.description} | {f.remediation_instruction} |"
                )
        else:
            lines.append("| `N/A` | **None** | Compliance | Whole Blueprint | No defects identified across implementation plan. | None required. |")
        lines.append("")

        # Remediation Action Plan
        lines.append("## 4. Remediation Action Plan (If REJECTED)\n")
        if self.remediation_action_plan and self.overall_verdict != "PASSED":
            for idx, item in enumerate(self.remediation_action_plan, 1):
                lines.append(f"{idx}. **Action Item {idx}:** {item}")
        else:
            lines.append("No remediation required. Plan is approved for developer execution.")
        lines.append("")

        # Assumptions
        lines.append("## 5. Agent Verification Assumptions Made\n")
        if self.verifier_assumptions:
            for idx, a in enumerate(self.verifier_assumptions, 1):
                lines.append(f"- **Assumption {idx}:** {a}")
        else:
            lines.append("- None at this time.")
        lines.append("")

        # Done When Checklist
        lines.append("## 6. Done When Checklist\n")
        lines.append("- [ ] Implementation plan was audited against all 4 Adversarial Verification Rules.")
        lines.append("- [ ] Surgical editing limits (<10 files, <400 LOC) were strictly evaluated.")
        lines.append("- [ ] Verification Score and binary verdict (`PASSED` / `REJECTED`) are clearly stated.")
        lines.append("- [ ] Remediation items are actionable if status is `REJECTED`.")
        lines.append(f"- [ ] The audit report was saved to `docs/audits/{self.target_subtask}-verifier-report.md` on `SDLC_GOVERNANCE_REPO`.")
        lines.append("- [ ] A summary comment was posted to the Implementation Plan PR.")

        return "\n".join(lines)
