from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "outputs" / "kafka" / "student_matches.db"
TABLE = "student_resource_matches_events"

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


def connect_db(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise FileNotFoundError(
            f"SQLite DB not found: {db_path}\n"
            "Run scripts\\consumer_sink_sqlite.py first to create and populate it."
        )
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def table_exists(connection: sqlite3.Connection, table: str) -> bool:
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    ).fetchone()
    return row is not None


def rows_as_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def fetch_all(connection: sqlite3.Connection, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    return rows_as_dicts(connection.execute(sql, params).fetchall())


def fetch_one(connection: sqlite3.Connection, sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any]:
    row = connection.execute(sql, params).fetchone()
    return dict(row) if row else {}


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * len(title))


def print_table(headers: list[str], rows: list[dict[str, Any]]) -> None:
    if not rows:
        print("(no rows)")
        return

    widths = {
        header: max(
            len(header),
            *(len(str(row.get(header, ""))) for row in rows),
        )
        for header in headers
    }
    header_line = " | ".join(header.ljust(widths[header]) for header in headers)
    print(header_line)
    print("-" * len(header_line))
    for row in rows:
        print(" | ".join(str(row.get(header, "")).ljust(widths[header]) for header in headers))


def privacy_check(connection: sqlite3.Connection) -> dict[str, Any]:
    columns = [row["name"] for row in connection.execute(f"PRAGMA table_info({TABLE})").fetchall()]
    forbidden_columns = sorted(FORBIDDEN_PII_KEYS & set(columns))

    raw_event_violations: list[dict[str, Any]] = []
    for row in connection.execute(f"SELECT event_id, raw_event_json FROM {TABLE}"):
        try:
            event = json.loads(row["raw_event_json"])
        except json.JSONDecodeError as error:
            raw_event_violations.append(
                {"event_id": row["event_id"], "paths": [f"invalid JSON in raw_event_json: {error}"]}
            )
            continue
        forbidden_paths = find_forbidden_keys(event)
        if forbidden_paths:
            raw_event_violations.append({"event_id": row["event_id"], "paths": forbidden_paths})
        if len(raw_event_violations) >= 5:
            break

    return {
        "passed": not forbidden_columns and not raw_event_violations,
        "forbidden_columns": forbidden_columns,
        "raw_event_violations": raw_event_violations,
    }


def collect_report(connection: sqlite3.Connection, *, limit: int) -> dict[str, Any]:
    summary = fetch_one(
        connection,
        f"""
        SELECT
            COUNT(*) AS events,
            COUNT(DISTINCT student_token) AS student_tokens,
            COUNT(DISTINCT student_hash) AS students,
            COUNT(DISTINCT major) AS majors,
            COUNT(DISTINCT course) AS courses,
            COUNT(DISTINCT tiki_book_id) AS tiki_books,
            COUNT(DISTINCT repo_doc_id) AS repo_docs,
            MIN(occurred_at) AS first_event_at,
            MAX(occurred_at) AS last_event_at
        FROM {TABLE}
        """,
    )
    latest_run = fetch_one(
        connection,
        """
        SELECT
            topic,
            consumed_records,
            valid_records,
            inserted_records,
            duplicate_records,
            invalid_records,
            started_at,
            finished_at
        FROM sink_runs
        ORDER BY finished_at DESC
        LIMIT 1
        """,
    )
    tiki_confidence = fetch_all(
        connection,
        f"""
        SELECT tiki_confidence AS confidence, COUNT(*) AS events, ROUND(AVG(tiki_score), 2) AS avg_score
        FROM {TABLE}
        GROUP BY tiki_confidence
        ORDER BY events DESC
        """,
    )
    repo_confidence = fetch_all(
        connection,
        f"""
        SELECT repo_confidence AS confidence, COUNT(*) AS events, ROUND(AVG(repo_score), 2) AS avg_score
        FROM {TABLE}
        GROUP BY repo_confidence
        ORDER BY events DESC
        """,
    )
    majors = fetch_all(
        connection,
        f"""
        SELECT major, COUNT(*) AS events, COUNT(DISTINCT student_hash) AS students
        FROM {TABLE}
        GROUP BY major
        ORDER BY events DESC, major
        LIMIT ?
        """,
        (limit,),
    )
    top_tiki_books = fetch_all(
        connection,
        f"""
        SELECT
            tiki_book_id,
            tiki_title,
            COUNT(*) AS matches,
            ROUND(AVG(tiki_score), 2) AS avg_score,
            MIN(tiki_confidence) AS confidence
        FROM {TABLE}
        GROUP BY tiki_book_id, tiki_title
        ORDER BY matches DESC, avg_score DESC
        LIMIT ?
        """,
        (limit,),
    )
    top_repo_docs = fetch_all(
        connection,
        f"""
        SELECT
            repo_doc_id,
            repo_title,
            COUNT(*) AS matches,
            ROUND(AVG(repo_score), 2) AS avg_score,
            MIN(repo_confidence) AS confidence
        FROM {TABLE}
        GROUP BY repo_doc_id, repo_title
        ORDER BY matches DESC, avg_score DESC
        LIMIT ?
        """,
        (limit,),
    )
    sample_matches = fetch_all(
        connection,
        f"""
        SELECT
            major,
            student_token,
            course,
            tiki_title,
            tiki_score,
            repo_title,
            repo_score
        FROM {TABLE}
        ORDER BY (COALESCE(tiki_score, 0) + COALESCE(repo_score, 0)) DESC
        LIMIT ?
        """,
        (limit,),
    )
    return {
        "summary": summary,
        "latest_run": latest_run,
        "privacy_check": privacy_check(connection),
        "tiki_confidence": tiki_confidence,
        "repo_confidence": repo_confidence,
        "majors": majors,
        "top_tiki_books": top_tiki_books,
        "top_repo_docs": top_repo_docs,
        "sample_matches": sample_matches,
    }


def print_report(report: dict[str, Any]) -> None:
    print_section("SQLite Student Match DB")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))

    print_section("Latest Sink Run")
    print(json.dumps(report["latest_run"], ensure_ascii=False, indent=2))

    print_section("Privacy Check")
    privacy = report["privacy_check"]
    if privacy["passed"]:
        print("PASS: no forbidden PII columns or raw-event keys were found.")
    else:
        print(json.dumps(privacy, ensure_ascii=False, indent=2))

    print_section("Tiki Confidence")
    print_table(["confidence", "events", "avg_score"], report["tiki_confidence"])

    print_section("Repository Confidence")
    print_table(["confidence", "events", "avg_score"], report["repo_confidence"])

    print_section("Top Majors")
    print_table(["major", "events", "students"], report["majors"])

    print_section("Top Tiki Books")
    print_table(["tiki_book_id", "tiki_title", "matches", "avg_score", "confidence"], report["top_tiki_books"])

    print_section("Top UEH Repository Docs")
    print_table(["repo_doc_id", "repo_title", "matches", "avg_score", "confidence"], report["top_repo_docs"])

    print_section("Sample Strong Matches")
    print_table(["major", "student_token", "course", "tiki_title", "tiki_score", "repo_title", "repo_score"], report["sample_matches"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query and validate the SQLite student match event sink.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="SQLite database path.")
    parser.add_argument("--limit", type=int, default=8, help="Rows to show for top/sample sections.")
    parser.add_argument("--json", action="store_true", help="Print the report as JSON.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    connection = connect_db(args.db)
    if not table_exists(connection, TABLE):
        raise RuntimeError(f"Table not found: {TABLE}. Run scripts\\consumer_sink_sqlite.py first.")

    report = collect_report(connection, limit=args.limit)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report)

    if not report["privacy_check"]["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
