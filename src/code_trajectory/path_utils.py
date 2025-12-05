# SPDX-License-Identifier: MIT
import os
import pathlib
from typing import Optional

def to_posix_path(path: str) -> str:
    """Converts a path to POSIX format (forward slashes).

    This is useful for interacting with tools that expect POSIX paths,
    such as Git, even when running on Windows.
    """
    return path.replace("\\", "/")

def normalize_path(path: str) -> str:
    """Returns the absolute, normalized path."""
    return os.path.abspath(path)

def is_subpath(path: str, parent: str) -> bool:
    """Checks if path is a subpath of parent.

    Handles platform-specific case sensitivity and normalization.
    """
    try:
        # Resolve paths to handle symlinks and relative paths
        # We use pathlib for robust comparison
        p_path = pathlib.Path(path).resolve()
        p_parent = pathlib.Path(parent).resolve()

        # Check if p_path is relative to p_parent
        p_path.relative_to(p_parent)
        return True
    except (ValueError, RuntimeError):
        return False

def get_relative_path(path: str, start: str) -> str:
    """Returns a relative path from start to path.

    Wraps os.path.relpath but ensures consistent behavior or error handling if needed.
    """
    return os.path.relpath(path, start)

def is_git_directory(path: str) -> bool:
    """Checks if the path is a .git directory or inside one."""
    # Robust check for .git in path components
    p = pathlib.Path(path)
    return ".git" in p.parts
