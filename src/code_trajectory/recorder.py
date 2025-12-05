# SPDX-License-Identifier: MIT
import git
from git.exc import GitCommandError
import datetime
import logging
import os
from typing import Optional
from . import path_utils

logger = logging.getLogger(__name__)


class Recorder:
    def __init__(self, repo_path: str):
        self.project_root = path_utils.normalize_path(repo_path)
        self.shadow_repo_path = os.path.join(self.project_root, ".trajectory")
        self.current_intent: Optional[str] = None
        self.current_intent: Optional[str] = None

        self._ensure_gitignore()
        self._init_shadow_repo()

    def _ensure_gitignore(self):
        """Ensures .trajectory is ignored in the main project."""
        gitignore_path = os.path.join(self.project_root, ".gitignore")
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r") as f:
                content = f.read()
            if ".trajectory" not in content:
                with open(gitignore_path, "a") as f:
                    f.write("\n.trajectory/\n")
                logger.info("Added .trajectory to .gitignore")
        else:
            with open(gitignore_path, "w") as f:
                f.write(".trajectory/\n")
            logger.info("Created .gitignore with .trajectory")

    def _init_shadow_repo(self):
        """Initializes the shadow repository."""
        if not os.path.exists(self.shadow_repo_path):
            os.makedirs(self.shadow_repo_path)
            self.repo = git.Repo.init(self.shadow_repo_path)
            # Configure work tree to be the project root
            # Configure work tree to be the project root
            self.repo.git.config("core.worktree", self.project_root)
            self.repo.git.config("advice.addIgnoredFile", "false")
            logger.info(f"Initialized shadow repo at {self.shadow_repo_path}")
        else:
            self.repo = git.Repo(self.shadow_repo_path)
            # Ensure worktree is set correctly (in case moved)
            self.repo.git.config("core.worktree", self.project_root)
            self.repo.git.config("advice.addIgnoredFile", "false")

    def set_intent(self, intent: str):
        """Sets the current coding intent.

        The intent persists until it is explicitly changed or the server is restarted.

        Args:
            intent: A description of the current task.
        """
        self.current_intent = intent
        self.current_intent = intent
        logger.info(f"Intent set to: {intent}")

    def create_snapshot(self, filepath: str):
        """Creates a snapshot commit for the modified file.

        Args:
            filepath: Absolute path to the modified file.
        """
        try:
            # Check if there are changes to commit.
            if not self.repo.is_dirty(path=filepath, untracked_files=True):
                logger.info(f"No changes detected in {filepath}")
                return

            # Use git command directly to handle worktree correctly.
            self.repo.git.add(filepath)

            timestamp = datetime.datetime.now().strftime("%H:%M:%S")

            # Check for active intent (Persistent).
            intent_str = ""
            if self.current_intent:
                intent_str = f" - {self.current_intent}"

            commit_message = (
                f"[AUTO-TRJ] {timestamp}{intent_str} - Snapshot of {filepath}"
            )

            # Commit.
            self.repo.git.commit("-m", commit_message)
            logger.info(f"Created snapshot for {filepath}: {commit_message}")

        except GitCommandError as e:
            if "index.lock" in str(e):
                logger.warning(f"Git lock contention for {filepath}: {e}")
            else:
                logger.error(f"Git error during snapshot of {filepath}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during snapshot of {filepath}: {e}")

    def get_history(self, filepath: str, max_count: int = 5):
        """Retrieves the history of a file.

        Args:
            filepath: Path to the file (relative or absolute).
            max_count: Maximum number of commits to retrieve.

        Returns:
            A list of Commit objects.
        """
        # Normalize path to be relative to project root
        if not os.path.isabs(filepath):
            abs_path = os.path.join(self.project_root, filepath)
        else:
            abs_path = filepath

        abs_path = path_utils.normalize_path(abs_path)

        # Check if path is within project root
        if not path_utils.is_subpath(abs_path, self.project_root):
            logger.error(
                f"Path {filepath} is not within project root {self.project_root}"
            )
            return []

        # Use absolute path for git to avoid CWD issues with gitpython.
        commits = list(self.repo.iter_commits(paths=abs_path, max_count=max_count))
        return commits

    def consolidate(self, intent: str):
        """Squashes recent [AUTO-TRJ] snapshots and creates a consolidate commit.

        Args:
            intent: Description of the consolidation.

        Returns:
            A status message indicating the result of the consolidate operation.
        """
        try:
            commits = list(self.repo.iter_commits())
            if not commits:
                return "No commits to consolidate."

            # Find how many recent commits are AUTO-TRJ
            auto_trj_count = 0
            for commit in commits:
                message = str(commit.message)
                if message.startswith("[AUTO-TRJ]"):
                    auto_trj_count += 1
                else:
                    break

            if auto_trj_count > 0:
                if auto_trj_count == len(commits):
                    # We are squashing everything, including the root commit.
                    # Use update-ref to clear HEAD but keep index/working tree.
                    self.repo.git.update_ref("-d", "HEAD")
                    logger.info(f"Squashed all {auto_trj_count} commits (root reset).")
                else:
                    # Soft reset to HEAD~N.
                    self.repo.git.reset("--soft", f"HEAD~{auto_trj_count}")
                    logger.info(f"Squashed {auto_trj_count} trajectory snapshots.")

            # Check if there are changes to commit.
            if not self.repo.is_dirty() and not self.repo.index.diff("HEAD"):
                return "No changes to consolidate."

            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            commit_message = f"[CONSOLIDATE] {timestamp} - {intent}"

            # Add all files using -A to handle deletions and new files.
            # Also rely on advice.addIgnoredFile=false to avoid errors with .trajectory.
            self.repo.git.add("-A")
            self.repo.git.commit("-m", commit_message)

            logger.info(f"Created consolidation: {commit_message}")
            return (
                f"Successfully consolidated: '{intent}' (Squashed {auto_trj_count} snapshots).\n"
                "NOTE: This consolidation is saved in the shadow repository (.trajectory) ONLY.\n"
                "You must still commit your changes to the main project git repository separately."
            )

        except Exception as e:
            logger.error(f"Error creating consolidation: {e}")
            return f"Error creating consolidation: {e}"
