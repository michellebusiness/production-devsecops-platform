import os

import psycopg2
from psycopg2.extensions import connection


def get_database_connection() -> connection:
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "orders"),
        user=os.getenv("POSTGRES_USER", "orders_user"),
        password=os.getenv("POSTGRES_PASSWORD", "orders_password"),
    )


def initialize_database() -> None:
    connection = get_database_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    customer_name VARCHAR(100) NOT NULL,
                    product_name VARCHAR(100) NOT NULL,
                    quantity INTEGER NOT NULL CHECK (quantity > 0),
                    status VARCHAR(50) NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

        connection.commit()
    finally:
        connection.close()