# SPDX-License-Identifier: MIT
import pytest
import shutil
import tempfile
import git
import os
from code_trajectory.recorder import Recorder
from code_trajectory.trajectory import Trajectory

@pytest.fixture
def temp_project_dir():
    """Creates a temporary directory for the project."""
    temp_dir = tempfile.mkdtemp()
    # Initialize git in the temp dir.
    repo = git.Repo.init(temp_dir)
    # Configure user for commits.
    repo.git.config("user.name", "Test User")
    repo.git.config("user.email", "test@example.com")
    
    yield temp_dir
    
    def on_rm_error(func, path, excinfo):
        # path contains the path of the file that couldn't be removed
        # let's just assume that it's read-only and unlink it.
        import stat
        os.chmod(path, stat.S_IWRITE)
        func(path)

    # Retry a few times if needed, or just use the onerror callback
    try:
        shutil.rmtree(temp_dir, onexc=on_rm_error)
    except Exception as e:
        print(f"Warning: Failed to clean up temp dir {temp_dir}: {e}")

@pytest.fixture
def recorder(temp_project_dir):
    """Returns a Recorder instance initialized in the temp project."""
    rec = Recorder(temp_project_dir)
    # Configure user for the shadow repo used by Recorder
    rec.repo.git.config("user.name", "Test User")
    rec.repo.git.config("user.email", "test@example.com")
    return rec

@pytest.fixture
def trajectory(recorder):
    """Returns a Trajectory instance."""
    return Trajectory(recorder)
