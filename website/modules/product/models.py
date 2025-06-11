from ... import db
from datetime import datetime
from ..category.models import Category  # Importar Category desde el módulo de categorías

class Product(db.Model):
    """Modelo para los productos de la tienda"""
    __tablename__ = 'product'
    
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    current_price = db.Column(db.Float, nullable=False)
    previous_price = db.Column(db.Float)
    in_stock = db.Column(db.Boolean, default=True)
    stock_quantity = db.Column(db.Integer, default=0, nullable=False)
    flash_sale = db.Column(db.Boolean, default=False)
    product_picture = db.Column(db.String(200))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    # Usamos referencias completas para evitar problemas de importación circular
    order_items = db.relationship('website.models.OrderItem', backref='product', lazy=True, cascade='all, delete-orphan')
    carts = db.relationship('website.models.Cart', backref=db.backref('product', lazy=True), cascade='all, delete-orphan')
    
    def __str__(self):
        return self.product_name
    
    def to_dict(self):
        """Convierte el objeto a un diccionario"""
        return {
            'id': self.id,
            'product_name': self.product_name,
            'description': self.description,
            'current_price': self.current_price,
            'previous_price': self.previous_price,
            'in_stock': self.in_stock,
            'stock_quantity': self.stock_quantity,
            'flash_sale': self.flash_sale,
            'product_picture': self.product_picture,
            'category_id': self.category_id,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# La clase Category ha sido movida a website.modules.category.models
