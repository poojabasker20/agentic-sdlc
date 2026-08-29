"""Stage 1 User Story Refiner Agent runner using Google ADK and GitHub."""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from google.adk.agents import Agent
from schemas.user_story_schema import UserStoryPayload
from tools.ast_traversal_tool import query_codebase_ast
from utils.github_publisher import GitHubPublisherService


class UserStoryRefinerAgent:

  def __init__(
      self,
      github_token: Optional[str] = None,
      repo_name: Optional[str] = None,
  ):
    token = github_token or os.getenv("GITHUB_TOKEN", "")
    sdlc_repo = repo_name or os.getenv("SDLC_GOVERNANCE_REPO", "owner/agentic-sdlc")

    self.publisher = GitHubPublisherService(token, sdlc_repo)

    skill_path = (
        Path(__file__).resolve().parent.parent
        / "skills"
        / "sdlc-user-story-refiner"
        / "SKILL.md"
    )
    if not skill_path.exists():
      skill_path = Path("skills/sdlc-user-story-refiner/SKILL.md")

    with open(skill_path, "r", encoding="utf-8") as f:
      skill_instruction = f.read()

    self.adk_agent = Agent(
        model="gemini-3.7-flash",
        system_instruction=skill_instruction,
        tools=[query_codebase_ast],
        response_schema=UserStoryPayload,
    )

  def run_stage(
      self, story_id: str, pm_goal: str, context_docs: str
  ) -> Dict[str, Any]:
    branch_name = f"feature/story-{story_id.lower()}"
    file_path = f"user-stories/{story_id.upper()}.md"

    existing_pr = self.publisher.get_open_pr_for_branch(branch_name)

    if not existing_pr:
      return self._run_create_mode(
          story_id, pm_goal, context_docs, branch_name, file_path
      )
    else:
      return self._run_revise_mode(
          existing_pr, story_id, pm_goal, context_docs, branch_name, file_path
      )

  def _run_create_mode(
      self,
      story_id: str,
      pm_goal: str,
      context_docs: str,
      branch_name: str,
      file_path: str,
  ) -> Dict[str, Any]:
    self.publisher.create_branch_if_not_exists(branch_name, base_branch="main")

    prompt = f"""
        [CREATE MODE] Generate initial User Story for ID: {story_id}
        
        PM Goal:
        {pm_goal}
        
        Parsed Architecture & Governance Context:
        {context_docs}
        """

    response = self.adk_agent.run(prompt)
    payload: UserStoryPayload = response.structured_output

    commit_msg = f"docs({story_id}): generate initial user story specification"
    self.publisher.commit_file(
        file_path=file_path,
        content=payload.rendered_markdown,
        commit_message=commit_msg,
        branch_name=branch_name,
    )

    pr_body = (
        f"## 🤖 Agentic SDLC - Stage 1: User Story Draft\n\n"
        f"**Story ID:** `{payload.story_id}`\n"
        f"**Title:** {payload.title}\n\n"
        f"### Overview\n"
        f"**As a** {payload.persona}\n"
        f"**I want to** {payload.action}\n"
        f"**So that** {payload.benefit}\n\n"
        f"---\n"
        f"Please review `{file_path}` and leave comments on open questions."
    )

    pr = self.publisher.create_pull_request(
        title=f"docs({story_id}): {payload.title}",
        body=pr_body,
        head_branch=branch_name,
        base_branch="main",
    )

    return {
        "status": "AWAITING_HUMAN_REVIEW",
        "pr_number": pr.number,
        "pr_url": pr.html_url,
        "mode": "CREATE",
    }

  def _run_revise_mode(
      self,
      pr: Any,
      story_id: str,
      pm_goal: str,
      context_docs: str,
      branch_name: str,
      file_path: str,
  ) -> Dict[str, Any]:
    comments = self.publisher.fetch_pr_comments(pr)
    if not comments:
      return {"status": "NO_NEW_COMMENTS", "pr_number": pr.number}

    current_file = self.publisher.repo.get_contents(
        file_path, ref=branch_name
    )
    current_markdown = current_file.decoded_content.decode("utf-8")

    comments_str = "\n".join(f"- {c}" for c in comments)

    prompt = f"""
        [REVISE MODE] Refine existing User Story for ID: {story_id}
        
        PM Goal:
        {pm_goal}
        
        Current Story Markdown:
        {current_markdown}
        
        Human PR Reviewer Comments:
{comments_str}
        
        Architecture & Governance Context:
        {context_docs}
        """

    response = self.adk_agent.run(prompt)
    payload: UserStoryPayload = response.structured_output

    commit_msg = (
        f"docs({story_id}): update user story based on PR review feedback"
    )
    self.publisher.commit_file(
        file_path=file_path,
        content=payload.rendered_markdown,
        commit_message=commit_msg,
        branch_name=branch_name,
    )

    pr.create_issue_comment(
        "🤖 **User Story Updated Based on Feedback**\n\n"
        f"**Revision Summary:**\n{payload.revision_changelog or 'Incorporated requested updates.'}\n\n"
        f"Please review the latest commit on branch `{branch_name}`."
    )

    return {
        "status": "REVISED_AWAITING_REVIEW",
        "pr_number": pr.number,
        "pr_url": pr.html_url,
        "mode": "REVISE",
    }
