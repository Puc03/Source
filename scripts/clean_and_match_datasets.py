from __future__ import annotations

import ast
import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs" / "cleaned_matching"

SOURCE_FILES = {
    "tiki": Path(r"C:\Users\Minh Phuc\Downloads\tiki_books (2).csv"),
    "students": Path(r"C:\Users\Minh Phuc\Downloads\mock_ueh_students_2000.csv"),
    "repo": Path(r"C:\Users\Minh Phuc\Downloads\ueh_repository_raw.csv"),
}


STOPWORDS = {
    "a",
    "an",
    "and",
    "book",
    "books",
    "by",
    "for",
    "in",
    "of",
    "on",
    "sach",
    "the",
    "to",
    "va",
    "voi",
    "cua",
    "cac",
    "nhung",
    "mot",
    "cho",
    "trong",
    "theo",
    "la",
    "co",
    "duoc",
}

PHRASE_SYNONYMS_RAW = {
    "an toàn thông tin": ["cyber security", "cybersecurity", "information security"],
    "bảo hiểm": ["insurance"],
    "bất động sản": ["real estate"],
    "blockchain": ["distributed ledger"],
    "cơ sở dữ liệu": ["database", "data base"],
    "công nghệ thông tin": ["information technology", "it"],
    "đàm phán": ["negotiation"],
    "đầu tư": ["investment", "investing"],
    "điện toán đám mây": ["cloud computing"],
    "dữ liệu": ["data"],
    "dữ liệu lớn": ["big data"],
    "fintech": ["financial technology"],
    "hệ thống thông tin": ["information system", "information systems"],
    "hải quan": ["customs"],
    "học máy": ["machine learning"],
    "kế toán": ["accounting"],
    "kiểm toán": ["audit", "auditing"],
    "kinh doanh quốc tế": ["international business"],
    "kinh tế": ["economics", "economy"],
    "lập trình": ["programming"],
    "logistics": ["supply chain"],
    "luật": ["law", "legal"],
    "marketing số": ["digital marketing", "online marketing"],
    "mạng máy tính": ["computer network", "networking"],
    "ngân hàng": ["banking", "bank"],
    "phân tích dữ liệu": ["data analysis", "analytics"],
    "phát triển phần mềm": ["software development", "software engineering", "kỹ nghệ phần mềm", "công nghệ phần mềm"],
    "kiểm thử xâm nhập": ["penetration testing", "pentest"],
    "kiểm toán hệ thống thông tin": ["it audit", "information system audit", "kiểm toán công nghệ thông tin"],
    "kiến trúc máy tính": ["computer architecture"],
    "quản lý chuỗi cung ứng": ["supply chain management"],
    "quản trị cơ sở dữ liệu": ["database administration", "database management", "cơ sở dữ liệu quan hệ"],
    "quản trị kênh phân phối": ["distribution channel", "marketing channels", "sales channels", "kênh bán hàng"],
    "quản trị nền tảng số": ["digital platform", "platform business", "platform"],
    "quản trị": ["management", "administration"],
    "quản trị kinh doanh": ["business administration", "business management"],
    "rủi ro": ["risk"],
    "sap": ["erp"],
    "sản xuất nội dung số": ["digital content", "content creation", "content marketing"],
    "thanh toán số": ["digital payment", "payment", "thanh toán điện tử"],
    "thiết kế ux/ui": ["ux research", "ux design", "ui design", "user experience", "user interface", "thiết kế giao diện"],
    "thị trường chứng khoán": ["stock market", "securities market"],
    "thương mại điện tử": ["ecommerce", "e commerce", "electronic commerce"],
    "thương mại quốc tế": ["international trade"],
    "trí tuệ nhân tạo": ["artificial intelligence", "ai"],
    "xử lý tín hiệu số": ["digital signal processing", "signal processing"],
    "trực quan hóa dữ liệu": ["data visualization", "visualization"],
    "tài chính": ["finance", "financial"],
    "ux ui": ["user experience", "user interface"],
    "xuất nhập khẩu": ["import export", "export import"],
}

SPECIAL_TOKENS = {
    "ai",
    "bds",
    "bim",
    "erp",
    "gis",
    "ifrs",
    "sap",
    "seo",
    "sem",
    "ui",
    "ux",
}


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).replace("\ufeff", " ").replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def norm_text(value: object) -> str:
    text = strip_accents(clean_text(value)).lower()
    text = text.replace("đ", "d")
    text = re.sub(r"[^0-9a-zA-Z]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def words(value: object) -> list[str]:
    base = norm_text(value)
    if not base:
        return []
    return [w for w in base.split() if len(w) > 1 and w not in STOPWORDS]


def tokens_plus(value: object, max_ngram: int = 3) -> set[str]:
    base_words = words(value)
    result = set(base_words)
    for n in range(2, max_ngram + 1):
        for i in range(0, len(base_words) - n + 1):
            result.add("_".join(base_words[i : i + n]))
    return result


PHRASE_SYNONYMS = [
    (norm_text(phrase), tokens_plus(" ".join(synonyms)))
    for phrase, synonyms in PHRASE_SYNONYMS_RAW.items()
]


def expand_query_tokens(value: object) -> set[str]:
    text_norm = norm_text(value)
    result = tokens_plus(value)
    for phrase_norm, synonym_tokens in PHRASE_SYNONYMS:
        if phrase_norm and phrase_norm in text_norm:
            result.update(synonym_tokens)
    return result


def stable_unique(values: list[object]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        text = clean_text(value)
        key = norm_text(text)
        if text and key not in seen:
            seen.add(key)
            out.append(text)
    return out


def join_unique(series: pd.Series) -> str:
    return "; ".join(stable_unique(series.tolist()))


def parse_course_list(value: object) -> list[str]:
    if pd.isna(value):
        return []
    text = clean_text(value)
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list):
            return [clean_text(item) for item in parsed if clean_text(item)]
    except (SyntaxError, ValueError):
        pass
    return [part.strip() for part in re.split(r";|,", text) if part.strip()]


def dedupe_authors(value: object) -> str:
    parts = re.split(r";|,", clean_text(value))
    return "; ".join(stable_unique(parts))


def make_idf(token_sets: list[set[str]]) -> dict[str, float]:
    doc_freq: Counter[str] = Counter()
    for token_set in token_sets:
        doc_freq.update(token_set)
    n_docs = max(len(token_sets), 1)
    return {token: math.log((n_docs + 1) / (freq + 1)) + 1 for token, freq in doc_freq.items()}


def weighted_ratio(query_tokens: set[str], resource_tokens: set[str], idf: dict[str, float]) -> float:
    if not query_tokens:
        return 0.0
    default_weight = math.log(len(idf) + 1) if idf else 1.0
    denominator = sum(idf.get(token, default_weight) for token in query_tokens)
    if denominator == 0:
        return 0.0
    numerator = sum(idf.get(token, default_weight) for token in query_tokens if token in resource_tokens)
    return numerator / denominator


def confidence(score: float, resource_type: str) -> str:
    if resource_type == "tiki_book":
        if score >= 65:
            return "high"
        if score >= 30:
            return "medium"
        return "low"
    if score >= 60:
        return "high"
    if score >= 25:
        return "medium"
    return "low"


def score_reason(
    *,
    course_norm: str,
    major_norm: str,
    title_norm: str,
    secondary_norm: str,
    title_ratio: float,
    secondary_ratio: float,
    major_title_ratio: float,
) -> str:
    reasons: list[str] = []
    if course_norm and len(course_norm) >= 3 and course_norm in title_norm:
        reasons.append("exact_course_in_title")
    elif title_ratio >= 0.55:
        reasons.append("strong_course_tokens_in_title")
    elif title_ratio > 0:
        reasons.append("partial_course_tokens_in_title")

    if course_norm and len(course_norm) >= 3 and course_norm in secondary_norm:
        reasons.append("exact_course_in_secondary_text")
    elif secondary_ratio >= 0.45:
        reasons.append("strong_course_tokens_in_secondary_text")
    elif secondary_ratio > 0:
        reasons.append("partial_course_tokens_in_secondary_text")

    if major_norm and len(major_norm) >= 4 and major_norm in title_norm:
        reasons.append("exact_major_in_title")
    elif major_title_ratio >= 0.35:
        reasons.append("major_context_tokens")

    return "; ".join(reasons) if reasons else "weak_text_similarity"


def clean_tiki(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df.columns = [clean_text(col) for col in df.columns]

    df["book_id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")
    df["sku"] = df["sku"].astype("string")
    df["title"] = df["name"].map(clean_text).str.replace(r"^Sách\s+", "", regex=True)
    df["title_norm"] = df["title"].map(norm_text)
    df["source_key"] = df["source_key"].map(clean_text)
    df["source_key_norm"] = df["source_key"].map(norm_text)
    df["source_mode"] = df["source_mode"].map(clean_text)
    df["price"] = pd.to_numeric(df["price"], errors="coerce").astype("Int64")
    df["original_price"] = pd.to_numeric(df["original_price"], errors="coerce").astype("Int64")
    df["discount"] = pd.to_numeric(df["discount"], errors="coerce").astype("Int64")
    df["discount_rate"] = pd.to_numeric(df["discount_rate"], errors="coerce").astype("Int64")
    df["quantity_sold"] = pd.to_numeric(df["quantity_sold_value"], errors="coerce").astype("Int64")
    df["rating_average"] = pd.to_numeric(df["rating_average"], errors="coerce").fillna(0).round(2)
    df["review_count"] = pd.to_numeric(df["review_count"], errors="coerce").fillna(0).astype(int)
    df["fetched_at"] = pd.to_datetime(df["fetched_at"], errors="coerce", utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    df["url_path"] = df["url_path"].map(clean_text)
    df["tiki_url"] = "https://tiki.vn/" + df["url_path"].str.lstrip("/")

    grouped = (
        df.groupby("book_id", dropna=False, sort=False)
        .agg(
            sku=("sku", "first"),
            title=("title", "first"),
            title_norm=("title_norm", "first"),
            price=("price", "first"),
            original_price=("original_price", "first"),
            discount=("discount", "first"),
            discount_rate=("discount_rate", "first"),
            quantity_sold=("quantity_sold", "max"),
            rating_average=("rating_average", "max"),
            review_count=("review_count", "max"),
            source_keys=("source_key", join_unique),
            source_modes=("source_mode", join_unique),
            fetched_at_first=("fetched_at", "min"),
            fetched_at_last=("fetched_at", "max"),
            tiki_url=("tiki_url", "first"),
            url_path=("url_path", "first"),
        )
        .reset_index()
    )
    grouped["source_key_count"] = grouped["source_keys"].map(lambda x: len([p for p in x.split("; ") if p]))
    grouped["source_keys_norm"] = grouped["source_keys"].map(norm_text)
    grouped["match_text_norm"] = (grouped["title"] + " " + grouped["source_keys"]).map(norm_text)
    grouped["popularity_score"] = (
        np.log1p(grouped["quantity_sold"].fillna(0).astype(float))
        + 1.5 * np.log1p(grouped["review_count"].fillna(0).astype(float))
        + grouped["rating_average"].fillna(0).astype(float)
    ).round(4)
    return grouped[
        [
            "book_id",
            "sku",
            "title",
            "title_norm",
            "price",
            "original_price",
            "discount",
            "discount_rate",
            "quantity_sold",
            "rating_average",
            "review_count",
            "source_keys",
            "source_keys_norm",
            "source_key_count",
            "source_modes",
            "fetched_at_first",
            "fetched_at_last",
            "tiki_url",
            "url_path",
            "match_text_norm",
            "popularity_score",
        ]
    ]


def clean_students(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = raw.copy()
    df["student_id"] = pd.to_numeric(df["user_id"], errors="coerce").astype("Int64")
    df["student_code"] = df["ma_sv"].astype("string").map(clean_text)
    df["student_name"] = df["ho_ten"].map(clean_text)
    df["student_name_norm"] = df["student_name"].map(norm_text)
    df["gender"] = df["gioi_tinh"].map(clean_text)
    df["major"] = df["nganh"].map(clean_text)
    df["major_norm"] = df["major"].map(norm_text)
    df["cohort"] = pd.to_numeric(df["khoa_nhap_hoc"], errors="coerce").astype("Int64")
    df["course_list"] = df["mon_hoc"].map(parse_course_list)
    df["course_count"] = df["course_list"].map(len)
    df["courses"] = df["course_list"].map(lambda items: "; ".join(items))

    students_clean = df[
        [
            "student_id",
            "student_code",
            "student_name",
            "student_name_norm",
            "gender",
            "major",
            "major_norm",
            "cohort",
            "courses",
            "course_count",
        ]
    ].copy()

    rows: list[dict[str, object]] = []
    for record in df.to_dict("records"):
        for idx, course in enumerate(record["course_list"], start=1):
            rows.append(
                {
                    "student_id": record["student_id"],
                    "student_code": record["student_code"],
                    "student_name": record["student_name"],
                    "gender": record["gender"],
                    "major": record["major"],
                    "major_norm": record["major_norm"],
                    "cohort": record["cohort"],
                    "course_order": idx,
                    "course": course,
                    "course_norm": norm_text(course),
                }
            )
    student_courses = pd.DataFrame(rows)
    return students_clean, student_courses


def clean_repo(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df["doc_id"] = df["doc_id"].map(clean_text)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["title"] = df["title"].map(clean_text)
    df["title_norm"] = df["title"].map(norm_text)
    df["abstract"] = df["abstract"].map(clean_text)
    df["abstract_norm"] = df["abstract"].map(norm_text)
    df["collection"] = df["collection"].map(clean_text)
    df["authors"] = df["author"].map(dedupe_authors)
    df["author_count"] = df["authors"].map(lambda x: len([p for p in x.split("; ") if p]))
    df["views"] = pd.to_numeric(df["views"], errors="coerce").fillna(0).astype(int)
    df["uri"] = df["uri"].map(clean_text)
    df["url"] = df["url"].map(clean_text)
    df["match_text_norm"] = (df["title"] + " " + df["abstract"] + " " + df["collection"]).map(norm_text)

    df = df.sort_values(["doc_id", "views"], ascending=[True, False]).drop_duplicates("doc_id", keep="first")
    return df[
        [
            "doc_id",
            "year",
            "title",
            "title_norm",
            "abstract",
            "abstract_norm",
            "collection",
            "authors",
            "author_count",
            "views",
            "uri",
            "url",
            "match_text_norm",
        ]
    ].copy()


def build_book_records(tiki_clean: pd.DataFrame) -> tuple[list[dict[str, object]], dict[str, set[int]], dict[str, float]]:
    records: list[dict[str, object]] = []
    token_sets: list[set[str]] = []
    inverted: dict[str, set[int]] = defaultdict(set)
    for idx, row in enumerate(tiki_clean.to_dict("records")):
        title_tokens = tokens_plus(row["title"])
        source_tokens = tokens_plus(row["source_keys"])
        all_tokens = title_tokens | source_tokens
        record = {
            **row,
            "title_tokens": title_tokens,
            "source_tokens": source_tokens,
            "all_tokens": all_tokens,
        }
        records.append(record)
        token_sets.append(all_tokens)
        for token in all_tokens:
            inverted[token].add(idx)
    return records, inverted, make_idf(token_sets)


def build_repo_records(repo_clean: pd.DataFrame) -> tuple[list[dict[str, object]], dict[str, set[int]], dict[str, float]]:
    records: list[dict[str, object]] = []
    token_sets: list[set[str]] = []
    inverted: dict[str, set[int]] = defaultdict(set)
    for idx, row in enumerate(repo_clean.to_dict("records")):
        title_tokens = tokens_plus(row["title"])
        abstract_tokens = tokens_plus(row["abstract"])
        collection_tokens = tokens_plus(row["collection"])
        all_tokens = title_tokens | abstract_tokens | collection_tokens
        record = {
            **row,
            "title_tokens": title_tokens,
            "abstract_tokens": abstract_tokens,
            "collection_tokens": collection_tokens,
            "all_tokens": all_tokens,
        }
        records.append(record)
        token_sets.append(all_tokens)
        for token in all_tokens:
            inverted[token].add(idx)
    return records, inverted, make_idf(token_sets)


def candidate_indexes(query_tokens: set[str], inverted: dict[str, set[int]], total_count: int) -> set[int]:
    candidates: set[int] = set()
    for token in query_tokens:
        candidates.update(inverted.get(token, set()))
    if candidates:
        return candidates
    return set(range(total_count))


def score_tiki_record(query: dict[str, object], record: dict[str, object], idf: dict[str, float]) -> dict[str, object]:
    course_tokens = query["course_tokens"]
    major_tokens = query["major_tokens"]
    title_ratio = weighted_ratio(course_tokens, record["title_tokens"], idf)
    source_ratio = weighted_ratio(course_tokens, record["source_tokens"], idf)
    major_title_ratio = weighted_ratio(major_tokens, record["title_tokens"], idf) if major_tokens else 0.0
    major_source_ratio = weighted_ratio(major_tokens, record["source_tokens"], idf) if major_tokens else 0.0

    score = 72 * title_ratio + 22 * source_ratio + 4 * major_title_ratio + 2 * major_source_ratio
    course_norm = query["course_norm"]
    major_norm = query["major_norm"]
    title_norm = record["title_norm"]
    source_norm = record["source_keys_norm"]

    if course_norm and len(course_norm) >= 3 and course_norm in title_norm:
        score += 24
    elif course_norm and len(course_norm) >= 3 and course_norm in source_norm:
        score += 10
    special_tokens = course_tokens & SPECIAL_TOKENS
    if special_tokens & record["title_tokens"]:
        score += 28
    elif special_tokens & record["source_tokens"]:
        score += 10
    if major_norm and len(major_norm) >= 4 and major_norm in title_norm:
        score += 4

    if title_ratio == 0 and source_ratio > 0:
        score = min(score, 55)
    if title_ratio == 0 and source_ratio < 0.35:
        score = min(score, 32)

    score = round(float(min(score, 100)), 2)
    reason = score_reason(
        course_norm=course_norm,
        major_norm=major_norm,
        title_norm=title_norm,
        secondary_norm=source_norm,
        title_ratio=title_ratio,
        secondary_ratio=source_ratio,
        major_title_ratio=major_title_ratio,
    )
    return {
        "resource_type": "tiki_book",
        "resource_id": record["book_id"],
        "resource_title": record["title"],
        "score": score,
        "confidence": confidence(score, "tiki_book"),
        "match_reason": reason,
        "url": record["tiki_url"],
        "price": record["price"],
        "rating_average": record["rating_average"],
        "review_count": record["review_count"],
        "quantity_sold": record["quantity_sold"],
        "source_keys": record["source_keys"],
        "year": pd.NA,
        "collection": "",
        "views": pd.NA,
        "authors": "",
        "popularity_score": record["popularity_score"],
    }


def score_repo_record(query: dict[str, object], record: dict[str, object], idf: dict[str, float]) -> dict[str, object]:
    course_tokens = query["course_tokens"]
    major_tokens = query["major_tokens"]
    title_ratio = weighted_ratio(course_tokens, record["title_tokens"], idf)
    abstract_ratio = weighted_ratio(course_tokens, record["abstract_tokens"], idf)
    collection_ratio = weighted_ratio(course_tokens, record["collection_tokens"], idf)
    major_title_ratio = weighted_ratio(major_tokens, record["title_tokens"], idf) if major_tokens else 0.0
    major_abstract_ratio = weighted_ratio(major_tokens, record["abstract_tokens"], idf) if major_tokens else 0.0

    score = (
        76 * title_ratio
        + 18 * abstract_ratio
        + 2 * collection_ratio
        + 3 * major_title_ratio
        + 1 * major_abstract_ratio
    )
    course_norm = query["course_norm"]
    major_norm = query["major_norm"]
    title_norm = record["title_norm"]
    abstract_norm = record["abstract_norm"]
    secondary_norm = f"{abstract_norm} {norm_text(record['collection'])}"

    if course_norm and len(course_norm) >= 3 and course_norm in title_norm:
        score += 22
    elif course_norm and len(course_norm) >= 3 and course_norm in abstract_norm:
        score += 7
    special_tokens = course_tokens & SPECIAL_TOKENS
    if special_tokens & record["title_tokens"]:
        score += 26
    elif special_tokens & record["abstract_tokens"]:
        score += 8
    if major_norm and len(major_norm) >= 4 and major_norm in title_norm:
        score += 4

    score = round(float(min(score, 100)), 2)
    reason = score_reason(
        course_norm=course_norm,
        major_norm=major_norm,
        title_norm=title_norm,
        secondary_norm=secondary_norm,
        title_ratio=title_ratio,
        secondary_ratio=abstract_ratio,
        major_title_ratio=major_title_ratio,
    )
    return {
        "resource_type": "ueh_repository",
        "resource_id": record["doc_id"],
        "resource_title": record["title"],
        "score": score,
        "confidence": confidence(score, "ueh_repository"),
        "match_reason": reason,
        "url": record["url"],
        "price": pd.NA,
        "rating_average": pd.NA,
        "review_count": pd.NA,
        "quantity_sold": pd.NA,
        "source_keys": "",
        "year": record["year"],
        "collection": record["collection"],
        "views": record["views"],
        "authors": record["authors"],
        "popularity_score": pd.NA,
    }


def build_matches(
    student_courses: pd.DataFrame,
    tiki_clean: pd.DataFrame,
    repo_clean: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    book_records, book_inverted, book_idf = build_book_records(tiki_clean)
    repo_records, repo_inverted, repo_idf = build_repo_records(repo_clean)

    unique_pairs = (
        student_courses[["major", "major_norm", "course", "course_norm"]]
        .drop_duplicates()
        .sort_values(["major", "course"])
        .reset_index(drop=True)
    )

    match_rows: list[dict[str, object]] = []
    best_rows: list[dict[str, object]] = []

    for pair in unique_pairs.to_dict("records"):
        query = {
            **pair,
            "course_tokens": expand_query_tokens(pair["course"]),
            "major_tokens": expand_query_tokens(pair["major"]),
        }
        all_query_tokens = query["course_tokens"] | query["major_tokens"]

        book_candidates = candidate_indexes(all_query_tokens, book_inverted, len(book_records))
        scored_books = [score_tiki_record(query, book_records[idx], book_idf) for idx in book_candidates]
        scored_books.sort(
            key=lambda x: (
                x["score"],
                0 if pd.isna(x["popularity_score"]) else x["popularity_score"],
                0 if pd.isna(x["review_count"]) else x["review_count"],
            ),
            reverse=True,
        )

        repo_candidates = candidate_indexes(all_query_tokens, repo_inverted, len(repo_records))
        scored_docs = [score_repo_record(query, repo_records[idx], repo_idf) for idx in repo_candidates]
        scored_docs.sort(
            key=lambda x: (
                x["score"],
                0 if pd.isna(x["views"]) else x["views"],
                0 if pd.isna(x["year"]) else x["year"],
            ),
            reverse=True,
        )

        top_books = scored_books[:3]
        top_docs = scored_docs[:3]

        for rank, match in enumerate(top_books, start=1):
            match_rows.append({**pair, "rank": rank, **match})
        for rank, match in enumerate(top_docs, start=1):
            match_rows.append({**pair, "rank": rank, **match})

        best_book = top_books[0] if top_books else {}
        best_doc = top_docs[0] if top_docs else {}
        best_rows.append(
            {
                **pair,
                "tiki_book_id": best_book.get("resource_id", pd.NA),
                "tiki_title": best_book.get("resource_title", ""),
                "tiki_score": best_book.get("score", pd.NA),
                "tiki_confidence": best_book.get("confidence", ""),
                "tiki_match_reason": best_book.get("match_reason", ""),
                "tiki_price": best_book.get("price", pd.NA),
                "tiki_rating_average": best_book.get("rating_average", pd.NA),
                "tiki_review_count": best_book.get("review_count", pd.NA),
                "tiki_quantity_sold": best_book.get("quantity_sold", pd.NA),
                "tiki_source_keys": best_book.get("source_keys", ""),
                "tiki_url": best_book.get("url", ""),
                "repo_doc_id": best_doc.get("resource_id", pd.NA),
                "repo_title": best_doc.get("resource_title", ""),
                "repo_score": best_doc.get("score", pd.NA),
                "repo_confidence": best_doc.get("confidence", ""),
                "repo_match_reason": best_doc.get("match_reason", ""),
                "repo_year": best_doc.get("year", pd.NA),
                "repo_collection": best_doc.get("collection", ""),
                "repo_views": best_doc.get("views", pd.NA),
                "repo_authors": best_doc.get("authors", ""),
                "repo_url": best_doc.get("url", ""),
            }
        )

    course_matches = pd.DataFrame(match_rows)
    best_by_pair = pd.DataFrame(best_rows)

    student_matches = student_courses.merge(
        best_by_pair.drop(columns=["major_norm", "course_norm"]),
        on=["major", "course"],
        how="left",
        validate="many_to_one",
    )
    return course_matches, student_matches


def quality_summary(
    raw_tiki: pd.DataFrame,
    raw_students: pd.DataFrame,
    raw_repo: pd.DataFrame,
    tiki_clean: pd.DataFrame,
    students_clean: pd.DataFrame,
    student_courses: pd.DataFrame,
    repo_clean: pd.DataFrame,
    course_matches: pd.DataFrame,
    student_matches: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, object]]:
    top_course_matches = course_matches[course_matches["rank"] == 1].copy()
    metrics: list[dict[str, object]] = [
        {"metric": "raw_tiki_rows", "value": len(raw_tiki)},
        {"metric": "clean_tiki_unique_books", "value": len(tiki_clean)},
        {"metric": "raw_student_rows", "value": len(raw_students)},
        {"metric": "clean_student_rows", "value": len(students_clean)},
        {"metric": "student_course_rows", "value": len(student_courses)},
        {"metric": "unique_major_course_pairs", "value": student_courses[["major", "course"]].drop_duplicates().shape[0]},
        {"metric": "raw_repo_rows", "value": len(raw_repo)},
        {"metric": "clean_repo_unique_docs", "value": len(repo_clean)},
        {"metric": "course_resource_match_rows_top3_each_type", "value": len(course_matches)},
        {"metric": "student_resource_match_rows", "value": len(student_matches)},
        {"metric": "student_rows_with_tiki_match", "value": int(student_matches["tiki_book_id"].notna().sum())},
        {"metric": "student_rows_with_repo_match", "value": int(student_matches["repo_doc_id"].notna().sum())},
        {
            "metric": "student_rows_with_both_matches",
            "value": int((student_matches["tiki_book_id"].notna() & student_matches["repo_doc_id"].notna()).sum()),
        },
    ]

    for resource_type in ["tiki_book", "ueh_repository"]:
        subset = top_course_matches[top_course_matches["resource_type"] == resource_type]
        for label, count in subset["confidence"].value_counts(dropna=False).to_dict().items():
            metrics.append(
                {
                    "metric": f"top1_{resource_type}_confidence_{label}",
                    "value": int(count),
                }
            )
        metrics.append(
            {
                "metric": f"top1_{resource_type}_avg_score",
                "value": round(float(subset["score"].mean()), 2) if len(subset) else 0,
            }
        )

    summary_df = pd.DataFrame(metrics)
    report = {
        "source_files": {key: str(path) for key, path in SOURCE_FILES.items()},
        "outputs": {
            "directory": str(OUTPUT_DIR),
            "tiki_books_clean": str(OUTPUT_DIR / "tiki_books_clean.csv"),
            "ueh_students_clean": str(OUTPUT_DIR / "ueh_students_clean.csv"),
            "ueh_student_courses_clean": str(OUTPUT_DIR / "ueh_student_courses_clean.csv"),
            "ueh_repository_clean": str(OUTPUT_DIR / "ueh_repository_clean.csv"),
            "course_resource_matches": str(OUTPUT_DIR / "course_resource_matches.csv"),
            "student_resource_matches": str(OUTPUT_DIR / "student_resource_matches.csv"),
            "match_quality_summary": str(OUTPUT_DIR / "match_quality_summary.csv"),
        },
        "cleaning_notes": [
            "Tiki: dropped fully empty/high-missing operational columns, normalized titles, prices, dates, URLs, and deduplicated repeated products by book_id while preserving all source search keys.",
            "Students: preserved student rows, normalized names/majors, parsed mon_hoc into a course list, and exploded to one row per student-course.",
            "UEH repository: removed empty subject/doc_type noise, normalized titles/abstracts, deduplicated repeated author names, and kept one row per doc_id.",
            "Matching: used accent-insensitive Vietnamese/English text normalization, domain synonym expansion, token n-grams, weighted text overlap, exact phrase boosts, popularity/view tie-breakers, and confidence labels.",
        ],
        "validation": summary_df.to_dict("records"),
    }
    return summary_df, report


def write_readme(summary_df: pd.DataFrame) -> None:
    lines = [
        "# Cleaned and Matched Dataset Outputs",
        "",
        "Pipeline output for the three CSV files supplied by the user.",
        "",
        "## Files",
        "",
        "- `tiki_books_clean.csv`: unique cleaned Tiki book records.",
        "- `ueh_students_clean.csv`: cleaned student table, one row per student.",
        "- `ueh_student_courses_clean.csv`: exploded student-course table.",
        "- `ueh_repository_clean.csv`: cleaned UEH repository metadata.",
        "- `course_resource_matches.csv`: top 3 Tiki books and top 3 UEH repository documents for each major-course pair.",
        "- `student_resource_matches.csv`: final joined table, one row per student-course with the best Tiki and UEH repository match.",
        "- `match_quality_summary.csv`: row counts and confidence distribution.",
        "- `data_cleaning_report.json`: machine-readable audit notes.",
        "",
        "## Matching Method",
        "",
        "Text was normalized accent-insensitively, tokenized into words and n-grams, expanded with Vietnamese/English domain synonyms, then scored against resource titles and secondary text. Each match includes a numeric score, confidence label, and reason string.",
        "",
        "## Summary",
        "",
    ]
    for row in summary_df.to_dict("records"):
        lines.append(f"- {row['metric']}: {row['value']}")
    (OUTPUT_DIR / "README_matching.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    raw_tiki = pd.read_csv(SOURCE_FILES["tiki"], encoding="utf-8")
    raw_students = pd.read_csv(SOURCE_FILES["students"], encoding="utf-8", dtype={"ma_sv": "string"})
    raw_repo = pd.read_csv(SOURCE_FILES["repo"], encoding="utf-8")

    tiki_clean = clean_tiki(raw_tiki)
    students_clean, student_courses = clean_students(raw_students)
    repo_clean = clean_repo(raw_repo)

    course_matches, student_matches = build_matches(student_courses, tiki_clean, repo_clean)

    summary_df, report = quality_summary(
        raw_tiki,
        raw_students,
        raw_repo,
        tiki_clean,
        students_clean,
        student_courses,
        repo_clean,
        course_matches,
        student_matches,
    )

    outputs = {
        "tiki_books_clean.csv": tiki_clean,
        "ueh_students_clean.csv": students_clean,
        "ueh_student_courses_clean.csv": student_courses,
        "ueh_repository_clean.csv": repo_clean,
        "course_resource_matches.csv": course_matches,
        "student_resource_matches.csv": student_matches,
        "match_quality_summary.csv": summary_df,
    }
    for filename, frame in outputs.items():
        frame.to_csv(OUTPUT_DIR / filename, index=False, encoding="utf-8-sig")

    (OUTPUT_DIR / "data_cleaning_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_readme(summary_df)

    print(json.dumps(report["validation"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
