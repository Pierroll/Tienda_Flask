from website import create_app, db
from website.models import Customer, Product, Order, Cart, Category
import os

app = create_app()

with app.app_context():
    print("\n=== Starting Database Reset Process ===")
    print("Step 1: Dropping existing tables...")
    db.drop_all()
    print("✓ Tables dropped successfully")
    
    print("\nStep 2: Creating new tables...")
    db.create_all()
    print("✓ Tables created successfully")
    
    print("\nStep 3: Creating users...")
    # Create users
    admin = Customer(
        email="admin@example.com",
        username="admin",
        role="admin",
        phone_number="123456789",
        address="Admin Address"
    )
    admin.password = "admin123"
    print("✓ Admin user created")

    user1 = Customer(
        email="user1@example.com",
        username="user1",
        role="user",
        phone_number="987654321",
        address="User 1 Address"
    )
    user1.password = "user123"
    print("✓ User 1 created")

    user2 = Customer(
        email="user2@example.com",
        username="user2",
        role="user",
        phone_number="555555555",
        address="User 2 Address"
    )
    user2.password = "user123"
    print("✓ User 2 created")
    
    print("\nStep 4: Creating categories...")
    # Add categories
    categories = [
        Category(name="Electronics", description="Electronic devices and gadgets", icon="fa fa-laptop"),
        Category(name="Clothing", description="Apparel and fashion items", icon="fa fa-tshirt"),
        Category(name="Books", description="Books and literature", icon="fa fa-book"),
        Category(name="Home & Kitchen", description="Home appliances and kitchen items", icon="fa fa-home"),
        Category(name="Sports", description="Sports equipment and accessories", icon="fa fa-futbol")
    ]
    print("✓ Categories created")
    
    print("\nStep 5: Creating products...")
    # Add products
    products = [
        Product(
            product_name="Laptop Pro",
            current_price=999.99,
            previous_price=1299.99,
            in_stock=10,
            flash_sale=True,
            product_picture="../static/images/laptop.jpg",
            category=categories[0]
        ),
        Product(
            product_name="Smartphone X",
            current_price=699.99,
            previous_price=799.99,
            in_stock=15,
            flash_sale=True,
            product_picture="../static/images/phone.jpg",
            category=categories[0]
        ),
        Product(
            product_name="T-Shirt Classic",
            current_price=19.99,
            previous_price=29.99,
            in_stock=50,
            flash_sale=False,
            product_picture="../static/images/tshirt.jpg",
            category=categories[1]
        ),
        Product(
            product_name="Python Programming Book",
            current_price=39.99,
            previous_price=49.99,
            in_stock=20,
            flash_sale=True,
            product_picture="../static/images/book.jpg",
            category=categories[2]
        ),
        Product(
            product_name="Coffee Maker",
            current_price=79.99,
            previous_price=99.99,
            in_stock=8,
            flash_sale=False,
            product_picture="../static/images/coffee.jpg",
            category=categories[3]
        ),
        Product(
            product_name="Yoga Mat",
            current_price=29.99,
            previous_price=39.99,
            in_stock=25,
            flash_sale=True,
            product_picture="../static/images/yoga.jpg",
            category=categories[4]
        )
    ]
    print("✓ Products created")
    
    print("\nStep 6: Adding data to database...")
    # Add to database
    db.session.add(admin)
    db.session.add(user1)
    db.session.add(user2)
    print("✓ Users added to session")
    
    for category in categories:
        db.session.add(category)
    print("✓ Categories added to session")
    
    for product in products:
        db.session.add(product)
    print("✓ Products added to session")
    
    print("\nStep 7: Committing changes...")
    try:
        db.session.commit()
        print("✓ Data committed successfully!")
    except Exception as e:
        print(f"✗ Error committing data: {str(e)}")
        db.session.rollback()
        raise e
    
    print("\nStep 8: Verifying data...")
    # Verify data was saved
    users = Customer.query.all()
    categories = Category.query.all()
    products = Product.query.all()
    
    print(f"\nUsers in database: {len(users)}")
    for user in users:
        print(f"- {user.username} ({user.email})")
    
    print(f"\nCategories in database: {len(categories)}")
    for category in categories:
        print(f"- {category.name}")
    
    print(f"\nProducts in database: {len(products)}")
    for product in products:
        print(f"- {product.product_name} (${product.current_price})")
    
    print("\n=== Database reset and initialization complete! ===")