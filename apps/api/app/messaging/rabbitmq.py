import pika

from app.core.config import settings


def get_rabbitmq_connection() -> pika.BlockingConnection:
    credentials = pika.PlainCredentials(
        settings.rabbitmq_user,
        settings.rabbitmq_password,
    )

    parameters = pika.ConnectionParameters(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
        credentials=credentials,
    )

    return pika.BlockingConnection(parameters)