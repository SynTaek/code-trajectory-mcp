#!/usr/bin/env pwsh
# TestPyPI deployment script
# This script builds and uploads the package to TestPyPI for testing

param(
    [switch]$SkipBuild,
    [switch]$SkipTests,
    [switch]$TestInstall
)

$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  TestPyPI Deployment Script" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check if twine is installed
Write-Host "[1/5] Checking dependencies..." -ForegroundColor Yellow
try {
    uv pip show twine | Out-Null
    Write-Host "✓ twine is installed" -ForegroundColor Green
}
catch {
    Write-Host "Installing twine..." -ForegroundColor Yellow
    uv pip install twine
}

# Run tests before deploying
if (-not $SkipTests) {
    Write-Host ""
    Write-Host "[2/5] Running tests..." -ForegroundColor Yellow
    uv run pytest
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Tests failed! Aborting deployment." -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ All tests passed" -ForegroundColor Green
}
else {
    Write-Host ""
    Write-Host "[2/5] Skipping tests (--SkipTests flag)" -ForegroundColor Yellow
}

# Clean old builds
if (-not $SkipBuild) {
    Write-Host ""
    Write-Host "[3/5] Cleaning old build artifacts..." -ForegroundColor Yellow
    if (Test-Path "dist") {
        Remove-Item -Recurse -Force dist
        Write-Host "✓ Cleaned dist/" -ForegroundColor Green
    }

    # Build the package
    Write-Host ""
    Write-Host "[4/5] Building package..." -ForegroundColor Yellow
    uv build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Build failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Package built successfully" -ForegroundColor Green
    
    # Validate package
    Write-Host ""
    Write-Host "Validating package..." -ForegroundColor Yellow
    uv run twine check dist/*
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Package validation failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Package validation passed" -ForegroundColor Green
}
else {
    Write-Host ""
    Write-Host "[3/5] Skipping build (--SkipBuild flag)" -ForegroundColor Yellow
    Write-Host "[4/5] Skipping build (--SkipBuild flag)" -ForegroundColor Yellow
}

# Upload to TestPyPI
Write-Host ""
Write-Host "[5/5] Uploading to TestPyPI..." -ForegroundColor Yellow
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "You will be prompted for TestPyPI credentials:" -ForegroundColor Cyan
Write-Host "  Username: __token__" -ForegroundColor White
Write-Host "  Password: pypi-... (your API token)" -ForegroundColor White
Write-Host ""
Write-Host "Or configure ~/.pypirc to avoid this prompt." -ForegroundColor Gray
Write-Host "See DEPLOYMENT.md for details." -ForegroundColor Gray
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

uv run twine upload --repository testpypi dist/*

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Upload failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  - Invalid credentials: Check your API token" -ForegroundColor Gray
    Write-Host "  - Version already exists: Increment version in pyproject.toml" -ForegroundColor Gray
    Write-Host "  - Package name taken: Choose a different name" -ForegroundColor Gray
    exit 1
}

Write-Host ""
Write-Host "✓ Successfully uploaded to TestPyPI!" -ForegroundColor Green

# Get package info
$version = (Select-String -Path "pyproject.toml" -Pattern 'version = "(.+)"').Matches.Groups[1].Value
$name = (Select-String -Path "pyproject.toml" -Pattern 'name = "(.+)"').Matches.Groups[1].Value

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Deployment Summary" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Package: $name" -ForegroundColor White
Write-Host "Version: $version" -ForegroundColor White
Write-Host "URL: https://test.pypi.org/project/$name/" -ForegroundColor Cyan
Write-Host ""

# Test installation if requested
if ($TestInstall) {
    Write-Host "Testing installation from TestPyPI..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Creating test environment..." -ForegroundColor Gray
    
    $testEnv = Join-Path $env:TEMP "testpypi-install-test"
    if (Test-Path $testEnv) {
        Remove-Item -Recurse -Force $testEnv
    }
    
    Write-Host "Installing package..." -ForegroundColor Gray
    Write-Host ""
    
    # Try to install
    $installCmd = "uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ $name==$version"
    Write-Host "> $installCmd" -ForegroundColor DarkGray
    
    Invoke-Expression $installCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ Installation successful!" -ForegroundColor Green
    }
    else {
        Write-Host ""
        Write-Host "✗ Installation failed" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "To install from TestPyPI:" -ForegroundColor Yellow
Write-Host "  uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ $name" -ForegroundColor White
Write-Host ""
Write-Host "To test with uvx:" -ForegroundColor Yellow
Write-Host "  uvx --index-url https://test.pypi.org/simple/ $name" -ForegroundColor White
Write-Host ""

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Next Steps" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Test the package from TestPyPI" -ForegroundColor White
Write-Host "2. If everything works, deploy to production PyPI:" -ForegroundColor White
Write-Host "   twine upload dist/*" -ForegroundColor Gray
Write-Host ""
