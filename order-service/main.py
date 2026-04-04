from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
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


class Order(OrderCreate):
	id: int
	status: str = "created"

	class Config:
		from_attributes = True


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


@app.get("/")
def root():
	return {"service": "order-service", "status": "running", "docs": "/docs"}


@app.get("/health")
def health():
	return {"ok": True}


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


@app.delete("/api/orders/{order_id}", status_code=204)
def delete_order(order_id: int, db: Session = Depends(get_db)):
	order = db.query(DBOrder).filter(DBOrder.id == order_id).first()
	if not order:
		raise HTTPException(status_code=404, detail="Order not found")
	db.delete(order)
	db.commit()
	return None
