from . import db
from .models import Customer, Cart, Order
from .modules.product.models import Product, Category

def init_db():
    # Drop all tables
    db.drop_all()
    
    # Create all tables
    db.create_all()
    
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db() 