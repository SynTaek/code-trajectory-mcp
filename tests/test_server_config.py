# SPDX-License-Identifier: MIT
from unittest.mock import patch
from code_trajectory.server import state, configure_project, _check_configured

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

def test_no_auto_configuration(temp_project_dir):
    """Test that the server does NOT auto-configure."""
    # Reset state
    state.recorder = None
    state.watcher = None
    state.trajectory = None
    state.project_path = None

    with patch("os.getcwd", return_value=temp_project_dir):
        # Calling _check_configured should return an error message
        error = _check_configured()
        
    assert error is not None
    assert "Server is NOT configured" in error
    assert state.project_path is None

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

def test_check_configured_returns_error():
    """Test that _check_configured returns error when not configured."""
    # Reset state completely
    state.recorder = None
    state.watcher = None
    state.trajectory = None
    state.project_path = None
    
    error = _check_configured()
    assert error is not None
    assert "Server is NOT configured" in error
