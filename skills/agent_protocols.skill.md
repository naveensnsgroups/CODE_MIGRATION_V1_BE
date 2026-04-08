---
name: agent-industrial-protocols
description: "Rules of Engagement for AI coding agents. Enforces Research-First auditing, Execution Safety Gates, and mandatory Verification Loops."
category: meta
metadata:
  triggers: [all-missions, code-refactor, project-setup, surgical-extraction]
---

# Industrial Agent Protocols (v21.0)

Professional behavioral layer for AI-driven modernization missions.

##  Doctrine 1: Research-First (Auditing)
- **Rule**: You MUST execute `list_dir` and `view_file` on all related components BEFORE proposing or implementing an edit.
- **Rule**: Audit existing design patterns (e.g., `AnalysisClient.ts`, `CommonElements.tsx`) to ensure any new code follows established industrial conventions.
- **Rule**: Identify all dependencies and type signatures before modifying function calls.

##  Doctrine 2: Execution Safety Gates
- **Rule**: Perform surgical, atomic edits (one feature/fix per turn).
- **Rule**: You MUST create a localized backup code snippet or copy for any destructive `del` or massive refactor mission.
- **Rule**: Never use `multi_replace_file_content` for more than 2 files in a single turn to prevent context drift.

##  Doctrine 3: Verification Mastery
- **Rule**: Every code change MUST be followed by a **Verification Loop**:
    - **Frontend**: `npm run build` or `npm run dev` (if applicable).
    - **Backend**: `uv run uvicorn` or `uv run pytest`.
- **Rule**: Final mission check: "Is the fix live and verified via terminal output or browser test?" No "ghost closures."

##  Doctrine 4: Communication Excellence
- **Rule**: Use high-fidelity **GitHub Alerts** (`[!IMPORTANT]`, `[!TIP]`) in all plans and artifacts to highlight critical context.
- **Rule**: Maintain technical depth with industrial conciseness. Remove fluff; focus on ground-truth facts.
- **Rule**: Present all work via high-fidelity **Walkthrough** artifacts including diffs and verification logs.
