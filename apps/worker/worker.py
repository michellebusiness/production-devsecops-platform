import json
import os
import time

import pika
import psycopg2
import redis


def get_database_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "orders"),
        user=os.getenv("POSTGRES_USER", "orders_user"),
        password=os.getenv("POSTGRES_PASSWORD", "orders_password"),
    )


def get_redis_client():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
    )


def process_order(channel, method, properties, body):
    del properties

    message = json.loads(body)
    order_id = message["order_id"]

    print(f"Processing order {order_id}")

    time.sleep(3)

    database_connection = get_database_connection()

    try:
        with database_connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE orders
                SET status = %s
                WHERE id = %s;
                """,
                ("completed", order_id),
            )

        database_connection.commit()
    except Exception:
        database_connection.rollback()
        raise
    finally:
        database_connection.close()

    get_redis_client().delete("orders:list")

    channel.basic_ack(
        delivery_tag=method.delivery_tag,
    )

    print(f"Order {order_id} completed")


def main():
    credentials = pika.PlainCredentials(
        os.getenv("RABBITMQ_USER", "orders_user"),
        os.getenv("RABBITMQ_PASSWORD", "orders_password"),
    )

    parameters = pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
        port=int(os.getenv("RABBITMQ_PORT", "5672")),
        credentials=credentials,
        connection_attempts=20,
        retry_delay=3,
    )

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(
        queue="orders",
        durable=True,
    )

    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue="orders",
        on_message_callback=process_order,
    )

    print("Worker is waiting for orders")
    channel.start_consuming()


if __name__ == "__main__":
    main()