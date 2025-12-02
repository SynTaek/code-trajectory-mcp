# Code Trajectory MCP Server

[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-blue?style=flat&logo=anthropic)](https://modelcontextprotocol.io)
[![Python Version](https://img.shields.io/badge/python-3.14+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/SynTaek/code-trajectory/graphs/commit-activity)
[![GitHub Stars](https://img.shields.io/github/stars/SynTaek/code-trajectory?style=social)](https://github.com/SynTaek/code-trajectory)

[![README](https://img.shields.io/badge/README-ENGLISH-blue)](README.md)
[![README_KR](https://img.shields.io/badge/README-KOREAN-blue)](README_ko.md)

> **From "State-Based" to "Flow-Based" Coding with LLMs.**

**Code Trajectory MCP** is a Model Context Protocol (MCP) server that empowers Large Language Models (LLMs) to understand the *evolutionary history* of your code, not just its current state. By tracking automated snapshots and analyzing development patterns, it allows LLMs to write code that aligns with your current momentum, intent, and architectural direction.

## 🚀 Why Code Trajectory?

Current LLMs operate like a GPS that knows your current location but not your direction or speed.
  * **Without Trajectory:** "Fix this function." (The LLM might suggest a fix that contradicts the refactoring you did 5 minutes ago).
  * **With Trajectory:** "I see you are migrating from SQL to ORM and handling errors with `try-catch` blocks in the last 3 edits. I will fix this function following that exact pattern."

## ✨ Key Features

  * **⚡ Automated Shadow Snapshots:** A background file watcher (using `watchdog`) automatically creates micro-commits (snapshots) to a **shadow git repository** (`.trajectory`) whenever you save a file. This keeps your main git history clean and isolated.
  * **Context-Aware Retrieval:**
      * **`get_file_trajectory`**: formatting the history of a specific file into a narrative flow (Past -> Present).
      * **`get_global_trajectory`**: Understanding cross-file dependencies and recent project-wide changes (Ripple Effect).
  * **Smart Noise Filtering:** Automatically detects and summarizes "Trial & Error" loops. If you revert a file to a previous state, it is explicitly annotated as `[Revert Detected]`.
  * **Intent Recording:** Allows the LLM (or user) to declare their current intent (e.g., "Refactoring login"), which is attached to subsequent snapshots for better context.
  * **Session Continuity:** Bridges the gap between work sessions by summarizing where you left off.

## 🛠️ Tech Stack

  * **Runtime:** Python 3.14+
  * **Package Manager:** [uv](https://github.com/astral-sh/uv) (Blazing fast Python package installer)
  * **Core Libraries:** `mcp`, `gitpython`, `watchdog`

## 📦 Installation & Setup

### 1. Prerequisites
Ensure you have `uv` installed:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```



### 2. Configuration

Make sure the target project you want to track has `git` initialized.

```bash
cd /path/to/your/project
git init
```

## 🔌 Configuration

### Claude Desktop

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "code-trajectory": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/SynTaek/code-trajectory.git",
        "code-trajectory"
      ]
    }
  }
}
```
> **Important:** You MUST provide the `--path` argument pointing to your project root. If omitted, the server will require an explicit `configure_project` call before functionality is available.


### Gemini (Google AI Studio / Vertex AI)

If you are using an MCP-compatible Gemini interface, use the following command settings:

*   **Command:** `uvx`
*   **Args:** `--from git+https://github.com/SynTaek/code-trajectory.git code-trajectory`

### VSCode & Derivatives (Cursor, Windsurf, etc.)

If you are using the MCP extension in **VSCode**, **Cursor**, **Windsurf**, **Antigravity**, or any other VSCode-based editor, add this to your `.vscode(or your editor's equivalent)/settings.json` or global settings:

```json
"mcp.servers": {
    "code-trajectory": {
        "command": "uvx",
        "args": [
            "--from",
            "git+https://github.com/SynTaek/code-trajectory.git",
            "code-trajectory"
        ]
    }
}
```

## 🤖 Agent Usage Guide

This MCP server is designed to be a "Context Partner" for AI Agents. Here is the recommended workflow for agents:

### 1. Initialization (Configuration)
The server does **not** auto-configure. You MUST call `configure_project` at the start of a session.

1.  **Action:** Call `configure_project(path="/absolute/path/to/project")`.
2.  **Result:** The server initializes the recorder and watcher for that path.

### 2. The "Flow" Loop
As an agent, you should follow this loop to maintain high-quality context:

1.  **Start Task:** When you begin a logical unit of work (e.g., "Implement Login"), call `set_trajectory_intent("Implementing Login")`.
    *   *Why?* This intent is attached to every auto-snapshot until you change it or restart the server. It makes the history readable and semantic.
2.  **Work:** Perform your file edits (write_to_file, etc.).
    *   *Behind the scenes:* The server watches your edits and creates `[AUTO-TRJ]` snapshots in the shadow repo.
3.  **Consolidate:** When the task is complete (or you reach a stable state), call `consolidate("Completed Login Implementation")`.
    *   *Effect:* This squashes all the noisy `[AUTO-TRJ]` snapshots into a single, clean commit with your message.
    *   *Benefit:* It keeps the history clean while preserving the "thought process" during the work phase.
    *   **⚠️ Best Practice:** Only consolidate when you are **DONE** with a feature. If you consolidate while still debugging, you lose the detailed history of what you tried and failed.
    *   **Note:** Consolidation does NOT create a commit in your main project's git history. It only organizes the shadow history.

### 3. Context Retrieval Tools
Use these tools to understand the codebase before making changes:

*   **`get_session_summary()`**: Call this first when entering a session. It tells you what happened recently.
*   **`get_file_trajectory(filepath)`**: Call this before editing a complex file. It shows you *how* the file evolved, not just its current state.
*   **`get_global_trajectory(limit=20, since_consolidate=False)`**: Call this to see if your changes are causing ripple effects in other files. Use `since_consolidate=True` to see all changes since your last consolidation.

## 🗺️ Workflow Example

1.  **Agent:** `set_trajectory_intent("Refactoring auth logic")`
2.  **Agent:** Edits `auth.py` (Save 1) -> *Server creates [AUTO-TRJ] snapshot*
3.  **Agent:** Edits `user.py` (Save 2) -> *Server creates [AUTO-TRJ] snapshot*
4.  **Agent:** `consolidate("Refactored auth logic to use JWT")`
    *   *Server:* Squashes snapshots -> Creates `[CONSOLIDATE] Refactored auth logic to use JWT` commit.

## 📊 Viewing Trajectory History

Since `.trajectory` is a standard Git repository, you can inspect it using your favorite tools to see the detailed "thought process" of your coding session.

### Method A: VSCode (Recommended)
1.  Open a **New Window** in VSCode.
2.  **Open Folder** and select the `.trajectory` folder inside your project.
3.  Use extensions like **Git Graph** to visualize the history tree.

### Method B: Terminal
You can run git commands pointing to the shadow repo without leaving your project root:

```bash
# View log graph
git --git-dir=.trajectory/.git log --graph --oneline --all

# View detailed diffs
git --git-dir=.trajectory/.git log -p
```

### Method C: Git GUI Tools
Open your favorite Git GUI (SourceTree, GitKraken, Fork, etc.) and add the `.trajectory` folder as a local repository.

## 📄 License

MIT