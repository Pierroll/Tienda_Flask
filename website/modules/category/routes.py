from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, current_app
from flask_login import login_required, current_user
from ... import db
from .models import Category

# Crear el blueprint para categorías
category_blueprint = Blueprint('category', __name__,
                             template_folder='templates',
                             static_folder='static',
                             url_prefix='/category')

@category_blueprint.route('/', methods=['GET'])
def list_categories():
    # Obtener todas las categorías ordenadas por nombre
    categories = Category.query.order_by(Category.name).all()
    return render_template('category/categoria.html', categories=categories)

@category_blueprint.route('/<int:category_id>')
def category_products(category_id):
    # Obtener la categoría con sus productos
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Paginación de productos
    products = category.products.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('category/category_products.html', 
                         category=category, 
                         products=products)

@category_blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add_category():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            
            # Validar que el nombre no esté vacío
            if not name:
                flash('El nombre de la categoría es requerido', 'error')
                return redirect(request.url)
            
            # Verificar si ya existe una categoría con ese nombre
            existing_category = Category.query.filter_by(name=name).first()
            if existing_category:
                flash('Ya existe una categoría con ese nombre', 'error')
                return redirect(request.url)
            
            # Crear la nueva categoría
            new_category = Category(
                name=name,
                description=description
            )
            
            db.session.add(new_category)
            db.session.commit()
            
            flash('¡Categoría creada exitosamente!', 'success')
            return redirect(url_for('category.list_categories'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al crear categoría: {str(e)}")
            flash('Error al crear la categoría. Por favor, intente nuevamente.', 'error')
    
    return render_template('category/agregar_categoria.html')

@category_blueprint.route('/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            
            # Validar que el nombre no esté vacío
            if not name:
                flash('El nombre de la categoría es requerido', 'error')
                return redirect(request.url)
            
            # Verificar si ya existe otra categoría con el mismo nombre
            existing_category = Category.query.filter(
                Category.id != category_id,
                Category.name == name
            ).first()
            
            if existing_category:
                flash('Ya existe otra categoría con ese nombre', 'error')
                return redirect(request.url)
            
            # Actualizar la categoría
            category.name = name
            category.description = description
            
            db.session.commit()
            
            flash('¡Categoría actualizada exitosamente!', 'success')
            return redirect(url_for('category.list_categories'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al actualizar categoría: {str(e)}")
            flash('Error al actualizar la categoría. Por favor, intente nuevamente.', 'error')
    
    return render_template('category/editar_categoria.html', category=category)

@category_blueprint.route('/delete/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    try:
        # Verificar si la categoría tiene productos asociados
        if category.products:
            flash('No se puede eliminar la categoría porque tiene productos asociados', 'error')
            return redirect(url_for('category.list_categories'))
        
        # Eliminar la categoría
        db.session.delete(category)
        db.session.commit()
        
        flash('¡Categoría eliminada exitosamente!', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error al eliminar categoría: {str(e)}")
        flash('Error al eliminar la categoría. Por favor, intente nuevamente.', 'error')
    
    return redirect(url_for('category.list_categories'))
