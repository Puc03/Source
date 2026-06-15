"""Train a Spark ALS recommender for the UEH-Tiki library project.

This script is designed for a classroom/demo setting.

Current project data does not contain real user behavior logs such as clicks,
borrows, renewals, PDF downloads, or ratings from students. To demonstrate ALS,
the script builds proxy implicit interactions from the protected analytics file:

    student + recommended resource + match/quality signals -> implicit rating

In production, replace the proxy interaction builder with real OPAC, repository,
and LMS behavior logs.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import StringIndexer
from pyspark.ml.recommendation import ALS
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "outputs" / "privacy_layer" / "student_resource_matches_analytics.csv"
DEFAULT_OUTPUT = ROOT / "outputs" / "spark_als"


def create_spark(app_name: str) -> SparkSession:
    return (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .config("spark.driver.memory", "4g")
        .getOrCreate()
    )


def as_double(column: str) -> F.Column:
    return F.col(column).cast(DoubleType())


def confidence_bonus(column: str) -> F.Column:
    return (
        F.when(F.col(column) == "high", F.lit(2.0))
        .when(F.col(column) == "medium", F.lit(1.0))
        .when(F.col(column) == "low", F.lit(0.2))
        .otherwise(F.lit(0.5))
    )


def bounded_log_score(column: str, weight: float, max_score: float) -> F.Column:
    return F.least(
        F.lit(max_score),
        F.log1p(F.coalesce(as_double(column), F.lit(0.0))) * F.lit(weight),
    )


def read_analytics(spark: SparkSession, input_path: Path) -> DataFrame:
    return (
        spark.read.option("header", "true")
        .option("encoding", "UTF-8")
        .csv(str(input_path))
    )


def build_proxy_interactions(analytics: DataFrame) -> DataFrame:
    """Create user-item implicit ratings from existing protected analytics data."""

    tiki = (
        analytics.where(F.col("tiki_book_id").isNotNull() & (F.col("tiki_title") != ""))
        .select(
            "student_token",
            "major",
            "course",
            F.concat(F.lit("TIKI_"), F.col("tiki_book_id")).alias("resource_id"),
            F.lit("tiki_book").alias("resource_type"),
            F.col("tiki_title").alias("resource_title"),
            F.col("tiki_url").alias("resource_url"),
            (
                as_double("tiki_score") * F.lit(0.055)
                + confidence_bonus("tiki_confidence")
                + F.coalesce(as_double("tiki_rating_average"), F.lit(0.0)) * F.lit(0.30)
                + bounded_log_score("tiki_review_count", 0.15, 1.0)
                + bounded_log_score("tiki_quantity_sold", 0.18, 1.5)
            ).alias("raw_rating"),
            F.lit("proxy_from_tiki_match_rating_review_sales").alias("interaction_source"),
        )
    )

    repo = (
        analytics.where(F.col("repo_doc_id").isNotNull() & (F.col("repo_title") != ""))
        .select(
            "student_token",
            "major",
            "course",
            F.concat(F.lit("REPO_"), F.regexp_replace(F.col("repo_doc_id"), "/", "_")).alias(
                "resource_id"
            ),
            F.lit("ueh_repository").alias("resource_type"),
            F.col("repo_title").alias("resource_title"),
            F.col("repo_url").alias("resource_url"),
            (
                as_double("repo_score") * F.lit(0.065)
                + confidence_bonus("repo_confidence")
                + F.when(as_double("repo_year") >= 2023, F.lit(1.0))
                .when(as_double("repo_year") >= 2020, F.lit(0.7))
                .when(as_double("repo_year") >= 2017, F.lit(0.4))
                .otherwise(F.lit(0.2))
                + bounded_log_score("repo_views", 0.12, 1.0)
            ).alias("raw_rating"),
            F.lit("proxy_from_repo_match_year_views").alias("interaction_source"),
        )
    )

    combined = tiki.unionByName(repo)

    return (
        combined.groupBy(
            "student_token",
            "resource_id",
            "resource_type",
            "resource_title",
            "resource_url",
        )
        .agg(
            F.first("major", ignorenulls=True).alias("major"),
            F.concat_ws("; ", F.sort_array(F.collect_set("course"))).alias("related_courses"),
            F.max("raw_rating").alias("rating"),
            F.concat_ws("; ", F.sort_array(F.collect_set("interaction_source"))).alias(
                "interaction_source"
            ),
        )
        .withColumn("rating", F.least(F.lit(10.0), F.greatest(F.lit(0.1), F.col("rating"))))
    )


def add_numeric_ids(interactions: DataFrame) -> tuple[DataFrame, DataFrame, DataFrame]:
    user_indexer = StringIndexer(
        inputCol="student_token",
        outputCol="user_id_raw",
        handleInvalid="skip",
    )
    item_indexer = StringIndexer(
        inputCol="resource_id",
        outputCol="item_id_raw",
        handleInvalid="skip",
    )

    with_users = user_indexer.fit(interactions).transform(interactions)
    with_items = item_indexer.fit(with_users).transform(with_users)

    ratings = (
        with_items.withColumn("user_id", F.col("user_id_raw").cast("int"))
        .withColumn("item_id", F.col("item_id_raw").cast("int"))
        .select(
            "student_token",
            "resource_id",
            "resource_type",
            "resource_title",
            "resource_url",
            "major",
            "related_courses",
            "interaction_source",
            "user_id",
            "item_id",
            F.col("rating").cast("float").alias("rating"),
        )
    )

    users = ratings.select("student_token", "user_id", "major").dropDuplicates(["user_id"])
    items = ratings.select(
        "resource_id",
        "item_id",
        "resource_type",
        "resource_title",
        "resource_url",
    ).dropDuplicates(["item_id"])

    return ratings, users, items


def train_als(
    ratings: DataFrame,
    *,
    rank: int,
    max_iter: int,
    reg_param: float,
    top_k: int,
) -> tuple[DataFrame, DataFrame, DataFrame]:
    training, test = ratings.randomSplit([0.8, 0.2], seed=42)

    als = ALS(
        maxIter=max_iter,
        rank=rank,
        regParam=reg_param,
        userCol="user_id",
        itemCol="item_id",
        ratingCol="rating",
        implicitPrefs=True,
        coldStartStrategy="drop",
        nonnegative=True,
    )

    model = als.fit(training)
    predictions = model.transform(test)

    evaluator = RegressionEvaluator(
        metricName="rmse",
        labelCol="rating",
        predictionCol="prediction",
    )
    metrics = predictions.select(
        F.count("*").alias("prediction_rows"),
        F.lit(float(evaluator.evaluate(predictions))).alias("rmse"),
    )

    recommendations = model.recommendForAllUsers(top_k)
    return metrics, predictions, recommendations


def explode_recommendations(
    recommendations: DataFrame,
    users: DataFrame,
    items: DataFrame,
) -> DataFrame:
    return (
        recommendations.select(
            "user_id",
            F.posexplode("recommendations").alias("rank_zero_based", "rec"),
        )
        .select(
            "user_id",
            (F.col("rank_zero_based") + F.lit(1)).alias("rank"),
            F.col("rec.item_id").alias("item_id"),
            F.round(F.col("rec.rating"), 4).alias("als_score"),
        )
        .join(users, on="user_id", how="left")
        .join(items, on="item_id", how="left")
        .select(
            "student_token",
            "major",
            "rank",
            "resource_type",
            "resource_id",
            "resource_title",
            "resource_url",
            "als_score",
        )
        .orderBy("student_token", "rank")
    )


def write_csv(df: DataFrame, path: Path) -> None:
    (
        df.coalesce(1)
        .write.mode("overwrite")
        .option("header", "true")
        .csv(str(path))
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train Spark ALS recommender.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--rank", type=int, default=20)
    parser.add_argument("--max-iter", type=int, default=10)
    parser.add_argument("--reg-param", type=float, default=0.1)
    parser.add_argument("--top-k", type=int, default=10)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    spark = create_spark("UEH-Tiki-Spark-ALS-Recommendation")
    spark.sparkContext.setLogLevel("WARN")

    analytics = read_analytics(spark, args.input)
    interactions = build_proxy_interactions(analytics)
    ratings, users, items = add_numeric_ids(interactions)

    metrics, predictions, recommendations = train_als(
        ratings,
        rank=args.rank,
        max_iter=args.max_iter,
        reg_param=args.reg_param,
        top_k=args.top_k,
    )
    final_recommendations = explode_recommendations(recommendations, users, items)

    summary = ratings.select(
        F.count("*").alias("interaction_rows"),
        F.countDistinct("user_id").alias("users"),
        F.countDistinct("item_id").alias("items"),
        F.round(F.avg("rating"), 4).alias("avg_proxy_rating"),
        F.round(F.min("rating"), 4).alias("min_proxy_rating"),
        F.round(F.max("rating"), 4).alias("max_proxy_rating"),
    )

    write_csv(ratings, args.output / "als_proxy_interactions")
    write_csv(users, args.output / "als_user_mapping")
    write_csv(items, args.output / "als_item_mapping")
    write_csv(summary, args.output / "als_input_summary")
    write_csv(metrics, args.output / "als_model_metrics")
    write_csv(final_recommendations, args.output / "als_top_recommendations")

    print("Spark ALS workflow finished.")
    print(f"Output folder: {args.output}")
    print("Important outputs:")
    print("- als_input_summary")
    print("- als_model_metrics")
    print("- als_top_recommendations")
    print("")
    print("Note: interactions are proxy implicit ratings from existing analytics data.")
    print("For production, replace them with real OPAC/repository/LMS behavior logs.")

    spark.stop()


if __name__ == "__main__":
    main()

