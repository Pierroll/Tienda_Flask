from website import create_app, db
from website.models import Customer, Product, Order, Cart, Category, OrderItem
import sqlalchemy as sa
from sqlalchemy.exc import OperationalError

app = create_app()

with app.app_context():
    # First, create all tables that don't exist yet
    db.create_all()
    print("Created any missing tables")
    
    # Add the new tables if they don't exist
    inspector = sa.inspect(db.engine)
    
    # Check if Category table exists, if not create it
    if 'category' not in inspector.get_table_names():
        Category.__table__.create(db.engine)
        print("Created Category table")
        
        # Add some initial categories
        category1 = Category(name="Electronics", description="Electronic devices and gadgets")
        category2 = Category(name="Clothing", description="Apparel and fashion items")
        db.session.add(category1)
        db.session.add(category2)
        db.session.commit()
    
    # Add new columns to existing tables
    # This is a safer approach than dropping and recreating tables
    
    # Add columns to Product table if they don't exist
    product_columns = [column['name'] for column in inspector.get_columns('product')]
    
    if 'description' not in product_columns:
        try:
            db.engine.execute('ALTER TABLE product ADD COLUMN description TEXT')
            print("Added description column to Product")
        except Exception as e:
            print(f"Could not add description column: {e}")
    
    if 'category_id' not in product_columns:
        try:
            db.engine.execute('ALTER TABLE product ADD COLUMN category_id INTEGER REFERENCES category(id)')
            print("Added category_id column to Product")
        except Exception as e:
            print(f"Could not add category_id column: {e}")
    
    if 'discount' not in product_columns:
        try:
            db.engine.execute('ALTER TABLE product ADD COLUMN discount FLOAT DEFAULT 0.0')
            print("Added discount column to Product")
        except Exception as e:
            print(f"Could not add discount column: {e}")
            
    if 'flash_sale' not in product_columns:
        try:
            with db.engine.connect() as conn:
                conn.execute(sa.text('ALTER TABLE product ADD COLUMN flash_sale BOOLEAN DEFAULT 0'))
                conn.commit()
            print("Added flash_sale column to Product")
        except Exception as e:
            print(f"Could not add flash_sale column: {e}")
    
    # Add columns to Customer table if they don't exist
    customer_columns = [column['name'] for column in inspector.get_columns('customer')]
    
    if 'phone_number' not in customer_columns:
        try:
            db.engine.execute('ALTER TABLE customer ADD COLUMN phone_number VARCHAR(15)')
            print("Added phone_number column to Customer")
        except Exception as e:
            print(f"Could not add phone_number column: {e}")
    
    if 'address' not in customer_columns:
        try:
            db.engine.execute('ALTER TABLE customer ADD COLUMN address VARCHAR(255)')
            print("Added address column to Customer")
        except Exception as e:
            print(f"Could not add address column: {e}")
    
    if 'role' not in customer_columns:
        try:
            db.engine.execute('ALTER TABLE customer ADD COLUMN role VARCHAR(50) DEFAULT "customer"')
            print("Added role column to Customer")
        except Exception as e:
            print(f"Could not add role column: {e}")
    
    if 'last_login' not in customer_columns:
        try:
            db.engine.execute('ALTER TABLE customer ADD COLUMN last_login DATETIME')
            print("Added last_login column to Customer")
        except Exception as e:
            print(f"Could not add last_login column: {e}")
    
    # Add columns to Order table if they don't exist
    order_columns = [column['name'] for column in inspector.get_columns('order')]
    
    if 'total_price' not in order_columns:
        try:
            db.engine.execute('ALTER TABLE "order" ADD COLUMN total_price FLOAT NOT NULL DEFAULT 0')
            print("Added total_price column to Order")
        except Exception as e:
            print(f"Could not add total_price column: {e}")
    
    if 'payment_status' not in order_columns:
        try:
            db.engine.execute('ALTER TABLE "order" ADD COLUMN payment_status VARCHAR(50) NOT NULL DEFAULT "pending"')
            print("Added payment_status column to Order")
        except Exception as e:
            print(f"Could not add payment_status column: {e}")
    
    if 'payment_method' not in order_columns:
        try:
            db.engine.execute('ALTER TABLE "order" ADD COLUMN payment_method VARCHAR(50) NOT NULL DEFAULT "cash"')
            print("Added payment_method column to Order")
        except Exception as e:
            print(f"Could not add payment_method column: {e}")
    
    if 'order_date' not in order_columns:
        try:
            db.engine.execute('ALTER TABLE "order" ADD COLUMN order_date DATETIME DEFAULT CURRENT_TIMESTAMP')
            print("Added order_date column to Order")
        except Exception as e:
            print(f"Could not add order_date column: {e}")
    
    if 'shipping_address' not in order_columns:
        try:
            db.engine.execute('ALTER TABLE "order" ADD COLUMN shipping_address VARCHAR(255) DEFAULT ""')
            print("Added shipping_address column to Order")
        except Exception as e:
            print(f"Could not add shipping_address column: {e}")
    
    # Add columns to Cart table if they don't exist
    cart_columns = [column['name'] for column in inspector.get_columns('cart')]
    
    if 'total_price' not in cart_columns:
        try:
            db.engine.execute('ALTER TABLE cart ADD COLUMN total_price FLOAT NOT NULL DEFAULT 0')
            print("Added total_price column to Cart")
        except Exception as e:
            print(f"Could not add total_price column: {e}")
    
    # Check if admin user exists, if not create one
    admin = Customer.query.filter_by(email="admin@example.com").first()
    if not admin:
        admin = Customer(
            email="admin@example.com",
            username="admin",
            role="admin",
            phone_number="123456789",
            address="Admin Address"
        )
        admin.password = "admin123"  # This will use your password setter to hash
        db.session.add(admin)
        db.session.commit()
        print("Created admin user")
    
    print("Database has been updated with new schema while preserving existing data!")