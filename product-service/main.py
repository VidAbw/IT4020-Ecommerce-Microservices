from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, field_validator
from sqlalchemy import create_engine, Column, Float, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import List

app = FastAPI(title="Product Service", version="1.0")

SQLALCHEMY_DATABASE_URL = "sqlite:///./products.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DBProduct(Base):
    __tablename__ = "products"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    stock_status = Column(String, nullable=False)


Base.metadata.create_all(bind=engine)


class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    stock_status: str

    @field_validator("id", "name", "description", "category", "stock_status")
    @classmethod
    def validate_non_empty_text(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Field cannot be empty")
        return value.strip()

    @field_validator("price")
    @classmethod
    def validate_positive_price(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("Price must be greater than 0")
        return value

    @field_validator("stock_status")
    @classmethod
    def validate_stock_status(cls, value: str) -> str:
        allowed_statuses = {"In Stock", "Out of Stock", "Low Stock"}
        normalized = value.strip()
        if normalized not in allowed_statuses:
            raise ValueError("Stock status must be one of: In Stock, Out of Stock, Low Stock")
        return normalized

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    products: List[Product]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_products_if_empty():
    db = SessionLocal()
    try:
        if db.query(DBProduct).count() == 0:
            db.add_all([
                DBProduct(
                    id="p-101",
                    name="Wireless Headphones",
                    description="Noise-cancelling over-ear headphones.",
                    price=199.99,
                    category="Electronics",
                    stock_status="In Stock",
                ),
                DBProduct(
                    id="p-102",
                    name="Mechanical Keyboard",
                    description="RGB wired mechanical keyboard.",
                    price=89.99,
                    category="Electronics",
                    stock_status="Out of Stock",
                ),
            ])
            db.commit()
    finally:
        db.close()


seed_products_if_empty()


@app.get("/", response_model=ProductListResponse)
def read_products(db: Session = Depends(get_db)):
    return {"products": db.query(DBProduct).all()}


@app.get("/{product_id}", response_model=Product)
def read_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
    if product:
        return product
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/", response_model=Product, status_code=201)
def create_product(product: Product, db: Session = Depends(get_db)):
    existing = db.query(DBProduct).filter(DBProduct.id == product.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product with this ID already exists")
    new_product = DBProduct(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@app.put("/{product_id}", response_model=Product)
def update_product(product_id: str, updated_product: Product, db: Session = Depends(get_db)):
    product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    payload = updated_product.model_dump()
    payload["id"] = product_id
    for key, value in payload.items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


@app.delete("/{product_id}", status_code=204)
def delete_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return None