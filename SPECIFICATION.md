# Functional Specification: Code Trajectory MCP System

## 1. System Overview
The **Code Trajectory MCP System** acts as a bridge between a developer's local development environment and an LLM. It captures high-resolution temporal data (code edits) and processes this data into semantic context (intent/trajectory) for the LLM.

## 2. Architecture Components

### 2.1. The Watcher (Background Service)
* **Role:** Monitors the file system for changes.
* **Behavior:**
    * **Auto-Start:** Starts automatically when `configure_project` is called.
    * Triggers on `FileModified` events.
    * **Debouncing:** Implements a debounce mechanism (e.g., 2.0 seconds) to prevent spamming snapshots during rapid typing/saving.
    * **Scope:** Respects `.gitignore` rules to avoid tracking build artifacts or sensitive environment files.
    * **Dynamic Config:** Can be re-configured to watch a different path at runtime via `configure_project` or `checkpoint`.

### 2.2. The Recorder (Git Storage Layer)
* **Role:** Persists the state of the code.
* **Mechanism:** Uses a shadow git repository located in `.trajectory` within the project root.
* **Isolation:** The main project's `.git` repository is NOT used. The `.trajectory` folder is automatically added to `.gitignore`.
* **Commit Strategy:**
    * Creates commits with a specific prefix: `[AUTO-TRJ]`.
    * Includes a timestamp and a brief diff summary in the message if possible.
    * **Intent Awareness:** If an intent is set via `set_trajectory_intent`, it is appended to the commit message (e.g., `[AUTO-TRJ] 12:00:00 - Refactoring - Snapshot...`).
    * **Constraint:** Must handle `git.lock` contentions gracefully.

### 2.3. The Provider (MCP Server Layer)
* **Role:** Exposes tools to the LLM Client (e.g., Claude).
* **Data Processing:** Converts raw `git diff` outputs into a structured, narrative format optimized for LLM token limits and reasoning.

## 3. Detailed Functional Requirements

### 3.1. Tool: `get_file_trajectory`
**Goal:** Provide the evolutionary context of a single file.

* **Input:**
    * `filepath` (string, required): Relative path to the file.
    * `depth` (integer, optional, default=5): Number of recent snapshots to retrieve.
* **Processing:**
    * Retrieve the last `N` commits affecting the file.
    * Sort chronologically (Oldest → Newest).
    * **Revert Detection:** Calculates content hashes for each snapshot. If a file's content matches a previous state in the history, it appends `**[Revert Detected]** (Matches state from <timestamp>)` to the message.
* **Output:** Markdown formatted string containing timestamps, commit messages, and semantic diffs.

### 3.2. Tool: `get_global_trajectory`

*   **Purpose:** Retrieve the recent history of the entire project to understand broader context and detect ripple effects.
*   **Input:**
    *   `limit` (int, default=20): Maximum number of commits to retrieve.
    *   `since_consolidate` (bool, default=False): If True, retrieves all commits since the last `[CONSOLIDATE]` commit.
*   **Processing:**
    *   Iterate through the git log of the shadow repo.
    *   If `since_consolidate` is True, stop when a commit message starting with `[CONSOLIDATE]` is found.
    *   Otherwise, stop after `limit` commits.
    *   Format the output as a chronological list of changes (Timestamp, Message, Files Changed).
*   **Output:** Markdown-formatted summary of global activity.

### 3.3. Tool: `get_session_summary`
**Goal:** Handle context switching.

* **Logic:**
    * Identify the "gap" in commit times. If the last commit was > 1 hour ago, treat the current interaction as a "New Session".
    * Provide a summary of the *last* session's final state and intent.

    * **Constraint:** Requires server to be configured via `configure_project`.

### 3.4. Tool: `consolidate`

*   **Purpose:** Squash recent `[AUTO-TRJ]` snapshots into a single, meaningful commit to clean up history.
*   **Input:**
    *   `intent` (string): A summary of the work accomplished (e.g., "Implemented Login Feature").
*   **Processing:**
    *   Identify the sequence of recent `[AUTO-TRJ]` commits.
    *   Perform a soft reset to the commit before the first `[AUTO-TRJ]` in the sequence.
    *   Create a new commit with the message `[CONSOLIDATE] {Timestamp} - {Intent}`.
    *   **IMPORTANT:** This operation is performed ONLY on the shadow repository. It does not affect the main project's git history.
*   **Output:** Success message indicating the number of snapshots squashed.
*   **Goal:** Maintain repository hygiene and consolidate work.

### 3.5. Tool: `set_trajectory_intent`
**Goal:** Capture the "Why" behind the changes.

* **Input:**
    * `intent` (string, required): A short description of the current task (e.g., "Fixing bug #123").
* **Processing:**
    * Stores the intent in memory.
    * **Persistence:** The intent persists until it is explicitly changed by another `set_trajectory_intent` call or the server is restarted.
* **Effect:** Subsequent snapshots will include this intent in their commit messages.

### 3.6. Tool: `configure_project`
**Goal:** Set the target project path dynamically.

* **Input:**
    * `path` (string, required): Absolute path to the project to track.
* **Processing:**
    * Stops any existing Watcher.
    * Initializes new Recorder and Watcher for the given path.
    * **Optimization:** If already watching the target path, skips re-initialization to maintain continuity.
* **Effect:** Starts tracking the new project.

## 4. Edge Case Handling

| Scenario | System Behavior |
| :--- | :--- |
| **Rapid Saving (Ctrl+S spam)** | The Debounce logic in the Watcher ensures only the final state after the delay is committed. |
| **Compilation Error / Broken Code** | The system snapshots *everything*, even broken code. This is intentional, as the LLM needs to see "what broke" to fix it. |
| **Branch Switching** | If the user switches branches externally, the Watcher must detect the new HEAD and continue tracking on the new branch without error. |
| **Large Files** | Logic to truncate huge Diffs in the `get_trajectory` output to prevent exceeding LLM context windows. |

## 5. Future Roadmap
* **Test Status Integration:** Capture the output of a test runner (Pass/Fail) and append it to the trajectory metadata.
* **Shadow Branch Strategy:** Instead of committing to the active branch, maintain a parallel `refs/heads/shadow/branch-name` to keep the user's history completely clean until explicit save.