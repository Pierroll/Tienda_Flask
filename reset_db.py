from website import create_app, db
from website.models import Customer, Product, Order, Cart, Category

app = create_app()

with app.app_context():
    # Drop all existing tables and recreate them
    db.drop_all()
    db.create_all()
    
    # Optionally add initial data
    # For example, create an admin user
    admin = Customer(
        email="admin@example.com",
        username="admin",
        role="admin",
        phone_number="123456789",
        address="Admin Address"
    )
    admin.password = "admin123"  # This will use your password setter to hash
    
    # Add some categories
    category1 = Category(name="Electronics", description="Electronic devices and gadgets")
    category2 = Category(name="Clothing", description="Apparel and fashion items")
    
    # Add to database
    db.session.add(admin)
    db.session.add(category1)
    db.session.add(category2)
    db.session.commit()
    
    print("Database has been reset and initialized with new schema!")