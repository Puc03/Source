from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COMPOSE = ROOT / "kafka" / "docker-compose.yml"
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


def consume_with_docker_cli(*, compose_file: Path, topic: str, bootstrap_server: str, max_messages: int, timeout_ms: int) -> str:
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
        "/opt/kafka/bin/kafka-console-consumer.sh",
        "--bootstrap-server",
        bootstrap_server,
        "--topic",
        topic,
        "--from-beginning",
        "--max-messages",
        str(max_messages),
        "--timeout-ms",
        str(timeout_ms),
        "--property",
        "print.key=true",
        "--property",
        "key.separator=\t",
    ]
    process = subprocess.run(
        command,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    # kafka-console-consumer may emit a timeout warning on stderr after max messages are read.
    if process.returncode != 0 and not process.stdout.strip():
        raise RuntimeError(
            "Kafka consume failed.\n"
            f"Command: {' '.join(command)}\n"
            f"STDOUT:\n{process.stdout}\n"
            f"STDERR:\n{process.stderr}"
        )
    return process.stdout


def parse_records(output: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        if "\t" in line:
            key, event_json = line.split("\t", 1)
        else:
            key, event_json = None, line
        event = json.loads(event_json)
        records.append({"key": key, "event": event})
    return records


def validate_records(records: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for index, record in enumerate(records, start=1):
        event = record["event"]
        payload = event.get("payload", {})
        forbidden_paths = find_forbidden_keys(event)
        if forbidden_paths:
            errors.append(f"message {index} contains forbidden PII keys: {forbidden_paths}")

        student_hash = payload.get("student_hash")
        if not isinstance(student_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", student_hash):
            errors.append(f"message {index} has invalid student_hash")
        student_token = payload.get("student_token")
        if not isinstance(student_token, str) or not re.fullmatch(r"stu_[0-9a-f]{16}", student_token):
            errors.append(f"message {index} has invalid student_token")

        if record.get("key") and record["key"] != student_hash:
            errors.append(f"message {index} key does not equal payload.student_hash")

        if event.get("event_type") != "student_resource_match_created":
            errors.append(f"message {index} has unexpected event_type: {event.get('event_type')}")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Consume and validate sample student match events from Kafka.")
    parser.add_argument("--compose-file", type=Path, default=DEFAULT_COMPOSE)
    parser.add_argument("--topic", default=DEFAULT_TOPIC)
    parser.add_argument("--bootstrap-server", default=DEFAULT_BOOTSTRAP)
    parser.add_argument("--max-messages", type=int, default=5)
    parser.add_argument("--timeout-ms", type=int, default=10000)
    parser.add_argument("--print-events", action="store_true", help="Print full consumed events.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = consume_with_docker_cli(
        compose_file=args.compose_file,
        topic=args.topic,
        bootstrap_server=args.bootstrap_server,
        max_messages=args.max_messages,
        timeout_ms=args.timeout_ms,
    )
    records = parse_records(output)
    errors = validate_records(records)

    summary = {
        "topic": args.topic,
        "messages_consumed": len(records),
        "privacy_validation_passed": not errors,
        "errors": errors,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.print_events:
        print(json.dumps(records[: args.max_messages], ensure_ascii=False, indent=2))
    if not records or errors:
        raise SystemExit(1)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
