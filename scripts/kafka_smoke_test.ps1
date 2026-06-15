param(
    [int]$Limit = 10
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Python = "C:\Users\Minh Phuc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$Compose = Join-Path $Root "kafka\docker-compose.yml"
$DockerConfig = Join-Path $Root ".docker"
New-Item -ItemType Directory -Path $DockerConfig -Force | Out-Null
$env:DOCKER_CONFIG = $DockerConfig
$env:PYTHONIOENCODING = "utf-8"

function Assert-Success {
    param([string]$Step)
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE"
    }
}

Write-Host "Starting Kafka..."
docker compose -f $Compose up -d
Assert-Success "Starting Kafka"

Write-Host "Topics:"
docker compose -f $Compose exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
Assert-Success "Listing topics"

Write-Host "Publishing $Limit student match events..."
& $Python (Join-Path $Root "scripts\producer_student_matches.py") --limit $Limit
Assert-Success "Publishing student match events"

Write-Host "Consuming and validating $Limit events..."
& $Python (Join-Path $Root "scripts\consumer_debug_student_matches.py") --max-messages $Limit --print-events
Assert-Success "Consuming student match events"
