from prometheus_client import Counter, Histogram


http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)

orders_created_total = Counter(
    "orders_created_total",
    "Total number of created orders",
)

application_errors_total = Counter(
    "application_errors_total",
    "Total number of application errors",
    ["operation"],
)