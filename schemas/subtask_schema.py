"""Pydantic schema definition for Stage 2: Subtask Generator Agent."""

from typing import List, Optional
from pydantic import BaseModel, Field


class AffectedFile(BaseModel):
    file_path: str = Field(
        description="Path to target source code file (e.g. src/main/java/com/nordea/demo/helloworld/GreetingService.java)"
    )
    action: str = Field(
        default="Modify",
        description="Action to perform: 'New', 'Modify', or 'Delete'",
    )


class SubtaskItem(BaseModel):
    subtask_id: str = Field(
        description="Unique subtask identifier, e.g., SUBTASK-STORY-101-1"
    )
    title: str = Field(
        description="Short, action-oriented subtask title, e.g., Data Models & DTO Definition"
    )
    target_component_layer: str = Field(
        description="Architectural layer (e.g. Domain Models / DTOs, Business Service Layer, REST Controller)"
    )
    estimated_scope: str = Field(
        default="1 PR",
        description="Estimated PR scope, must be '1 PR' or '1-2 PRs'",
    )
    fulfills_criteria: List[str] = Field(
        default_factory=list,
        description="List of User Story Acceptance Criteria fulfilled (e.g. ['AC1', 'AC2'])",
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="List of prerequisite subtask IDs (e.g. ['SUBTASK-STORY-101-1'])",
    )
    affected_files: List[AffectedFile] = Field(
        default_factory=list,
        description="Specific source files created or modified by this subtask",
    )
    overview_of_changes: str = Field(
        description="Concise high-level summary of what will be added or modified in the system without low-level code implementation details",
    )
    verification_goals: List[str] = Field(
        default_factory=list,
        description="High-level verification and testing goals",
    )


class SubtaskPayload(BaseModel):
    story_id: str = Field(description="Parent User Story Identifier, e.g. STORY-101")
    story_title: str = Field(description="Title of the parent user story")
    target_repository: str = Field(
        default="poojabasker20/springboot-hello-world",
        description="Target codebase repository name",
    )
    status: str = Field(
        default="Ready for Implementation", description="Status of the subtask plan"
    )
    estimated_total_prs: str = Field(
        default="2-3 PRs", description="Estimated total PR count across all subtasks"
    )
    overview_architectural_approach: str = Field(
        description="Concise summary of implementation strategy and impacted layers"
    )
    subtasks: List[SubtaskItem] = Field(
        default_factory=list,
        description="List of discrete technical subtasks ordered sequentially by technical dependency",
    )
    execution_dependency_graph: str = Field(
        default="",
        description="ASCII diagram illustrating execution order, e.g. SUBTASK-101-1 ──► SUBTASK-101-2",
    )
    open_questions: List[str] = Field(
        default_factory=list,
        description="High-level functional or scope questions for human reviewers. If none, state 'None at this time.'",
    )
    agent_assumptions: List[str] = Field(
        default_factory=list,
        description="High-level architectural or business scoping assumptions made by the agent",
    )
    revision_changelog: Optional[str] = Field(
        default=None,
        description="Changelog of revisions made in response to PR reviews",
    )

    @property
    def rendered_markdown(self) -> str:
        """Renders the subtask plan into the standard SKILL.md Markdown format."""
        lines = [
            f"# Technical Subtask Decomposition: {self.story_title}\n",
            f"**Story ID:** {self.story_id}  ",
            f"**Target Repository:** `{self.target_repository}`  ",
            f"**Status:** {self.status}  ",
            f"**Estimated Total PRs:** {self.estimated_total_prs}\n",
            "## 1. Overview & Architectural Approach\n",
            f"{self.overview_architectural_approach.strip()}\n",
            "## 2. Technical Subtasks Breakdown\n",
        ]

        for idx, task in enumerate(self.subtasks, 1):
            lines.append(f"### Subtask {idx}: {task.title}\n")
            lines.append(f"- **Subtask ID:** `{task.subtask_id}`")
            lines.append(f"- **Target Component / Layer:** {task.target_component_layer}")
            lines.append(f"- **Estimated Scope:** {task.estimated_scope}")
            
            if task.fulfills_criteria:
                lines.append(f"- **Fulfills User Story Criteria:** {', '.join(task.fulfills_criteria)}")
            
            if task.dependencies:
                lines.append(f"- **Dependencies:** {', '.join(f'`{d}`' for d in task.dependencies)}")
            
            if task.affected_files:
                lines.append("- **Affected / Target Files:**")
                for af in task.affected_files:
                    lines.append(f"  - `{af.file_path}` ({af.action})")
            
            lines.append(f"- **Overview of Changes:** {task.overview_of_changes.strip()}")
            
            if task.verification_goals:
                lines.append("- **Verification & Testing Goals:**")
                for goal in task.verification_goals:
                    lines.append(f"  - [ ] {goal}")
            
            lines.append("\n---\n")

        # Dependency Graph
        lines.append("## 3. Execution Dependency Graph\n")
        graph_text = self.execution_dependency_graph.strip()
        if not graph_text and self.subtasks:
            graph_text = " ──► ".join(f"`{t.subtask_id}`" for t in self.subtasks)
        lines.append(f"```text\n{graph_text}\n```\n")

        # Open Questions
        lines.append("## 4. Open Questions & Clarifications Needed\n")
        if self.open_questions:
            for idx, q in enumerate(self.open_questions, 1):
                lines.append(f"- [ ] **Q{idx}:** {q}")
        else:
            lines.append("- None at this time.")
        lines.append("")

        # Assumptions
        lines.append("## 5. Agent Assumptions Made\n")
        if self.agent_assumptions:
            for idx, a in enumerate(self.agent_assumptions, 1):
                lines.append(f"- **Assumption {idx}:** {a}")
        else:
            lines.append("- None at this time.")
        lines.append("")

        # Revision Changelog
        lines.append("## 6. Revision Changelog\n")
        changelog = self.revision_changelog or "v1.0: Initial PR creation for tech lead review."
        lines.append(f"- {changelog.strip()}\n")

        # Done When Checklist
        lines.append("## 7. Done When Checklist\n")
        lines.append("- [ ] Subtask plan was generated from refined User Story (`user-stories/<story_id>.md`) and grounded in AST context (`docs/architecture/AST_CODE_MAP.md`).")
        lines.append("- [ ] Every subtask is bounded to 1–2 PRs in scope with explicit file paths and verification goals.")
        lines.append("- [ ] Dependencies between subtasks are mapped sequentially in Section 3.")
        lines.append("- [ ] Output conforms strictly to the Markdown template with all [...] placeholders replaced.")
        lines.append("- [ ] The subtask plan was saved to `tasks/<story_id>/subtasks.md` on `agentic-sdlc`.")
        lines.append("- [ ] A GitHub Pull Request was created (CREATE mode) or updated with a revision commit and comment (REVISE mode) on `agentic-sdlc`.")

        return "\n".join(lines)
