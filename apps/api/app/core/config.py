import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    service_name: str = os.getenv("SERVICE_NAME", "orders-api")

    postgres_host: str = os.getenv("POSTGRES_HOST", "postgres")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db: str = os.getenv("POSTGRES_DB", "orders")
    postgres_user: str = os.getenv("POSTGRES_USER", "orders_user")
    postgres_password: str = os.getenv(
        "POSTGRES_PASSWORD",
        "orders_password",
    )

    redis_host: str = os.getenv("REDIS_HOST", "redis")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))

    rabbitmq_host: str = os.getenv("RABBITMQ_HOST", "rabbitmq")
    rabbitmq_port: int = int(os.getenv("RABBITMQ_PORT", "5672"))
    rabbitmq_user: str = os.getenv("RABBITMQ_USER", "orders_user")
    rabbitmq_password: str = os.getenv(
        "RABBITMQ_PASSWORD",
        "orders_password",
    )


settings = Settings()