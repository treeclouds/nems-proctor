# Set environment variables
$env:DATABASE_URL = "postgresql://nems-proctor:P@ssw0rd123@127.0.0.1:5432/nems-proctor-db"
$env:CELERY_BROKER_URL = "redis://redis:6379"
$env:USE_DOCKER = "no"

# Get existing jobs
$existingJobs = Get-Job

# Stop existing jobs if any
if ($existingJobs) {
    Stop-Job
    Write-Output "Stopped existing jobs."
}

# Start CML processes in the background
Start-Job -ScriptBlock { python manage.py runserver }
Start-Job -ScriptBlock { npm run dev }

# Display information about running jobs (optional)
Get-Job
