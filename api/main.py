"""Agentic SDLC FastAPI Service exposing AST Ingestion, Doc Ingestion, User Story Refiner, and Subtask Generator Agents."""

import glob
import logging
import os
import re
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from agents.implementation_plan_agent import ImplementationPlanGeneratorAgent
from agents.subtask_agent import SubtaskGeneratorAgent
from agents.user_story_agent import UserStoryRefinerAgent
from api.models import (
    AstIngestionRequest,
    AstIngestionResponse,
    DocIngestionRequest,
    DocIngestionResponse,
    ImplementationPlanRequest,
    ImplementationPlanResponse,
    SubtaskRefineRequest,
    SubtaskRefineResponse,
    UserStoryRefineRequest,
    UserStoryRefineResponse,
)
from utils.code_parser import ASTMapPublisher
from utils.doc_parser import PdfParserService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agentic-sdlc-api")

app = FastAPI(
    title="Agentic SDLC Service API",
    description="REST API service for AST Code Parsing, Multimodal Document Ingestion, Stage 1 User Story Refinement, and Stage 2 Subtask Generation.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_governance_context_docs() -> str:
    """Aggregates all markdown documents from docs/ directory, excluding AST code maps."""
    doc_sections = []
    for md_file in sorted(glob.glob("docs/**/*.md", recursive=True)):
        if "AST_CODE_MAP" not in md_file:
            with open(md_file, "r", encoding="utf-8") as f:
                doc_sections.append(f.read().strip())
    return (
        "\n\n---\n\n".join(doc_sections)
        if doc_sections
        else "Spring Boot 3.x REST API conventions."
    )


def extract_story_id_from_branch(branch_name: str, fallback_pr_number: int) -> str:
    """Extracts normalized STORY-XXX identifier from a git branch name or fallback PR number."""
    match = re.search(r"(?:story|subtasks)-([a-zA-Z0-9\-]+)", branch_name, re.I)
    if match:
        clean_id = re.sub(r"^story-?", "", match.group(1), flags=re.I).strip()
        return f"STORY-{clean_id.upper()}" if clean_id else f"PR-{fallback_pr_number}"
    return f"PR-{fallback_pr_number}"


def load_content(
    file_path: Optional[str] = None,
    raw_content: Optional[str] = None,
    fallback_default: str = "",
) -> str:
    """Resolves content from raw string or file path, with a default fallback."""
    if raw_content:
        return raw_content
    if file_path and os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return fallback_default


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "agentic-sdlc-api", "version": "1.0.0"}


@app.post(
    "/api/v1/ingest/ast",
    response_model=AstIngestionResponse,
    tags=["Ingestion"],
    summary="Generate & Commit Codebase AST Map",
)
def ingest_codebase_ast(req: AstIngestionRequest):
    """Parses AST from the target codebase and publishes AST_CODE_MAP.md to the SDLC governance repository."""
    token = os.getenv("GITHUB_TOKEN", "")
    sdlc_repo = req.sdlc_repo or os.getenv("SDLC_GOVERNANCE_REPO", "owner/agentic-sdlc")

    try:
        publisher = ASTMapPublisher(
            github_token=token,
            source_code_repo=req.target_codebase_repo,
            target_sdlc_repo=sdlc_repo,
        )
        result = publisher.generate_and_commit_ast_map(
            source_branch=req.codebase_branch,
            target_branch=req.sdlc_branch,
            artifact_path=req.artifact_path,
        )
        return AstIngestionResponse(
            status="SUCCESS",
            message=result,
            artifact_path=req.artifact_path,
        )
    except Exception as e:
        logger.error("AST Ingestion failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AST Ingestion failed: {str(e)}",
        )


@app.post(
    "/api/v1/ingest/docs",
    response_model=DocIngestionResponse,
    tags=["Ingestion"],
    summary="Parse & Publish Multimodal PDF Specifications from GCS",
)
def ingest_documents(req: DocIngestionRequest):
    """Scans all PDF files in the GCS bucket, extracts tables and diagram descriptions with Gemini Vision, and commits to docs/."""
    token = os.getenv("GITHUB_TOKEN", "")
    sdlc_repo = req.sdlc_repo or os.getenv("SDLC_GOVERNANCE_REPO", "owner/agentic-sdlc")

    try:
        service = PdfParserService(
            gcs_bucket_name=req.gcs_bucket_name,
            github_token=token,
            github_repo_name=sdlc_repo,
        )
        results = service.process_and_publish_all_bucket_documents(
            target_github_branch=req.target_branch,
            github_output_dir=req.output_dir,
        )
        return DocIngestionResponse(status="SUCCESS", results=results)
    except Exception as e:
        logger.error("Document Ingestion failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document Ingestion failed: {str(e)}",
        )


@app.post(
    "/api/v1/agent/user-story",
    response_model=UserStoryRefineResponse,
    tags=["Agents"],
    summary="Execute Stage 1 User Story Refiner Agent",
)
def refine_user_story(req: UserStoryRefineRequest):
    """Executes the User Story Refiner Agent in CREATE mode (opening a new PR) or REVISE mode (updating based on review comments)."""
    token = os.getenv("GITHUB_TOKEN", "")
    sdlc_repo = req.sdlc_repo or os.getenv("SDLC_GOVERNANCE_REPO", "owner/agentic-sdlc")

    try:
        agent = UserStoryRefinerAgent(github_token=token, repo_name=sdlc_repo)
        context_docs = load_governance_context_docs()

        # REVISE Mode (Triggered by review comments on an open PR)
        if req.pr_number:
            pr = agent.publisher.repo.get_pull(req.pr_number)
            story_id = extract_story_id_from_branch(pr.head.ref, req.pr_number)
            pm_goal = req.pm_goal or f"Refine user story based on reviewer feedback on PR #{req.pr_number}"
            mode = "REVISE"
        # CREATE Mode (Initial story draft generation)
        else:
            story_id = req.story_id
            pm_goal = load_content(
                file_path=req.goal_file,
                raw_content=req.pm_goal,
                fallback_default=f"Feature specification for {story_id}",
            )
            mode = "CREATE"

        result = agent.run_stage(story_id=story_id, pm_goal=pm_goal, context_docs=context_docs)
        return UserStoryRefineResponse(
            status=result.get("status", "SUCCESS"),
            mode=mode,
            story_id=story_id,
            pr_number=result.get("pr_number"),
            pr_url=result.get("pr_url"),
            details=result,
        )
    except Exception as e:
        logger.error("User Story refinement failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User Story Agent execution failed: {str(e)}",
        )


@app.post(
    "/api/v1/agent/subtasks",
    response_model=SubtaskRefineResponse,
    tags=["Agents"],
    summary="Execute Stage 2 Subtask Generator Agent",
)
def generate_subtasks(req: SubtaskRefineRequest):
    """Executes the Subtask Generator Agent in CREATE mode (opening a new subtasks PR) or REVISE mode (updating based on review comments)."""
    token = os.getenv("GITHUB_TOKEN", "")
    sdlc_repo = req.sdlc_repo or os.getenv("SDLC_GOVERNANCE_REPO", "owner/agentic-sdlc")
    target_codebase = req.target_codebase_repo or os.getenv("TARGET_CODEBASE_REPO", "poojabasker20/springboot-hello-world")

    try:
        agent = SubtaskGeneratorAgent(
            github_token=token,
            repo_name=sdlc_repo,
            target_codebase_repo=target_codebase,
        )
        context_docs = load_governance_context_docs()

        # REVISE Mode (Triggered by review comments on an open subtasks PR)
        if req.pr_number:
            pr = agent.publisher.repo.get_pull(req.pr_number)
            story_id = extract_story_id_from_branch(pr.head.ref, req.pr_number)
            story_content = load_content(
                file_path=f"user-stories/{story_id}.md",
                raw_content=req.story_content,
                fallback_default="",
            )
            mode = "REVISE"
        # CREATE Mode (Initial subtasks decomposition)
        else:
            clean_id = re.sub(r"^story-?", "", req.story_id, flags=re.I).strip()
            story_id = f"STORY-{clean_id.upper()}" if clean_id else req.story_id.upper()
            target_story_file = req.story_file or f"user-stories/{story_id}.md"
            story_content = load_content(
                file_path=target_story_file,
                raw_content=req.story_content,
                fallback_default="",
            )
            mode = "CREATE"

        if not story_content or not story_content.strip():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"User story specification for '{story_id}' was not found in 'user-stories/'. "
                    f"Please run Stage 1 (User Story Refiner Agent) first to generate and approve 'user-stories/{story_id}.md'."
                ),
            )

        result = agent.run_stage(story_id=story_id, story_content=story_content, context_docs=context_docs)
        return SubtaskRefineResponse(
            status=result.get("status", "SUCCESS"),
            mode=mode,
            story_id=story_id,
            pr_number=result.get("pr_number"),
            pr_url=result.get("pr_url"),
            subtasks_count=result.get("subtasks_count", 0),
            details=result,
        )
    except Exception as e:
        logger.error("Subtask generation failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Subtask Agent execution failed: {str(e)}",
        )


@app.post(
    "/api/v1/agent/implementation-plan",
    response_model=ImplementationPlanResponse,
    tags=["Agents"],
    summary="Execute Stage 3 Implementation Plan Generator Agent",
)
def generate_implementation_plan(req: ImplementationPlanRequest):
    """Executes the Implementation Plan Generator Agent in CREATE mode (opening a new plan PR) or REVISE mode (updating based on reviewer feedback)."""
    token = os.getenv("GITHUB_TOKEN", "")
    sdlc_repo = req.sdlc_repo or os.getenv("SDLC_GOVERNANCE_REPO", "owner/agentic-sdlc")
    target_codebase = req.target_codebase_repo or os.getenv("TARGET_CODEBASE_REPO", "poojabasker20/springboot-hello-world")

    try:
        agent = ImplementationPlanGeneratorAgent(
            github_token=token,
            repo_name=sdlc_repo,
            target_codebase_repo=target_codebase,
        )
        context_docs = load_governance_context_docs()

        # REVISE Mode (Triggered by reviewer comments on an open plan PR)
        if req.pr_number:
            pr = agent.publisher.repo.get_pull(req.pr_number)
            story_id = extract_story_id_from_branch(pr.head.ref, req.pr_number)

            subtasks_content = load_content(
                file_path=f"tasks/{story_id}/subtasks.md",
                raw_content=req.subtasks_content,
                fallback_default="",
            )
            story_content = load_content(
                file_path=f"user-stories/{story_id}.md",
                raw_content=req.story_content,
                fallback_default="",
            )
            mode = "REVISE"
        # CREATE Mode (Initial blueprint generation for all subtasks)
        else:
            clean_story_id = re.sub(r"^story-?", "", req.story_id, flags=re.I).strip()
            story_id = f"STORY-{clean_story_id.upper()}" if clean_story_id else req.story_id.upper()

            subtasks_file = req.subtasks_file or f"tasks/{story_id}/subtasks.md"
            story_file = req.story_file or f"user-stories/{story_id}.md"

            subtasks_content = load_content(
                file_path=subtasks_file,
                raw_content=req.subtasks_content,
                fallback_default="",
            )
            story_content = load_content(
                file_path=story_file,
                raw_content=req.story_content,
                fallback_default="",
            )
            mode = "CREATE"

        if not story_content or not story_content.strip():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Parent user story specification for '{story_id}' was not found in 'user-stories/'. "
                    f"Please run Stage 1 (User Story Refiner Agent) first."
                ),
            )

        if not subtasks_content or not subtasks_content.strip():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Subtask plan for '{story_id}' was not found in 'tasks/{story_id}/subtasks.md'. "
                    f"Please run Stage 2 (Subtask Generator Agent) first."
                ),
            )

        result = agent.run_stage(
            story_id=story_id,
            subtasks_content=subtasks_content,
            story_content=story_content,
            context_docs=context_docs,
        )
        return ImplementationPlanResponse(
            status=result.get("status", "SUCCESS"),
            mode=mode,
            story_id=story_id,
            pr_number=result.get("pr_number"),
            pr_url=result.get("pr_url"),
            subtasks_count=result.get("subtasks_count", 0),
            total_files=result.get("total_files", 0),
            details=result,
        )
    except Exception as e:
        logger.error("Implementation Plan generation failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Implementation Plan Agent execution failed: {str(e)}",
        )
