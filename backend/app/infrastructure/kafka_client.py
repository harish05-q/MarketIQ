"""Kafka producer and consumer wrappers using confluent-kafka."""

from __future__ import annotations

import json
from typing import Any, Callable

from confluent_kafka import Consumer, KafkaException, Producer
from confluent_kafka.admin import AdminClient, NewTopic

from app.config import get_settings
from app.core.constants import KafkaTopic
from app.core.exceptions import KafkaError as KafkaAppError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Module-level singletons
_producer: Producer | None = None
_admin_client: AdminClient | None = None


def get_producer() -> Producer:
    """Return the global Kafka producer, creating it on first call."""
    global _producer
    if _producer is None:
        settings = get_settings()
        conf = {
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "client.id": "marketiq-producer",
            "acks": "all",
            "retries": 3,
            "retry.backoff.ms": 500,
            "linger.ms": 10,
            "batch.size": 16384,
            "compression.type": "snappy",
        }
        _producer = Producer(conf)
        logger.info("kafka_producer_created", servers=settings.KAFKA_BOOTSTRAP_SERVERS)
    return _producer


def get_admin_client() -> AdminClient:
    """Return the global Kafka admin client."""
    global _admin_client
    if _admin_client is None:
        settings = get_settings()
        _admin_client = AdminClient({"bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS})
    return _admin_client


def _delivery_callback(err: Any, msg: Any) -> None:
    """Log delivery confirmation or failure."""
    if err is not None:
        logger.error("kafka_delivery_failed", error=str(err), topic=msg.topic())
    else:
        logger.debug(
            "kafka_message_delivered",
            topic=msg.topic(),
            partition=msg.partition(),
            offset=msg.offset(),
        )


async def produce_message(topic: str, value: dict[str, Any], key: str | None = None) -> None:
    """Produce a JSON message to a Kafka topic.

    Args:
        topic: Target Kafka topic name.
        value: Dictionary to serialize as JSON message value.
        key: Optional message key for partitioning.

    Raises:
        KafkaAppError: If message production fails.
    """
    try:
        producer = get_producer()
        serialized_value = json.dumps(value, default=str).encode("utf-8")
        serialized_key = key.encode("utf-8") if key else None

        producer.produce(
            topic=topic,
            value=serialized_value,
            key=serialized_key,
            callback=_delivery_callback,
        )
        producer.poll(0)
    except (KafkaException, BufferError) as exc:
        logger.error("kafka_produce_error", topic=topic, error=str(exc))
        raise KafkaAppError(f"Failed to produce message to {topic}: {exc}") from exc


def flush_producer(timeout: float = 10.0) -> None:
    """Flush all pending messages from the producer.

    Args:
        timeout: Maximum seconds to wait for delivery.
    """
    if _producer is not None:
        remaining = _producer.flush(timeout)
        if remaining > 0:
            logger.warning("kafka_flush_incomplete", remaining_messages=remaining)


def create_consumer(
    topics: list[str],
    group_id: str | None = None,
) -> Consumer:
    """Create a new Kafka consumer subscribed to the given topics.

    Args:
        topics: List of topic names to subscribe to.
        group_id: Consumer group id. Defaults to the configured group.

    Returns:
        A confluent-kafka Consumer instance.
    """
    settings = get_settings()
    conf = {
        "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
        "group.id": group_id or settings.KAFKA_GROUP_ID,
        "auto.offset.reset": settings.KAFKA_AUTO_OFFSET_RESET,
        "enable.auto.commit": True,
        "auto.commit.interval.ms": 5000,
        "session.timeout.ms": 30000,
        "max.poll.interval.ms": 300000,
    }
    consumer = Consumer(conf)
    consumer.subscribe(topics)
    logger.info("kafka_consumer_created", topics=topics, group_id=conf["group.id"])
    return consumer


async def ensure_topics_exist() -> None:
    """Create all required Kafka topics if they do not already exist."""
    try:
        admin = get_admin_client()
        existing_metadata = admin.list_topics(timeout=2)
        existing_topics = set(existing_metadata.topics.keys())

        required_topics = [t.value for t in KafkaTopic]
        new_topics = [
            NewTopic(topic, num_partitions=3, replication_factor=1)
            for topic in required_topics
            if topic not in existing_topics
        ]

        if new_topics:
            futures = admin.create_topics(new_topics)
            for topic_name, future in futures.items():
                try:
                    future.result()
                    logger.info("kafka_topic_created", topic=topic_name)
                except Exception as exc:
                    logger.warning("kafka_topic_creation_warning", topic=topic_name, error=str(exc))
        else:
            logger.info("kafka_all_topics_exist")
    except Exception as exc:
        logger.error("kafka_topic_setup_error", error=str(exc))
        raise KafkaAppError(f"Failed to ensure Kafka topics: {exc}") from exc


def close_kafka() -> None:
    """Flush producer and release global references."""
    global _producer, _admin_client
    flush_producer()
    _producer = None
    _admin_client = None
    logger.info("kafka_clients_closed")
