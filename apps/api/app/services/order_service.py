import json

import pika

from app.cache.redis_client import get_redis_client
from app.core.metrics import (
    application_errors_total,
    orders_created_total,
)
from app.db.database import get_database_connection
from app.messaging.rabbitmq import get_rabbitmq_connection
from app.schemas.order import OrderCreate, OrderResponse


def create_order(order: OrderCreate) -> OrderResponse:
    database_connection = get_database_connection()

    try:
        with database_connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO orders (
                    customer_name,
                    product_name,
                    quantity,
                    status
                )
                VALUES (%s, %s, %s, %s)
                RETURNING id, customer_name, product_name, quantity, status;
                """,
                (
                    order.customer_name,
                    order.product_name,
                    order.quantity,
                    "pending",
                ),
            )

            created_order = cursor.fetchone()

        database_connection.commit()
        orders_created_total.inc()

    except Exception:
        application_errors_total.labels(
            operation="create_order",
        ).inc()

        database_connection.rollback()
        raise

    finally:
        database_connection.close()

    message = {
        "order_id": created_order[0],
        "customer_name": created_order[1],
        "product_name": created_order[2],
        "quantity": created_order[3],
    }

    rabbitmq_connection = get_rabbitmq_connection()

    try:
        channel = rabbitmq_connection.channel()
        channel.queue_declare(
            queue="orders",
            durable=True,
        )

        channel.basic_publish(
            exchange="",
            routing_key="orders",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
            ),
        )

    except Exception:
        application_errors_total.labels(
            operation="publish_order",
        ).inc()
        raise

    finally:
        rabbitmq_connection.close()

    get_redis_client().delete("orders:list")

    return OrderResponse(
        id=created_order[0],
        customer_name=created_order[1],
        product_name=created_order[2],
        quantity=created_order[3],
        status=created_order[4],
    )


def list_orders() -> dict:
    redis_client = get_redis_client()
    cached_orders = redis_client.get("orders:list")

    if cached_orders:
        return {
            "source": "redis-cache",
            "orders": json.loads(cached_orders),
        }

    database_connection = get_database_connection()

    try:
        with database_connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    customer_name,
                    product_name,
                    quantity,
                    status,
                    created_at
                FROM orders
                ORDER BY id DESC;
                """
            )

            rows = cursor.fetchall()

    except Exception:
        application_errors_total.labels(
            operation="list_orders",
        ).inc()
        raise

    finally:
        database_connection.close()

    orders = [
        {
            "id": row[0],
            "customer_name": row[1],
            "product_name": row[2],
            "quantity": row[3],
            "status": row[4],
            "created_at": row[5].isoformat(),
        }
        for row in rows
    ]

    redis_client.setex(
        "orders:list",
        30,
        json.dumps(orders),
    )

    return {
        "source": "postgresql",
        "orders": orders,
    }