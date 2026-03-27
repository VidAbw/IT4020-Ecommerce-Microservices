from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Order Microservice", version="1.0.0")


class OrderCreate(BaseModel):
	user_id: int
	product_id: str
	quantity: int


class Order(OrderCreate):
	id: int
	status: str = "created"


orders_db: List[Order] = []


@app.get("/api/orders", response_model=List[Order])
def list_orders():
	return orders_db


@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: int):
	order = next((o for o in orders_db if o.id == order_id), None)
	if not order:
		raise HTTPException(status_code=404, detail="Order not found")
	return order


@app.post("/api/orders", response_model=Order, status_code=201)
def create_order(order_in: OrderCreate):
	new_id = max((o.id for o in orders_db), default=0) + 1
	new_order = Order(id=new_id, **order_in.model_dump())
	orders_db.append(new_order)
	return new_order
