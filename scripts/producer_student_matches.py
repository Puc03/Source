from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
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
DEFAULT_CSV = ROOT / "outputs" / "privacy_layer" / "student_resource_matches_analytics.csv"
DEFAULT_SCHEMA = ROOT / "schemas" / "student_resource_match.schema.json"
DEFAULT_COMPOSE = ROOT / "kafka" / "docker-compose.yml"
DEFAULT_TOPIC = "dataset.analytics.student_matches.v1"
DEFAULT_BOOTSTRAP = "localhost:9092"
DEFAULT_DLQ = ROOT / "outputs" / "kafka" / "dead_letter_student_matches.jsonl"

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

PAYLOAD_COLUMNS = [
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
]

INT_COLUMNS = {
    "cohort",
    "course_order",
    "tiki_book_id",
    "tiki_review_count",
    "repo_year",
    "repo_views",
}

FLOAT_COLUMNS = {
    "tiki_score",
    "tiki_price",
    "tiki_rating_average",
    "tiki_quantity_sold",
    "repo_score",
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


def clean_cell(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null", "<na>"}:
        return None
    return text


def parse_value(column: str, value: str | None) -> Any:
    text = clean_cell(value)
    if text is None:
        return None
    if column in INT_COLUMNS:
        try:
            return int(float(text))
        except ValueError:
            return text
    if column in FLOAT_COLUMNS:
        try:
            return float(text)
        except ValueError:
            return text
    return text


def event_time() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def row_to_event(row: dict[str, str], *, trace_id: str) -> dict[str, Any]:
    payload = {column: parse_value(column, row.get(column)) for column in PAYLOAD_COLUMNS}
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": "student_resource_match_created",
        "schema_version": "1.0",
        "occurred_at": event_time(),
        "source": "privacy-layer-export",
        "trace_id": trace_id,
        "privacy_level": row.get("privacy_level") or "internal",
        "payload": payload,
    }


def validate_event(event: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for key in schema.get("required", []):
        value = event.get(key)
        if value is None or value == "":
            errors.append(f"missing top-level field: {key}")

    extra_top = set(event) - set(schema.get("properties", {}))
    if extra_top:
        errors.append(f"unexpected top-level fields: {sorted(extra_top)}")

    payload = event.get("payload")
    if not isinstance(payload, dict):
        return errors + ["payload must be an object"]

    forbidden = sorted(FORBIDDEN_PII_KEYS & set(payload))
    if forbidden:
        errors.append(f"forbidden PII keys in payload: {forbidden}")

    missing_payload = sorted(key for key in REQUIRED_PAYLOAD if payload.get(key) in {None, ""})
    if missing_payload:
        errors.append(f"missing payload fields: {missing_payload}")

    student_hash = payload.get("student_hash")
    if not isinstance(student_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", student_hash):
        errors.append("student_hash must be 64 lowercase hex characters")
    student_token = payload.get("student_token")
    if not isinstance(student_token, str) or not re.fullmatch(r"stu_[0-9a-f]{16}", student_token):
        errors.append("student_token must match stu_ plus 16 lowercase hex characters")

    for score_key in ["tiki_score", "repo_score"]:
        score = payload.get(score_key)
        if score is not None and (not isinstance(score, (int, float)) or not 0 <= score <= 100):
            errors.append(f"{score_key} must be a number between 0 and 100")

    for confidence_key in ["tiki_confidence", "repo_confidence"]:
        confidence = payload.get(confidence_key)
        if confidence not in {"high", "medium", "low", None}:
            errors.append(f"{confidence_key} has invalid value: {confidence}")

    return errors


def iter_events(csv_path: Path, schema_path: Path, *, trace_id: str, limit: int | None) -> tuple[list[str], list[dict[str, Any]]]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    lines: list[str] = []
    dead_letters: list[dict[str, Any]] = []

    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        forbidden_columns = sorted(FORBIDDEN_PII_KEYS & set(reader.fieldnames or []))
        if forbidden_columns:
            raise ValueError(f"CSV contains forbidden PII columns: {forbidden_columns}")

        for index, row in enumerate(reader, start=1):
            if limit is not None and len(lines) >= limit:
                break
            event = row_to_event(row, trace_id=trace_id)
            errors = validate_event(event, schema)
            if errors:
                dead_letters.append({"row_number": index, "errors": errors, "row": row, "event": event})
                continue
            key = event["payload"]["student_hash"]
            lines.append(f"{key}\t{json.dumps(event, ensure_ascii=False, separators=(',', ':'))}\n")

    return lines, dead_letters


def publish_with_docker_cli(lines: list[str], *, compose_file: Path, topic: str, bootstrap_server: str) -> None:
    if shutil.which("docker") is None:
        raise RuntimeError("Docker CLI was not found in PATH. Install Docker Desktop or add docker.exe to PATH.")

    command = [
        "docker",
        "compose",
        "-f",
        str(compose_file),
        "exec",
        "-T",
        "kafka",
        "/opt/kafka/bin/kafka-console-producer.sh",
        "--bootstrap-server",
        bootstrap_server,
        "--topic",
        topic,
        "--property",
        "parse.key=true",
        "--property",
        "key.separator=\t",
    ]
    process = subprocess.run(
        command,
        input="".join(lines),
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        raise RuntimeError(
            "Kafka publish failed.\n"
            f"Command: {' '.join(command)}\n"
            f"STDOUT:\n{process.stdout}\n"
            f"STDERR:\n{process.stderr}"
        )


def write_dead_letters(path: Path, dead_letters: list[dict[str, Any]]) -> None:
    if not dead_letters:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in dead_letters:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish privacy-safe student-resource match events to Kafka.")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Input analytics CSV.")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="JSON schema path.")
    parser.add_argument("--compose-file", type=Path, default=DEFAULT_COMPOSE, help="Kafka Docker Compose file.")
    parser.add_argument("--topic", default=DEFAULT_TOPIC, help="Target Kafka topic.")
    parser.add_argument("--bootstrap-server", default=DEFAULT_BOOTSTRAP, help="Bootstrap server from inside Kafka container.")
    parser.add_argument("--trace-id", default=f"privacy-export-{uuid.uuid4()}", help="Trace ID for this publish run.")
    parser.add_argument("--limit", type=int, default=None, help="Limit events for smoke tests.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print sample events without publishing.")
    parser.add_argument("--dead-letter-file", type=Path, default=DEFAULT_DLQ, help="Where invalid CSV rows are written.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    lines, dead_letters = iter_events(args.csv, args.schema, trace_id=args.trace_id, limit=args.limit)
    write_dead_letters(args.dead_letter_file, dead_letters)

    if dead_letters:
        print(f"Invalid rows: {len(dead_letters)}. Dead letters written to {args.dead_letter_file}", file=sys.stderr)
        raise SystemExit(1)

    if args.dry_run:
        print(json.dumps({"valid_events": len(lines), "topic": args.topic, "trace_id": args.trace_id}, ensure_ascii=False))
        for line in lines[:3]:
            key, event_json = line.rstrip("\n").split("\t", 1)
            print(json.dumps({"key": key, "event": json.loads(event_json)}, ensure_ascii=False, indent=2))
        return

    publish_with_docker_cli(lines, compose_file=args.compose_file, topic=args.topic, bootstrap_server=args.bootstrap_server)
    print(json.dumps({"published_events": len(lines), "topic": args.topic, "trace_id": args.trace_id}, ensure_ascii=False))


if __name__ == "__main__":
    main()
