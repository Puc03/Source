from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CLEAN_DIR = ROOT / "outputs" / "cleaned_matching"
PRIVACY_DIR = ROOT / "outputs" / "privacy_layer"
SECRET_DIR = ROOT / ".secrets"
SECRET_PATH = SECRET_DIR / "student_hash_secret"
LEGACY_SECRET_PATH = PRIVACY_DIR / ".student_hash_secret"
PRIVATE_TOKEN_MAP_PATH = SECRET_DIR / "student_token_mapping_private.csv"

SENSITIVE_COLUMNS = {
    "student_id",
    "student_code",
    "student_name",
    "student_name_norm",
    "ma_sv",
    "ho_ten",
    "user_id",
}

ANALYTICS_FORBIDDEN_COLUMNS = SENSITIVE_COLUMNS | {
    "student_code_masked",
    "student_name_initials",
}

SOURCE_FILES = {
    "students_clean": CLEAN_DIR / "ueh_students_clean.csv",
    "student_courses_clean": CLEAN_DIR / "ueh_student_courses_clean.csv",
    "student_resource_matches": CLEAN_DIR / "student_resource_matches.csv",
    "course_resource_matches": CLEAN_DIR / "course_resource_matches.csv",
    "tiki_books_clean": CLEAN_DIR / "tiki_books_clean.csv",
    "ueh_repository_clean": CLEAN_DIR / "ueh_repository_clean.csv",
}


def read_csv(path: Path, **kwargs) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig", **kwargs)


def load_or_create_secret() -> tuple[str, bool]:
    env_secret = os.environ.get("STUDENT_HASH_SECRET", "").strip()
    if env_secret:
        return env_secret, False

    SECRET_DIR.mkdir(parents=True, exist_ok=True)
    if SECRET_PATH.exists():
        return SECRET_PATH.read_text(encoding="utf-8").strip(), False
    if LEGACY_SECRET_PATH.exists():
        secret = LEGACY_SECRET_PATH.read_text(encoding="utf-8").strip()
        SECRET_PATH.write_text(secret, encoding="utf-8")
        LEGACY_SECRET_PATH.unlink()
        try:
            os.chmod(SECRET_PATH, 0o600)
        except OSError:
            pass
        return secret, False

    secret = secrets.token_urlsafe(48)
    SECRET_PATH.write_text(secret, encoding="utf-8")
    try:
        os.chmod(SECRET_PATH, 0o600)
    except OSError:
        pass
    return secret, True


def student_hash(student_code: object, secret: str) -> str:
    value = "" if pd.isna(student_code) else str(student_code).strip()
    return hmac.new(secret.encode("utf-8"), value.encode("utf-8"), hashlib.sha256).hexdigest()


def student_token(student_code: object, secret: str) -> str:
    value = "" if pd.isna(student_code) else str(student_code).strip()
    digest = hmac.new(secret.encode("utf-8"), f"student_token:{value}".encode("utf-8"), hashlib.sha256).hexdigest()
    return f"stu_{digest[:16]}"


def mask_student_code(student_code: object) -> str:
    value = "" if pd.isna(student_code) else re.sub(r"\D", "", str(student_code))
    if not value:
        return ""
    visible_digits = max(len(value) - 5, 0)
    return value[:visible_digits] + "*" * min(5, len(value))


def name_initials(name: object) -> str:
    if pd.isna(name):
        return ""
    parts = [part for part in str(name).strip().split() if part]
    return ".".join(part[0].upper() for part in parts) + "." if parts else ""


def secret_fingerprint(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()[:16]


def add_privacy_fields(
    df: pd.DataFrame,
    secret: str,
    *,
    code_col: str = "student_code",
    include_debug_masks: bool,
) -> pd.DataFrame:
    out = df.copy()
    out["student_token"] = out[code_col].map(lambda value: student_token(value, secret))
    out["student_hash"] = out[code_col].map(lambda value: student_hash(value, secret))
    if include_debug_masks:
        out["student_code_masked"] = out[code_col].map(mask_student_code)
        if "student_name" in out.columns:
            out["student_name_initials"] = out["student_name"].map(name_initials)
    out["privacy_level"] = "internal"
    out["pii_removed"] = True
    out["pii_fields_removed"] = "student_id; student_code; student_name; student_name_norm"
    out["privacy_transform_version"] = "privacy_v1"
    return out


def drop_sensitive_columns(df: pd.DataFrame, *, keep_masks: bool) -> pd.DataFrame:
    drop_cols = [col for col in SENSITIVE_COLUMNS if col in df.columns]
    if not keep_masks:
        drop_cols.extend([col for col in ["student_code_masked", "student_name_initials"] if col in df.columns])
    return df.drop(columns=drop_cols, errors="ignore")


def reorder_front(df: pd.DataFrame, front_cols: list[str]) -> pd.DataFrame:
    cols = [col for col in front_cols if col in df.columns]
    cols.extend([col for col in df.columns if col not in cols])
    return df[cols]


def make_student_token_maps(students: pd.DataFrame, secret: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = students.copy()
    base["student_token"] = base["student_code"].map(lambda value: student_token(value, secret))
    base["student_hash"] = base["student_code"].map(lambda value: student_hash(value, secret))
    base["student_code_masked"] = base["student_code"].map(mask_student_code)
    base["student_name_initials"] = base["student_name"].map(name_initials)
    base["mapping_scope"] = "student_identity"
    base["token_version"] = "token_v1"
    base["privacy_transform_version"] = "privacy_v1"
    base["created_at"] = datetime.now(timezone.utc).isoformat()

    private_cols = [
        "student_token",
        "student_hash",
        "student_id",
        "student_code",
        "student_name",
        "student_name_norm",
        "student_code_masked",
        "student_name_initials",
        "gender",
        "major",
        "major_norm",
        "cohort",
        "mapping_scope",
        "token_version",
        "privacy_transform_version",
        "created_at",
    ]
    private = base[[col for col in private_cols if col in base.columns]].copy()

    protected_cols = [
        "student_token",
        "student_hash",
        "student_code_masked",
        "student_name_initials",
        "gender",
        "major",
        "major_norm",
        "cohort",
        "mapping_scope",
        "token_version",
        "privacy_transform_version",
    ]
    protected = base[protected_cols].copy()
    protected["privacy_level"] = "restricted"
    protected["contains_raw_pii"] = False
    protected["contains_debug_masks"] = True
    return private, reorder_front(
        protected,
        [
            "student_token",
            "student_hash",
            "student_code_masked",
            "student_name_initials",
            "gender",
            "major",
            "major_norm",
            "cohort",
            "privacy_level",
            "contains_raw_pii",
            "contains_debug_masks",
            "mapping_scope",
            "token_version",
            "privacy_transform_version",
        ],
    )


def make_students_protected(students: pd.DataFrame, secret: str) -> pd.DataFrame:
    protected = add_privacy_fields(students, secret, include_debug_masks=True)
    protected = drop_sensitive_columns(protected, keep_masks=True)
    return reorder_front(
        protected,
        [
            "student_token",
            "student_hash",
            "student_code_masked",
            "student_name_initials",
            "gender",
            "major",
            "major_norm",
            "cohort",
            "courses",
            "course_count",
            "privacy_level",
            "pii_removed",
            "pii_fields_removed",
            "privacy_transform_version",
        ],
    )


def make_student_courses_protected(student_courses: pd.DataFrame, secret: str) -> pd.DataFrame:
    protected = add_privacy_fields(student_courses, secret, include_debug_masks=True)
    protected = drop_sensitive_columns(protected, keep_masks=True)
    return reorder_front(
        protected,
        [
            "student_token",
            "student_hash",
            "student_code_masked",
            "student_name_initials",
            "gender",
            "major",
            "major_norm",
            "cohort",
            "course_order",
            "course",
            "course_norm",
            "privacy_level",
            "pii_removed",
            "pii_fields_removed",
            "privacy_transform_version",
        ],
    )


def make_student_matches_analytics(matches: pd.DataFrame, secret: str) -> pd.DataFrame:
    analytics = add_privacy_fields(matches, secret, include_debug_masks=False)
    analytics = drop_sensitive_columns(analytics, keep_masks=False)
    analytics["privacy_level"] = "internal"
    return reorder_front(
        analytics,
        [
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
            "repo_doc_id",
            "repo_title",
            "repo_score",
            "repo_confidence",
            "privacy_level",
            "pii_removed",
            "pii_fields_removed",
            "privacy_transform_version",
        ],
    )


def make_course_matches_analytics(course_matches: pd.DataFrame) -> pd.DataFrame:
    analytics = course_matches.copy()
    analytics["privacy_level"] = "internal"
    analytics["pii_removed"] = True
    analytics["pii_fields_removed"] = "not_applicable"
    analytics["privacy_transform_version"] = "privacy_v1"
    return analytics


def validate_outputs(outputs: dict[str, pd.DataFrame], raw_students: pd.DataFrame, secret: str) -> tuple[pd.DataFrame, list[str]]:
    checks: list[dict[str, object]] = []
    failures: list[str] = []

    def add_check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})
        if not passed:
            failures.append(f"{name}: {detail}")

    students_protected = outputs["students_protected"]
    student_courses_protected = outputs["student_courses_protected"]
    student_matches_analytics = outputs["student_resource_matches_analytics"]
    token_map_protected = outputs["student_token_map_protected"]

    expected_hashes = raw_students["student_code"].map(lambda value: student_hash(value, secret))
    expected_tokens = raw_students["student_code"].map(lambda value: student_token(value, secret))

    add_check(
        "students_protected_row_count_matches_source",
        len(students_protected) == len(raw_students),
        {"source": len(raw_students), "protected": len(students_protected)},
    )
    add_check(
        "student_hash_unique_per_student",
        students_protected["student_hash"].nunique() == len(raw_students),
        {"unique_hashes": int(students_protected["student_hash"].nunique()), "students": len(raw_students)},
    )
    add_check(
        "student_hash_is_hmac_sha256_length",
        students_protected["student_hash"].astype(str).str.fullmatch(r"[0-9a-f]{64}").all(),
        "all hashes are 64 lowercase hex characters",
    )
    add_check(
        "student_hash_reproducible",
        students_protected["student_hash"].reset_index(drop=True).equals(expected_hashes.reset_index(drop=True)),
        "protected hashes match deterministic HMAC output",
    )
    add_check(
        "student_token_unique_per_student",
        students_protected["student_token"].nunique() == len(raw_students),
        {"unique_tokens": int(students_protected["student_token"].nunique()), "students": len(raw_students)},
    )
    add_check(
        "student_token_format",
        students_protected["student_token"].astype(str).str.fullmatch(r"stu_[0-9a-f]{16}").all(),
        "all tokens match stu_ plus 16 lowercase hex characters",
    )
    add_check(
        "student_token_reproducible",
        students_protected["student_token"].reset_index(drop=True).equals(expected_tokens.reset_index(drop=True)),
        "protected tokens match deterministic HMAC token output",
    )
    add_check(
        "student_token_map_protected_row_count",
        len(token_map_protected) == len(raw_students),
        {"source": len(raw_students), "token_map": len(token_map_protected)},
    )
    add_check(
        "student_token_map_protected_has_no_raw_pii_columns",
        not sorted(set(token_map_protected.columns) & SENSITIVE_COLUMNS),
        sorted(set(token_map_protected.columns) & SENSITIVE_COLUMNS) or "no raw PII columns",
    )

    for output_name, frame in outputs.items():
        if output_name.endswith("_analytics"):
            leaked_cols = sorted(set(frame.columns) & ANALYTICS_FORBIDDEN_COLUMNS)
            add_check(
                f"{output_name}_has_no_forbidden_pii_columns",
                not leaked_cols,
                leaked_cols or "no forbidden columns",
            )
        leaked_raw_codes = []
        if "student_hash" in frame.columns:
            sample = frame.astype(str).head(1000).to_string(index=False)
            for value in raw_students["student_code"].astype(str).head(20):
                if value in sample:
                    leaked_raw_codes.append(value)
            add_check(
                f"{output_name}_sample_has_no_raw_student_codes",
                not leaked_raw_codes,
                leaked_raw_codes or "first 1000 rows do not contain sampled raw student codes",
            )

    add_check(
        "student_courses_protected_row_count",
        len(student_courses_protected) == 12000,
        len(student_courses_protected),
    )
    add_check(
        "student_matches_analytics_row_count",
        len(student_matches_analytics) == 12000,
        len(student_matches_analytics),
    )
    add_check(
        "student_matches_analytics_has_all_matches",
        student_matches_analytics["tiki_book_id"].notna().all() and student_matches_analytics["repo_doc_id"].notna().all(),
        {
            "missing_tiki": int(student_matches_analytics["tiki_book_id"].isna().sum()),
            "missing_repo": int(student_matches_analytics["repo_doc_id"].isna().sum()),
        },
    )

    return pd.DataFrame(checks), failures


def build_report(
    outputs: dict[str, pd.DataFrame],
    validation: pd.DataFrame,
    *,
    secret_created: bool,
    secret: str,
) -> dict[str, object]:
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "privacy_transform_version": "privacy_v1",
        "hashing": {
            "algorithm": "HMAC-SHA256",
            "identifier_source": "student_code",
            "hash_column": "student_hash",
            "secret_source": "STUDENT_HASH_SECRET environment variable or local .student_hash_secret file",
            "secret_created_this_run": secret_created,
            "secret_fingerprint_sha256_first16": secret_fingerprint(secret),
        },
        "tokenization": {
            "algorithm": "HMAC-SHA256 with student_token domain prefix",
            "token_column": "student_token",
            "token_format": "stu_<16 lowercase hex chars>",
            "public_or_analytics_usage": "Use student_token for API/dashboard identifiers; keep student_hash for legacy joins and Kafka compatibility.",
            "private_mapping_path": str(PRIVATE_TOKEN_MAP_PATH),
            "protected_mapping_path": str(PRIVACY_DIR / "student_token_map_protected.csv"),
        },
        "policy": {
            "restricted_pii_columns_removed_from_analytics": sorted(ANALYTICS_FORBIDDEN_COLUMNS),
            "student_code_mask_policy": "show prefix and mask the final 5 digits",
            "protected_outputs_keep_debug_masks": True,
            "analytics_outputs_keep_debug_masks": False,
            "kafka_recommended_inputs": [
                "student_resource_matches_analytics.csv",
                "course_resource_matches_analytics.csv",
            ],
        },
        "outputs": {
            name: {
                "rows": int(len(frame)),
                "columns": list(frame.columns),
                "path": str(PRIVACY_DIR / f"{name}.csv"),
            }
            for name, frame in outputs.items()
        },
        "validation": validation.to_dict("records"),
    }


def write_readme(report: dict[str, object]) -> None:
    lines = [
        "# Privacy Layer Outputs",
        "",
        "These files are generated from the cleaned and matched datasets.",
        "",
        "## Key Rules",
        "",
        "- `student_hash` is generated with HMAC-SHA256 from `student_code`.",
        "- `student_token` is a stable short pseudonymous ID for API, dashboard, and downstream analytics use.",
        "- The private raw token mapping is stored in `.secrets/student_token_mapping_private.csv`, not in this output folder.",
        "- Analytics files do not contain raw student IDs, student codes, names, masked codes, or initials.",
        "- Protected files keep initials and `student_code_masked`, where the final 5 digits are hidden.",
        "- Kafka, dashboards, and APIs should use analytics files by default.",
        "",
        "## Files",
        "",
    ]
    for name, meta in report["outputs"].items():
        lines.append(f"- `{name}.csv`: {meta['rows']} rows")
    lines.extend(
        [
            "",
            "## Validation",
            "",
        ]
    )
    for row in report["validation"]:
        status = "PASS" if row["passed"] else "FAIL"
        lines.append(f"- {status}: {row['check']} - {row['detail']}")
    (PRIVACY_DIR / "README_privacy_layer.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    missing = [str(path) for path in SOURCE_FILES.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing source files: {missing}")

    PRIVACY_DIR.mkdir(parents=True, exist_ok=True)
    secret, secret_created = load_or_create_secret()

    students = read_csv(SOURCE_FILES["students_clean"], dtype={"student_code": "string"})
    student_courses = read_csv(SOURCE_FILES["student_courses_clean"], dtype={"student_code": "string"})
    student_matches = read_csv(SOURCE_FILES["student_resource_matches"], dtype={"student_code": "string"})
    course_matches = read_csv(SOURCE_FILES["course_resource_matches"])
    tiki_books = read_csv(SOURCE_FILES["tiki_books_clean"])
    repo = read_csv(SOURCE_FILES["ueh_repository_clean"])
    private_token_map, protected_token_map = make_student_token_maps(students, secret)

    outputs = {
        "student_token_map_protected": protected_token_map,
        "students_protected": make_students_protected(students, secret),
        "student_courses_protected": make_student_courses_protected(student_courses, secret),
        "student_resource_matches_analytics": make_student_matches_analytics(student_matches, secret),
        "course_resource_matches_analytics": make_course_matches_analytics(course_matches),
        "tiki_books_public": tiki_books,
        "ueh_repository_public": repo,
    }

    validation, failures = validate_outputs(outputs, students, secret)
    outputs["privacy_validation"] = validation

    report = build_report(outputs, validation, secret_created=secret_created, secret=secret)

    for name, frame in outputs.items():
        frame.to_csv(PRIVACY_DIR / f"{name}.csv", index=False, encoding="utf-8-sig")
    private_token_map.to_csv(PRIVATE_TOKEN_MAP_PATH, index=False, encoding="utf-8-sig")
    try:
        os.chmod(PRIVATE_TOKEN_MAP_PATH, 0o600)
    except OSError:
        pass

    (PRIVACY_DIR / "privacy_audit_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_readme(report)

    print(json.dumps({"output_dir": str(PRIVACY_DIR), "failures": failures, "validation": report["validation"]}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
