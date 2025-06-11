from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_, desc, asc
import os
from werkzeug.utils import secure_filename
from .models import Product, Category
from ... import db

# Crear el blueprint para productos
product_blueprint = Blueprint('product', __name__, 
                           template_folder='templates',
                           static_folder='static',
                           url_prefix='/product')

@product_blueprint.route('/')
def product_list():
    # Paginación
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Búsqueda
    search_query = request.args.get('q', '')
    if search_query:
        products = Product.query.filter(
            or_(
                Product.product_name.ilike(f'%{search_query}%'),
                Product.description.ilike(f'%{search_query}%')
            )
        )
    else:
        products = Product.query
    
    # Ordenamiento
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'desc')
    
    if sort == 'name':
        products = products.order_by(asc(Product.product_name) if order == 'asc' else desc(Product.product_name))
    elif sort == 'price':
        products = products.order_by(asc(Product.current_price) if order == 'asc' else desc(Product.current_price))
    else:
        products = products.order_by(Product.id.desc())
    
    # Aplicar paginación
    products = products.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('product/list.html', products=products, search_query=search_query)

@product_blueprint.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    categories = Category.query.all()
    if request.method == 'POST':
        try:
            product_name = request.form.get('product_name')
            description = request.form.get('description')
            current_price = request.form.get('current_price')
            previous_price = request.form.get('previous_price')
            in_stock = request.form.get('in_stock')
            category_id = request.form.get('category_id')
            discount = request.form.get('discount', 0)
            flash_sale = True if request.form.get('flash_sale') else False
            
            # Manejo de la carga de archivos
            product_picture = request.files.get('product_picture')
            picture_path = '/static/images/default.jpg'
            
            if product_picture and product_picture.filename:
                filename = secure_filename(product_picture.filename)
                # Crear directorio si no existe
                os.makedirs(os.path.join(current_app.root_path, 'static', 'uploads', 'products'), exist_ok=True)
                # Guardar el archivo
                filepath = os.path.join(current_app.root_path, 'static', 'uploads', 'products', filename)
                product_picture.save(filepath)
                picture_path = f'/static/uploads/products/{filename}'
            
            new_product = Product(
                product_name=product_name,
                description=description,
                current_price=float(current_price),
                previous_price=float(previous_price) if previous_price else 0,
                in_stock=int(in_stock),
                product_picture=picture_path,
                category_id=int(category_id) if category_id else None,
                discount=float(discount) if discount else 0,
                flash_sale=flash_sale
            )
            
            db.session.add(new_product)
            db.session.commit()
            flash('¡Producto agregado exitosamente!', 'success')
            return redirect(url_for('product.product_list'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al agregar producto: {str(e)}")
            flash('Error al agregar el producto. Por favor, intente nuevamente.', 'error')
    
    return render_template('product/add.html', categories=categories)

@product_blueprint.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    categories = Category.query.all()
    
    if request.method == 'POST':
        try:
            product.product_name = request.form.get('product_name')
            product.description = request.form.get('description')
            product.current_price = float(request.form.get('current_price'))
            product.previous_price = float(request.form.get('previous_price')) if request.form.get('previous_price') else 0
            product.in_stock = int(request.form.get('in_stock'))
            product.category_id = int(request.form.get('category_id')) if request.form.get('category_id') else None
            product.discount = float(request.form.get('discount', 0))
            product.flash_sale = True if request.form.get('flash_sale') else False
            
            # Manejo de la carga de archivos
            product_picture = request.files.get('product_picture')
            if product_picture and product_picture.filename:
                filename = secure_filename(product_picture.filename)
                # Crear directorio si no existe
                os.makedirs(os.path.join(current_app.root_path, 'static', 'uploads', 'products'), exist_ok=True)
                # Guardar el archivo
                filepath = os.path.join(current_app.root_path, 'static', 'uploads', 'products', filename)
                product_picture.save(filepath)
                product.product_picture = f'/static/uploads/products/{filename}'
            
            db.session.commit()
            flash('¡Producto actualizado exitosamente!', 'success')
            return redirect(url_for('product.product_list'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al actualizar producto: {str(e)}")
            flash('Error al actualizar el producto. Por favor, intente nuevamente.', 'error')
    
    return render_template('product/edit.html', product=product, categories=categories)

@product_blueprint.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_product(id):
    if request.method == 'GET':
        # Mostrar página de confirmación
        product = Product.query.get_or_404(id)
        return render_template('product/delete_confirm.html', product=product)
    else:
        # Procesar el borrado
        try:
            product = Product.query.get_or_404(id)
            product_name = product.product_name
            db.session.delete(product)
            db.session.commit()
            flash(f'El producto "{product_name}" ha sido eliminado exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al eliminar producto: {str(e)}")
            flash('Error al eliminar el producto. Por favor, intente nuevamente.', 'error')
        return redirect(url_for('product.product_list'))

@product_blueprint.route('/detail/<int:id>')
def detail(id):
    product = Product.query.get_or_404(id)
    return render_template('product/detail.html', product=product)

@product_blueprint.route('/category/<int:category_id>')
def category_products(category_id):
    category = Category.query.get_or_404(category_id)
    
    # Paginación
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Búsqueda
    search_query = request.args.get('q', '')
    products = Product.query.filter_by(category_id=category_id)
    
    if search_query:
        products = products.filter(
            or_(
                Product.product_name.ilike(f'%{search_query}%'),
                Product.description.ilike(f'%{search_query}%')
            )
        )
    
    # Ordenamiento
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'desc')
    
    if sort == 'name':
        products = products.order_by(asc(Product.product_name) if order == 'asc' else desc(Product.product_name))
    elif sort == 'price':
        products = products.order_by(asc(Product.current_price) if order == 'asc' else desc(Product.current_price))
    else:
        products = products.order_by(Product.id.desc())
    
    # Aplicar paginación
    products = products.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('product/category.html', 
                         category=category, 
                         products=products,
                         search_query=search_query)
