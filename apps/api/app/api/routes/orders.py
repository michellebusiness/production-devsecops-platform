from fastapi import APIRouter

from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import create_order, list_orders


router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


@router.post(
    "",
    response_model=OrderResponse,
    status_code=201,
)
def create_order_endpoint(order: OrderCreate):
    return create_order(order)


@router.get("")
def list_orders_endpoint():
    return list_orders()