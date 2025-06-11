from datetime import datetime
from website import db

class DireccionEnvio(db.Model):
    """Modelo para las direcciones de envío del cliente"""
    __tablename__ = 'direcciones_envio'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100))
    codigo_postal = db.Column(db.String(20))
    telefono = db.Column(db.String(20))
    es_principal = db.Column(db.Boolean, default=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con el cliente
    cliente = db.relationship('Customer', backref=db.backref('direcciones', lazy=True))
    
    def __repr__(self):
        return f'<DireccionEnvio {self.nombre} - {self.ciudad}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'direccion': self.direccion,
            'ciudad': self.ciudad,
            'region': self.region,
            'codigo_postal': self.codigo_postal,
            'telefono': self.telefono,
            'es_principal': self.es_principal
        }

class ListaDeseos(db.Model):
    """Modelo para las listas de deseos de los clientes"""
    __tablename__ = 'listas_deseos'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    es_publica = db.Column(db.Boolean, default=False)
    creada_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizada_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    cliente = db.relationship('Customer', backref=db.backref('listas_deseos', lazy=True))
    productos = db.relationship('ProductoListaDeseos', back_populates='lista', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ListaDeseos {self.nombre} - {self.cliente.username}>'

class ProductoListaDeseos(db.Model):
    """Tabla intermedia para la relación muchos a muchos entre ListaDeseos y Product"""
    __tablename__ = 'productos_lista_deseos'
    
    id = db.Column(db.Integer, primary_key=True)
    lista_id = db.Column(db.Integer, db.ForeignKey('listas_deseos.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    cantidad = db.Column(db.Integer, default=1)
    anadido_en = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    lista = db.relationship('ListaDeseos', back_populates='productos')
    producto = db.relationship('Product')
    
    def __repr__(self):
        return f'<ProductoListaDeseos {self.producto.nombre} en lista {self.lista_id}>'
