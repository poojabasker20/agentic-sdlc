"""Agentic SDLC FastAPI Service exposing AST, Doc Ingestion, and User Story Refiner Agent."""

import glob
import logging
import os
import re
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from agents.user_story_agent import UserStoryRefinerAgent
from api.models import (
    AstIngestionRequest,
    AstIngestionResponse,
    DocIngestionRequest,
    DocIngestionResponse,
    UserStoryRefineRequest,
    UserStoryRefineResponse,
)
from utils.code_parser import ASTMapPublisher
from utils.doc_parser import PdfParserService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agentic-sdlc-api")

app = FastAPI(
    title="Agentic SDLC Service API",
    description="REST API service for AST Code Parsing, Multimodal Document Ingestion, and Stage 1 User Story Refinement Agent.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

        # Aggregate context docs from docs/ directory
        doc_sections = []
        for md_file in sorted(glob.glob("docs/**/*.md", recursive=True)):
            if "AST_CODE_MAP" not in md_file:
                with open(md_file, "r", encoding="utf-8") as f:
                    doc_sections.append(f.read().strip())
        context_docs = (
            "\n\n---\n\n".join(doc_sections)
            if doc_sections
            else "Spring Boot 3.x REST API conventions."
        )

        # Determine mode and execute
        is_comment_event = req.event_name in [
            "issue_comment",
            "pull_request_review_comment",
            "pull_request_review",
        ]

        if is_comment_event and req.pr_number:
            pr = agent.publisher.repo.get_pull(req.pr_number)
            match = re.search(r"story-([a-zA-Z0-9\-]+)", pr.head.ref, re.I)
            story_id = f"STORY-{match.group(1).upper()}" if match else f"PR-{pr.number}"
            pm_goal = req.pm_goal or f"Refine user story based on reviewer feedback on PR #{pr.number}"

            result = agent.run_stage(story_id=story_id, pm_goal=pm_goal, context_docs=context_docs)
            return UserStoryRefineResponse(
                status=result.get("status", "SUCCESS"),
                mode="REVISE",
                story_id=story_id,
                pr_number=result.get("pr_number"),
                pr_url=result.get("pr_url"),
                details=result,
            )
        else:
            # CREATE mode
            story_id = req.story_id
            if req.pm_goal:
                pm_goal = req.pm_goal
            elif req.goal_file and os.path.exists(req.goal_file):
                with open(req.goal_file, "r", encoding="utf-8") as f:
                    pm_goal = f.read()
            else:
                pm_goal = f"Feature specification for {story_id}"

            result = agent.run_stage(story_id=story_id, pm_goal=pm_goal, context_docs=context_docs)
            return UserStoryRefineResponse(
                status=result.get("status", "SUCCESS"),
                mode="CREATE",
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
