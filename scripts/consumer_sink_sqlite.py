from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COMPOSE = ROOT / "kafka" / "docker-compose.yml"
DEFAULT_DB = ROOT / "outputs" / "kafka" / "student_matches.db"
DEFAULT_DLQ = ROOT / "outputs" / "kafka" / "dead_letter_student_match_events.jsonl"
DEFAULT_TOPIC = "dataset.analytics.student_matches.v1"
DEFAULT_BOOTSTRAP = "localhost:9092"

FORBIDDEN_PII_KEYS = {
    "student_id",
    "student_code",
    "student_name",
    "student_name_norm",
    "student_code_masked",
    "student_name_initials",
    "ma_sv",
    "ho_ten",
    "user_id",
}

REQUIRED_TOP_LEVEL = {
    "event_id",
    "event_type",
    "schema_version",
    "occurred_at",
    "source",
    "trace_id",
    "privacy_level",
    "payload",
}

REQUIRED_PAYLOAD = {
    "student_token",
    "student_hash",
    "major",
    "cohort",
    "course_order",
    "course",
    "tiki_book_id",
    "tiki_title",
    "tiki_score",
    "tiki_confidence",
    "repo_doc_id",
    "repo_title",
    "repo_score",
    "repo_confidence",
}

INT_FIELDS = {
    "cohort",
    "course_order",
    "tiki_book_id",
    "tiki_review_count",
    "repo_year",
    "repo_views",
}

FLOAT_FIELDS = {
    "tiki_score",
    "tiki_price",
    "tiki_rating_average",
    "tiki_quantity_sold",
    "repo_score",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def find_forbidden_keys(value: Any, path: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_PII_KEYS:
                found.append(child_path)
            found.extend(find_forbidden_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(find_forbidden_keys(child, f"{path}[{index}]"))
    return found


def is_blank(value: Any) -> bool:
    return value is None or value == ""


def consume_with_docker_cli(
    *,
    compose_file: Path,
    topic: str,
    bootstrap_server: str,
    max_messages: int,
    timeout_ms: int,
    from_beginning: bool,
) -> tuple[str, str]:
    if shutil.which("docker") is None:
        raise RuntimeError("Docker CLI was not found in PATH. Install Docker Desktop or add docker.exe to PATH.")

    docker_config = ROOT / ".docker"
    docker_config.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["DOCKER_CONFIG"] = str(docker_config)

    command = [
        "docker",
        "compose",
        "-f",
        str(compose_file),
        "exec",
        "-T",
        "kafka",
        "/opt/kafka/bin/kafka-console-consumer.sh",
        "--bootstrap-server",
        bootstrap_server,
        "--topic",
        topic,
        "--max-messages",
        str(max_messages),
        "--timeout-ms",
        str(timeout_ms),
        "--property",
        "print.key=true",
        "--property",
        "key.separator=\t",
    ]
    if from_beginning:
        command.insert(command.index("--max-messages"), "--from-beginning")

    process = subprocess.run(
        command,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=env,
    )

    # The console consumer can return non-zero after a timeout even when it read valid records.
    if process.returncode != 0 and not process.stdout.strip():
        raise RuntimeError(
            "Kafka consume failed.\n"
            f"Command: {' '.join(command)}\n"
            f"STDOUT:\n{process.stdout}\n"
            f"STDERR:\n{process.stderr}"
        )
    return process.stdout, process.stderr


def parse_records(output: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    dead_letters: list[dict[str, Any]] = []

    for line_number, line in enumerate(output.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        if "\t" not in line:
            dead_letters.append(
                {
                    "line_number": line_number,
                    "errors": ["Kafka record is missing a tab key separator"],
                    "raw_line": line,
                }
            )
            continue

        key, event_json = line.split("\t", 1)
        try:
            event = json.loads(event_json)
        except json.JSONDecodeError as error:
            dead_letters.append(
                {
                    "line_number": line_number,
                    "key": key,
                    "errors": [f"Invalid JSON: {error}"],
                    "raw_line": line,
                }
            )
            continue
        records.append({"line_number": line_number, "key": key, "event": event})

    return records, dead_letters


def validate_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    event = record.get("event")
    if not isinstance(event, dict):
        return ["event must be a JSON object"]

    missing_top = sorted(field for field in REQUIRED_TOP_LEVEL if is_blank(event.get(field)))
    if missing_top:
        errors.append(f"missing top-level fields: {missing_top}")

    forbidden_paths = find_forbidden_keys(event)
    if forbidden_paths:
        errors.append(f"forbidden PII keys found: {forbidden_paths}")

    if event.get("event_type") != "student_resource_match_created":
        errors.append(f"unexpected event_type: {event.get('event_type')}")
    if event.get("schema_version") != "1.0":
        errors.append(f"unexpected schema_version: {event.get('schema_version')}")
    if event.get("privacy_level") != "internal":
        errors.append(f"unexpected privacy_level: {event.get('privacy_level')}")

    payload = event.get("payload")
    if not isinstance(payload, dict):
        return errors + ["payload must be a JSON object"]

    missing_payload = sorted(field for field in REQUIRED_PAYLOAD if is_blank(payload.get(field)))
    if missing_payload:
        errors.append(f"missing payload fields: {missing_payload}")

    student_hash = payload.get("student_hash")
    if not isinstance(student_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", student_hash):
        errors.append("payload.student_hash must be 64 lowercase hex characters")
    student_token = payload.get("student_token")
    if not isinstance(student_token, str) or not re.fullmatch(r"stu_[0-9a-f]{16}", student_token):
        errors.append("payload.student_token must match stu_ plus 16 lowercase hex characters")
    if record.get("key") and record["key"] != student_hash:
        errors.append("Kafka key does not match payload.student_hash")

    for score_field in ("tiki_score", "repo_score"):
        score = payload.get(score_field)
        if score is not None and (not isinstance(score, (int, float)) or not 0 <= score <= 100):
            errors.append(f"payload.{score_field} must be a number between 0 and 100")

    for confidence_field in ("tiki_confidence", "repo_confidence"):
        confidence = payload.get(confidence_field)
        if confidence not in {"high", "medium", "low", None}:
            errors.append(f"payload.{confidence_field} has invalid value: {confidence}")

    return errors


def coerce_payload_value(payload: dict[str, Any], field: str) -> Any:
    value = payload.get(field)
    if value in {"", "nan", "NaN", "None", "null"}:
        return None
    if value is None:
        return None
    if field in INT_FIELDS:
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return value
    if field in FLOAT_FIELDS:
        try:
            return float(value)
        except (TypeError, ValueError):
            return value
    return value


def connect_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def recreate_db(db_path: Path) -> None:
    for path in (db_path, Path(f"{db_path}-wal"), Path(f"{db_path}-shm")):
        if path.exists():
            path.unlink()


def init_db(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS student_resource_matches_events (
            event_id TEXT PRIMARY KEY,
            event_key TEXT NOT NULL,
            event_type TEXT NOT NULL,
            schema_version TEXT NOT NULL,
            occurred_at TEXT NOT NULL,
            source TEXT NOT NULL,
            trace_id TEXT NOT NULL,
            privacy_level TEXT NOT NULL,
            student_token TEXT NOT NULL,
            student_hash TEXT NOT NULL,
            gender TEXT,
            major TEXT,
            major_norm TEXT,
            cohort INTEGER,
            course_order INTEGER,
            course TEXT,
            course_norm TEXT,
            tiki_book_id INTEGER,
            tiki_title TEXT,
            tiki_score REAL,
            tiki_confidence TEXT,
            tiki_match_reason TEXT,
            tiki_price REAL,
            tiki_rating_average REAL,
            tiki_review_count INTEGER,
            tiki_quantity_sold REAL,
            tiki_source_keys TEXT,
            tiki_url TEXT,
            repo_doc_id TEXT,
            repo_title TEXT,
            repo_score REAL,
            repo_confidence TEXT,
            repo_match_reason TEXT,
            repo_year INTEGER,
            repo_collection TEXT,
            repo_views INTEGER,
            repo_authors TEXT,
            repo_url TEXT,
            raw_event_json TEXT NOT NULL,
            ingested_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_student_matches_student_hash
            ON student_resource_matches_events(student_hash);
        CREATE INDEX IF NOT EXISTS idx_student_matches_student_token
            ON student_resource_matches_events(student_token);
        CREATE INDEX IF NOT EXISTS idx_student_matches_major_course
            ON student_resource_matches_events(major, course);
        CREATE INDEX IF NOT EXISTS idx_student_matches_tiki_confidence
            ON student_resource_matches_events(tiki_confidence);
        CREATE INDEX IF NOT EXISTS idx_student_matches_repo_confidence
            ON student_resource_matches_events(repo_confidence);
        CREATE INDEX IF NOT EXISTS idx_student_matches_tiki_book_id
            ON student_resource_matches_events(tiki_book_id);
        CREATE INDEX IF NOT EXISTS idx_student_matches_repo_doc_id
            ON student_resource_matches_events(repo_doc_id);
        CREATE INDEX IF NOT EXISTS idx_student_matches_occurred_at
            ON student_resource_matches_events(occurred_at);

        CREATE TABLE IF NOT EXISTS sink_runs (
            run_id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            consumed_records INTEGER NOT NULL,
            valid_records INTEGER NOT NULL,
            inserted_records INTEGER NOT NULL,
            duplicate_records INTEGER NOT NULL,
            invalid_records INTEGER NOT NULL,
            started_at TEXT NOT NULL,
            finished_at TEXT NOT NULL
        );
        """
    )


def event_to_row(record: dict[str, Any], *, ingested_at: str) -> dict[str, Any]:
    event = record["event"]
    payload = event["payload"]
    row = {
        "event_id": event["event_id"],
        "event_key": record["key"],
        "event_type": event["event_type"],
        "schema_version": event["schema_version"],
        "occurred_at": event["occurred_at"],
        "source": event["source"],
        "trace_id": event["trace_id"],
        "privacy_level": event["privacy_level"],
        "raw_event_json": json.dumps(event, ensure_ascii=False, separators=(",", ":")),
        "ingested_at": ingested_at,
    }
    for field in (
        "student_hash",
        "student_token",
        "gender",
        "major",
        "major_norm",
        "cohort",
        "course_order",
        "course",
        "course_norm",
        "tiki_book_id",
        "tiki_title",
        "tiki_score",
        "tiki_confidence",
        "tiki_match_reason",
        "tiki_price",
        "tiki_rating_average",
        "tiki_review_count",
        "tiki_quantity_sold",
        "tiki_source_keys",
        "tiki_url",
        "repo_doc_id",
        "repo_title",
        "repo_score",
        "repo_confidence",
        "repo_match_reason",
        "repo_year",
        "repo_collection",
        "repo_views",
        "repo_authors",
        "repo_url",
    ):
        row[field] = coerce_payload_value(payload, field)
    return row


def insert_records(
    connection: sqlite3.Connection,
    records: list[dict[str, Any]],
    *,
    topic: str,
    parse_dead_letters: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    started_at = utc_now()
    ingested_at = started_at
    columns = [
        "event_id",
        "event_key",
        "event_type",
        "schema_version",
        "occurred_at",
        "source",
        "trace_id",
        "privacy_level",
        "student_token",
        "student_hash",
        "gender",
        "major",
        "major_norm",
        "cohort",
        "course_order",
        "course",
        "course_norm",
        "tiki_book_id",
        "tiki_title",
        "tiki_score",
        "tiki_confidence",
        "tiki_match_reason",
        "tiki_price",
        "tiki_rating_average",
        "tiki_review_count",
        "tiki_quantity_sold",
        "tiki_source_keys",
        "tiki_url",
        "repo_doc_id",
        "repo_title",
        "repo_score",
        "repo_confidence",
        "repo_match_reason",
        "repo_year",
        "repo_collection",
        "repo_views",
        "repo_authors",
        "repo_url",
        "raw_event_json",
        "ingested_at",
    ]
    placeholders = ", ".join(f":{column}" for column in columns)
    insert_sql = f"""
        INSERT OR IGNORE INTO student_resource_matches_events ({", ".join(columns)})
        VALUES ({placeholders})
    """

    dead_letters = list(parse_dead_letters)
    valid = 0
    inserted = 0
    duplicates = 0

    with connection:
        for record in records:
            errors = validate_record(record)
            if errors:
                dead_letters.append(
                    {
                        "line_number": record.get("line_number"),
                        "key": record.get("key"),
                        "errors": errors,
                        "event": record.get("event"),
                    }
                )
                continue

            valid += 1
            cursor = connection.execute(insert_sql, event_to_row(record, ingested_at=ingested_at))
            if cursor.rowcount == 1:
                inserted += 1
            else:
                duplicates += 1

        finished_at = utc_now()
        connection.execute(
            """
            INSERT INTO sink_runs (
                run_id,
                topic,
                consumed_records,
                valid_records,
                inserted_records,
                duplicate_records,
                invalid_records,
                started_at,
                finished_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                topic,
                len(records) + len(parse_dead_letters),
                valid,
                inserted,
                duplicates,
                len(dead_letters),
                started_at,
                finished_at,
            ),
        )

    summary = {
        "topic": topic,
        "db": str(DEFAULT_DB),
        "consumed_records": len(records) + len(parse_dead_letters),
        "valid_records": valid,
        "inserted_records": inserted,
        "duplicate_records": duplicates,
        "invalid_records": len(dead_letters),
        "privacy_validation_passed": len(dead_letters) == 0,
    }
    return summary, dead_letters


def write_dead_letters(path: Path, dead_letters: list[dict[str, Any]]) -> None:
    if not dead_letters:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    written_at = utc_now()
    with path.open("a", encoding="utf-8") as handle:
        for item in dead_letters:
            handle.write(json.dumps({"written_at": written_at, **item}, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Consume student match Kafka events and sink them into SQLite.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="SQLite database path.")
    parser.add_argument("--compose-file", type=Path, default=DEFAULT_COMPOSE, help="Kafka Docker Compose file.")
    parser.add_argument("--topic", default=DEFAULT_TOPIC, help="Source Kafka topic.")
    parser.add_argument("--bootstrap-server", default=DEFAULT_BOOTSTRAP, help="Bootstrap server inside the Kafka container.")
    parser.add_argument("--max-messages", type=int, default=100, help="Maximum Kafka messages to read in one run.")
    parser.add_argument("--timeout-ms", type=int, default=10000, help="Kafka consumer timeout in milliseconds.")
    parser.add_argument("--dead-letter-file", type=Path, default=DEFAULT_DLQ, help="JSONL file for invalid records.")
    parser.add_argument("--no-from-beginning", dest="from_beginning", action="store_false", help="Read only new messages.")
    parser.add_argument("--allow-empty", action="store_true", help="Do not fail when Kafka returns zero messages.")
    parser.add_argument("--recreate-db", action="store_true", help="Delete and rebuild the target SQLite DB before ingest.")
    parser.set_defaults(from_beginning=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output, stderr = consume_with_docker_cli(
        compose_file=args.compose_file,
        topic=args.topic,
        bootstrap_server=args.bootstrap_server,
        max_messages=args.max_messages,
        timeout_ms=args.timeout_ms,
        from_beginning=args.from_beginning,
    )
    records, parse_dead_letters = parse_records(output)
    if not records and not parse_dead_letters and not args.allow_empty:
        print("No Kafka records were consumed. Start Kafka and publish events first.", file=sys.stderr)
        if stderr.strip():
            print(stderr.strip(), file=sys.stderr)
        raise SystemExit(1)

    if args.recreate_db:
        recreate_db(args.db)
    connection = connect_db(args.db)
    init_db(connection)
    summary, dead_letters = insert_records(
        connection,
        records,
        topic=args.topic,
        parse_dead_letters=parse_dead_letters,
    )
    summary["db"] = str(args.db)
    summary["dead_letter_file"] = str(args.dead_letter_file) if dead_letters else None
    write_dead_letters(args.dead_letter_file, dead_letters)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if dead_letters:
        raise SystemExit(1)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
