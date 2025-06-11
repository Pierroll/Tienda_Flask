from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def admin_required(f):
    """
    Decorador para rutas que requieren privilegios de administrador.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('No tienes permiso para acceder a esta página.', 'error')
            return redirect(url_for('views.home'))
        return f(*args, **kwargs)
    return decorated_function

def validate_password(password):
    """
    Valida que la contraseña cumpla con los requisitos de seguridad.
    """
    if len(password) < 8:
        return False, 'La contraseña debe tener al menos 8 caracteres.'
    if not re.search(r'[A-Z]', password):
        return False, 'La contraseña debe contener al menos una letra mayúscula.'
    if not re.search(r'[a-z]', password):
        return False, 'La contraseña debe contener al menos una letra minúscula.'
    if not re.search(r'\d', password):
        return False, 'La contraseña debe contener al menos un número.'
    return True, ''

def send_reset_email(user_email):
    """
    Envía un correo electrónico para restablecer la contraseña.
    """
    token = serializer.dumps(user_email, salt='password-reset-salt')
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    msg = Message('Restablecer Contraseña',
                  sender='noreply@tutienda.com',
                  recipients=[user_email])
    
    msg.body = f'''Para restablecer tu contraseña, visita el siguiente enlace:
    {reset_url}

Si no solicitaste este cambio, ignora este correo.
'''
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False
