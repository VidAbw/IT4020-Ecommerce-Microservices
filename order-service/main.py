from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, field_validator
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import List

app = FastAPI(title="Order Microservice", version="1.0.0")

SQLALCHEMY_DATABASE_URL = "sqlite:///./orders.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DBOrder(Base):
	__tablename__ = "orders"
	id = Column(Integer, primary_key=True, index=True)
	user_id = Column(Integer, nullable=False)
	product_id = Column(String, nullable=False)
	quantity = Column(Integer, nullable=False)
	status = Column(String, nullable=False, default="created")


Base.metadata.create_all(bind=engine)


class OrderCreate(BaseModel):
	user_id: int
	product_id: str
	quantity: int

	@field_validator("user_id")
	@classmethod
	def validate_user_id_positive(cls, value: int) -> int:
		if value <= 0:
			raise ValueError("user_id must be greater than 0")
		return value

	@field_validator("product_id")
	@classmethod
	def validate_product_id_non_empty(cls, value: str) -> str:
		cleaned = value.strip()
		if not cleaned:
			raise ValueError("product_id cannot be empty")
		return cleaned

	@field_validator("quantity")
	@classmethod
	def validate_quantity_positive(cls, value: int) -> int:
		if value <= 0:
			raise ValueError("quantity must be greater than 0")
		return value


class Order(OrderCreate):
	id: int
	status: str = "created"

	@field_validator("status")
	@classmethod
	def validate_status_allowed(cls, value: str) -> str:
		allowed_statuses = {"created", "processing", "shipped", "cancelled"}
		cleaned = value.strip().lower()
		if cleaned not in allowed_statuses:
			raise ValueError("status must be one of: created, processing, shipped, cancelled")
		return cleaned

	class Config:
		from_attributes = True


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def seed_orders_if_empty():
	db = SessionLocal()
	try:
		if db.query(DBOrder).count() == 0:
			db.add_all([
				DBOrder(user_id=1, product_id="p-101", quantity=1, status="shipped"),
				DBOrder(user_id=2, product_id="p-102", quantity=2, status="created"),
				DBOrder(user_id=1, product_id="p-102", quantity=1, status="processing"),
			])
			db.commit()
	finally:
		db.close()


seed_orders_if_empty()


@app.get("/")
def root():
	return {"service": "order-service", "status": "running", "docs": "/docs"}
	

@app.get("/api/orders", response_model=List[Order])
def list_orders(db: Session = Depends(get_db)):
	return db.query(DBOrder).all()


@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
	order = db.query(DBOrder).filter(DBOrder.id == order_id).first()
	if not order:
		raise HTTPException(status_code=404, detail="Order not found")
	return order


@app.post("/api/orders", response_model=Order, status_code=201)
def create_order(order_in: OrderCreate, db: Session = Depends(get_db)):
	new_order = DBOrder(**order_in.model_dump())
	db.add(new_order)
	db.commit()
	db.refresh(new_order)
	return new_order


@app.put("/api/orders/{order_id}", response_model=Order)
def update_order(order_id: int, order_in: OrderCreate, status: str = None, db: Session = Depends(get_db)):
	order = db.query(DBOrder).filter(DBOrder.id == order_id).first()
	if not order:
		raise HTTPException(status_code=404, detail="Order not found")

	order.user_id = order_in.user_id
	order.product_id = order_in.product_id
	order.quantity = order_in.quantity
	if status:
		allowed_statuses = {"created", "processing", "shipped", "cancelled"}
		normalized_status = status.strip().lower()
		if normalized_status not in allowed_statuses:
			raise HTTPException(
				status_code=422,
				detail="status must be one of: created, processing, shipped, cancelled",
			)
		order.status = normalized_status
	
	db.commit()
	db.refresh(order)
	return order


@app.delete("/api/orders/{order_id}", status_code=204)
def delete_order(order_id: int, db: Session = Depends(get_db)):
	order = db.query(DBOrder).filter(DBOrder.id == order_id).first()
	if not order:
		raise HTTPException(status_code=404, detail="Order not found")
	db.delete(order)
	db.commit()
	return None
