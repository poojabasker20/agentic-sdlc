# SDLC HOTL Workflow — Runtime Agent Operating Rules (AGENTS.md)

Welcome to the **Human-Over-The-Loop (HOTL) SDLC Workflow** runtime operating guide. This document equips external AI coding assistants (such as Antigravity, Claude Code, Cursor, Codex, or generic AI agents) and human engineering leads with the exact runtime operating rules and workflow routing procedures required to operate the framework inside any target repository.

> [!IMPORTANT]
> For setup, workspace overlay installation, and tool-specific configuration templates (e.g., Claude Code, Cursor, Copilot), refer to [INSTALL.md](INSTALL.md). This document (`AGENTS.md`) defines the mandatory **runtime operating rules and workflow routing** for active development sessions.

---

## 1. Framework Directory Discovery

The SDLC HOTL Workflow framework consists of five core components. When inspecting or onboarding a project, recognize the following structure at the repository root:

- `agents/`  
  Contains structured system prompts, persona specifications, and subagent instruction profiles (e.g., `sdlc-coding-agent`, `sdlc-review-agent`).
- `skills/`  
  Contains modular capabilities and specialized toolsets (e.g., `artifacts-skill/`, `tools/`).
- `workflows/`  
  Contains the deterministic end-to-end orchestration pipelines governing implementation (`SDLC_IMPLEMENT_WORKFLOW.md`) and self-healing review loops (`SDLC_REVIEW_WORKFLOW.md`).
- `schemas/`  
  Contains JSON validation schemas ensuring configuration integrity (e.g., `sdlc-agents-config.schema.json`).
- `sdlc-agents-config.json`  
  The runtime configuration file defining project-level parameters such as `hitl_mode` (`"strict"`, `"autonomous"`, or `"exception_only"`) and `artifact_tracking_mode` (`"local"`, `"github"`, or `"gitlab"`).

---

## 2. Operating SOP

To guarantee consistent quality, strict architectural compliance, and human oversight across all repositories adopting this framework, all AI coding assistants **MUST** adhere to the following default operating procedure:

1. **Default Feature Routing**  
   All new feature implementations, enhancements, architectural modifications, and general task executions MUST run via `workflows/SDLC_IMPLEMENT_WORKFLOW.md`.
2. **Default Review Routing**  
   All code reviews, pull request inspections, vulnerability assessments, and quality audits MUST run via `workflows/SDLC_REVIEW_WORKFLOW.md`.
3. **Explicit User Opt-Out**  
   The assistant must strictly enforce these default workflow routes **unless the user explicitly opts out** for a specific task (e.g., by providing an instruction such as *"Quick typo fix, bypass SDLC workflow"* or *"Skip workflow routing for this edit"*).
