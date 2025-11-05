from website import create_app, db
from website.models import Customer
from website.modules.product.models import Product, Category
from werkzeug.security import generate_password_hash

def seed_database():
    app = create_app()
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()

        # Crear usuarios de prueba
        print("Creating test users...")
        users_to_create = [
            {'email': 'cinthia@tienda.com', 'password': 'Cinthia123456', 'username': 'Cinthia', 'role': 'customer'},
            {'email': 'luacas@tienda.com', 'password': 'Lucas123456', 'username': 'Lucas', 'role': 'admin'},
            {'email': 'admin@tienda.com', 'password': 'Admin123', 'username': 'Admin', 'role': 'admin'},
            {'email': 'test@example.com', 'password': 'password123', 'username': 'Test', 'role': 'customer'}
        ]

        for user_data in users_to_create:
            if not Customer.query.filter_by(email=user_data['email']).first():
                new_user = Customer(
                    email=user_data['email'],
                    username=user_data['username'],
                    role=user_data['role'],
                    password_hash=generate_password_hash(user_data['password'], method='pbkdf2:sha256')
                )
                db.session.add(new_user)
                print(f"User {user_data['email']} created.")

        # Crear categorías
        print("Creating categories...")
        cat1 = Category(name='Electrónicos')
        cat2 = Category(name='Ropa y Accesorios')
        db.session.add_all([cat1, cat2])
        db.session.commit() # Commit para que las categorías obtengan sus IDs
        print("Categories created.")

        # Crear productos
        print("Creating products...")
        product1 = Product(
            product_name='Laptop de Prueba',
            description='Una laptop para pruebas automatizadas.',
            current_price=999.99,
            in_stock=50,
            category_id=cat1.id
        )
        product2 = Product(
            product_name='Camiseta de Prueba',
            description='Una camiseta para la prueba de agregar al carrito.',
            current_price=25.50,
            in_stock=100,
            category_id=cat2.id # Asignar a la categoría 2
        )
        db.session.add_all([product1, product2])

        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()
