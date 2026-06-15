"""Simulate UEH Smart Library user behavior events.

The generated dataset is intentionally synthetic. It is based on the four
Smart Library systems described in the project report:

- Sierra: circulation / print collection behavior
- DSpace: UEH Repository behavior
- EBSCO Discovery Service / OneSearch: search behavior
- OpenAthens: authentication and access behavior

The script uses protected student tokens from the privacy layer, so no raw
student identifiers are written to the analytics outputs.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STUDENTS = ROOT / "outputs" / "privacy_layer" / "students_protected.csv"
DEFAULT_MATCHES = ROOT / "outputs" / "privacy_layer" / "student_resource_matches_analytics.csv"
DEFAULT_OUTPUT = ROOT / "outputs" / "behavior_simulation"


@dataclass(frozen=True)
class Student:
    student_token: str
    major: str
    major_norm: str
    cohort: str
    courses: list[str]


@dataclass(frozen=True)
class ResourceMatch:
    student_token: str
    major: str
    course: str
    tiki_book_id: str
    tiki_title: str
    repo_doc_id: str
    repo_title: str
    repo_collection: str
    repo_url: str


EVENT_WEIGHTS = {
    "login": 0.1,
    "session_start": 0.1,
    "access_granted": 0.2,
    "access_denied": 0.0,
    "session_end": 0.1,
    "search_query": 0.6,
    "filter_apply": 0.4,
    "search_result_click": 1.2,
    "open_database": 0.8,
    "open_article": 1.5,
    "repository_search": 0.8,
    "view_metadata": 1.0,
    "open_fulltext": 2.2,
    "download_pdf": 4.0,
    "view_collection": 0.7,
    "item_view": 0.8,
    "hold_request": 3.0,
    "borrow": 5.0,
    "renew": 3.0,
    "return": 2.0,
}


CHANNELS = ["library_portal", "mobile_app", "touchscreen_kiosk", "remote_web"]
DEVICES = ["desktop", "mobile", "tablet", "kiosk"]
ZONES = [
    "remote",
    "Ask-us-now area",
    "Conversational study",
    "Quiet Study",
    "Meeting rooms",
    "Reading and Mini-auditorium",
]
DATABASES = ["EBSCO", "ScienceDirect", "ProQuest", "Emerald", "iG Library", "Open Educational Resources"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: Iterable[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def parse_courses(value: str) -> list[str]:
    return [item.strip() for item in str(value or "").split(";") if item.strip()]


def load_students(path: Path, limit: int) -> list[Student]:
    rows = read_csv(path)
    students: list[Student] = []
    for row in rows[:limit]:
        students.append(
            Student(
                student_token=row["student_token"],
                major=row.get("major", ""),
                major_norm=row.get("major_norm", ""),
                cohort=row.get("cohort", ""),
                courses=parse_courses(row.get("courses", "")),
            )
        )
    return students


def load_matches(path: Path) -> dict[str, list[ResourceMatch]]:
    by_student: dict[str, list[ResourceMatch]] = defaultdict(list)
    for row in read_csv(path):
        match = ResourceMatch(
            student_token=row["student_token"],
            major=row.get("major", ""),
            course=row.get("course", ""),
            tiki_book_id=str(row.get("tiki_book_id", "")),
            tiki_title=row.get("tiki_title", ""),
            repo_doc_id=str(row.get("repo_doc_id", "")),
            repo_title=row.get("repo_title", ""),
            repo_collection=row.get("repo_collection", ""),
            repo_url=row.get("repo_url", ""),
        )
        by_student[match.student_token].append(match)
    return by_student


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def random_timestamp(rng: random.Random, start: datetime, end: datetime) -> datetime:
    seconds = int((end - start).total_seconds())
    return start + timedelta(seconds=rng.randint(0, seconds))


def event_id(source_system: str, timestamp: datetime, student_token: str) -> str:
    raw = f"{source_system}:{timestamp.isoformat()}:{student_token}:{uuid.uuid4()}"
    return "evt_" + uuid.uuid5(uuid.NAMESPACE_URL, raw).hex[:24]


def choose_match(rng: random.Random, matches: list[ResourceMatch], student: Student) -> ResourceMatch:
    if matches:
        return rng.choice(matches)
    fallback_course = rng.choice(student.courses) if student.courses else student.major
    return ResourceMatch(
        student_token=student.student_token,
        major=student.major,
        course=fallback_course,
        tiki_book_id="SIM_BOOK_UNKNOWN",
        tiki_title=f"Tai lieu tham khao cho {fallback_course}",
        repo_doc_id="UEH/SIM_UNKNOWN",
        repo_title=f"Tai lieu so ve {fallback_course}",
        repo_collection="SIMULATED_COLLECTION",
        repo_url="",
    )


def make_event(
    rng: random.Random,
    student: Student,
    source_system: str,
    event_type: str,
    timestamp: datetime,
    session_id: str,
    resource_type: str = "",
    resource_id: str = "",
    resource_title: str = "",
    query_text: str = "",
    access_result: str = "",
    channel: str = "",
    device_type: str = "",
    location_zone: str = "",
    metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "event_id": event_id(source_system, timestamp, student.student_token),
        "student_token": student.student_token,
        "major": student.major,
        "major_norm": student.major_norm,
        "cohort": student.cohort,
        "source_system": source_system,
        "event_type": event_type,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "resource_title": resource_title,
        "query_text": query_text,
        "timestamp": timestamp.isoformat(timespec="seconds"),
        "session_id": session_id,
        "channel": channel or rng.choice(CHANNELS),
        "device_type": device_type or rng.choice(DEVICES),
        "location_zone": location_zone or rng.choice(ZONES),
        "access_result": access_result,
        "duration_seconds": rng.randint(15, 2400),
        "interaction_weight": EVENT_WEIGHTS.get(event_type, 0.0),
        "is_simulated": True,
        "privacy_level": "analytics_mock",
        "metadata_json": json.dumps(metadata or {}, ensure_ascii=False),
    }


def make_openathens_session(
    rng: random.Random,
    student: Student,
    start_time: datetime,
    session_id: str,
    channel: str,
    device_type: str,
) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    access_ok = rng.random() > 0.04
    events.append(
        make_event(
            rng,
            student,
            "openathens",
            "login",
            start_time,
            session_id,
            access_result="success",
            channel=channel,
            device_type=device_type,
            metadata={"auth_method": "ueh_email_sso"},
        )
    )
    events.append(
        make_event(
            rng,
            student,
            "openathens",
            "session_start",
            start_time + timedelta(seconds=rng.randint(2, 20)),
            session_id,
            access_result="active",
            channel=channel,
            device_type=device_type,
            metadata={"role": "student"},
        )
    )
    events.append(
        make_event(
            rng,
            student,
            "openathens",
            "access_granted" if access_ok else "access_denied",
            start_time + timedelta(seconds=rng.randint(20, 180)),
            session_id,
            resource_type="licensed_database",
            resource_id=rng.choice(DATABASES),
            access_result="granted" if access_ok else "denied",
            channel=channel,
            device_type=device_type,
            metadata={"access_provider": "OpenAthens"},
        )
    )
    return events


def make_onesearch_events(
    rng: random.Random,
    student: Student,
    match: ResourceMatch,
    base_time: datetime,
    session_id: str,
    channel: str,
    device_type: str,
) -> list[dict[str, object]]:
    query = rng.choice([match.course, student.major, f"{match.course} {student.major}", match.repo_title[:60]])
    database = rng.choice(DATABASES)
    return [
        make_event(
            rng,
            student,
            "ebsco_onesearch",
            "search_query",
            base_time,
            session_id,
            query_text=query,
            channel=channel,
            device_type=device_type,
            metadata={"search_scope": "all_collections"},
        ),
        make_event(
            rng,
            student,
            "ebsco_onesearch",
            rng.choice(["filter_apply", "search_result_click", "open_database"]),
            base_time + timedelta(seconds=rng.randint(20, 220)),
            session_id,
            resource_type="discovery_result",
            resource_id=database if rng.random() < 0.35 else match.repo_doc_id,
            resource_title=database if rng.random() < 0.35 else match.repo_title,
            query_text=query,
            channel=channel,
            device_type=device_type,
            metadata={"database": database, "result_rank": rng.randint(1, 20)},
        ),
    ]


def make_dspace_events(
    rng: random.Random,
    student: Student,
    match: ResourceMatch,
    base_time: datetime,
    session_id: str,
    channel: str,
    device_type: str,
) -> list[dict[str, object]]:
    event_types = ["repository_search", "view_metadata", "open_fulltext", "download_pdf", "view_collection"]
    selected = rng.sample(event_types, k=rng.randint(2, 4))
    rows = []
    for offset, event_type_name in enumerate(selected):
        rows.append(
            make_event(
                rng,
                student,
                "dspace_repository",
                event_type_name,
                base_time + timedelta(seconds=offset * rng.randint(35, 180)),
                session_id,
                resource_type="digital_repository",
                resource_id=match.repo_doc_id,
                resource_title=match.repo_title,
                query_text=match.course if event_type_name == "repository_search" else "",
                access_result="granted",
                channel=channel,
                device_type=device_type,
                metadata={"collection": match.repo_collection, "url": match.repo_url},
            )
        )
    return rows


def make_sierra_events(
    rng: random.Random,
    student: Student,
    match: ResourceMatch,
    base_time: datetime,
    session_id: str,
    channel: str,
    device_type: str,
) -> list[dict[str, object]]:
    event_flow = ["item_view"]
    if rng.random() < 0.62:
        event_flow.append("hold_request")
    if rng.random() < 0.38:
        event_flow.append("borrow")
        if rng.random() < 0.22:
            event_flow.append("renew")
        if rng.random() < 0.58:
            event_flow.append("return")

    rows = []
    for offset, event_type_name in enumerate(event_flow):
        rows.append(
            make_event(
                rng,
                student,
                "sierra_circulation",
                event_type_name,
                base_time + timedelta(minutes=offset * rng.randint(3, 90)),
                session_id,
                resource_type="print_book",
                resource_id=f"SIERRA_BOOK_{match.tiki_book_id}",
                resource_title=match.tiki_title,
                access_result="available",
                channel=channel,
                device_type=device_type,
                location_zone=rng.choice([zone for zone in ZONES if zone != "remote"]),
                metadata={
                    "simulated_opac_code": f"OPAC-SIM-{match.tiki_book_id}",
                    "catalog_proxy_source": "matched_tiki_book_metadata",
                },
            )
        )
    return rows


def simulate_events(
    students: list[Student],
    matches_by_student: dict[str, list[ResourceMatch]],
    seed: int,
    min_sessions: int,
    max_sessions: int,
    start_date: datetime,
    end_date: datetime,
) -> list[dict[str, object]]:
    rng = random.Random(seed)
    events: list[dict[str, object]] = []

    for student in students:
        student_matches = matches_by_student.get(student.student_token, [])
        sessions = rng.randint(min_sessions, max_sessions)
        for _ in range(sessions):
            session_id = "ses_" + uuid.uuid5(uuid.NAMESPACE_URL, f"{student.student_token}:{rng.random()}").hex[:16]
            base_time = random_timestamp(rng, start_date, end_date)
            channel = rng.choices(CHANNELS, weights=[0.36, 0.34, 0.08, 0.22], k=1)[0]
            device_type = {
                "library_portal": "desktop",
                "mobile_app": "mobile",
                "touchscreen_kiosk": "kiosk",
                "remote_web": rng.choice(["desktop", "tablet"]),
            }[channel]
            match = choose_match(rng, student_matches, student)

            events.extend(make_openathens_session(rng, student, base_time, session_id, channel, device_type))

            intent = rng.choices(
                ["search", "repository", "circulation", "mixed"],
                weights=[0.30, 0.30, 0.22, 0.18],
                k=1,
            )[0]

            if intent in {"search", "mixed"}:
                events.extend(
                    make_onesearch_events(
                        rng,
                        student,
                        match,
                        base_time + timedelta(minutes=rng.randint(1, 8)),
                        session_id,
                        channel,
                        device_type,
                    )
                )
            if intent in {"repository", "mixed"}:
                events.extend(
                    make_dspace_events(
                        rng,
                        student,
                        match,
                        base_time + timedelta(minutes=rng.randint(3, 18)),
                        session_id,
                        channel,
                        device_type,
                    )
                )
            if intent in {"circulation", "mixed"}:
                events.extend(
                    make_sierra_events(
                        rng,
                        student,
                        match,
                        base_time + timedelta(minutes=rng.randint(4, 30)),
                        session_id,
                        channel,
                        device_type,
                    )
                )

            events.append(
                make_event(
                    rng,
                    student,
                    "openathens",
                    "session_end",
                    base_time + timedelta(minutes=rng.randint(12, 180)),
                    session_id,
                    access_result="closed",
                    channel=channel,
                    device_type=device_type,
                    metadata={"close_reason": "normal"},
                )
            )

    events.sort(key=lambda row: (str(row["timestamp"]), str(row["student_token"]), str(row["event_id"])))
    return events


def summarize_events(events: list[dict[str, object]], students: list[Student]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    system_counter = Counter(row["source_system"] for row in events)
    type_counter = Counter((row["source_system"], row["event_type"]) for row in events)
    student_counter = Counter(row["student_token"] for row in events)

    system_summary = [
        {
            "source_system": system,
            "events": count,
            "percentage": round(100.0 * count / len(events), 2) if events else 0,
        }
        for system, count in sorted(system_counter.items())
    ]

    event_type_summary = [
        {
            "source_system": system,
            "event_type": event_type_name,
            "events": count,
            "avg_interaction_weight": EVENT_WEIGHTS.get(event_type_name, 0.0),
        }
        for (system, event_type_name), count in sorted(type_counter.items())
    ]

    major_by_student = {student.student_token: student.major for student in students}
    major_counts: dict[str, int] = defaultdict(int)
    major_students: dict[str, set[str]] = defaultdict(set)
    for token, count in student_counter.items():
        major = major_by_student.get(token, "")
        major_counts[major] += count
        major_students[major].add(token)

    major_summary = [
        {
            "major": major,
            "students": len(tokens),
            "events": major_counts[major],
            "avg_events_per_student": round(major_counts[major] / len(tokens), 2) if tokens else 0,
        }
        for major, tokens in sorted(major_students.items(), key=lambda item: (-major_counts[item[0]], item[0]))
    ]

    return system_summary, event_type_summary, major_summary


def write_readme(output_dir: Path, student_count: int, event_count: int) -> None:
    content = f"""# Smart Library Behavior Simulation

Dataset nay la du lieu mo phong hanh vi nguoi dung cho UEH Smart Library.

## Quy mo

```text
students = {student_count}
events = {event_count}
```

## Bon he thong mo phong

```text
Sierra: muon, tra, gia han, dat truoc sach
DSpace / UEH Repository: xem metadata, doc full-text, tai PDF
EBSCO Discovery Service / OneSearch: tim kiem, loc, click ket qua
OpenAthens: dang nhap SSO, phien truy cap, quyen truy cap
```

## File output

```text
smart_library_behavior_events.csv
system_event_summary.csv
event_type_summary.csv
major_behavior_summary.csv
```

## Luu y bao cao

Day la dataset mo phong, khong phai log that cua UEH. Dataset chi dung student_token da an danh,
khong chua ma sinh vien goc hoac ho ten sinh vien.
"""
    (output_dir / "README_behavior_simulation.md").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate UEH Smart Library behavior events.")
    parser.add_argument("--students", type=int, default=2000, help="Number of protected students to simulate.")
    parser.add_argument("--min-sessions", type=int, default=3, help="Minimum sessions per student.")
    parser.add_argument("--max-sessions", type=int, default=8, help="Maximum sessions per student.")
    parser.add_argument("--seed", type=int, default=20260606, help="Random seed for reproducible output.")
    parser.add_argument("--students-file", type=Path, default=DEFAULT_STUDENTS)
    parser.add_argument("--matches-file", type=Path, default=DEFAULT_MATCHES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    students = load_students(args.students_file, args.students)
    if not students:
        raise RuntimeError(f"No students loaded from {args.students_file}")

    matches_by_student = load_matches(args.matches_file)
    start_date = datetime(2026, 1, 1, 7, 0, 0)
    end_date = datetime(2026, 5, 31, 22, 0, 0)

    events = simulate_events(
        students=students,
        matches_by_student=matches_by_student,
        seed=args.seed,
        min_sessions=args.min_sessions,
        max_sessions=args.max_sessions,
        start_date=start_date,
        end_date=end_date,
    )

    event_fields = [
        "event_id",
        "student_token",
        "major",
        "major_norm",
        "cohort",
        "source_system",
        "event_type",
        "resource_type",
        "resource_id",
        "resource_title",
        "query_text",
        "timestamp",
        "session_id",
        "channel",
        "device_type",
        "location_zone",
        "access_result",
        "duration_seconds",
        "interaction_weight",
        "is_simulated",
        "privacy_level",
        "metadata_json",
    ]
    write_csv(args.output_dir / "smart_library_behavior_events.csv", events, event_fields)

    system_summary, event_type_summary, major_summary = summarize_events(events, students)
    write_csv(args.output_dir / "system_event_summary.csv", system_summary, ["source_system", "events", "percentage"])
    write_csv(
        args.output_dir / "event_type_summary.csv",
        event_type_summary,
        ["source_system", "event_type", "events", "avg_interaction_weight"],
    )
    write_csv(
        args.output_dir / "major_behavior_summary.csv",
        major_summary,
        ["major", "students", "events", "avg_events_per_student"],
    )
    write_readme(args.output_dir, len(students), len(events))

    print("Smart Library behavior simulation finished.")
    print(f"Students: {len(students)}")
    print(f"Events: {len(events)}")
    print(f"Output folder: {args.output_dir}")
    print("Important outputs:")
    print("- smart_library_behavior_events.csv")
    print("- system_event_summary.csv")
    print("- event_type_summary.csv")
    print("- major_behavior_summary.csv")


if __name__ == "__main__":
    main()
