import json
import os
import time
from contextlib import asynccontextmanager

import pika
import redis
from fastapi import FastAPI, HTTPException

from database import get_database_connection, initialize_database
from models import OrderCreate, OrderResponse


def connect_with_retry(operation, service_name: str, attempts: int = 20):
    for attempt in range(1, attempts + 1):
        try:
            return operation()
        except Exception as error:
            print(
                f"Waiting for {service_name}: "
                f"attempt {attempt}/{attempts}: {error}"
            )
            time.sleep(3)

    raise RuntimeError(f"Could not connect to {service_name}")


def get_redis_client() -> redis.Redis:
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
    )


def get_rabbitmq_connection() -> pika.BlockingConnection:
    credentials = pika.PlainCredentials(
        os.getenv("RABBITMQ_USER", "orders_user"),
        os.getenv("RABBITMQ_PASSWORD", "orders_password"),
    )

    parameters = pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
        port=int(os.getenv("RABBITMQ_PORT", "5672")),
        credentials=credentials,
    )

    return pika.BlockingConnection(parameters)


@asynccontextmanager
async def lifespan(_: FastAPI):
    connect_with_retry(initialize_database, "PostgreSQL")
    connect_with_retry(lambda: get_redis_client().ping(), "Redis")

    connection = connect_with_retry(
        get_rabbitmq_connection,
        "RabbitMQ",
    )

    channel = connection.channel()
    channel.queue_declare(queue="orders", durable=True)
    connection.close()

    yield


app = FastAPI(
    title="Orders API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "orders-api",
    }


@app.get("/ready")
def readiness():
    checks: dict[str, str] = {}

    try:
        database_connection = get_database_connection()
        database_connection.close()
        checks["postgresql"] = "ready"
    except Exception as error:
        checks["postgresql"] = str(error)

    try:
        get_redis_client().ping()
        checks["redis"] = "ready"
    except Exception as error:
        checks["redis"] = str(error)

    try:
        rabbitmq_connection = get_rabbitmq_connection()
        rabbitmq_connection.close()
        checks["rabbitmq"] = "ready"
    except Exception as error:
        checks["rabbitmq"] = str(error)

    if any(value != "ready" for value in checks.values()):
        raise HTTPException(
            status_code=503,
            detail=checks,
        )

    return {
        "status": "ready",
        "dependencies": checks,
    }


@app.post(
    "/orders",
    response_model=OrderResponse,
    status_code=201,
)
def create_order(order: OrderCreate):
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
    except Exception:
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
        channel.queue_declare(queue="orders", durable=True)

        channel.basic_publish(
            exchange="",
            routing_key="orders",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
            ),
        )
    finally:
        rabbitmq_connection.close()

    return OrderResponse(
        id=created_order[0],
        customer_name=created_order[1],
        product_name=created_order[2],
        quantity=created_order[3],
        status=created_order[4],
    )


@app.get("/orders")
def list_orders():
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