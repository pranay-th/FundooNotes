# start.ps1 - Start Django + Celery + FastAPI Collaboration Service together in one terminal
# Run from the fundoonotes/ directory: .\start.ps1

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

# Resolve the collab_service directory (sibling of fundoonotes/)
$repoRoot   = Split-Path -Parent $scriptDir
$collabDir  = Join-Path $repoRoot "collab_service"

Write-Host "==> Running Django migrations..." -ForegroundColor Cyan
python manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "Migration failed. Fix errors above before starting." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==> Running Alembic migrations (collab_service)..." -ForegroundColor Cyan
Push-Location $collabDir
python -m alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "Alembic migration failed. Fix errors above before starting." -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

# Ensure logs directory exists
New-Item -ItemType Directory -Force -Path "$scriptDir\logs" | Out-Null
$celeryOut = "$scriptDir\logs\celery.log"
$celeryErr = "$scriptDir\logs\celery_err.log"
$collabOut = "$scriptDir\logs\collab_service.log"
$collabErr = "$scriptDir\logs\collab_service_err.log"

Write-Host ""
Write-Host "==> Starting Celery worker in background..." -ForegroundColor Cyan

# -P solo is required on Windows (prefork pool does not work on Windows)
$celery = Start-Process -FilePath "python" `
    -ArgumentList "-m celery -A fundoonotes worker --loglevel=info -P solo" `
    -WorkingDirectory $scriptDir `
    -RedirectStandardOutput $celeryOut `
    -RedirectStandardError $celeryErr `
    -PassThru `
    -NoNewWindow

Start-Sleep -Seconds 2

if ($celery.HasExited) {
    Write-Host "ERROR: Celery failed to start. Check logs\celery_err.log" -ForegroundColor Red
    Get-Content $celeryErr
    exit 1
}

Write-Host "    Celery PID: $($celery.Id) - OK" -ForegroundColor Green
Write-Host "    Celery logs: $celeryOut / $celeryErr" -ForegroundColor DarkGray

Write-Host ""
Write-Host "==> Starting FastAPI Collaboration Service in background..." -ForegroundColor Cyan

$collab = Start-Process -FilePath "python" `
    -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload" `
    -WorkingDirectory $collabDir `
    -RedirectStandardOutput $collabOut `
    -RedirectStandardError $collabErr `
    -PassThru `
    -NoNewWindow

Start-Sleep -Seconds 3

if ($collab.HasExited) {
    Write-Host "ERROR: Collaboration Service failed to start. Check logs\collab_service_err.log" -ForegroundColor Red
    Get-Content $collabErr
    Stop-Process -Id $celery.Id -Force -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "    Collab Service PID: $($collab.Id) - OK" -ForegroundColor Green
Write-Host "    Collab logs: $collabOut / $collabErr" -ForegroundColor DarkGray

Write-Host ""
Write-Host "==> Starting Django dev server..." -ForegroundColor Cyan
Write-Host "    Django API:          http://localhost:8000" -ForegroundColor Green
Write-Host "    Django Docs:         http://localhost:8000/api/docs/" -ForegroundColor Green
Write-Host "    Collab Service API:  http://localhost:8001" -ForegroundColor Green
Write-Host "    Collab Service Docs: http://localhost:8001/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop all services." -ForegroundColor Yellow
Write-Host ""

try {
    python manage.py runserver
} finally {
    Write-Host ""
    Write-Host "==> Stopping background services..." -ForegroundColor Cyan
    Stop-Process -Id $celery.Id -Force -ErrorAction SilentlyContinue
    Write-Host "    Celery (PID $($celery.Id)) stopped." -ForegroundColor DarkGray
    Stop-Process -Id $collab.Id -Force -ErrorAction SilentlyContinue
    Write-Host "    Collaboration Service (PID $($collab.Id)) stopped." -ForegroundColor DarkGray
    Write-Host "Done." -ForegroundColor Green
}
