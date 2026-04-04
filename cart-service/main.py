from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# --- 1. SQLITE DATABASE SETUP ---
# Creates a separate 'cart.db' file specifically for this microservice
SQLALCHEMY_DATABASE_URL = "sqlite:///./cart.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 2. DATABASE MODEL (SQLAlchemy) ---
class DBCartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    product_id = Column(Integer, index=True)
    quantity = Column(Integer, default=1)

# Create the database tables automatically
Base.metadata.create_all(bind=engine)

# --- 3. PYDANTIC MODELS (For FastAPI) ---
class CartItemBase(BaseModel):
    user_id: int
    product_id: int
    quantity: int

class CartItemResponse(CartItemBase):
    id: int
    class Config:
        from_attributes = True

# --- 4. FASTAPI APP ---
app = FastAPI(title="Cart Microservice (SQLite)", version="1.0.0")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_cart_if_empty():
    db = SessionLocal()
    try:
        if db.query(DBCartItem).count() == 0:
            db.add_all([
                DBCartItem(user_id=1, product_id=101, quantity=2),
                DBCartItem(user_id=1, product_id=102, quantity=1),
                DBCartItem(user_id=2, product_id=101, quantity=5),
            ])
            db.commit()
    finally:
        db.close()


seed_cart_if_empty()


# --- 5. ENDPOINTS ---
@app.get("/api/cart/{user_id}", response_model=list[CartItemResponse])
def get_cart_items(user_id: int, db: Session = Depends(get_db)):
    """Retrieve all items in a specific user's cart"""
    return db.query(DBCartItem).filter(DBCartItem.user_id == user_id).all()


@app.get("/api/cart/item/{item_id}", response_model=CartItemResponse)
def get_cart_item(item_id: int, db: Session = Depends(get_db)):
    """Retrieve a single cart item by its unique ID"""
    item = db.query(DBCartItem).filter(DBCartItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return item

@app.post("/api/cart", response_model=CartItemResponse, status_code=201)
def add_to_cart(item: CartItemBase, db: Session = Depends(get_db)):
    """Add a product to the cart. If it's already in the cart, it increases the quantity."""
    # Check if this user already has this exact product in their cart
    existing_item = db.query(DBCartItem).filter(
        DBCartItem.user_id == item.user_id,
        DBCartItem.product_id == item.product_id
    ).first()

    if existing_item:
        # If it exists, just update the quantity!
        existing_item.quantity += item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        # Otherwise, create a brand new cart item
        new_item = DBCartItem(user_id=item.user_id, product_id=item.product_id, quantity=item.quantity)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item


@app.put("/api/cart/{item_id}", response_model=CartItemResponse)
def update_cart_item(item_id: int, quantity: int, db: Session = Depends(get_db)):
    """Update the quantity of a specific item in the cart"""
    item = db.query(DBCartItem).filter(DBCartItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    if quantity <= 0:
        # If quantity is 0 or less, remove the item
        db.delete(item)
        db.commit()
        raise HTTPException(status_code=204, detail="Item removed (quantity set to 0)")

    item.quantity = quantity
    db.commit()
    db.refresh(item)
    return item

@app.delete("/api/cart/{item_id}", status_code=204)
def remove_from_cart(item_id: int, db: Session = Depends(get_db)):
    """Remove a specific item from the cart by its ID"""
    item = db.query(DBCartItem).filter(DBCartItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(item)
    db.commit()
    return None