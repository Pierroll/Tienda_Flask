from website import create_app, db
from website.models import Customer, Product, Order, Cart, Category

app = create_app()

with app.app_context():
    print("Checking database contents...")
    
    # Check users
    users = Customer.query.all()
    print(f"\nUsers in database: {len(users)}")
    for user in users:
        print(f"- {user.username} ({user.email})")
    
    # Check categories
    categories = Category.query.all()
    print(f"\nCategories in database: {len(categories)}")
    for category in categories:
        print(f"- {category.name}")
    
    # Check products
    products = Product.query.all()
    print(f"\nProducts in database: {len(products)}")
    for product in products:
        print(f"- {product.product_name} (${product.current_price})")
    
    print("\nDatabase check complete!") 