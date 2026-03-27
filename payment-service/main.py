from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Payment Microservice", version="1.0.0")


class PaymentRequest(BaseModel):
	order_id: int
	amount: float
	method: str


class Payment(PaymentRequest):
	id: int
	status: str = "paid"


payments_db: List[Payment] = []


@app.get("/api/payments", response_model=List[Payment])
def list_payments():
	return payments_db


@app.get("/api/payments/{payment_id}", response_model=Payment)
def get_payment(payment_id: int):
	payment = next((p for p in payments_db if p.id == payment_id), None)
	if not payment:
		raise HTTPException(status_code=404, detail="Payment not found")
	return payment


@app.post("/api/payments", response_model=Payment, status_code=201)
def create_payment(payment_in: PaymentRequest):
	new_id = max((p.id for p in payments_db), default=0) + 1
	new_payment = Payment(id=new_id, **payment_in.model_dump())
	payments_db.append(new_payment)
	return new_payment
