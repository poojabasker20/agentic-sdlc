# SDLC End-to-End Workflow

This document defines the standard operating procedure (SOP) for the orchestrator agent to execute the complete Software Development Life Cycle (SDLC) pipeline using specialized subagents.

**To execute this workflow, the user should instruct the orchestrator agent:** 
*"Execute the workflow defined in workflows/SDLC_IMPLEMENT_WORKFLOW.md for the following feature: [Feature Description]"*

## 0. Prerequisite Check & Configuration Loading

Before starting the workflow, the orchestrator agent MUST load the central configuration at the repository root:
1. **Read Configuration**: Use `view_file` to read `sdlc-agents-config.json`.
2. **Extract Governance & Tracking Parameters**: Note `hitl_mode` (`"strict"`, `"autonomous"`, `"exception_only"`) and `artifact_tracking_mode` (`"local"`, `"github"`, `"gitlab"`).
3. **Initialize/Load State Checkpoint**: Initialize or load `.agent_artifacts/SDLC_STATE.md` to track current workflow progress and recovery state.

## 1. Agent Initialization & Prompts

The orchestrator agent executes initial requirements gathering and technical design directly in the primary conversation thread (to enable interactive multi-turn question loops with the user) and registers autonomous subagents for task planning and coding.

1. **Load Instructions**: Use `view_file` to read system prompts and instructions from:
   - `agents/sdlc-user-story-refiner/INSTRUCTION.md` (Adopted directly by the orchestrator in Step 1)
   - `agents/sdlc-technical-designer/INSTRUCTION.md` (Adopted directly by the orchestrator in Step 2)
   - `agents/sdlc-task-planner/INSTRUCTION.md`
   - `agents/sdlc-coding-agent/INSTRUCTION.md`
   - `skills/artifacts-skill/SKILL.md`
   - `workflows/SDLC_REVIEW_WORKFLOW.md` (Adopted in Step 5 for automated verification)
2. **Define Subagents**: Use the `define_subagent` tool to register subagents for autonomous downstream phases:
   - `sdlc-task-planner`: Uses the planner instructions (Set `enable_write_tools=True` so it can save `execution_plan.md` locally and post comments).
   - `sdlc-coding-agent`: Uses the coding agent instructions (`enable_write_tools=True` so it can edit files and run verification tests).
   - `sdlc-review-orchestrator`: Uses `workflows/SDLC_REVIEW_WORKFLOW.md` instructions (`enable_write_tools=True` so it can run clean-room diff verification in Step 5).

## 2. Execution Flow & Data Handoffs

Step transitions are governed by the **HITL Autonomy Pacing (AC9)** protocol based on the `hitl_mode` extracted from `sdlc-agents-config.json`:
- **`strict`**: Require explicit human confirmation (`ask_user`) after Step 1 (User Story), Step 2 (Technical Design), and Step 3 (Task Planning) before advancing to the next step.
- **`autonomous`**: Advance seamlessly from User Story through Task Planning, Coding, and Review without intermediate pauses or manual confirmation steps.
- **`exception_only`**: Run continuously without routine pauses, halting and prompting the user (`ask_user`) only when clarification is needed, verification fails after circuit breaker retries, or high-risk architectural trade-offs arise.

### Step 1: User Story Refinement (Primary Conversation Thread)
- **Action**: Execute User Story Refinement directly in the main orchestrator conversation adopting `agents/sdlc-user-story-refiner/INSTRUCTION.md`.
- **Interactive Refinement**: If requirements are vague or rough, interact directly with the user (asking one choice-based question at a time) to fill identified gaps.
- **Output Artifact & Routing**: Once refined, route outputs according to `skills/artifacts-skill/SKILL.md` (always saving locally to `.agent_artifacts/user_story.md` first, and syncing/creating an issue if external tracking is configured).
- **State Checkpoint**: Read/write phase status and progress to `.agent_artifacts/SDLC_STATE.md` at phase boundaries.
- **Step Transition Governance**: Inspect `hitl_mode`. If `strict`, pause and present the User Story artifact to the user via `ask_user` for explicit confirmation before proceeding.

### Step 2: Technical Design (Primary Conversation Thread)
- **Action**: Execute Technical Design directly in the main orchestrator conversation adopting `agents/sdlc-technical-designer/INSTRUCTION.md`.
- **Interactive Alignment**: Propose architecture trade-offs and clarify technical decisions directly with the user.
- **Output Artifact & Routing**: Route outputs according to `skills/artifacts-skill/SKILL.md` (saving locally to `.agent_artifacts/technical_design.md` first, and commenting on the issue if external tracking is active).
- **State Checkpoint**: Read/write phase status and progress to `.agent_artifacts/SDLC_STATE.md` at phase boundaries.
- **Step Transition Governance**: Inspect `hitl_mode`. If `strict`, pause and present the Technical Design RFC artifact to the user via `ask_user` for explicit confirmation before proceeding to Step 3.

### Step 3: Task Planning
- **Action**: Invoke the `sdlc-task-planner` subagent.
- **Input**: BOTH the User Story (Step 1) and the Technical Design RFC (Step 2), along with the `artifact_tracking_mode` parameter (e.g., `github` or `local`) and created `issue_number` passed from the orchestrator.
- **Goal**: Translate the requirements and technical design into an Execution Plan consisting of manageable, actionable developer tasks with dependency chains.
- **Output Artifact & Routing**: Subagents route outputs according to `skills/artifacts-skill/SKILL.md` (always saving locally inside `.agent_artifacts/execution_plan.md` first, and syncing/commenting on the issue if external tracking is configured).
- **State Checkpoint**: Read/write phase status and progress to `.agent_artifacts/SDLC_STATE.md` at phase boundaries.
- **Step Transition Governance**: Inspect `hitl_mode`. If `strict`, pause and present the Execution Plan artifact to the user via `ask_user` for explicit confirmation before proceeding to Step 4 implementation. If `autonomous` or `exception_only` (and no blocking trade-offs were raised), advance automatically to Step 4.

### Step 4: Fan-Out Task Execution (Implementation Stage)
Once Task Planning completes (and upon user confirmation in `strict` mode), the orchestrator executes the developer tasks from the local Execution Plan (`.agent_artifacts/execution_plan.md`) using `sdlc-coding-agent` in a **fan-out manner**:
- **Dependency Graph Analysis**: Analyze the Comprehensive Task Table from Step 3 to identify independent tasks (`Requires: None` or base branch) versus sequential dependent tasks (`Requires: [Task IDs]`).
- **Parallel Fan-Out**:
  - For tasks that have no unresolved dependencies and can be executed concurrently without file conflicts, invoke multiple instances of `sdlc-coding-agent` simultaneously in a single `invoke_subagent` tool call by providing multiple entries in the `Subagents` array.
  - Set the appropriate `Workspace` mode (`'branch'`, `'share'`, or `'inherit'`) depending on git isolation requirements for each parallel task branch.
  - Pass each subagent its specific task details: Task ID, Title, Technical Description, target files, acceptance criteria, verification commands, and branch configuration.
- **Sequential Synchronization**:
  - As parallel `sdlc-coding-agent` subagents complete their verification loops and report back, verify their success status.
  - When an upstream task completes and merges/commits to its target branch, unblock its dependent downstream tasks and fan them out concurrently.
- **Closed-Loop Verification**:
  - Each `sdlc-coding-agent` strictly applies the 4 Karpathy principles (Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution).
  - If a subagent reports `clarification_needed` or exhausts verification loops, pause and coordinate resolution before advancing downstream stages.
- **State Checkpoint**: Read/write active tasks and phase status to `.agent_artifacts/SDLC_STATE.md` at phase boundaries as tasks start and complete.

### Step 5: Pull Request Creation & Automated Review Pipeline
Once all developer tasks in Step 4 are complete and committed to the feature branch:
1. **Pull Request Creation**: Inspect `artifact_tracking_mode`. If `artifact_tracking_mode` is `"github"` or `"gitlab"`, invoke remote PR creation tools (`create_pull_request`) first to open a pull request against `main`, linking it to the target issue (`Resolves #<issue_number>`). If `artifact_tracking_mode` is `"local"`, skip remote PR creation and proceed directly on local files.
2. **Automated Clean-Room Verification & Review**: Invoke `sdlc-review-orchestrator` (or execute `workflows/SDLC_REVIEW_WORKFLOW.md`). If a pull request was created (`github` or `gitlab`), the review workflow MUST work directly on the existing PR—running clean-room diff inspections across all 4 pillars, adding its own review comments to the PR, and updating the PR if necessary by responding to comments. If `artifact_tracking_mode` is `"local"`, the review workflow runs directly on the local files against `main`.
3. **Remediation & PR Updates**: If any defects or regression issues are found during review verification or reported in PR comments, allow the review workflow to remediate them via `sdlc-coding-agent`, push updated commits to the feature branch, and reply to open comment threads on the PR.
4. **Pull Request Finalization & Closure**: Once the review and remediation cycle completes cleanly with zero remaining issues (`# Review Status: PASSED (Zero Issues)`), close the pull request (or merge into `main`) and enforce the Issue Closure Safeguard (`skills/artifacts-skill/SKILL.md` Section 5).
5. **State Checkpoint**: Read/write review and remediation checkpoint updates in `.agent_artifacts/SDLC_STATE.md` at phase boundaries.

## 3. Finalization
Once all planned tasks in the execution plan have been successfully implemented, submitted as a Pull Request, verified and updated across the review pipeline in Step 5, and closed upon clean completion, summarize the completed work, list modified files, and present the final verified solution to the user. Set status to `COMPLETED` and retain `.agent_artifacts/SDLC_STATE.md` upon clean finalization.
