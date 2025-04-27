from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Product, Category
from . import db
import os
from werkzeug.utils import secure_filename

product = Blueprint('product', __name__, 
                    template_folder='templates/product',
                    url_prefix='/product')

@product.route('/')
def product_list():
    products = Product.query.all()
    return render_template('product/list.html', products=products)

@product.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    categories = Category.query.all()
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        description = request.form.get('description')
        current_price = request.form.get('current_price')
        previous_price = request.form.get('previous_price')
        in_stock = request.form.get('in_stock')
        category_id = request.form.get('category_id')
        discount = request.form.get('discount', 0)
        flash_sale = True if request.form.get('flash_sale') else False
        
        # Handle file upload
        product_picture = request.files.get('product_picture')
        if product_picture:
            filename = secure_filename(product_picture.filename)
            # Save the file
            product_picture.save(os.path.join('website/static/images', filename))
            picture_path = f'/static/images/{filename}'
        else:
            picture_path = '/static/images/default.jpg'
        
        new_product = Product(
            product_name=product_name,
            description=description,
            current_price=float(current_price),
            previous_price=float(previous_price),
            in_stock=int(in_stock),
            product_picture=picture_path,
            category_id=int(category_id) if category_id else None,
            discount=float(discount),
            flash_sale=flash_sale
        )
        
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('product.product_list'))
    
    return render_template('product/add.html', categories=categories)

@product.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    categories = Category.query.all()
    
    if request.method == 'POST':
        product.product_name = request.form.get('product_name')
        product.description = request.form.get('description')
        product.current_price = float(request.form.get('current_price'))
        product.previous_price = float(request.form.get('previous_price'))
        product.in_stock = int(request.form.get('in_stock'))
        product.category_id = int(request.form.get('category_id')) if request.form.get('category_id') else None
        product.discount = float(request.form.get('discount', 0))
        product.flash_sale = True if request.form.get('flash_sale') else False
        
        # Handle file upload
        product_picture = request.files.get('product_picture')
        if product_picture and product_picture.filename:
            filename = secure_filename(product_picture.filename)
            # Save the file
            product_picture.save(os.path.join('website/static/images', filename))
            product.product_picture = f'/static/images/{filename}'
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('product.product_list'))
    
    return render_template('product/edit.html', product=product, categories=categories)

@product.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_product(id):
    if request.method == 'GET':
        # Mostrar página de confirmación
        product = Product.query.get_or_404(id)
        return render_template('product/delete_product.html', product=product)
    else:
        # Procesar el borrado
        try:
            product = Product.query.get_or_404(id)
            nombre = product.product_name
            db.session.delete(product)
            db.session.commit()
            flash(f'El producto "{nombre}" ha sido eliminado exitosamente', 'success')
        except Exception as e:
            print('Error al eliminar:', e)
            flash('Error al eliminar el producto', 'error')
        return redirect(url_for('admin.shop_items'))

@product.route('/detail/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    return render_template('product/detail.html', product=product)