from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, NumberRange
# Importación diferida para evitar importaciones circulares
from flask import current_app

def get_customer_model():
    from website.models import Customer
    return Customer

class PerfilForm(FlaskForm):
    """Formulario para editar el perfil del cliente"""
    username = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    phone_number = StringField('Teléfono', validators=[DataRequired(), Length(min=9, max=15)])
    address = TextAreaField('Dirección', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Actualizar perfil')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(PerfilForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
    
    def validate_username(self, username):
        if username.data != self.original_username:
            Customer = get_customer_model()
            user = Customer.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Por favor usa un nombre de usuario diferente.')
    
    def validate_email(self, email):
        if email.data != self.original_email:
            Customer = get_customer_model()
            user = Customer.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Por favor usa un correo electrónico diferente.')

class DireccionEnvioForm(FlaskForm):
    """Formulario para agregar/editar direcciones de envío"""
    nombre = StringField('Nombre completo', validators=[DataRequired(), Length(max=100)])
    direccion = TextAreaField('Dirección', validators=[DataRequired(), Length(max=200)])
    ciudad = StringField('Ciudad', validators=[DataRequired(), Length(max=100)])
    region = StringField('Región/Departamento', validators=[Optional(), Length(max=100)])
    codigo_postal = StringField('Código postal', validators=[Optional(), Length(max=20)])
    telefono = StringField('Teléfono', validators=[DataRequired(), Length(max=20)])
    es_principal = BooleanField('Establecer como dirección principal')
    submit = SubmitField('Guardar dirección')

class ListaDeseosForm(FlaskForm):
    """Formulario para crear/editar listas de deseos"""
    nombre = StringField('Nombre de la lista', validators=[DataRequired(), Length(max=100)])
    es_publica = BooleanField('Lista pública')
    submit = SubmitField('Guardar lista')

class AgregarAlCarritoForm(FlaskForm):
    """Formulario para agregar productos al carrito"""
    cantidad = IntegerField('Cantidad', default=1, validators=[
        NumberRange(min=1, message='La cantidad debe ser al menos 1')
    ])
    submit = SubmitField('Agregar al carrito')

class CheckoutForm(FlaskForm):
    """Formulario para el proceso de pago"""
    direccion_envio = SelectField('Dirección de envío', coerce=int, validators=[DataRequired()])
    notas = TextAreaField('Notas adicionales', validators=[Optional(), Length(max=500)])
    metodo_pago = SelectField('Método de pago', 
                             choices=[
                                 ('tarjeta', 'Tarjeta de crédito/débito'),
                                 ('paypal', 'PayPal'),
                                 ('efectivo', 'Contra entrega')
                             ], 
                             validators=[DataRequired()])
    aceptar_terminos = BooleanField('Acepto los términos y condiciones', validators=[DataRequired()])
    submit = SubmitField('Realizar pedido')
    
    def validate_aceptar_terminos(self, field):
        if not field.data:
            raise ValidationError('Debes aceptar los términos y condiciones para continuar.')
