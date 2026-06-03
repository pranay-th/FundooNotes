# start.ps1 - Start Django + Celery together in one terminal
# Run from the fundoonotes/ directory: .\start.ps1

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

Write-Host "==> Running migrations..." -ForegroundColor Cyan
python manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "Migration failed. Fix errors above before starting." -ForegroundColor Red
    exit 1
}

# Ensure logs directory exists
New-Item -ItemType Directory -Force -Path "$scriptDir\logs" | Out-Null
$celeryOut = "$scriptDir\logs\celery.log"
$celeryErr = "$scriptDir\logs\celery_err.log"

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
Write-Host "==> Starting Django dev server..." -ForegroundColor Cyan
Write-Host "    API:  http://localhost:8000" -ForegroundColor Green
Write-Host "    Docs: http://localhost:8000/api/docs/" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop." -ForegroundColor Yellow
Write-Host ""

try {
    python manage.py runserver
} finally {
    Write-Host ""
    Write-Host "==> Stopping Celery worker (PID $($celery.Id))..." -ForegroundColor Cyan
    Stop-Process -Id $celery.Id -Force -ErrorAction SilentlyContinue
    Write-Host "Done." -ForegroundColor Green
}
