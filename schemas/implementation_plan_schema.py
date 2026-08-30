"""Pydantic schema definition for Stage 3: Implementation Plan Generator Agent."""

from typing import List, Optional
from pydantic import BaseModel, Field


class FileDeltaItem(BaseModel):
    file_path: str = Field(
        description="Relative file path (e.g. src/main/java/com/nordea/demo/dto/RequestDTO.java)"
    )
    action: str = Field(
        default="Create",
        description="Action to perform: 'Create', 'Modify', or 'Delete'",
    )
    layer_component: str = Field(
        description="Architectural layer (e.g. DTO Schema, Business Logic, API / Controller, Unit Test)"
    )
    description_of_changes: str = Field(
        description="Concise description of changes for this file"
    )


class ImplementationStep(BaseModel):
    step_title: str = Field(
        description="Step header (e.g. Step 3.1: Data Models & DTO Schemas)"
    )
    target_file: str = Field(description="Exact relative target file path")
    detailed_instructions: List[str] = Field(
        default_factory=list,
        description="Step-by-step implementation instructions and logic rules",
    )


class BlastRadiusAnalysis(BaseModel):
    downstream_components_impacted: List[str] = Field(
        default_factory=list,
        description="Existing classes, services, or APIs affected by these changes",
    )
    breaking_changes: str = Field(
        default="None",
        description="Description of breaking contract/schema changes, or 'None'",
    )
    database_migration_impact: str = Field(
        default="N/A",
        description="Database schema changes, migration scripts needed, or 'N/A'",
    )
    risk_mitigation_strategy: str = Field(
        default="Standard regression testing",
        description="Safeguards, feature flags, or backward compatibility measures",
    )


class SecurityGuardrails(BaseModel):
    security_requirements: List[str] = Field(
        default_factory=list,
        description="Input sanitization, authentication/authorization checks, OWASP compliance",
    )
    performance_constraints: List[str] = Field(
        default_factory=list,
        description="Latency targets, caching strategies, query efficiency constraints",
    )
    error_handling_standards: List[str] = Field(
        default_factory=list,
        description="Standardized exception responses and logging guidelines",
    )


class TestCase(BaseModel):
    target_test_file: str = Field(
        description="Relative path to test file (e.g. src/test/java/com/nordea/demo/service/FeatureServiceTest.java)"
    )
    test_scenarios: List[str] = Field(
        default_factory=list,
        description="List of specific test scenarios and assertions",
    )


class TestingStrategy(BaseModel):
    unit_tests: List[TestCase] = Field(
        default_factory=list, description="Unit test targets and scenarios"
    )
    integration_tests: List[TestCase] = Field(
        default_factory=list,
        description="Integration and API contract test targets mapped to ACs",
    )


class ImplementationPlanPayload(BaseModel):
    subtask_id: str = Field(description="Subtask ID, e.g. SUBTASK-STORY-101-1")
    subtask_title: str = Field(description="Title of the subtask")
    parent_story_id: str = Field(description="Parent User Story ID, e.g. STORY-101")
    target_repository: str = Field(
        default="poojabasker20/springboot-hello-world",
        description="Target codebase repository name",
    )
    status: str = Field(
        default="Ready for Technical Review",
        description="Status of the implementation plan",
    )
    estimated_scope: str = Field(
        default="1 PR", description="Estimated PR scope, e.g. '1 PR' or '1-2 PRs'"
    )
    executive_summary: str = Field(
        description="Concise technical goal, architectural layers modified, and user story criteria fulfilled"
    )
    affected_files_delta: List[FileDeltaItem] = Field(
        default_factory=list,
        description="List of files to be created, modified, or deleted",
    )
    step_by_step_guide: List[ImplementationStep] = Field(
        default_factory=list,
        description="Step-by-step implementation instructions per component",
    )
    blast_radius: BlastRadiusAnalysis = Field(
        default_factory=BlastRadiusAnalysis,
        description="Blast radius and impact analysis",
    )
    security_guardrails: SecurityGuardrails = Field(
        default_factory=SecurityGuardrails,
        description="Security, performance, and compliance guardrails",
    )
    testing_strategy: TestingStrategy = Field(
        default_factory=TestingStrategy,
        description="Comprehensive unit and integration testing strategy",
    )
    open_questions: List[str] = Field(
        default_factory=list,
        description="Explicit questions or technical ambiguities for reviewers",
    )
    agent_assumptions: List[str] = Field(
        default_factory=list,
        description="Technical or architectural assumptions made by the agent",
    )
    revision_changelog: Optional[str] = Field(
        default=None,
        description="Changelog of revisions made in response to reviews or audit findings",
    )

    @property
    def rendered_markdown(self) -> str:
        """Renders the implementation blueprint into the standard SKILL.md Markdown format."""
        lines = [
            f"# Implementation Blueprint: {self.subtask_title}\n",
            f"**Subtask ID:** `{self.subtask_id}`  ",
            f"**Parent Story ID:** `{self.parent_story_id}`  ",
            f"**Target Repository:** `{self.target_repository}`  ",
            f"**Status:** {self.status}  ",
            f"**Estimated Scope:** {self.estimated_scope}\n",
            "## 1. Executive Summary & Objective\n",
            f"{self.executive_summary.strip()}\n",
            "## 2. Affected Files & File Change Delta Matrix\n",
            "| Relative File Path | Action | Layer / Component | Description of Changes |",
            "| ------------------ | ------ | ----------------- | ---------------------- |",
        ]

        for item in self.affected_files_delta:
            lines.append(
                f"| `{item.file_path}` | **{item.action}** | {item.layer_component} | {item.description_of_changes} |"
            )
        lines.append("")

        # Step by step guide
        lines.append("## 3. Step-by-Step Technical Implementation Guide\n")
        for step in self.step_by_step_guide:
            lines.append(f"### {step.step_title}\n")
            lines.append(f"- **Target File:** `{step.target_file}`")
            lines.append("- **Detailed Instructions:**")
            for idx, inst in enumerate(step.detailed_instructions, 1):
                lines.append(f"  {idx}. {inst}")
            lines.append("")

        # Blast Radius
        lines.append("## 4. Blast Radius & Impact Analysis\n")
        downstream = ", ".join(f"`{c}`" for c in self.blast_radius.downstream_components_impacted) if self.blast_radius.downstream_components_impacted else "None"
        lines.append(f"- **Downstream Components Impacted:** {downstream}")
        lines.append(f"- **Breaking Changes:** {self.blast_radius.breaking_changes}")
        lines.append(f"- **Database / Migration Impact:** {self.blast_radius.database_migration_impact}")
        lines.append(f"- **Risk Mitigation Strategy:** {self.blast_radius.risk_mitigation_strategy}\n")

        # Security Guardrails
        lines.append("## 5. Security, Performance & Compliance Guardrails\n")
        sec_reqs = "; ".join(self.security_guardrails.security_requirements) if self.security_guardrails.security_requirements else "Standard enterprise security practices"
        perf_reqs = "; ".join(self.security_guardrails.performance_constraints) if self.security_guardrails.performance_constraints else "Standard SLA targets"
        err_reqs = "; ".join(self.security_guardrails.error_handling_standards) if self.security_guardrails.error_handling_standards else "Standard GlobalExceptionHandler mapping"
        lines.append(f"- **Security Requirements:** {sec_reqs}")
        lines.append(f"- **Performance Constraints:** {perf_reqs}")
        lines.append(f"- **Error Handling Standards:** {err_reqs}\n")

        # Testing Strategy
        lines.append("## 6. Comprehensive Testing Strategy\n")
        lines.append("### Unit Tests\n")
        if self.testing_strategy.unit_tests:
            for ut in self.testing_strategy.unit_tests:
                lines.append(f"- **Target Test File:** `{ut.target_test_file}`")
                lines.append("- **Test Scenarios:**")
                for sc in ut.test_scenarios:
                    lines.append(f"  - [ ] {sc}")
                lines.append("")
        else:
            lines.append("- None specified.\n")

        lines.append("### Integration & API Contract Tests\n")
        if self.testing_strategy.integration_tests:
            for it in self.testing_strategy.integration_tests:
                lines.append(f"- **Target Test File:** `{it.target_test_file}`")
                lines.append("- **BDD Scenario Mapping:**")
                for sc in it.test_scenarios:
                    lines.append(f"  - [ ] {sc}")
                lines.append("")
        else:
            lines.append("- None specified.\n")

        # Open Questions
        lines.append("## 7. Open Questions & Clarifications Needed\n")
        if self.open_questions:
            for idx, q in enumerate(self.open_questions, 1):
                lines.append(f"- [ ] **Q{idx}:** {q}")
        else:
            lines.append("- None at this time.")
        lines.append("")

        # Assumptions
        lines.append("## 8. Agent Assumptions Made\n")
        if self.agent_assumptions:
            for idx, a in enumerate(self.agent_assumptions, 1):
                lines.append(f"- **Assumption {idx}:** {a}")
        else:
            lines.append("- None at this time.")
        lines.append("")

        # Revision Changelog
        lines.append("## 9. Revision Changelog\n")
        changelog = self.revision_changelog or "v1.0: Initial PR creation for tech lead review."
        lines.append(f"- {changelog.strip()}\n")

        # Done When Checklist
        lines.append("## 10. Done When Checklist\n")
        lines.append("- [ ] Implementation plan was generated from target subtask and parent story.")
        lines.append("- [ ] All file additions, modifications, and deletions are explicitly listed with exact relative paths.")
        lines.append("- [ ] Blast radius and security guardrails are fully evaluated in Sections 4 and 5.")
        lines.append("- [ ] Unit and integration test specifications map directly to parent User Story BDD acceptance criteria.")
        lines.append("- [ ] Output conforms strictly to the Markdown template with all [...] placeholders replaced.")
        lines.append(f"- [ ] The plan was saved to `implementation-plans/{self.parent_story_id}/{self.subtask_id}/plan.md` on `SDLC_GOVERNANCE_REPO`.")
        lines.append("- [ ] A GitHub Pull Request was created targeting `main` for human review.")

        return "\n".join(lines)
