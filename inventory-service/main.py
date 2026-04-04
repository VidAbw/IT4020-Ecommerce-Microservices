from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import List

app = FastAPI(title="Inventory Microservice", version="1.0.0")

SQLALCHEMY_DATABASE_URL = "sqlite:///./inventory.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DBInventoryItem(Base):
	__tablename__ = "inventory_items"
	product_id = Column(String, primary_key=True, index=True)
	quantity = Column(Integer, nullable=False)


Base.metadata.create_all(bind=engine)


class InventoryItem(BaseModel):
	product_id: str
	quantity: int

	class Config:
		from_attributes = True


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def seed_inventory_if_empty():
	db = SessionLocal()
	try:
		if db.query(DBInventoryItem).count() == 0:
			db.add_all([
				DBInventoryItem(product_id="p-101", quantity=25),
				DBInventoryItem(product_id="p-102", quantity=0),
			])
			db.commit()
	finally:
		db.close()


seed_inventory_if_empty()


@app.get("/api/inventory", response_model=List[InventoryItem])
def get_inventory(db: Session = Depends(get_db)):
	return db.query(DBInventoryItem).all()


@app.get("/api/inventory/{product_id}", response_model=InventoryItem)
def get_inventory_item(product_id: str, db: Session = Depends(get_db)):
	item = db.query(DBInventoryItem).filter(DBInventoryItem.product_id == product_id).first()
	if not item:
		raise HTTPException(status_code=404, detail="Inventory item not found")
	return item


@app.put("/api/inventory/{product_id}", response_model=InventoryItem)
def upsert_inventory_item(product_id: str, payload: InventoryItem, db: Session = Depends(get_db)):
	if payload.product_id != product_id:
		raise HTTPException(status_code=400, detail="Path product_id must match body product_id")

	item = db.query(DBInventoryItem).filter(DBInventoryItem.product_id == product_id).first()
	if item:
		item.quantity = payload.quantity
	else:
		item = DBInventoryItem(**payload.model_dump())
		db.add(item)

	db.commit()
	db.refresh(item)
	return item
