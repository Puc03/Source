#!/usr/bin/env bash
set -euo pipefail

BOOTSTRAP_SERVER="${BOOTSTRAP_SERVER:-kafka:19092}"
KAFKA_TOPICS_BIN="${KAFKA_TOPICS_BIN:-/opt/kafka/bin/kafka-topics.sh}"

echo "Creating Kafka topics on ${BOOTSTRAP_SERVER}"

create_topic() {
  local topic="$1"
  local partitions="$2"
  local retention_ms="$3"

  "${KAFKA_TOPICS_BIN}" \
    --bootstrap-server "${BOOTSTRAP_SERVER}" \
    --create \
    --if-not-exists \
    --topic "${topic}" \
    --partitions "${partitions}" \
    --replication-factor 1 \
    --config "retention.ms=${retention_ms}"
}

create_topic "privacy.validation.v1" 1 604800000
create_topic "dataset.analytics.student_matches.v1" 3 1209600000
create_topic "dataset.analytics.course_matches.v1" 3 1209600000
create_topic "dataset.public.tiki_books.v1" 3 1209600000
create_topic "dataset.public.ueh_repository.v1" 3 1209600000
create_topic "data_quality.report.v1" 1 1209600000
create_topic "audit.privacy_access.v1" 1 2592000000
create_topic "dead_letter.dataset_pipeline.v1" 1 2592000000

echo "Topics:"
"${KAFKA_TOPICS_BIN}" --bootstrap-server "${BOOTSTRAP_SERVER}" --list
