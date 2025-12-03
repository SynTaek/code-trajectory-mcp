# Agent Guide: Code Trajectory MCP

This document provides detailed scenarios and system prompt rules to effectively use the Code Trajectory MCP server.

## 🎭 Usage Scenarios

### Scenario 1: The "Cold Start" (Resuming Work)
**Context:** You are starting a new session and don't know the current state of the project.
1.  **Action:** Call `get_session_summary()`.
2.  **Insight:** You see that the last session ended with "Implemented basic JWT auth" but the file `auth.py` was left in a broken state.
3.  **Action:** Call `get_file_trajectory("src/auth.py")` to see the last few edits and understand *how* it broke.
4.  **Result:** You fix the code based on the trajectory, rather than guessing.

### Scenario 2: The "Trial & Error" Debugging
**Context:** You are trying to fix a stubborn bug.
1.  **Action:** `set_trajectory_intent("Attempting Fix #1: Changing timeout")`.
2.  **Action:** Edit `network.py`. (Test fails).
3.  **Action:** Revert changes to `network.py`.
4.  **Action:** `set_trajectory_intent("Attempting Fix #2: Increasing buffer size")`.
5.  **Action:** Edit `network.py`. (Test passes).
6.  **Review:** You call `get_file_trajectory("network.py")`.
7.  **Insight:** You see the revert explicitly marked as `[Revert Detected]`. You know Fix #1 failed and Fix #2 worked.
8.  **Action:** `consolidate("Fixed network bug via buffer size increase")`.

### Scenario 3: The "Ripple Effect" Check
**Context:** You modified a core utility function in `utils.py`.
1.  **Action:** You finish editing `utils.py`.
2.  **Action:** Call `get_global_trajectory(limit=10)` or `get_global_trajectory(since_consolidate=True)`.
3.  **Insight:** You see that `user_service.py` and `product_service.py` were modified *before* your change, but haven't been touched since.
4.  **Reasoning:** "I might have broken those services with my change to `utils.py`."
5.  **Action:** You check those files and run tests.

### Scenario 4: The "Clean Handover"
**Context:** You finished a complex feature and want to save your work.
1.  **Action:** You have made 15 small edits (typos, logic tweaks).
2.  **Action:** Call `consolidate("Implemented User Profile Page")`.
3.  **Result:** The 15 messy snapshots are squashed into one clean commit. The next agent (or user) sees a clean history.

---

## 🤖 System Prompt Rules (Enforced Workflow)

Add the following rules to your System Prompt to enforce the use of Code Trajectory.

```markdown
## Code Trajectory MCP Rules
You are connected to a "Code Trajectory" server that tracks the evolutionary history of the codebase. You MUST follow these rules to maintain context and history hygiene:

1.  **INITIALIZATION (Must Do):**
    - At the very beginning of a session, you MUST call `configure_project(path="/absolute/path/to/project")` to initialize the server.
    - Then, call `get_session_summary()` to understand the previous work context.
    - If you are unsure about a file's state, call `get_file_trajectory(filepath)` BEFORE editing it.

2.  **INTENT DECLARATION:**
    - Before starting any logical unit of work (e.g., refactoring, fixing a bug), you MUST call `set_trajectory_intent(intent_description)`.
    - Example: `set_trajectory_intent("Refactoring auth middleware to use async/await")`
    - **Note:** The intent persists until you call this tool again with a new intent.

3.  **CONSOLIDATION (Definition of Done):**
    - When you have successfully completed a task or feature, you MUST call `consolidate(summary)`.
    - **WARNING:** Do NOT call `consolidate` if you are still debugging or experimenting. Only consolidate stable, working states.
    - This action squashes your intermediate "trial & error" snapshots into a permanent history log.
    - **IMPORTANT:** This ONLY affects the shadow repo. You must still commit to the main repo separately.

4.  **CONTEXT AWARENESS:**
    - If you encounter a revert or a failed attempt in the trajectory (marked as `[Revert Detected]`), acknowledge it and do not repeat the same mistake.
    - Use `get_global_trajectory()` to check for ripple effects if you modify shared dependencies.
```
