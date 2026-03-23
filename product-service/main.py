from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Product Service", version="1.0")

# 1. Example Data Model
class Product (BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    stock_status: str

# 2. Mock Database (Using a list of dictionaries)
db = [
    {
        "id": "p-101",
        "name": "Wireless Headphones",
        "description": "Noise-cancelling over-ear headphones.",
        "price": 199.99,
        "category": "Electronics",
        "stock_status": "In Stock"
    },
    {
        "id": "p-102",
        "name": "Mechanical Keyboard",
        "description": "RGB wired mechanical keyboard.",
        "price": 89.99,
        "category": "Electronics",
        "stock_status": "Out of Stock"
    }
]

# 3. Endpoints
@app.get("/")
def read_products():
    return {"products": db}

@app.get("/{product_id}")
def read_product(product_id: str):
    # Find the product or return None
    product = next((p for p in db if p["id"] == product_id), None)
    
    if product:
        return product
    
    # Return a proper 404 if the ID doesn't exist
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/", status_code=201)
def create_product(product: Product):
    if any(p["id"] == product.id for p in db):
        raise HTTPException(status_code=400, detail="Product with this ID already exists")
    db.append(product.model_dump() if hasattr(product, "model_dump") else product.dict())
    return product

@app.put("/{product_id}")
def update_product(product_id: str, updated_product: Product):
    for index, p in enumerate(db):
        if p["id"] == product_id:
            product_dict = updated_product.model_dump() if hasattr(updated_product, "model_dump") else updated_product.dict()
            product_dict["id"] = product_id
            db[index] = product_dict
            return product_dict
    
    raise HTTPException(status_code=404, detail="Product not found")

@app.delete("/{product_id}", status_code=204)
def delete_product(product_id: str):
    for index, p in enumerate(db):
        if p["id"] == product_id:
            del db[index]
            return
    
    raise HTTPException(status_code=404, detail="Product not found")


# To run this specific service:
# uvicorn main:app --reload --port 8002