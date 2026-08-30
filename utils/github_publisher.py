"""Unified GitHub Service for committing files, managing branches, and creating PRs."""

import os
from typing import Any, List, Optional
from github import Github, GithubException


class GitHubPublisherService:
  """Centralized GitHub operations helper using PyGithub."""

  def __init__(self, github_token: Optional[str] = None, repo_name: str = ""):
    token = github_token or os.getenv("GITHUB_TOKEN", "")
    if not token:
      raise ValueError("GITHUB_TOKEN is required.")
    self.gh = Github(token)
    self.repo = self.gh.get_repo(repo_name)

  def commit_file(
      self,
      file_path: str,
      content: str,
      commit_message: str,
      branch_name: str = "main",
  ) -> str:
    """Creates or updates a file on a specified branch."""
    self.create_branch_if_not_exists(branch_name)
    try:
      existing_file = self.repo.get_contents(file_path, ref=branch_name)
      self.repo.update_file(
          path=file_path,
          message=commit_message,
          content=content,
          sha=existing_file.sha,
          branch=branch_name,
      )
      return "Updated"
    except GithubException as e:
      if e.status == 404:
        self.repo.create_file(
            path=file_path,
            message=commit_message,
            content=content,
            branch=branch_name,
        )
        return "Created"
      raise e

  def create_branch_if_not_exists(
      self, branch_name: str, base_branch: Optional[str] = None
  ) -> str:
    """Creates a new branch from base_branch (or repository default branch) if it doesn't exist."""
    target_base = base_branch or getattr(self.repo, "default_branch", "main")
    try:
      self.repo.get_branch(branch_name)
      return f"Branch '{branch_name}' already exists."
    except GithubException as e:
      if e.status == 404:
        base_ref = self.repo.get_branch(target_base)
        self.repo.create_git_ref(
            ref=f"refs/heads/{branch_name}", sha=base_ref.commit.sha
        )
        return f"Created branch '{branch_name}'."
      raise e

  def create_pull_request(
      self,
      title: str,
      body: str,
      head_branch: str,
      base_branch: Optional[str] = None,
  ) -> Any:
    """Opens a GitHub Pull Request."""
    target_base = base_branch or getattr(self.repo, "default_branch", "main")
    return self.repo.create_pull(
        title=title, body=body, head=head_branch, base=target_base
    )

  def get_open_pr_for_branch(self, head_branch: str) -> Optional[Any]:
    """Checks if an open PR exists for the given head branch."""
    prs = list(
        self.repo.get_pulls(
            state="open", head=f"{self.repo.owner.login}:{head_branch}"
        )
    )
    return prs[0] if prs else None

  def fetch_pr_comments(self, pr: Any) -> List[str]:
    """Ingests review line comments and PR comments left by human reviewers."""
    review_comments = []
    for c in pr.get_review_comments():
      if not c.user.login.endswith("[bot]"):
        loc = f" [{c.path}:{c.line}]" if getattr(c, "path", None) and getattr(c, "line", None) else ""
        review_comments.append(f"{c.user.login}{loc}: {c.body}")

    issue_comments = [
        f"{c.user.login}: {c.body}"
        for c in pr.get_issue_comments()
        if not c.user.login.endswith("[bot]")
    ]
    return review_comments + issue_comments
