# SPDX-License-Identifier: MIT
import os
from unittest.mock import patch, MagicMock
import pytest
from code_trajectory.server import _ensure_configured, state, configure_project

def test_explicit_configuration(temp_project_dir):
    """Test configuring the server with an explicit path."""
    # Reset state
    state.recorder = None
    state.watcher = None
    state.trajectory = None
    state.project_path = None

    result = configure_project(temp_project_dir)
    
    assert "Successfully configured" in result
    assert state.project_path == temp_project_dir
    assert state.recorder is not None
    assert state.recorder.project_root == temp_project_dir

def test_auto_configuration_cwd(temp_project_dir):
    """Test that the server auto-configures to CWD if not configured."""
    # Reset state
    state.recorder = None
    state.watcher = None
    state.trajectory = None
    state.project_path = None

    with patch("os.getcwd", return_value=temp_project_dir):
        # _ensure_configured no longer auto-configures by default unless path is provided
        # It just returns status. Auto-config happens in _check_configured or main.
        # But wait, _ensure_configured DOES NOT call _auto_configure anymore.
        # So calling it without path just returns "Server is configured to track: None"
        
        # We need to simulate the behavior of a tool call that triggers auto-config
        from code_trajectory.server import _auto_configure
        _auto_configure()
        
    assert state.project_path == temp_project_dir

def test_reconfiguration(temp_project_dir):
    """Test switching projects."""
    # 1. Configure first project
    configure_project(temp_project_dir)
    old_watcher = state.watcher
    
    # 2. Create second project
    import tempfile
    import shutil
    second_dir = tempfile.mkdtemp()
    try:
        # Configure second project
        result = configure_project(second_dir)
        
        assert "Successfully configured" in result
        assert state.project_path == second_dir
        assert state.watcher != old_watcher
        
    finally:
        shutil.rmtree(second_dir)

def test_root_directory_safety():
    """Test behavior when CWD is root (simulating the user's error)."""
    # Reset state completely
    state.recorder = None
    state.watcher = None
    state.trajectory = None
    state.project_path = None
    
    # Mock os.getcwd to return root
    with patch("os.getcwd", return_value="/"):
        # We expect this NOT to raise RuntimeError anymore.
        # It should log a warning and return None (or just not configure).
        from code_trajectory.server import _auto_configure
        _auto_configure()
        
        # Verify it didn't configure
        assert state.project_path is None
