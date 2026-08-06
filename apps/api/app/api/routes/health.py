from fastapi import APIRouter, HTTPException

from app.cache.redis_client import get_redis_client
from app.core.config import settings
from app.db.database import get_database_connection
from app.messaging.rabbitmq import get_rabbitmq_connection


router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {
        "status": "healthy",
        "service": settings.service_name,
    }


@router.get("/ready")
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