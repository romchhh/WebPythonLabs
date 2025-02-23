from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate
from models import Order
from schemas import OrderCreate

def get_order(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()

def create_order(db: Session, order: OrderCreate):
    db_order = Order(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order
