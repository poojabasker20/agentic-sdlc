# SDLC HOTL Workflow — Universal Agent Installation & Configuration Guide

Welcome to the **Human-Over-The-Loop (HOTL) SDLC Workflow** universal installation and configuration guide. This document equips developers and AI coding assistants with the exact setup commands, discovery mechanisms, and configuration templates required to integrate this framework into any target repository.

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

## 2. Universal Workspace Overlay

To adopt the SDLC HOTL Workflow into an existing target workspace, execute the following shell commands from the root directory of your target repository. These commands clone the framework and overlay all necessary directories directly into your workspace while preserving directory structure:

```bash
git clone https://github.com/Swington/sdlc-hotl-workflow.git
cp -r sdlc-hotl-workflow/agents sdlc-hotl-workflow/skills sdlc-hotl-workflow/workflows sdlc-hotl-workflow/schemas sdlc-hotl-workflow/sdlc-agents-config.json sdlc-hotl-workflow/AGENTS.md ./
mkdir -p .agents/skills && cp -r sdlc-hotl-workflow/skills/* .agents/skills/
rm -rf sdlc-hotl-workflow
```

> [!NOTE]
> Copying skills into `.agents/skills/` ensures immediate auto-discovery for agents like Antigravity and Gemini CLI.

---

## 3. Tool-Specific Configuration & Adaptation

To ensure your AI coding assistant correctly discovers framework workflows, enforces `hitl_mode` confirmation gates, and adheres to operational routing rules, apply the appropriate configuration template below.

### Antigravity / Gemini CLI
- **Skill Discovery**: Antigravity and Gemini CLI automatically discover skills populated inside `.agents/skills/`.
- **Operational Routing**: Maintain the root `AGENTS.md` file (or link to it inside `GEMINI.md`) so the agent understands mandatory workflow routing (`SDLC_IMPLEMENT_WORKFLOW.md` and `SDLC_REVIEW_WORKFLOW.md`) and configuration loading rules.

### Claude Code (`CLAUDE.md`)
Place the following exact snippet inside your root-level `CLAUDE.md` file:

```markdown
# SDLC HOTL Workflow Governance
Please review and strictly adhere to the operational rules and routing procedures defined in @AGENTS.md.
Before initiating tasks, inspect `sdlc-agents-config.json` for `hitl_mode` and `artifact_tracking_mode`.
All feature implementations MUST run via `workflows/SDLC_IMPLEMENT_WORKFLOW.md` and reviews via `workflows/SDLC_REVIEW_WORKFLOW.md`.
```

### Cursor (`.cursorrules`)
Place the following exact snippet inside your repository root `.cursorrules` file:

```markdown
# SDLC HOTL Workflow Governance
Please review and strictly adhere to the operational rules and routing procedures defined in `AGENTS.md`.
Before initiating tasks or modifying codebase files, inspect `sdlc-agents-config.json` and check `hitl_mode` (`strict`, `autonomous`, or `exception_only`) to respect human confirmation gates.
All feature implementations MUST run via `workflows/SDLC_IMPLEMENT_WORKFLOW.md` and reviews via `workflows/SDLC_REVIEW_WORKFLOW.md`.
```

### GitHub Copilot (`.github/copilot-instructions.md`)
To adapt `AGENTS.md` for GitHub Copilot Workspace and coding agents, link or copy `AGENTS.md` into `.github/copilot-instructions.md` by running:

```bash
mkdir -p .github && ln -s ../AGENTS.md .github/copilot-instructions.md
```

### Generic AI CLI Harnesses
For custom agent frameworks, scripted harnesses, or generic AI tools:
- **Initialization**: Ensure your startup initialization routine reads `sdlc-agents-config.json` at launch to configure runtime governance (`hitl_mode`, `artifact_tracking_mode`).
- **Workflow Binding**: Bind feature task execution loops directly to `workflows/SDLC_IMPLEMENT_WORKFLOW.md` and review execution loops directly to `workflows/SDLC_REVIEW_WORKFLOW.md`.
