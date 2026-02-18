<#
    Setup script for first-time local development.

    This script is intended for someone pulling the project fresh from GitHub.
    It can do all of the following in one run:
      - Verify required tools are installed
      - Create default backend/frontend .env files (if missing)
      - Start Docker services (Postgres + API app)
      - Install backend dependencies with Poetry
      - Apply Alembic migrations
      - Seed database data from alembic/versions/sql_data.sql
      - Install frontend dependencies with npm
    - Start the frontend dev server

    Prerequisites:
      - Make sure Docker Desktop is installed and running.
      - Make sure Python 3.12+ is installed.
      - Make sure Poetry is installed.
      - Make sure Node.js and npm are installed.

    Usage examples:
      .\setup-dev.ps1
      .\setup-dev.ps1 -SkipSeed
            .\setup-dev.ps1 -FromScratch
#>

param(
    [switch]$SkipNpmInstall,
    [switch]$SkipPoetryInstall,
        [switch]$SkipSeed,
        [switch]$FromScratch
)

$ErrorActionPreference = "Stop"

function Assert-Command {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [string]$InstallHint
    )

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Missing required command '$Name'. $InstallHint"
    }
}

function Ensure-FileWithContent {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [string]$Content,
        [Parameter(Mandatory = $true)]
        [string]$DisplayName
    )

    if (-not (Test-Path $Path)) {
        Set-Content -Path $Path -Value $Content
        Write-Host "Created $DisplayName"
    }
    else {
        Write-Host "$DisplayName already exists."
    }
}

function Ensure-LocalDatabaseUrl {
    param(
        [Parameter(Mandatory = $true)]
        [string]$EnvPath
    )

    if (-not (Test-Path $EnvPath)) {
        return
    }

    $expectedUrl = "postgresql+psycopg://postgres:password@localhost:5432/merge_conflicts_flights_db"
    $envContent = Get-Content -Path $EnvPath -Raw

    if ($envContent -match "DATABASE_URL=.*@db:") {
        $updated = [regex]::Replace(
            $envContent,
            "(?m)^DATABASE_URL=.*$",
            "DATABASE_URL=$expectedUrl"
        )
        Set-Content -Path $EnvPath -Value $updated
        Write-Host "Updated .env DATABASE_URL from Docker host 'db' to local host 'localhost'."
        return
    }

    if ($envContent -notmatch "(?m)^DATABASE_URL=") {
        Add-Content -Path $EnvPath -Value "`nDATABASE_URL=$expectedUrl"
        Write-Host "Added missing DATABASE_URL to .env for local setup."
    }
}

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendDir = Join-Path $projectRoot "airline-ops-frontend"
$seedFile = Join-Path $projectRoot "alembic\versions\sql_data.sql"
$backendEnv = Join-Path $projectRoot ".env"
$frontendEnv = Join-Path $frontendDir ".env"

Write-Host "=== Revature ATC Project: Local Setup ==="
Write-Host "Make sure Docker Desktop is running before continuing."

Write-Host "[1/8] Verifying required tooling..."
Assert-Command -Name docker -InstallHint "Install Docker Desktop from https://www.docker.com/products/docker-desktop/"
Assert-Command -Name poetry -InstallHint "Install Poetry from https://python-poetry.org/docs/#installation"
Assert-Command -Name node -InstallHint "Install Node.js (LTS) from https://nodejs.org/"
Assert-Command -Name npm -InstallHint "npm is bundled with Node.js; reinstall Node.js if npm is missing."

Write-Host "[2/8] Preparing environment files..."
Ensure-FileWithContent -Path $backendEnv -DisplayName ".env" -Content @"
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/merge_conflicts_flights_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=merge_conflicts_flights_db
"@
Ensure-LocalDatabaseUrl -EnvPath $backendEnv
Ensure-FileWithContent -Path $frontendEnv -DisplayName "airline-ops-frontend/.env" -Content "VITE_API_BASE_URL=http://localhost:8000`n"

if (-not (Test-Path $seedFile)) {
    throw "Seed file not found: $seedFile"
}

Push-Location $projectRoot
try {
    if ($FromScratch) {
        Write-Host "[3/8] From-scratch reset enabled: removing containers, networks, and named volumes..."
        docker compose down -v --remove-orphans
    }

    Write-Host "[3/8] Starting Docker services (db + app)..."
    docker compose up -d db app

    if (-not $SkipPoetryInstall) {
        Write-Host "[4/8] Installing backend dependencies with Poetry..."
        poetry install
    }
    else {
        Write-Host "[4/8] Skipping Poetry install (--SkipPoetryInstall)."
    }

    Write-Host "[5/8] Applying Alembic migrations..."
    poetry run alembic upgrade head

    if (-not $SkipSeed) {
        Write-Host "[6/8] Seeding database from alembic/versions/sql_data.sql..."
        Get-Content $seedFile -Raw | docker compose exec -T db psql -U postgres -d merge_conflicts_flights_db
    }
    else {
        Write-Host "[6/8] Skipping database seed (--SkipSeed)."
    }
}
finally {
    Pop-Location
}

Push-Location $frontendDir
try {
    if (-not $SkipNpmInstall) {
        Write-Host "[7/8] Installing frontend dependencies (npm install)..."
        npm install
    }
    else {
        Write-Host "[7/8] Skipping npm install (--SkipNpmInstall)."
    }

    Write-Host "[8/8] Opening frontend in browser and starting dev server (Vite)..."
    Start-Process "http://localhost:5173"
    npm run dev
}
finally {
    Pop-Location
}