from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String(150))
    phone_number = db.Column(db.String(15), nullable=True)  # New attribute
    address = db.Column(db.String(255), nullable=True)  # New attribute
    role = db.Column(db.String(50), default='customer')  # New attribute
    date_joined = db.Column(db.DateTime(), default=datetime.utcnow)
    last_login = db.Column(db.DateTime(), nullable=True)  # New attribute

    cart_items = db.relationship('Cart', backref=db.backref('customer', lazy=True))
    orders = db.relationship('Order', backref=db.backref('customer', lazy=True))

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def password(self):
        raise AttributeError('Password is not a readable Attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password=password)

    def __str__(self):
        return '<Customer %r>' % self.id


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)  # New attribute
    current_price = db.Column(db.Float, nullable=False)
    previous_price = db.Column(db.Float, nullable=False)
    in_stock = db.Column(db.Integer, nullable=False)
    product_picture = db.Column(db.String(1000), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)  # New attribute
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    discount = db.Column(db.Float, default=0.0)  # New attribute
    flash_sale = db.Column(db.Boolean, default=False)  # Add this new column

    carts = db.relationship('Cart', backref=db.backref('product', lazy=True))
    # Modified relationship
    orders = db.relationship('OrderItem', backref=db.backref('product', lazy=True))

    def __str__(self):
        return '<Product %r>' % self.product_name


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)  # New attribute
    payment_status = db.Column(db.String(50), nullable=False)  # New attribute
    payment_method = db.Column(db.String(50), nullable=False)  # New attribute
    order_date = db.Column(db.DateTime, default=datetime.utcnow)  # New attribute
    shipping_address = db.Column(db.String(255), nullable=False)  # New attribute
    
    # Add relationship with OrderItem
    items = db.relationship('OrderItem', backref=db.backref('order', lazy=True))
    
    # Add this property to resolve the error
    @property
    def customer_link(self):
        return self.customer

    def __str__(self):
        return '<Order %r>' % self.id


# New OrderItem model
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)
    
    def __str__(self):
        return '<OrderItem %r>' % self.id


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)  # New attribute
    
    # Modified property with getter and setter
    @property
    def customer_link(self):
        return self.customer
    
    @customer_link.setter
    def customer_link(self, value):
        # Check if value is an integer (customer ID)
        if isinstance(value, int):
            # Set the customer_id directly
            self.customer_id = value
        else:
            # Otherwise, assume it's a Customer object
            self.customer = value
    
    # Modified property with getter and setter
    @property
    def product_link(self):
        return self.product
    
    @product_link.setter
    def product_link(self, value):
        # Check if value is an integer (product ID)
        if isinstance(value, int):
            # Set the product_id directly
            self.product_id = value
        else:
            # Otherwise, assume it's a Product object
            self.product = value
    
    def __str__(self):
        return '<Cart %r>' % self.id


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), nullable=True)
    products = db.relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'











