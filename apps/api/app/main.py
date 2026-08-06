import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from app.api.routes.health import router as health_router
from app.api.routes.orders import router as orders_router
from app.cache.redis_client import get_redis_client
from app.core.metrics import (
    http_request_duration_seconds,
    http_requests_total,
)
from app.messaging.rabbitmq import get_rabbitmq_connection


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


@asynccontextmanager
async def lifespan(_: FastAPI):
    connect_with_retry(
        lambda: get_redis_client().ping(),
        "Redis",
    )

    rabbitmq_connection = connect_with_retry(
        get_rabbitmq_connection,
        "RabbitMQ",
    )

    channel = rabbitmq_connection.channel()
    channel.queue_declare(queue="orders", durable=True)
    rabbitmq_connection.close()

    yield


app = FastAPI(
    title="Orders API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(orders_router)

import time

from fastapi import Request
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

from app.core.metrics import (
    http_request_duration_seconds,
    http_requests_total,
)
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration = time.perf_counter() - start_time

        http_request_duration_seconds.labels(
            method=request.method,
            path=request.url.path,
        ).observe(duration)

        http_requests_total.labels(
            method=request.method,
            path=request.url.path,
            status="500",
        ).inc()

        raise

    duration = time.perf_counter() - start_time

    http_request_duration_seconds.labels(
        method=request.method,
        path=request.url.path,
    ).observe(duration)

    http_requests_total.labels(
        method=request.method,
        path=request.url.path,
        status=str(response.status_code),
    ).inc()

    return response


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )