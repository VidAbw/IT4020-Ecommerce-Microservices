from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Float, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import List

app = FastAPI(title="Payment Microservice", version="1.0.0")

SQLALCHEMY_DATABASE_URL = "sqlite:///./payments.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DBPayment(Base):
	__tablename__ = "payments"
	id = Column(Integer, primary_key=True, index=True)
	order_id = Column(Integer, nullable=False)
	amount = Column(Float, nullable=False)
	method = Column(String, nullable=False)
	status = Column(String, nullable=False, default="paid")


Base.metadata.create_all(bind=engine)


class PaymentRequest(BaseModel):
	order_id: int
	amount: float
	method: str


class Payment(PaymentRequest):
	id: int
	status: str = "paid"

	class Config:
		from_attributes = True


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


@app.get("/api/payments", response_model=List[Payment])
def list_payments(db: Session = Depends(get_db)):
	return db.query(DBPayment).all()


@app.get("/api/payments/{payment_id}", response_model=Payment)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
	payment = db.query(DBPayment).filter(DBPayment.id == payment_id).first()
	if not payment:
		raise HTTPException(status_code=404, detail="Payment not found")
	return payment


@app.post("/api/payments", response_model=Payment, status_code=201)
def create_payment(payment_in: PaymentRequest, db: Session = Depends(get_db)):
	new_payment = DBPayment(**payment_in.model_dump())
	db.add(new_payment)
	db.commit()
	db.refresh(new_payment)
	return new_payment
