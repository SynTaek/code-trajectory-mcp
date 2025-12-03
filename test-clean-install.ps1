#!/usr/bin/env pwsh
# Clean installation test script
# This script simulates a fresh clone and installation of the project

param(
    [string]$Tag = "v0.1.1",
    [switch]$KeepTemp,
    [switch]$SkipLint
)

$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Clean Installation Test for code-trajectory-mcp" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Create a unique temporary directory
$tempDir = Join-Path $env:TEMP "code-trajectory-test-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Write-Host "[1/8] Creating temporary directory: $tempDir" -ForegroundColor Yellow
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

try {
    # Save current git config (user)
    Write-Host "[2/8] Saving current git config..." -ForegroundColor Yellow
    $originalGitUser = git config --global user.name 2>$null
    $originalGitEmail = git config --global user.email 2>$null
    
    # Unset git config to simulate fresh install
    Write-Host "[3/8] Simulating fresh git installation (clearing git config)..." -ForegroundColor Yellow
    if ($originalGitUser) {
        git config --global --unset user.name 2>$null
    }
    if ($originalGitEmail) {
        git config --global --unset user.email 2>$null
    }
    
    # Set temporary test git config
    Write-Host "[4/8] Setting temporary test git config..." -ForegroundColor Yellow
    git config --global user.name "Test User"
    git config --global user.email "test@example.com"
    
    # Clone the repository
    Write-Host "[5/8] Cloning repository from GitHub..." -ForegroundColor Yellow
    git clone https://github.com/SynTaek/code-trajectory-mcp.git $tempDir 2>&1 | Write-Host
    
    # Change to the cloned directory
    Push-Location $tempDir
    
    # Checkout the specified tag
    Write-Host "[6/8] Checking out tag: $Tag" -ForegroundColor Yellow
    git checkout $Tag 2>&1 | Write-Host
    
    # Install dependencies
    Write-Host "[7/8] Installing dependencies with uv sync..." -ForegroundColor Yellow
    uv sync
    
    # Run tests
    Write-Host "[8/8] Running tests..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "====== TEST OUTPUT ======" -ForegroundColor Green
    $testResult = $null
    try {
        uv run pytest -v
        $testResult = $LASTEXITCODE
    } catch {
        $testResult = 1
    }
    Write-Host "=========================" -ForegroundColor Green
    Write-Host ""
    
    # Run linting if not skipped
    if (-not $SkipLint) {
        Write-Host "Running linting checks..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "--- Ruff Check ---" -ForegroundColor Magenta
        uv run ruff check .
        $ruffResult = $LASTEXITCODE
        
        Write-Host ""
        Write-Host "--- Pyrefly Check ---" -ForegroundColor Magenta
        uv run pyrefly check .
        $pyreflyResult = $LASTEXITCODE
        Write-Host ""
    }
    
    Pop-Location
    
    # Summary
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "  TEST SUMMARY" -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    
    if ($testResult -eq 0) {
        Write-Host "[✓] Tests: PASSED" -ForegroundColor Green
    } else {
        Write-Host "[✗] Tests: FAILED (exit code: $testResult)" -ForegroundColor Red
    }
    
    if (-not $SkipLint) {
        if ($ruffResult -eq 0) {
            Write-Host "[✓] Ruff: PASSED" -ForegroundColor Green
        } else {
            Write-Host "[✗] Ruff: FAILED (exit code: $ruffResult)" -ForegroundColor Red
        }
        
        if ($pyreflyResult -eq 0) {
            Write-Host "[✓] Pyrefly: PASSED" -ForegroundColor Green
        } else {
            Write-Host "[✗] Pyrefly: FAILED (exit code: $pyreflyResult)" -ForegroundColor Red
        }
    }
    
    Write-Host ""
    Write-Host "Test directory: $tempDir" -ForegroundColor Cyan
    
    $overallSuccess = ($testResult -eq 0)
    if (-not $SkipLint) {
        $overallSuccess = $overallSuccess -and ($ruffResult -eq 0) -and ($pyreflyResult -eq 0)
    }
    
    if ($overallSuccess) {
        Write-Host ""
        Write-Host "✓ All checks passed!" -ForegroundColor Green
        $exitCode = 0
    } else {
        Write-Host ""
        Write-Host "✗ Some checks failed. See details above." -ForegroundColor Red
        $exitCode = 1
    }
    
} finally {
    # Restore original git config
    Write-Host ""
    Write-Host "Restoring original git config..." -ForegroundColor Yellow
    
    # Clear temporary config
    git config --global --unset user.name 2>$null
    git config --global --unset user.email 2>$null
    
    # Restore original if they existed
    if ($originalGitUser) {
        git config --global user.name $originalGitUser
    }
    if ($originalGitEmail) {
        git config --global user.email $originalGitEmail
    }
    
    # Cleanup
    if (-not $KeepTemp) {
        Write-Host "Cleaning up temporary directory..." -ForegroundColor Yellow
        try {
            Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "✓ Cleanup complete" -ForegroundColor Green
        } catch {
            Write-Host "⚠ Warning: Could not fully clean up $tempDir" -ForegroundColor Yellow
            Write-Host "  You may need to delete it manually." -ForegroundColor Yellow
        }
    } else {
        Write-Host "✓ Temporary directory preserved: $tempDir" -ForegroundColor Green
    }
}

Write-Host ""
exit $exitCode
