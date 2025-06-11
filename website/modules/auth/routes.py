from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import re
import os
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_mail import Message
from ... import db
from ...models import Customer
from . import mail, serializer
from .forms import (
    LoginForm, 
    SignUpForm, 
    ForgotPasswordForm, 
    ResetPasswordForm,
    ChangePasswordForm,
    EditProfileForm
)

# Obtener la ruta absoluta al directorio de plantillas
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# Crear el blueprint de autenticación
auth_bp = Blueprint('auth', __name__,
                   template_folder=template_dir,
                   static_folder='static',
                   url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember.data
        
        user = Customer.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            flash('Por favor verifica tus credenciales e intenta de nuevo.', 'error')
            return redirect(url_for('auth.login'))
            
        # Verificar si la cuenta está bloqueada
        if user.locked_until and user.locked_until > datetime.utcnow():
            remaining = user.locked_until - datetime.utcnow()
            minutes, seconds = divmod(int(remaining.total_seconds()), 60)
            flash(f'Tu cuenta está bloqueada. Intenta nuevamente en {minutes} minutos y {seconds} segundos.', 'error')
            return render_template('auth/login.html', form=form)
            
        login_user(user, remember=remember)
        user.last_login = datetime.utcnow()
        user.login_attempts = 0  # Reiniciar intentos fallidos
        db.session.commit()
        
        flash('¡Inicio de sesión exitoso!', 'success')
        
        # Redirigir a cambio de contraseña si es el primer inicio de sesión
        if user.is_first_login:
            return redirect(url_for('auth.change_password'))
            
        next_page = request.args.get('next')
        return redirect(next_page or url_for('views.home'))
        
    return render_template('auth/login.html', form=form)
        

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
        
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = Customer.query.filter_by(email=email).first()
        
        if user:
            try:
                # Generar token de restablecimiento
                token = serializer.dumps(user.email, salt='password-reset')
                reset_url = url_for('auth.reset_password', token=token, _external=True)
                
                # Enviar correo electrónico
                msg = Message(
                    'Restablecer Contraseña',
                    sender=current_app.config.get('MAIL_DEFAULT_SENDER'),
                    recipients=[user.email]
                )
                msg.body = f'''Para restablecer tu contraseña, visita el siguiente enlace:
{reset_url}

Este enlace expirará en 1 hora.

Si no solicitaste este restablecimiento, ignora este correo.
'''
                
                mail.send(msg)
                flash('Se ha enviado un correo con instrucciones para restablecer tu contraseña.', 'info')
                return redirect(url_for('auth.login'))
                
            except Exception as e:
                current_app.logger.error(f"Error al enviar correo de restablecimiento: {str(e)}")
                flash('Ocurrió un error al enviar el correo. Por favor, inténtalo de nuevo más tarde.', 'error')
        else:
            # Por seguridad, no revelamos si el correo existe o no
            flash('Si existe una cuenta con ese correo, se ha enviado un enlace para restablecer la contraseña.', 'info')
            return redirect(url_for('auth.login'))
        
    return render_template('auth/forgot_password.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
        
    form = ResetPasswordForm()
    
    try:
        # Verificar y cargar el token (válido por 1 hora)
        email = serializer.loads(token, salt='password-reset', max_age=3600)
        user = Customer.query.filter_by(email=email).first()
        
        if not user:
            flash('El enlace de restablecimiento no es válido.', 'error')
            return redirect(url_for('auth.login'))
            
        if form.validate_on_submit():
            # Validar que las contraseñas coincidan
            if form.password.data != form.confirm_password.data:
                flash('Las contraseñas no coinciden.', 'error')
                return render_template('auth/reset_password.html', form=form, token=token)
            
            # Validar fortaleza de la contraseña
            if len(form.password.data) < 8:
                flash('La contraseña debe tener al menos 8 caracteres.', 'error')
                return render_template('auth/reset_password.html', form=form, token=token)
            
            # Actualizar la contraseña
            user.password = form.password.data
            user.is_first_login = False
            db.session.commit()
            
            flash('Tu contraseña ha sido actualizada. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
            
    except SignatureExpired:
        flash('El enlace de restablecimiento ha expirado. Por favor, solicita uno nuevo.', 'error')
        return redirect(url_for('auth.forgot_password'))
    except BadSignature:
        flash('El enlace de restablecimiento no es válido.', 'error')
        return redirect(url_for('auth.forgot_password'))
    except Exception as e:
        current_app.logger.error(f"Error al restablecer contraseña: {str(e)}")
        flash('Ocurrió un error al procesar tu solicitud. Por favor, inténtalo de nuevo.', 'error')
        return redirect(url_for('auth.forgot_password'))
        
    return render_template('auth/reset_password.html', form=form, token=token)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
        
    form = SignUpForm()
    
    if form.validate_on_submit():
        try:
            # Verificar si el correo ya está registrado
            existing_user = Customer.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('Ya existe una cuenta con este correo electrónico. Por favor, inicia sesión.', 'error')
                return redirect(url_for('auth.login'))
                
            # Validar que las contraseñas coincidan
            if form.password.data != form.confirm_password.data:
                flash('Las contraseñas no coinciden.', 'error')
                return render_template('auth/sign_up.html', form=form)
            
            # Validar fortaleza de la contraseña
            if len(form.password.data) < 8:
                flash('La contraseña debe tener al menos 8 caracteres.', 'error')
                return render_template('auth/sign_up.html', form=form)
            
            # Crear nuevo usuario
            new_user = Customer(
                email=form.email.data,
                username=form.username.data,
                role='customer',
                is_first_login=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                login_attempts=0,
                last_attempt=datetime.utcnow()
            )
            new_user.password = form.password.data  # Esto usará el setter para hashear la contraseña
            
            db.session.add(new_user)
            db.session.commit()
            
            # Enviar correo de bienvenida
            try:
                msg = Message(
                    '¡Bienvenido a Nuestra Tienda!',
                    sender=current_app.config.get('MAIL_DEFAULT_SENDER'),
                    recipients=[new_user.email]
                )
                msg.body = f'''¡Gracias por registrarte, {new_user.first_name}!

Ahora puedes disfrutar de todos los beneficios de nuestra tienda en línea.

Atentamente,
El equipo de la tienda'''
                mail.send(msg)
            except Exception as e:
                current_app.logger.error(f"Error al enviar correo de bienvenida: {str(e)}")
            
            # Iniciar sesión automáticamente
            login_user(new_user)
            
            flash('¡Registro exitoso! Ya puedes comenzar a comprar.', 'success')
            return redirect(url_for('views.home'))
            
        except Exception as e:
            db.session.rollback()
            # Log the full error with traceback
            current_app.logger.error(f"Error en el registro: {str(e)}", exc_info=True)
            # Log form data for debugging (without password)
            current_app.logger.error(f"Form data: email={form.email.data}, username={form.username.data}")
            # Log form validation errors if any
            if form.errors:
                current_app.logger.error(f"Form errors: {form.errors}")
            flash('Ocurrió un error al procesar tu registro. Por favor, verifica los datos e inténtalo de nuevo.', 'error')
        
    return render_template('auth/sign_up.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    # Registrar el cierre de sesión
    current_user.last_logout = datetime.utcnow()
    db.session.commit()
    
    # Cerrar la sesión
    logout_user()
    
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        try:
            # Verificar la contraseña actual
            if not check_password_hash(current_user.password_hash, form.current_password.data):
                flash('La contraseña actual es incorrecta.', 'error')
                return render_template('auth/change_password.html', form=form)
                
            # Verificar que la nueva contraseña sea diferente
            if check_password_hash(current_user.password_hash, form.new_password.data):
                flash('La nueva contraseña debe ser diferente a la actual.', 'error')
                return render_template('auth/change_password.html', form=form)
            
            # Validar fortaleza de la nueva contraseña
            if len(form.new_password.data) < 8:
                flash('La nueva contraseña debe tener al menos 8 caracteres.', 'error')
                return render_template('auth/change_password.html', form=form)
                
            # Actualizar la contraseña
            current_user.password = form.new_password.data
            current_user.is_first_login = False
            current_user.password_changed_at = datetime.utcnow()
            db.session.commit()
            
            # Enviar notificación por correo
            try:
                msg = Message(
                    'Contraseña actualizada',
                    sender=current_app.config.get('MAIL_DEFAULT_SENDER'),
                    recipients=[current_user.email]
                )
                msg.body = f'''Hola {current_user.first_name or 'usuario'},

Tu contraseña ha sido actualizada exitosamente. Si no realizaste este cambio, por favor contacta a soporte de inmediato.

Atentamente,
El equipo de la tienda'''
                mail.send(msg)
            except Exception as e:
                current_app.logger.error(f"Error al enviar notificación de cambio de contraseña: {str(e)}")
            
            flash('Tu contraseña ha sido actualizada exitosamente.', 'success')
            return redirect(url_for('views.profile'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al cambiar contraseña: {str(e)}")
            flash('Ocurrió un error al actualizar tu contraseña. Por favor, inténtalo de nuevo.', 'error')
        
    return render_template('auth/change_password.html', form=form)

@auth_bp.route('/profile')
@login_required
def profile():
    # Redirigir al formulario de edición del perfil del usuario actual
    return redirect(url_for('auth.edit_profile', user_id=current_user.id))

@auth_bp.route('/profile/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    # Si el usuario no es admin, solo puede editar su propio perfil
    if not current_user.is_admin and current_user.id != user_id:
        flash('No tienes permiso para editar este perfil.', 'error')
        return redirect(url_for('views.home'))
    
    # Obtener el usuario a editar
    user = Customer.query.get_or_404(user_id)
    form = EditProfileForm(obj=user)
    
    if form.validate_on_submit():
        try:
            # Actualizar datos básicos
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            
            # Verificar si el email ya está en uso por otro usuario
            if user.email != form.email.data:
                existing_user = Customer.query.filter(Customer.email == form.email.data, Customer.id != user.id).first()
                if existing_user:
                    flash('Este correo electrónico ya está en uso por otra cuenta.', 'error')
                    return render_template('auth/edit_profile.html', form=form, user=user, is_editing=True)
                user.email = form.email.data
            
            # Solo los administradores pueden cambiar ciertos campos
            if current_user.is_admin:
                user.role = form.role.data
                user.is_active = form.is_active.data
            
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            flash('Perfil actualizado exitosamente.', 'success')
            
            # Redirigir según el tipo de usuario
            if current_user.is_admin and current_user.id != user_id:
                return redirect(url_for('admin.management'))
            return redirect(url_for('views.profile'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al actualizar perfil: {str(e)}")
            flash('Ocurrió un error al actualizar el perfil. Por favor, inténtalo de nuevo.', 'error')
    
    # Si es GET o hay errores en el formulario
    return render_template('auth/edit_profile.html', form=form, user=user, is_editing=True)
