from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=100)
    product_name: str = Field(min_length=2, max_length=100)
    quantity: int = Field(gt=0, le=100)


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    product_name: str
    quantity: int
    status: str