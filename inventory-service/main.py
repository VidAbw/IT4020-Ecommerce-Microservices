from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Inventory Microservice", version="1.0.0")


class InventoryItem(BaseModel):
	product_id: str
	quantity: int


inventory_db: List[InventoryItem] = [
	InventoryItem(product_id="p-101", quantity=25),
	InventoryItem(product_id="p-102", quantity=0),
]


@app.get("/api/inventory", response_model=List[InventoryItem])
def get_inventory():
	return inventory_db


@app.get("/api/inventory/{product_id}", response_model=InventoryItem)
def get_inventory_item(product_id: str):
	item = next((i for i in inventory_db if i.product_id == product_id), None)
	if not item:
		raise HTTPException(status_code=404, detail="Inventory item not found")
	return item


@app.put("/api/inventory/{product_id}", response_model=InventoryItem)
def upsert_inventory_item(product_id: str, payload: InventoryItem):
	if payload.product_id != product_id:
		raise HTTPException(status_code=400, detail="Path product_id must match body product_id")

	for idx, item in enumerate(inventory_db):
		if item.product_id == product_id:
			inventory_db[idx] = payload
			return payload

	inventory_db.append(payload)
	return payload
