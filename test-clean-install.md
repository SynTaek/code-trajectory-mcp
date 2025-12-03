# Clean Installation Test Script

This script simulates a fresh installation of the project, including a clean git environment, to verify that everything works as expected for new users.

## What It Does

1. **Creates a temporary directory** for testing
2. **Saves and clears current git config** (user.name and user.email) to simulate a fresh git installation
3. **Sets temporary test git credentials**
4. **Clones the repository** from GitHub
5. **Checks out the specified tag** (default: v0.1.1)
6. **Installs dependencies** using `uv sync`
7. **Runs all tests** with pytest
8. **Runs linting checks** (ruff and pyrefly)
9. **Restores original git config**
10. **Cleans up temporary directory**

## Usage

### Basic Usage

```powershell
.\test-clean-install.ps1
```

### Test a Different Tag

```powershell
.\test-clean-install.ps1 -Tag "v0.2.0"
```

### Keep Temporary Directory for Inspection

```powershell
.\test-clean-install.ps1 -KeepTemp
```

### Skip Linting Checks (Run Tests Only)

```powershell
.\test-clean-install.ps1 -SkipLint
```

### Combined Options

```powershell
.\test-clean-install.ps1 -Tag "v0.1.1" -KeepTemp -SkipLint
```

## Parameters

- `-Tag <string>`: Git tag to checkout (default: "v0.1.1")
- `-KeepTemp`: Don't delete the temporary directory after testing
- `-SkipLint`: Skip ruff and pyrefly checks, run tests only

## Exit Codes

- `0`: All checks passed
- `1`: One or more checks failed

## Example Output

```
==================================================
  Clean Installation Test for code-trajectory-mcp
==================================================

[1/8] Creating temporary directory: C:\Users\...\Temp\code-trajectory-test-20251203-221530
[2/8] Saving current git config...
[3/8] Simulating fresh git installation (clearing git config)...
[4/8] Setting temporary test git config...
[5/8] Cloning repository from GitHub...
[6/8] Checking out tag: v0.1.1
[7/8] Installing dependencies with uv sync...
[8/8] Running tests...

====== TEST OUTPUT ======
...
=========================

Running linting checks...

--- Ruff Check ---
...

--- Pyrefly Check ---
...

==================================================
  TEST SUMMARY
==================================================
[✓] Tests: PASSED
[✓] Ruff: PASSED
[✓] Pyrefly: PASSED

Test directory: C:\Users\...\Temp\code-trajectory-test-20251203-221530

✓ All checks passed!

Restoring original git config...
Cleaning up temporary directory...
✓ Cleanup complete
```

## Safety Features

- **Git config restoration**: Your original git user.name and user.email are always restored, even if the script fails
- **Error handling**: Uses PowerShell's error handling to ensure cleanup runs
- **Unique temp directories**: Uses timestamps to avoid conflicts
- **Optional cleanup**: Use `-KeepTemp` to inspect the test environment

## Use Cases

- **Pre-release testing**: Verify that a new version works from scratch
- **CI simulation**: Test the same environment that CI uses
- **Bug reproduction**: Test with a clean state when debugging issues
- **Documentation verification**: Ensure the setup process works for new users
