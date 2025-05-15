from website import create_app, db
from website.models import Customer
from werkzeug.security import generate_password_hash

def create_test_user():
    app = create_app()
    with app.app_context():
        # Check if test user already exists
        test_user = Customer.query.filter_by(email='test@example.com').first()
        if test_user:
            print("Test user already exists")
            return
        
        # Create test user
        test_user = Customer(
            email='test@example.com',
            username='testuser',
            role='customer',
            is_first_login=False
        )
        test_user.password = 'password123'  # This will be hashed by the setter
        
        db.session.add(test_user)
        db.session.commit()
        print("Test user created successfully!")
        print(f"Email: test@example.com")
        print(f"Password: password123")

if __name__ == '__main__':
    create_test_user()
