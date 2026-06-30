from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from contextlib import asynccontextmanager  
import uvicorn

from database import Base, engine, get_db
from models import Order
from config import redis_client, INVENTORY_KEY

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This block executes BEFORE the server starts accepting requests
    Base.metadata.create_all(bind=engine)
    redis_client.set(INVENTORY_KEY, 500)
    print("[System Init] Flash sale stock initialized to 500 tokens in Redis.")
    yield


app = FastAPI(title="Distributed Flash Sale Engine", lifespan=lifespan)

class OrderRequest(BaseModel):
    user_id: str
    product_id: str

@app.post("/orders", status_code=status.HTTP_201_CREATED)
async def place_order(payload: OrderRequest, db: Session = Depends(get_db)):
    # --- PHASE 1: ATOMIC REDIS DECREMENT ---
    current_stock = redis_client.decr(INVENTORY_KEY)

    if current_stock < 0:
        redis_client.incr(INVENTORY_KEY)
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED, 
            detail="Transaction Rejected: Product is completely sold out!"
        )

    # --- PHASE 2: PERSISTENCE LAYER WRITE ---
    try:
        new_order = Order(user_id=payload.user_id, product_id=payload.product_id)
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        return {"status": "SUCCESS", "order_id": new_order.id, "message": "Item secured successfully!"}
    
    except Exception as e:
        redis_client.incr(INVENTORY_KEY)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database write crash: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, workers=4)