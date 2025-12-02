# SPDX-License-Identifier: MIT
from mcp.server.fastmcp import FastMCP
import argparse
import logging
import os
from .recorder import Recorder
from .watcher import Watcher
from .trajectory import Trajectory

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Global state
class ServerState:
    def __init__(self):
        self.recorder: Recorder | None = None
        self.watcher: Watcher | None = None
        self.trajectory: Trajectory | None = None
        self.project_path: str | None = None


state = ServerState()

# Initialize MCP Server
mcp = FastMCP("code-trajectory")


def _ensure_configured(path: str | None = None) -> str:
    if path:
        return _initialize_components(path)

    return f"Server is configured to track: {state.project_path}"


def _check_configured() -> str | None:
    """Checks if configured, returns error message if not."""
    if state.trajectory is None:
        return (
            "Server is NOT configured. "
            "Please call 'configure_project(path=...)' with the absolute path to the project root."
        )
    return None


def _initialize_components(path: str) -> str:
    target_path = os.path.abspath(path)
    if not os.path.exists(target_path):
        raise ValueError(f"Target path does not exist: {target_path}")

    # Check if we are already watching this path
    if state.watcher and state.project_path == target_path:
        logger.info(f"Already watching {target_path}, skipping re-initialization.")
        return f"Already configured to track: {target_path}"

    # Stop existing watcher if any (different path)
    if state.watcher:
        state.watcher.stop()

    try:
        state.recorder = Recorder(target_path)
        state.watcher = Watcher(target_path, state.recorder)
        state.trajectory = Trajectory(state.recorder)
        state.project_path = target_path

        state.watcher.start()
        logger.info(f"Initialized components for {target_path}")
        return f"Successfully configured to track: {target_path}"
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise RuntimeError(f"Failed to initialize: {e}")


@mcp.tool()
def configure_project(path: str) -> str:
    """Configures the server to track a specific project path.

    This tool MUST be called before using any other tools.
    It initializes the server to track the specified project directory.

    Args:
        path: Absolute path to the target project directory.

    Returns:
        A confirmation message indicating the server is configured.
    """
    if path:
        return _initialize_components(path)
    return "Please provide a path."


@mcp.tool()
def get_file_trajectory(filepath: str, depth: int = 5) -> str:
    """Retrieves the evolutionary trajectory of a specific file.

    Use this tool before modifying a complex file to understand its recent history,
    or to see the "flow" of changes leading up to the present.

    Args:
        filepath: Relative path to the file (e.g., "src/main.py").
        depth: Number of recent snapshots to retrieve (default: 5).

    Returns:
        A markdown-formatted narrative of the file's history, including timestamps,
        intents, and diff summaries. Reverts are annotated with `[Revert Detected]`.
    """
    error = _check_configured()
    if error:
        return error
    assert state.trajectory is not None
    return state.trajectory.get_file_trajectory(filepath, depth)


@mcp.tool()
def get_global_trajectory(limit: int = 20, since_consolidate: bool = False) -> str:
    """Retrieves the global trajectory (ripple effect) across the project.

    Use this to understand the broader context of recent changes or to detect
    ripple effects (e.g., "I changed User.py, did I also update UserTest.py?").

    Args:
        limit: Maximum number of commits to retrieve (default: 20).
        since_consolidate: If True, retrieves all commits since the last consolidation.
            This overrides the 'limit' argument.

    Returns:
        A summary of modified files and their relationships, grouped by time and intent.
    """
    error = _check_configured()
    if error:
        return error
    assert state.trajectory is not None
    return state.trajectory.get_global_trajectory(limit, since_consolidate)


@mcp.tool()
def get_session_summary() -> str:
    """Retrieves a summary of the last session and current context.

    Use this at the beginning of a chat session to "catch up" on what happened
    previously or to understand the last known state of the project.

    Returns:
        A summary of the last recorded session, including the final intent and modified files.
    """
    error = _check_configured()
    if error:
        return error
    assert state.trajectory is not None
    return state.trajectory.get_session_summary()


@mcp.tool()
def consolidate(intent: str) -> str:
    """Consolidates recent snapshots into a single commit with a descriptive intent.

    Use this after completing a logical unit of work to "save" your progress semantically.
    This squashes recent [AUTO-TRJ] snapshots into a single commit.

    IMPORTANT: This action ONLY affects the shadow repository (.trajectory).
    It does NOT create a commit in the main project's git history.
    You must still commit your changes to the main project separately if desired.

    Args:
        intent: A clear, past-tense description of what was accomplished (e.g., "Refactored auth middleware").

    Returns:
        A success message indicating the consolidation was created and how many snapshots were squashed.
    """
    error = _check_configured()
    if error:
        return error
    assert state.recorder is not None
    return state.recorder.consolidate(intent)


@mcp.tool()
def set_trajectory_intent(intent: str) -> str:
    """Sets the current coding intent.

    The intent will be attached to all subsequent [AUTO-TRJ] snapshots until it is
    changed or the server is restarted.

    Args:
        intent: A short description of the task (e.g., "Debugging connection timeout").

    Returns:
        A confirmation message indicating the intent is set.
    """
    error = _check_configured()
    if error:
        return error
    assert state.recorder is not None
    state.recorder.set_intent(intent)
    return f"Intent set to: '{intent}'"


def main():
    parser = argparse.ArgumentParser(description="Code Trajectory MCP Server")
    parser.add_argument("--path", help="Path to the target project to track (optional)")
    args = parser.parse_args()

    # Initial configuration
    try:
        # Check if git is available.
        import shutil
        if not shutil.which("git"):
            logger.error("Git is not installed or not in PATH. Code Trajectory requires git.")
            raise RuntimeError("Git is not installed or not in PATH.")

        if args.path:
            _initialize_components(args.path)
        else:
            logger.info("Server started. Waiting for 'configure_project' call.")
    except Exception as e:
        logger.error(f"Startup configuration failed: {e}")
        # We don't exit here, allowing the server to run.
        # Tools will try to configure again if needed, or fail gracefully.

    # Run server
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Stopping server...")
    finally:
        if state.watcher:
            state.watcher.stop()


if __name__ == "__main__":
    main()
