from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from ... import db
from ...models import Order, Customer
from ...modules.product.models import Product
from ...forms import ShopItemsForm, CreateAdminForm
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_module():
    admin_bp = Blueprint('admin', __name__, template_folder='templates')
    
    @admin_bp.route('/')
    @login_required
    def admin_dashboard():
        if not current_user.is_admin:
            flash('Acceso denegado. Se requiere ser administrador.', 'danger')
            return redirect(url_for('views.home'))
            
        # Obtener estadísticas para el dashboard
        total_products = Product.query.count()
        total_orders = Order.query.count()
        total_customers = Customer.query.filter_by(is_admin=False).count()
        
        # Obtener órdenes recientes
        recent_orders = Order.query.order_by(Order.date_created.desc()).limit(5).all()
        
        return render_template('admin/dashboard.html', 
                             total_products=total_products,
                             total_orders=total_orders,
                             total_customers=total_customers,
                             recent_orders=recent_orders)
    
    @admin_bp.route('/admin-management')
    @login_required
    def admin_management():
        if not current_user.is_admin:
            flash('Acceso denegado. Se requiere ser administrador.', 'danger')
            return redirect(url_for('views.home'))
            
        # Obtener todos los usuarios con rol 'admin' o 'super_admin'
        admins = Customer.query.filter(Customer.role.in_(['admin', 'super_admin'])).all()
        
        # Imprimir información de depuración
        print("\n=== DEBUG: Admin Management ===")
        print(f"Total de administradores encontrados: {len(admins)}")
        for admin in admins:
            print(f"- {admin.username} (ID: {admin.id}, Email: {admin.email}, Role: {admin.role})")
        print("============================\n")
        
        return render_template('admin/admin_management.html', admins=admins)
    
    @admin_bp.route('/create-admin', methods=['GET', 'POST'])
    @login_required
    def create_admin():
        if not current_user.is_admin:
            flash('Acceso denegado. Se requiere ser administrador.', 'danger')
            return redirect(url_for('views.home'))
            
        form = CreateAdminForm()
        
        if form.validate_on_submit():
            try:
                hashed_password = generate_password_hash(form.password.data, method='sha256')
                
                new_admin = Customer(
                    username=form.username.data,
                    email=form.email.data,
                    password=hashed_password,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    is_admin=True,
                    created_at=datetime.utcnow()
                )
                
                db.session.add(new_admin)
                db.session.commit()
                
                flash('Nuevo administrador creado exitosamente!', 'success')
                return redirect(url_for('admin.admin_management'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error al crear el administrador: {str(e)}', 'danger')
        
        return render_template('admin/create_admin.html', form=form)
    
    @admin_bp.route('/update-user-role/<int:user_id>', methods=['POST'])
    @login_required
    def update_user_role(user_id):
        if not current_user.is_admin:
            flash('Acceso denegado. Se requiere ser administrador.', 'danger')
            return redirect(url_for('views.home'))
            
        user = Customer.query.get_or_404(user_id)
        new_role = request.form.get('role')
        
        # Validar que el rol sea válido
        if new_role not in ['customer', 'admin', 'super_admin']:
            flash('Rol no válido', 'danger')
            return redirect(url_for('admin.admin_management'))
            
        # No permitir modificar el rol del super administrador actual
        if user.role == 'super_admin' and user.id != current_user.id:
            flash('No puedes modificar el rol de otro super administrador', 'danger')
            return redirect(url_for('admin.admin_management'))
            
        user.role = new_role
        db.session.commit()
        
        flash(f'Rol de {user.username} actualizado a {new_role}', 'success')
        return redirect(url_for('admin.admin_management'))
    
    @admin_bp.route('/delete-admin/<int:admin_id>', methods=['POST'])
    @login_required
    def delete_admin(admin_id):
        if not current_user.is_admin:
            flash('Acceso denegado. Se requiere ser administrador.', 'danger')
            return redirect(url_for('views.home'))
            
        # No permitir eliminarse a sí mismo
        if admin_id == current_user.id:
            flash('No puedes eliminarte a ti mismo', 'danger')
            return redirect(url_for('admin.admin_management'))
            
        admin_to_delete = Customer.query.get_or_404(admin_id)
        
        # No permitir eliminar super administradores
        if admin_to_delete.role == 'super_admin':
            flash('No puedes eliminar un super administrador', 'danger')
            return redirect(url_for('admin.admin_management'))
            
        # Cambiar el rol a customer en lugar de eliminar
        admin_to_delete.role = 'customer'
        db.session.commit()
        
        flash(f'Se ha quitado los privilegios de administrador a {admin_to_delete.username}', 'success')
        return redirect(url_for('admin.admin_management'))
    
    return admin_bp
