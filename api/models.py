"""Pydantic schemas for the Agentic SDLC FastAPI Service."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AstIngestionRequest(BaseModel):
    target_codebase_repo: str = Field(
        default="poojabasker20/springboot-hello-world",
        description="Target GitHub codebase repository to parse",
    )
    codebase_branch: str = Field(
        default="main", description="Target codebase branch to scan"
    )
    sdlc_repo: Optional[str] = Field(
        default=None, description="Governance repository to commit AST map to"
    )
    sdlc_branch: str = Field(
        default="main", description="Target branch in governance repo"
    )
    artifact_path: str = Field(
        default="docs/architecture/AST_CODE_MAP.md",
        description="Path for AST code map artifact",
    )


class AstIngestionResponse(BaseModel):
    status: str
    message: str
    artifact_path: str


class DocIngestionRequest(BaseModel):
    gcs_bucket_name: str = Field(
        description="Google Cloud Storage bucket containing specification PDFs"
    )
    sdlc_repo: Optional[str] = Field(
        default=None, description="Governance repository to commit markdown to"
    )
    target_branch: str = Field(
        default="main", description="Target branch in governance repo"
    )
    output_dir: str = Field(
        default="docs/", description="Directory in GitHub to store parsed markdown files"
    )


class DocIngestionResponse(BaseModel):
    status: str
    results: List[str]


class UserStoryRefineRequest(BaseModel):
    story_id: str = Field(
        default="STORY-101", description="Story identifier (e.g. STORY-101)"
    )
    goal_file: Optional[str] = Field(
        default="goals/GOAL-101.md", description="Path to goal document file"
    )
    pm_goal: Optional[str] = Field(
        default=None, description="Optional raw PM goal text if not using goal_file"
    )
    sdlc_repo: Optional[str] = Field(
        default=None, description="Governance repository for PR operations"
    )
    event_name: str = Field(
        default="workflow_dispatch",
        description="Trigger event ('workflow_dispatch', 'issue_comment', 'pull_request_review_comment', 'pull_request_review')",
    )
    pr_number: Optional[int] = Field(
        default=None, description="PR Number for comment/review revision events"
    )


class UserStoryRefineResponse(BaseModel):
    status: str
    mode: str
    story_id: str
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class SubtaskRefineRequest(BaseModel):
    story_id: str = Field(
        default="STORY-101", description="Story identifier (e.g. STORY-101)"
    )
    story_file: Optional[str] = Field(
        default="user-stories/STORY-101.md",
        description="Path to refined user story markdown file",
    )
    story_content: Optional[str] = Field(
        default=None, description="Optional raw user story markdown content"
    )
    target_codebase_repo: Optional[str] = Field(
        default="poojabasker20/springboot-hello-world",
        description="Target codebase repository name",
    )
    sdlc_repo: Optional[str] = Field(
        default=None, description="Governance repository for subtask PR operations"
    )
    event_name: str = Field(
        default="workflow_dispatch",
        description="Trigger event ('workflow_dispatch' or 'pull_request_review')",
    )
    pr_number: Optional[int] = Field(
        default=None, description="PR Number for comment/review revision events"
    )


class SubtaskRefineResponse(BaseModel):
    status: str
    mode: str
    story_id: str
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    subtasks_count: int = 0
    details: Dict[str, Any] = Field(default_factory=dict)


class ImplementationPlanRequest(BaseModel):
    story_id: str = Field(
        default="STORY-101", description="Parent Story identifier (e.g. STORY-101)"
    )
    subtask_id: str = Field(
        default="SUBTASK-STORY-101-1",
        description="Target Subtask identifier (e.g. SUBTASK-STORY-101-1)",
    )
    subtasks_file: Optional[str] = Field(
        default="tasks/STORY-101/subtasks.md",
        description="Path to subtasks plan markdown file",
    )
    story_file: Optional[str] = Field(
        default="user-stories/STORY-101.md",
        description="Path to parent user story markdown file",
    )
    subtasks_content: Optional[str] = Field(
        default=None, description="Optional raw subtasks plan markdown content"
    )
    story_content: Optional[str] = Field(
        default=None, description="Optional raw user story markdown content"
    )
    target_codebase_repo: Optional[str] = Field(
        default="poojabasker20/springboot-hello-world",
        description="Target codebase repository name",
    )
    sdlc_repo: Optional[str] = Field(
        default=None,
        description="Governance repository for implementation plan PR operations",
    )
    event_name: str = Field(
        default="workflow_dispatch",
        description="Trigger event ('workflow_dispatch' or 'pull_request_review')",
    )
    pr_number: Optional[int] = Field(
        default=None, description="PR Number for comment/review revision events"
    )


class ImplementationPlanResponse(BaseModel):
    status: str
    mode: str
    story_id: str
    subtask_id: str
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    files_count: int = 0
    details: Dict[str, Any] = Field(default_factory=dict)


class PlanVerifierRequest(BaseModel):
    story_id: str = Field(
        default="STORY-101", description="Parent Story ID (e.g. STORY-101)"
    )
    subtask_id: str = Field(
        default="SUBTASK-STORY-101-1",
        description="Target Subtask ID (e.g. SUBTASK-STORY-101-1)",
    )
    plan_file: Optional[str] = Field(
        default=None, description="Optional path to implementation plan markdown file"
    )
    plan_content: Optional[str] = Field(
        default=None, description="Optional raw implementation plan markdown content"
    )
    target_codebase_repo: Optional[str] = Field(
        default="poojabasker20/springboot-hello-world",
        description="Target codebase repository name",
    )
    sdlc_repo: Optional[str] = Field(
        default=None,
        description="Governance repository name",
    )
    pr_number: Optional[int] = Field(
        default=None, description="Optional PR number to post audit comments to"
    )


class PlanVerifierResponse(BaseModel):
    status: str
    verdict: str
    score: int
    subtask_id: str
    findings_count: int = 0
    report_path: str
    details: Dict[str, Any] = Field(default_factory=dict)



