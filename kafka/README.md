# Local Kafka Event Bus

This folder contains a local Apache Kafka stack for the privacy-safe UEH/Tiki matching dataset.

## Prerequisites

Install Docker Desktop and make sure `docker` is available in PowerShell:

```powershell
docker --version
docker compose version
```

No Python Kafka client is required. The producer and consumer use Kafka CLI tools inside the Kafka container.

This stack uses the official Apache Kafka Docker image:

```text
apache/kafka:3.7.2
```

## Start Kafka

From the project root:

```powershell
docker compose -f .\kafka\docker-compose.yml up -d
```

The `kafka-init` service creates these topics automatically:

```powershell
docker compose -f .\kafka\docker-compose.yml logs kafka-init
```

List topics:

```powershell
docker compose -f .\kafka\docker-compose.yml exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
```

## Validate Events Without Publishing

```powershell
& 'C:\Users\Minh Phuc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\scripts\producer_student_matches.py --dry-run --limit 2
```

## Publish Student Match Events

Publishes every row from:

```text
outputs/privacy_layer/student_resource_matches_analytics.csv
```

to:

```text
dataset.analytics.student_matches.v1
```

Command:

```powershell
& 'C:\Users\Minh Phuc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\scripts\producer_student_matches.py
```

Smoke-test only 10 events:

```powershell
& 'C:\Users\Minh Phuc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\scripts\producer_student_matches.py --limit 10
```

## Consume And Check Sample Events

```powershell
& 'C:\Users\Minh Phuc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\scripts\consumer_debug_student_matches.py --max-messages 5 --print-events
```

The consumer checks:

- `payload.student_token` exists and matches `stu_<16 lowercase hex chars>`
- event key equals `payload.student_hash`
- `student_hash` is 64 lowercase hex characters
- forbidden PII keys are absent
- event type is `student_resource_match_created`

## Sink Student Match Events To SQLite

This consumes Kafka events and writes them into:

```text
outputs/kafka/student_matches.db
```

The target table is:

```text
student_resource_matches_events
```

Smoke-test 10 events:

```powershell
& 'C:\Users\Minh Phuc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\scripts\consumer_sink_sqlite.py --max-messages 10
```

Ingest the full analytics topic after publishing all rows:

```powershell
& 'C:\Users\Minh Phuc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\scripts\consumer_sink_sqlite.py --max-messages 12000 --timeout-ms 30000 --recreate-db
```

The sink is idempotent by `event_id`, so re-reading the same Kafka records from the beginning will not duplicate rows already stored in SQLite.

If you have old smoke-test events in Kafka and want a completely clean final run, reset local Kafka first, then publish the full CSV again:

```powershell
docker compose -f .\kafka\docker-compose.yml down
docker compose -f .\kafka\docker-compose.yml up -d
& 'C:\Users\Minh Phuc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\scripts\producer_student_matches.py
& 'C:\Users\Minh Phuc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\scripts\consumer_sink_sqlite.py --max-messages 12000 --timeout-ms 30000 --recreate-db
```

Run this reset/publish sequence again after regenerating the privacy layer, because older Kafka events may not contain newly added fields such as `student_token`.

Invalid records are written to:

```text
outputs/kafka/dead_letter_student_match_events.jsonl
```

## Query The SQLite Sink

```powershell
& 'C:\Users\Minh Phuc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\scripts\query_student_matches_db.py
```

Show fewer rows in each top/sample section:

```powershell
& 'C:\Users\Minh Phuc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\scripts\query_student_matches_db.py --limit 5
```

Machine-readable report:

```powershell
& 'C:\Users\Minh Phuc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\scripts\query_student_matches_db.py --json
```

## Stop Kafka

Keep topic data:

```powershell
docker compose -f .\kafka\docker-compose.yml down
```

Remove topic data too:

```powershell
docker compose -f .\kafka\docker-compose.yml down -v
```

## Important Privacy Rule

Publish `student_resource_matches_analytics.csv`, not `students_protected.csv`.

`students_protected.csv` is only for controlled internal debugging because it still contains masked student codes and initials.

For API and dashboard identifiers, prefer `student_token`. The raw reverse lookup lives only in `.secrets/student_token_mapping_private.csv`.
