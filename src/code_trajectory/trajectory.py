# SPDX-License-Identifier: MIT
from datetime import datetime
import logging
import os

from .recorder import Recorder
from . import path_utils

logger = logging.getLogger(__name__)


class Trajectory:
    def __init__(self, recorder: Recorder):
        self.recorder = recorder

    def get_file_trajectory(self, filepath: str, depth: int = 5) -> str:
        """Generates a narrative trajectory for a specific file.

        Args:
            filepath: Path to the file.
            depth: Number of recent snapshots to include.

        Returns:
            A markdown-formatted string containing the file's history.
        """
        commits = self.recorder.get_history(filepath, max_count=depth)
        if not commits:
            return f"No trajectory found for {filepath}."

        trajectory = [f"# Trajectory for {filepath}"]

        # Normalize filepath for tree access (must be relative to project root).
        # We need a POSIX path for git tree traversal.
        if os.path.isabs(filepath):
            try:
                rel_filepath = path_utils.get_relative_path(filepath, self.recorder.project_root)
            except ValueError:
                rel_filepath = filepath  # Fallback
        else:
            rel_filepath = filepath

        # Ensure it is posix style for git
        rel_filepath = path_utils.to_posix_path(rel_filepath)

        # Track content hashes to detect reverts.
        # Map: content_hash -> (timestamp, message)
        seen_states = {}

        # Process from oldest to newest.
        for commit in reversed(commits):
            timestamp = datetime.fromtimestamp(commit.committed_date).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            message = commit.message.strip()

            # Calculate content hash.
            try:
                # gitpython: get blob for file at this commit.
                blob = commit.tree / rel_filepath
                content = blob.data_stream.read()
                import hashlib

                content_hash = hashlib.md5(content).hexdigest()
            except KeyError:
                # File might not exist in this commit (e.g. deleted).
                content_hash = None
            except Exception as e:
                logger.warning(
                    f"Failed to hash content for {filepath} at {commit.hexsha}: {e}"
                )
                content_hash = None

            revert_annotation = ""
            if content_hash and content_hash in seen_states:
                prev_ts, prev_msg = seen_states[content_hash]
                revert_annotation = (
                    f" **[Revert Detected]** (Matches state from {prev_ts})"
                )

            if content_hash:
                seen_states[content_hash] = (timestamp, message)

            # Get diff.
            if commit.parents:
                parent = commit.parents[0]
                diffs = parent.diff(commit, paths=filepath, create_patch=True)
                diff_text = ""
                for diff in diffs:
                    if diff.diff:
                        # Ensure diff is bytes before decoding.
                        if isinstance(diff.diff, bytes):
                            diff_text = diff.diff.decode("utf-8")
                        else:
                            diff_text = str(diff.diff)
                        break
            else:
                # First commit.
                diff_text = "[Initial Commit]"

            trajectory.append(f"## {timestamp} - {message}{revert_annotation}")
            trajectory.append(f"```diff\n{diff_text}\n```")

        return "\n\n".join(trajectory)

    def get_global_trajectory(self, limit: int = 20, since_consolidate: bool = False) -> str:
        """Generates a global trajectory summary.

        Args:
            limit: Maximum number of commits to retrieve (default: 20).
            since_consolidate: If True, retrieves all commits since the last consolidation.
                This overrides the 'limit' argument.

        Returns:
            A markdown-formatted summary of global activity.
        """
        try:
            # Fetch commits. We fetch a bit more than limit if checking for consolidation,
            # but for simplicity in this iteration, we'll iterate from HEAD.
            # If since_consolidate is True, we need to iterate until we find a consolidation.
            
            commits = []
            if since_consolidate:
                # Iterate commits until we find a consolidation or hit a reasonable safety limit (e.g. 1000)
                for commit in self.recorder.repo.iter_commits(max_count=1000):
                    message = str(commit.message)
                    if message.startswith("[CONSOLIDATE]") or message.startswith("[CHECKPOINT]"):
                        # Backward compatibility: also check for [CHECKPOINT]
                        break
                    commits.append(commit)
            else:
                commits = list(self.recorder.repo.iter_commits(max_count=limit))

        except Exception as e:
            # Check for empty repo error (gitpython usually raises ValueError or GitCommandError)
            error_msg = str(e)
            # More specific checks for empty repository states
            if "Reference at 'refs/heads/master' does not exist" in error_msg:
                 return "No history available"

            # Check for GitCommandError that indicates no commits (git log fails)
            if hasattr(e, 'stderr') and "does not have any commits yet" in str(e.stderr):
                 return "No history available"

            # Check for BadObject (happens when HEAD is invalid)
            if "BadObject" in error_msg and "HEAD" in error_msg:
                 return "No history available"

            logger.error(f"Failed to fetch global trajectory: {e}")
            return f"Error fetching global trajectory: {e}"

        if not commits:
            return "No global activity found."

        trajectory = []
        if since_consolidate:
            trajectory.append("# Global Trajectory (Since Last Consolidation)")
        else:
            trajectory.append(f"# Global Trajectory (Last {len(commits)} snapshots)")

        for commit in reversed(commits):
            timestamp = datetime.fromtimestamp(commit.committed_date).strftime(
                "%H:%M:%S"
            )
            message = commit.message.strip()
            files_changed = [str(f) for f in commit.stats.files.keys()]
            files_str = ", ".join(files_changed)

            trajectory.append(f"- **{timestamp}**: {message} (Files: `{files_str}`)")

        return "\n".join(trajectory)

    def get_session_summary(self) -> str:
        """Identifies session gaps and summarizes the last session.

        Returns:
            A markdown-formatted summary of the last session's activity.
        """
        # Optimization: Fetch only timestamps first to find the gap efficiently.
        # Look back up to 1000 commits to find a session boundary.
        try:
            # %ct = committer timestamp, unix epoch.
            timestamps_output = self.recorder.repo.git.log("-n", "1000", "--format=%ct")
            if not timestamps_output:
                return "No session history found."
            
            timestamps = [int(ts) for ts in timestamps_output.splitlines()]
        except Exception as e:
            error_msg = str(e)
            if "does not have any commits yet" in error_msg:
                return "No history available"

            logger.error(f"Failed to fetch commit timestamps: {e}")
            return f"Error analyzing session history: {e}"

        session_gap_threshold = 3600  # 1 hour
        commit_count = len(timestamps)
        last_session_count = commit_count # Default to all if no gap found

        for i in range(commit_count - 1):
            current_time = timestamps[i]
            prev_time = timestamps[i + 1]

            if (current_time - prev_time) > session_gap_threshold:
                # Gap found at index i.
                # The session includes commits 0 to i (inclusive), so count is i + 1.
                last_session_count = i + 1
                break

        # Now fetch the actual commit objects for the identified session.
        try:
            last_session_commits = list(self.recorder.repo.iter_commits(max_count=last_session_count))
        except Exception as e:
             return f"Error fetching session commits: {e}"

        if not last_session_commits:
             return "No session history found."

        # Summarize last session
        start_time = datetime.fromtimestamp(
            last_session_commits[-1].committed_date
        ).strftime("%Y-%m-%d %H:%M:%S")
        end_time = datetime.fromtimestamp(
            last_session_commits[0].committed_date
        ).strftime("%H:%M:%S")

        files_touched: set[str] = set()
        for c in last_session_commits:
            # Manually iterate to avoid type checker confusion with GitPython's dict_keys.
            for file_path in c.stats.files.keys():
                files_touched.add(str(file_path))

        summary = ["# Last Session Summary"]
        summary.append(f"**Time:** {start_time} to {end_time}")
        summary.append(f"**Files Modified:** {', '.join(files_touched)}")
        summary.append(f"**Commit Count:** {len(last_session_commits)}")

        return "\n".join(summary)
