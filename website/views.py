from flask import Blueprint, render_template, flash, redirect, request, jsonify
from .models import Product, Cart, Order
from flask_login import login_required, current_user
from . import db
from intasend import APIService
from .forms import ShopItemsForm
from werkzeug.utils import secure_filename


views = Blueprint('views', __name__)

API_PUBLISHABLE_KEY = 'YOUR_PUBLISHABLE_KEY'

API_TOKEN = 'YOUR_API_TOKEN'


@views.route('/')
def home():

    items = Product.query.filter_by(flash_sale=True)

    return render_template('home.html', items=items, cart=Cart.query.filter_by(customer_id=current_user.id).all()
                           if current_user.is_authenticated else [])


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
    items = Product.query.all()
    return render_template('product/list_products.html', items=items)














