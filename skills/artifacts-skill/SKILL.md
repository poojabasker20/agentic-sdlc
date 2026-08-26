---
name: artifacts-skill
description: Central authority and instructions for SDLC agents on routing workflow output artifacts to external collaboration platforms (GitHub, GitLab) via MCP tools or falling back to local storage inside .agent_artifacts/.
---

# Centralized Artifact Routing Skill (`artifacts-skill`)

This skill serves as the central authority and instruction set for all SDLC workflow agents on how to route, publish, and persist output documents (`user_story.md`, `technical_design.md`, `execution_plan.md`, `review_report.md`).

---

## 1. Overview & Principles

Agents must **never hardcode routing logic** or platform integration details inside their individual domain prompts or agent configurations. Instead, whenever an SDLC agent produces workflow output deliverables or review reports, it must consult and execute this skill to dynamically determine the appropriate delivery destination and protocol.

Before routing any output deliverables, an agent's **mandatory first step** is to read `sdlc-agents-config.json` at the repository root via `view_file` to determine `artifact_tracking_mode` (`"local"`, `"github"`, or `"gitlab"`) and `hitl_mode`.

---

## 2. Central Config Authority & Tool Capability Detection

Before delivering output deliverables, agents must inspect the central configuration and verify available tooling capabilities:

1. **Read Central Configuration (`sdlc-agents-config.json`)**:
   As a mandatory first step, read `sdlc-agents-config.json` at the repository root via `view_file` to determine:
   - `artifact_tracking_mode`:
     - `"github"`: Route deliverables to GitHub Issues or Pull Requests.
     - `"gitlab"`: Route deliverables to GitLab Issues or Merge Requests.
     - `"local"`: Save deliverables to local untracked artifact storage inside `.agent_artifacts/`.
   - `hitl_mode`: Governance level (`"strict"`, `"autonomous"`, or `"exception_only"`).

2. **Inspect Active MCP Tools & Invocation Pattern**:
   If `artifact_tracking_mode` is external (`"github"` or `"gitlab"`), inspect the runtime environment for active Model Context Protocol (MCP) server tools (`issue_write`, `add_issue_comment`, `pull_request_review_write`).
   - **Lazy-Loaded MCP Tools (Primary)**: Subagents must autonomously execute external tools by invoking `call_mcp_tool` with parameters `ServerName='<platform>-mcp-server'` (e.g., `'github-mcp-server'` or `'gitlab-mcp-server'`) and `ToolName='issue_write'` / `'add_issue_comment'` / `'pull_request_review_write'`.
   - **Eager Native Tool Calls (Fallback)**: If registered natively in the agent environment, agents may invoke eager native tool calls directly (`mcp_<platform>-mcp-server_<tool_name>`) as a fallback.

---

## 3. Universal Local Saving & External Issue Tracker Routing Protocol

All SDLC deliverables (`user_story.md`, `technical_design.md`, `execution_plan.md`, `review_report.md`) MUST ALWAYS be saved locally first inside `.agent_artifacts/` using `write_to_file`.

When executing the SDLC Implement Workflow with `artifact_tracking_mode` set to `"github"` or `"gitlab"` and verified MCP tools, agents MUST ALSO upload/sync local artifacts to the remote tracking system using `call_mcp_tool` with `ServerName='<platform>-mcp-server'` (e.g., `'github-mcp-server'` or `'gitlab-mcp-server'`) and `ToolName='issue_write'` / `'add_issue_comment'` (or fallback to eager native tool calls `mcp_<platform>-mcp-server_<tool_name>` if registered):

- **User Story Refiner (`sdlc-user-story-refiner`)**:
  - First, save the User Story locally to `.agent_artifacts/user_story.md`.
  - Second, invoke remote issue creation via `call_mcp_tool` (with parameters `ServerName='<platform>-mcp-server'` and `ToolName='issue_write'`) or eager native tool fallback (`mcp_<platform>-mcp-server_issue_write`) to create a new Issue titled `[Feature] <Story Title>` with the contents of `.agent_artifacts/user_story.md` in the issue body.
  - Extract and return the newly created `issue_number` to downstream agents.

- **Technical Designer (`sdlc-technical-designer`) & Task Planner (`sdlc-task-planner`)**:
  - First, save deliverables locally to `.agent_artifacts/technical_design.md` and `.agent_artifacts/execution_plan.md`.
  - Second, invoke `call_mcp_tool` (with parameters `ServerName='<platform>-mcp-server'` and `ToolName='add_issue_comment'`) or eager native tool fallback (`mcp_<platform>-mcp-server_add_issue_comment`) targeting the established `issue_number` to upload/sync the markdown contents directly as comments on the issue.

---

## 4. External Code Review Routing Protocol (SDLC Review Workflow)

When executing the SDLC Review Workflow with external tracking enabled:

- **Review Agent (`sdlc-review-agent`)**:
  - When reviewing a pull request or merge request, do not write a local disk report by default.
  - Call `pull_request_review_write` to submit the comprehensive review summary, or post targeted line-item PR review comments attached directly to the specific file paths and line numbers.

---

## 5. Issue Closure Lifecycle Governance Gate

To enforce strict lifecycle governance over linked issue tickets:

- Linked issue tickets (`issue_write` state `"closed"`) **MUST NEVER** be closed when a pull request is opened or while review remediation is in progress.
- Linked issues must remain **open** throughout all code authoring, PR creation, and review cycles.
- Tickets may only be closed after the corresponding pull request completes all review cycles and is **successfully merged into `main`**.

---

## 6. Graceful Fallback & Notification Protocol

If an external platform destination (`github`, `gitlab`) is requested but any required MCP tool is missing, unauthenticated, or returns an API failure during invocation, agents must execute graceful fallback:

1. Emit the exact explicit notification banner to the user and orchestrator:
   ```
   [Notification] External platform tool unavailable/failed. Falling back to local artifact storage.
   ```
2. Immediately switch routing strategy to execute **Local Filesystem Routing** (`local`).

---

## 7. Local Filesystem Routing & `.gitignore` Protection

- **Untracked Local Storage (`local` destination or fallback)**:
  - Save output files inside the `.agent_artifacts/` directory with standardized naming (e.g., `.agent_artifacts/<filename>.md`).
  - Verify that `.agent_artifacts/` is listed in the workspace `.gitignore` file so that intermediate or local artifacts are protected from accidental git commits.
  - Utilize helper utilities such as `save_local_artifact` in `skills/tools/artifact_tools.py` when writing local artifact files.
