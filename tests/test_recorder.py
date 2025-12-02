# SPDX-License-Identifier: MIT
import os
import time

def test_recorder_initialization(recorder, temp_project_dir):
    """Test that the recorder initializes the shadow repo correctly."""
    shadow_repo_path = os.path.join(temp_project_dir, ".trajectory")
    assert os.path.exists(shadow_repo_path)
    assert os.path.exists(os.path.join(shadow_repo_path, ".git"))

    # Check .gitignore.
    with open(os.path.join(temp_project_dir, ".gitignore"), "r") as f:
        content = f.read()
    assert ".trajectory/" in content

def test_create_snapshot(recorder, temp_project_dir):
    """Test creating a snapshot of a modified file."""
    test_file = os.path.join(temp_project_dir, "test.py")
    with open(test_file, "w") as f:
        f.write("print('hello')")
    with open(test_file, "w") as f:
        f.write("print('hello')")

    recorder.create_snapshot(test_file)
    
    commits = recorder.get_history(test_file)
    assert len(commits) == 1
    assert "Snapshot of" in commits[0].message
    assert "[AUTO-TRJ]" in commits[0].message

def test_intent_persistence(recorder, temp_project_dir):
    """Test that intent persists indefinitely."""
    recorder.set_intent("Persistent Task")
    
    test_file = os.path.join(temp_project_dir, "test.txt")
    
    # Snapshot 1
    with open(test_file, "w") as f:
        f.write("Change 1")
    recorder.create_snapshot(test_file)
    
    # Simulate time passing (mocking datetime not needed as we removed TTL)
    # Just verify it's still there for Snapshot 2
    
    # Snapshot 2
    with open(test_file, "a") as f:
        f.write("Change 2")
    recorder.create_snapshot(test_file)
    
    commits = list(recorder.repo.iter_commits())
    assert len(commits) == 2
    assert "Persistent Task" in commits[0].message
    assert "Persistent Task" in commits[0].message
    assert "Persistent Task" in commits[1].message

def test_intent_persistence_after_consolidation(recorder, temp_project_dir):
    """Test that intent persists even after a consolidation."""
    recorder.set_intent("Long Running Task")
    test_file = os.path.join(temp_project_dir, "test.txt")
    
    # 1. Create snapshot
    with open(test_file, "w") as f:
        f.write("v1")
    recorder.create_snapshot(test_file)
    
    # 2. Consolidate
    recorder.consolidate("Intermediate Save")
    
    # 3. Create another snapshot
    with open(test_file, "w") as f:
        f.write("v2")
    recorder.create_snapshot(test_file)
    
    # Verify the new snapshot still has the intent
    commits = list(recorder.repo.iter_commits())
    # commits[0] is the new snapshot
    # commits[1] is the consolidation
    assert "Long Running Task" in commits[0].message
    assert "[AUTO-TRJ]" in commits[0].message

def test_consolidate(recorder, temp_project_dir):
    """Test squashing snapshots into a consolidation."""
    test_file = os.path.join(temp_project_dir, "test.py")

    # Create 3 snapshots.
    for i in range(3):
        with open(test_file, "w") as f:
            f.write(f"print({i})")
        recorder.create_snapshot(test_file)
        time.sleep(0.1)  # Ensure timestamps differ slightly if needed.
        
    commits = recorder.get_history(test_file)
    assert len(commits) == 3

    # Consolidate.
    result = recorder.consolidate("Completed feature")
    assert "Successfully consolidated" in result
    assert "shadow repository (.trajectory) ONLY" in result

    # Verify squash.
    # Note: get_history might return the consolidation commit now.
    commits = list(recorder.repo.iter_commits())
    assert len(commits) == 1
    assert "[CONSOLIDATE]" in commits[0].message
    assert "Completed feature" in commits[0].message
