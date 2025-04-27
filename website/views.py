from flask import Blueprint, render_template, flash, redirect, request, jsonify, url_for
from .models import Product, Cart, Order, Category, Customer
from flask_login import login_required, current_user
from . import db
from intasend import APIService
from .forms import ShopItemsForm
from werkzeug.utils import secure_filename
import os
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired


views = Blueprint('views', __name__)

API_PUBLISHABLE_KEY = 'YOUR_PUBLISHABLE_KEY'

API_TOKEN = 'YOUR_API_TOKEN'


@views.route('/')
def home():
    try:
        items = Product.query.filter_by(flash_sale=True).all()
        categories = Category.query.all()
        cart = Cart.query.filter_by(customer_id=current_user.id).all() if current_user.is_authenticated else []
    except Exception as e:
        print(f"Error loading data: {e}")
        items = []
        categories = []
        cart = []
    
    return render_template('home.html', 
                         items=items, 
                         categories=categories,
                         cart=cart)


@views.route('/add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    # Debug print to see if the function is being called
    print(f"Adding item {item_id} to cart for user {current_user.id}")
    
    item_to_add = Product.query.get(item_id)
    if not item_to_add:
        flash('Product not found')
        return redirect(request.referrer)
    
    # Check if the item is already in the cart using product_id and customer_id
    item_exists = Cart.query.filter_by(product_id=item_id, customer_id=current_user.id).first()
    if item_exists:
        try:
            item_exists.quantity = item_exists.quantity + 1
            item_exists.total_price = item_exists.quantity * item_to_add.current_price
            db.session.commit()
            flash(f'Cantidad de {item_to_add.product_name} actualizada en el carrito')
            return redirect(request.referrer)
        except Exception as e:
            print('Quantity not Updated', e)
            flash(f'No se pudo actualizar la cantidad: {str(e)}')
            return redirect(request.referrer)

    # Create a new cart item
    new_cart_item = Cart()
    new_cart_item.quantity = 1
    new_cart_item.product_id = item_to_add.id  # Use product_id
    new_cart_item.customer_id = current_user.id  # Use customer_id
    new_cart_item.total_price = item_to_add.current_price

    try:
        db.session.add(new_cart_item)
        db.session.commit()
        flash(f'{item_to_add.product_name} agregado al carrito')
    except Exception as e:
        print('Item not added to cart', e)
        flash(f'Error al agregar al carrito: {str(e)}')

    return redirect(request.referrer)



@views.route('/cart')
@login_required
def show_cart():
    # Use customer_id instead of customer_link
    cart = Cart.query.filter_by(customer_id=current_user.id).all()
    amount = 0
    for item in cart:
        amount += item.product.current_price * item.quantity

    return render_template('cliente/cart.html', cart=cart, amount=amount, total=amount+200)


@views.route('/pluscart')
@login_required
def plus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity = cart_item.quantity + 1
        cart_item.total_price = cart_item.quantity * cart_item.product.current_price
        db.session.commit()

        cart = Cart.query.filter_by(customer_id=current_user.id).all()

        amount = 0
        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)

@views.route('/minuscart')
@login_required
def minus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        if cart_item.quantity > 1:
            cart_item.quantity = cart_item.quantity - 1
            cart_item.total_price = cart_item.quantity * cart_item.product.current_price
            db.session.commit()

        cart = Cart.query.filter_by(customer_id=current_user.id).all()

        amount = 0
        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)

@views.route('/removecart')
@login_required
def remove_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        db.session.delete(cart_item)
        db.session.commit()

        cart = Cart.query.filter_by(customer_id=current_user.id).all()

        amount = 0
        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)


@views.route('/place-order')
@login_required
def place_order():
    customer_cart = Cart.query.filter_by(customer_id=current_user.id)
    if customer_cart:
        try:
            total = 0
            for item in customer_cart:
                total += item.product.current_price * item.quantity

            service = APIService(token=API_TOKEN, publishable_key=API_PUBLISHABLE_KEY, test=True)
            create_order_response = service.collect.mpesa_stk_push(phone_number='YOUR_NUMBER ', email=current_user.email,
                                                                   amount=total + 200, narrative='Purchase of goods')

            for item in customer_cart:
                new_order = Order()
                new_order.quantity = item.quantity
                new_order.price = item.product.current_price
                new_order.status = create_order_response['invoice']['state'].capitalize()
                new_order.payment_id = create_order_response['id']

                new_order.product_id = item.product_id  # Use product_id
                new_order.customer_id = item.customer_id  # Use customer_id

                db.session.add(new_order)

                product = Product.query.get(item.product_id)

                product.in_stock -= item.quantity

                db.session.delete(item)

                db.session.commit()

            flash('Order Placed Successfully')

            return redirect('/orders')
        except Exception as e:
            print(e)
            flash('Order not placed')
            return redirect('/')
    else:
        flash('Your cart is Empty')
        return redirect('/')


@views.route('/orders')
@login_required
def order():
    orders = Order.query.filter_by(customer_id=current_user.id).all()
    return render_template('cliente/orders.html', orders=orders)


@views.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search')
        items = Product.query.filter(Product.product_name.ilike(f'%{search_query}%')).all()
        return render_template('search.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])

    return render_template('search.html')


@views.route('/add-product', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ShopItemsForm()
    
    if form.validate_on_submit():
        product_name = form.product_name.data
        current_price = form.current_price.data
        previous_price = form.previous_price.data
        in_stock = form.in_stock.data
        flash_sale = form.flash_sale.data

        file = form.product_picture.data
        file_name = secure_filename(file.filename)
        file_path = f'./media/{file_name}'
        file.save(file_path)

        new_product = Product()
        new_product.product_name = product_name
        new_product.current_price = current_price
        new_product.previous_price = previous_price
        new_product.in_stock = in_stock
        new_product.flash_sale = flash_sale
        new_product.product_picture = file_path

        try:
            db.session.add(new_product)
            db.session.commit()
            flash('Producto agregado exitosamente')
            return redirect('/')
        except Exception as e:
            flash('Error al agregar el producto')
            print(e)
            
    return render_template('product/add_product.html', form=form)


@views.route('/list-products')
def list_products():
    # Get filter parameters
    category_id = request.args.get('category', type=int)
    search_query = request.args.get('search', '')
    sort = request.args.get('sort', 'name_asc')
    
    # Base query
    query = Product.query
    
    # Apply filters
    if category_id:
        query = query.filter_by(category_id=category_id)
    if search_query:
        query = query.filter(Product.product_name.ilike(f'%{search_query}%'))
    
    # Apply sorting
    if sort == 'name_asc':
        query = query.order_by(Product.product_name.asc())
    elif sort == 'name_desc':
        query = query.order_by(Product.product_name.desc())
    elif sort == 'price_asc':
        query = query.order_by(Product.current_price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.current_price.desc())
    
    # Get all products
    items = query.all()
    
    # Get all categories for the filter dropdown
    categories = Category.query.all()
    
    return render_template('product/list_products.html', 
                         items=items, 
                         categories=categories,
                         selected_category=category_id,
                         search_query=search_query,
                         sort=sort)


@views.route('/delete-item/<int:item_id>')
def delete_item(item_id):
    try:
        item_to_delete = Product.query.get_or_404(item_id)
        nombre = item_to_delete.product_name
        db.session.delete(item_to_delete)
        db.session.commit()
        flash(f'El producto "{nombre}" ha sido eliminado exitosamente')
    except Exception as e:
        print('Error al eliminar:', e)
        flash('Error al eliminar el producto')
    return redirect('/list-products')


@views.route('/edit-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    if not current_user.is_admin:
        flash('No tienes permiso para editar productos', 'error')
        return redirect(url_for('views.list_products'))
        
    product = Product.query.get_or_404(item_id)
    
    if request.method == 'POST':
        try:
            product.product_name = request.form.get('product_name')
            product.current_price = float(request.form.get('current_price'))
            product.previous_price = float(request.form.get('previous_price'))
            product.in_stock = int(request.form.get('in_stock'))
            product.flash_sale = True if request.form.get('flash_sale') else False
            
            if 'product_picture' in request.files:
                file = request.files['product_picture']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join('website/static/images', filename))
                    product.product_picture = f'/static/images/{filename}'
            
            db.session.commit()
            flash(f'Producto "{product.product_name}" actualizado exitosamente', 'success')
            return redirect(url_for('views.list_products'))
        except Exception as e:
            db.session.rollback()
            print('Error al actualizar:', e)
            flash('Error al actualizar el producto', 'error')
            return redirect(url_for('views.list_products'))
    
    return render_template('product/edit_product.html', product=product)


@views.route('/confirm-delete/<int:item_id>')
def confirm_delete(item_id):
    product = Product.query.get_or_404(item_id)
    return render_template('product/confirm_delete.html', product=product)


@views.route('/categories')
@login_required
def categories():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('views.home'))
    
    categories = Category.query.all()
    return render_template('categoria/categoria.html', categories=categories)

class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    icon = StringField('Icon')

@views.route('/category/add', methods=['GET', 'POST'])
@login_required
def add_category():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('views.home'))
    
    form = CategoryForm()
    
    if form.validate_on_submit():
        try:
            new_category = Category(
                name=form.name.data,
                description=form.description.data,
                icon=form.icon.data
            )
            db.session.add(new_category)
            db.session.commit()
            flash('Category created successfully', 'success')
            return redirect(url_for('views.categories'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating category: {str(e)}', 'error')
    
    return render_template('categoria/agregar_categoria.html', form=form)

@views.route('/category/<int:category_id>/edit')
@login_required
def edit_category(category_id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('views.home'))
    
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    return render_template('categoria/editar_categoria.html', category=category, form=form)

@views.route('/category/<int:category_id>/edit', methods=['POST'])
@login_required
def edit_category_post(category_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    category = Category.query.get_or_404(category_id)
    form = CategoryForm()
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        category.icon = form.icon.data
        db.session.commit()
        flash('Category updated successfully', 'success')
        return redirect(url_for('views.categories'))
    
    return render_template('categoria/editar_categoria.html', category=category, form=form)

@views.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    
    flash('Category deleted successfully', 'success')
    return redirect(url_for('views.categories'))

@views.route('/category/<int:category_id>/products')
def category_products(category_id):
    category = Category.query.get_or_404(category_id)
    products = Product.query.filter_by(category_id=category_id).all()
    return render_template('category_products.html', category=category, products=products)

@views.route('/make_admin/<int:user_id>')
@login_required
def make_admin(user_id):
    # Solo el primer usuario puede hacer esto, o alguien que ya es admin
    if current_user.id != 1 and not current_user.is_admin:
        flash('You do not have permission to do this.', 'error')
        return redirect(url_for('views.home'))
    
    user = Customer.query.get_or_404(user_id)
    user.role = 'admin'
    db.session.commit()
    flash(f'User {user.username} is now an admin', 'success')
    return redirect(url_for('views.home'))

@views.route('/create-sample-categories')
@login_required
def create_sample_categories():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('views.home'))
    
    sample_categories = [
        {
            'name': 'Electronics',
            'description': 'Electronic devices and accessories',
            'icon': 'fa fa-laptop'
        },
        {
            'name': 'Clothing',
            'description': 'Fashion and apparel',
            'icon': 'fa fa-tshirt'
        },
        {
            'name': 'Books',
            'description': 'Books and literature',
            'icon': 'fa fa-book'
        },
        {
            'name': 'Home & Kitchen',
            'description': 'Home appliances and kitchen items',
            'icon': 'fa fa-home'
        },
        {
            'name': 'Sports',
            'description': 'Sports equipment and accessories',
            'icon': 'fa fa-futbol'
        }
    ]
    
    try:
        for category_data in sample_categories:
            # Check if category already exists
            existing_category = Category.query.filter_by(name=category_data['name']).first()
            if not existing_category:
                new_category = Category(
                    name=category_data['name'],
                    description=category_data['description'],
                    icon=category_data['icon']
                )
                db.session.add(new_category)
        
        db.session.commit()
        flash('Sample categories created successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating sample categories: {str(e)}', 'error')
    
    return redirect(url_for('views.categories'))

@views.route('/evaluation/module-quality')
@login_required
def module_quality():
    if not current_user.is_admin:
        flash('Acceso no autorizado. Solo los administradores pueden ver esta página.', 'error')
        return redirect(url_for('views.home'))
    return render_template('evaluation/module_quality.html')

@views.route('/evaluation/usage-quality')
@login_required
def usage_quality():
    if not current_user.is_admin:
        flash('Acceso no autorizado. Solo los administradores pueden ver esta página.', 'error')
        return redirect(url_for('views.home'))
    return render_template('evaluation/usage_quality.html')














