from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from . import cliente_bp
from .models import db, DireccionEnvio, ListaDeseos, ProductoListaDeseos
from website.models import Customer, Order, Cart, OrderItem
from website.modules.product.models import Product
import json

@cliente_bp.route('/perfil')
@login_required
def perfil():
    """Mostrar el perfil del cliente"""
    return render_template('cliente/perfil.html', user=current_user)

@cliente_bp.route('/pedidos')
@login_required
def pedidos():
    """Mostrar el historial de pedidos del cliente"""
    pedidos = Order.query.filter_by(customer_id=current_user.id)\
                         .order_by(Order.created_at.desc())\
                         .all()
    return render_template('cliente/pedidos.html', pedidos=pedidos)

@cliente_bp.route('/carrito')
@login_required
def carrito():
    """Mostrar el carrito de compras del cliente"""
    if current_user.is_admin:
        flash('Los administradores no pueden acceder al carrito.', 'warning')
        return redirect(url_for('views.home'))
        
    cart = Cart.query.filter_by(customer_id=current_user.id).all()
    amount = 0
    for item in cart:
        amount = item.product.current_price + item.quantity
    return render_template('cliente/cart.html', cart=cart, amount=amount, total=amount+200)

@cliente_bp.route('/agregar_al_carrito/<int:producto_id>', methods=['POST'])
@login_required
def agregar_al_carrito(producto_id):
    """Agregar un producto al carrito"""
    producto = Product.query.get_or_404(producto_id)
    cantidad = int(request.form.get('cantidad', 1))
    
    # Verificar si el producto ya está en el carrito
    item = Cart.query.filter_by(
        customer_id=current_user.id,
        product_id=producto_id
    ).first()
    
    if item:
        # Actualizar cantidad si ya existe
        item.quantity += cantidad
    else:
        # Crear nuevo ítem en el carrito
        item = Cart(
            customer_id=current_user.id,
            product_id=producto_id,
            quantity=cantidad,
            total_price=producto.current_price * cantidad
        )
        db.session.add(item)
    
    db.session.commit()
    flash(f'"{producto.product_name}" ha sido agregado al carrito', 'success')
    return redirect(url_for('cliente.carrito'))

@cliente_bp.route('/eliminar_del_carrito/<int:item_id>', methods=['POST'])
@login_required
def eliminar_del_carrito(item_id):
    """Eliminar un ítem del carrito"""
    try:
        item = Cart.query.get_or_404(item_id)
        if item.customer_id != current_user.id:
            return jsonify({'success': False, 'message': 'No tienes permiso para realizar esta acción'}), 403
        
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Artículo eliminado del carrito'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@cliente_bp.route('/actualizar_carrito/<int:item_id>', methods=['POST'])
@login_required
def actualizar_carrito(item_id):
    """Actualizar la cantidad de un ítem en el carrito"""
    try:
        item = Cart.query.get_or_404(item_id)
        if item.customer_id != current_user.id:
            return jsonify({'success': False, 'message': 'No autorizado'}), 403
        
        cantidad = int(request.form.get('cantidad', 1))
        if cantidad <= 0:
            db.session.delete(item)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Artículo eliminado'})
        
        item.quantity = cantidad
        db.session.commit()
        
        # Recalcular total
        cart = Cart.query.filter_by(customer_id=current_user.id).all()
        amount = sum(item.product.current_price + item.quantity for item in cart)
        return jsonify({
            'success': True,
            'subtotal': f"S/ {item.product.current_price * item.quantity:.2f}",
            'total': f"S/ {amount + 200:.2f}",
            'amount': f"S/ {amount:.2f}"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@cliente_bp.route('/pluscart')
@login_required
def plus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        
        if not cart_item:
            return jsonify({'success': False, 'message': 'Ítem no encontrado'}), 404
            
        if cart_item.customer_id != current_user.id:
            return jsonify({'success': False, 'message': 'No autorizado'}), 403
            
        # Verificar stock
        if cart_item.quantity >= cart_item.product.stock_quantity:
            return jsonify({
                'success': False, 
                'message': 'No hay suficiente stock disponible',
                'status': 2  # Código para indicar stock insuficiente
            })
            
        cart_item.quantity = cart_item.quantity
        db.session.commit()
        
        # Obtener el carrito actualizado
        cart = Cart.query.filter_by(customer_id=current_user.id).all()
        amount = sum(item.product.current_price + item.quantity for item in cart)
        
        return jsonify({
            'success': True,
            'quantity': cart_item.quantity,
            'amount': f"S/ {amount:.2f}",
            'total': f"S/ {amount - 400:.2f}"
        })

@cliente_bp.route('/minuscart')
@login_required
def minus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        
        if not cart_item:
            return jsonify({'success': False, 'message': 'Ítem no encontrado'}), 404
            
        if cart_item.customer_id != current_user.id:
            return jsonify({'success': False, 'message': 'No autorizado'}), 403
            
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            db.session.commit()
            
            # Obtener el carrito actualizado
            cart = Cart.query.filter_by(customer_id=current_user.id).all()
            amount = sum(item.product.current_price * item.quantity for item in cart)
            
            return jsonify({
                'success': True,
                'quantity': cart_item.quantity,
                'amount': f"S/ {amount:.2f}",
                'total': f"S/ {amount + 200:.2f}"
            })
        else:
            # Si la cantidad es 1, eliminar el ítem
            db.session.delete(cart_item)
            db.session.commit()
            
            # Obtener el carrito actualizado
            cart = Cart.query.filter_by(customer_id=current_user.id).all()
            amount = sum(item.product.current_price * item.quantity for item in cart)
            
            return jsonify({
                'success': True,
                'quantity': 0,
                'amount': f"S/ {amount:.2f}",
                'total': f"S/ {amount + 200:.2f}",
                'removed': True
            })

@cliente_bp.route('/removecart')
@login_required
def remove_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        
        if not cart_item:
            return jsonify({'success': False, 'message': 'Ítem no encontrado'}), 404
            
        if cart_item.customer_id != current_user.id:
            return jsonify({'success': False, 'message': 'No autorizado'}), 403
            
        db.session.delete(cart_item)
        db.session.commit()
        
        # Obtener el carrito actualizado
        cart = Cart.query.filter_by(customer_id=current_user.id).all()
        amount = sum(item.product.current_price * item.quantity for item in cart)
        
        return jsonify({
            'success': True,
            'amount': f"S/ {amount:.2f}",
            'total': f"S/ {amount + 200:.2f}",
            'removed': True
        })

@cliente_bp.route('/place-order')
@login_required
def place_order():
    # Verificar si el usuario es administrador
    if current_user.is_admin:
        flash('Los administradores no pueden realizar pedidos.', 'warning')
        return redirect(url_for('views.home'))
        
    customer_cart = Cart.query.filter_by(customer_id=current_user.id).all()
    if not customer_cart:
        flash('Tu carrito está vacío', 'warning')
        return redirect(url_for('cliente.carrito'))
    
    # Verificar stock antes de procesar el pedido
    for item in customer_cart:
        if item.quantity > item.product.stock_quantity:
            flash(f'No hay suficiente stock para {item.product.product_name}. Stock disponible: {item.product.stock_quantity}', 'warning')
            return redirect(url_for('cliente.carrito'))
    
    try:
        # Crear el pedido
        order = Order(
            customer_id=current_user.id,
            total=sum(item.product.current_price * item.quantity for item in customer_cart) + 200,  # +200 por envío
            status='Pendiente',
            shipping_address=current_user.address,
            payment_method='Contra entrega'  # Por defecto
        )
        db.session.add(order)
        db.session.flush()  # Para obtener el ID del pedido
        
        # Agregar los ítems al pedido
        for item in customer_cart:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.current_price
            )
            db.session.add(order_item)
            
            # Actualizar el stock del producto
            item.product.stock_quantity -= item.quantity
        
        # Vaciar el carrito
        Cart.query.filter_by(customer_id=current_user.id).delete()
        
        db.session.commit()
        flash('Pedido realizado exitosamente', 'success')
        return redirect(url_for('cliente.pedidos'))
        
    except Exception as e:
        db.session.rollback()
        print('Error al procesar el pedido:', e)
        flash('Error al procesar el pedido. Por favor, intente nuevamente.', 'error')
        return redirect(url_for('cliente.carrito'))
