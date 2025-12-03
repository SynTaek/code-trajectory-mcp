# Deployment Guide

This guide explains how to deploy `code-trajectory-mcp` to TestPyPI (for testing) and PyPI (for production).

## Prerequisites

### 1. Create TestPyPI Account

1. Go to [https://test.pypi.org/account/register/](https://test.pypi.org/account/register/)
2. Create an account
3. Verify your email

### 2. Create API Token

1. Log in to TestPyPI
2. Go to [Account Settings](https://test.pypi.org/manage/account/)
3. Scroll to "API tokens"
4. Click "Add API token"
5. Set name (e.g., "code-trajectory-upload")
6. Set scope to "Entire account" (or specific project if you've created it)
7. Copy the generated token (starts with `pypi-`)
8. **Important:** Save this token securely - you won't see it again!

### 3. Configure `.pypirc` (Optional but Recommended)

Create or edit `~/.pypirc` (Windows: `%USERPROFILE%\.pypirc`):

```ini
[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TOKEN_HERE

[pypi]
repository = https://pypi.org/legacy/
username = __token__
password = pypi-YOUR_TOKEN_HERE_WHEN_READY
```

**Note:** Replace `pypi-YOUR_TOKEN_HERE` with your actual token.

---

## Deployment to TestPyPI

### Method 1: Using the Automation Script (Recommended)

```powershell
.\deploy-testpypi.ps1
```

This script will:
1. Clean old build artifacts
2. Build the package
3. Upload to TestPyPI
4. Test installation from TestPyPI

### Method 2: Manual Deployment

```powershell
# 1. Clean old builds
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue

# 2. Build the package
uv build

# 3. Install twine (if not already installed)
uv pip install twine

# 4. Upload to TestPyPI
twine upload --repository testpypi dist/*

# You'll be prompted for username and password:
# Username: __token__
# Password: pypi-YOUR_TOKEN_HERE
```

---

## Testing the TestPyPI Package

### Install from TestPyPI

```bash
# Using pip
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ code-trajectory

# Using uv
uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ code-trajectory
```

**Note:** `--extra-index-url https://pypi.org/simple/` is needed because dependencies (like `mcp`, `gitpython`) are on regular PyPI, not TestPyPI.

### Test the Installation

```bash
# Check version
code-trajectory --version

# Or test with uvx
uvx --from code-trajectory --index-url https://test.pypi.org/simple/ code-trajectory
```

---

## Deployment to PyPI (Production)

**⚠️ Only deploy to PyPI when you're confident the package works correctly!**

### Prerequisites

1. Create PyPI account at [https://pypi.org/account/register/](https://pypi.org/account/register/)
2. Generate API token (same process as TestPyPI)
3. Update `~/.pypirc` with PyPI credentials

### Deploy to PyPI

```powershell
# 1. Clean and build
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
uv build

# 2. Upload to PyPI
twine upload dist/*
```

---

## Automated CI/CD Deployment (Optional)

You can automate deployment with GitHub Actions. Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v1
      
      - name: Set up Python
        run: uv python install 3.14
      
      - name: Build package
        run: uv build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: |
          uv pip install twine
          twine upload dist/*
```

Add `PYPI_API_TOKEN` to your GitHub repository secrets.

---

## Troubleshooting

### Package Name Already Exists

If `code-trajectory` is already taken on PyPI, you'll need to:
1. Choose a different name in `pyproject.toml`
2. Rebuild and reupload

### Version Already Exists

PyPI doesn't allow re-uploading the same version. You need to:
1. Increment version in `pyproject.toml`
2. Rebuild and reupload

### Dependencies Not Found

TestPyPI doesn't have all packages. When installing from TestPyPI, always use:
```bash
--extra-index-url https://pypi.org/simple/
```

---

## Version Management

Current version: `0.1.1` (in `pyproject.toml`)

To update version:
1. Edit `pyproject.toml`
2. Update `version = "0.1.2"` (or whatever the new version is)
3. Commit changes
4. Create new git tag: `git tag v0.1.2`
5. Push tag: `git push origin v0.1.2`
6. Build and deploy

---

## Package Information

- **Package name:** `code-trajectory`
- **Import name:** `code_trajectory`
- **Entry point:** `code-trajectory` command
- **TestPyPI URL:** https://test.pypi.org/project/code-trajectory/
- **PyPI URL:** https://pypi.org/project/code-trajectory/ (when published)

---

## Useful Commands

```powershell
# Check what will be included in the package
uv build --outdir dist-test

# Check package contents
tar -tzf dist/code_trajectory-0.1.1.tar.gz

# Validate package before upload
twine check dist/*
```
