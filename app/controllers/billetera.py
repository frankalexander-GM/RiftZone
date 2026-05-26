from datetime import date

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user, login_user
from app.factories.app_factory import db
from app.models.transaccion import Transaccion

billetera_bp = Blueprint('billetera', __name__, template_folder='../templates/jugador')

@billetera_bp.route('/')
@login_required
def index():
    if current_user.rol == 'invitado':
        flash('Inicia sesión para usar RiftCoins.', 'error')
        return redirect(url_for('jugador.dashboard'))
    
    transacciones = current_user.transacciones.all()
    hoy = date.today()
    from datetime import datetime as dt
    inicio_hoy = dt.combine(hoy, dt.min.time())
    ya_reclamo_hoy = (
        current_user.ultima_recompensa_diaria == hoy
        or Transaccion.query.filter(
            Transaccion.user_id == current_user.id_usuario,
            Transaccion.description == 'Recompensa diaria',
            Transaccion.created_at >= inicio_hoy,
        ).first() is not None
    )
    return render_template(
        'jugador/billetera.html',
        transacciones=transacciones,
        ya_reclamo_hoy=ya_reclamo_hoy,
        recompensa_diaria=50,
    )

@billetera_bp.route('/gastar', methods=['POST'])
@login_required
def gastar():
    if current_user.rol == 'invitado':
        return jsonify({'success': False, 'message': 'Inicia sesión para usar RiftCoins.'}), 403
        
    amount = request.form.get('amount', type=int)
    description = request.form.get('description', 'Compra en tienda')
    
    if not amount or amount <= 0:
        return jsonify({'success': False, 'message': 'Cantidad inválida.'}), 400
        
    if current_user.tokens < amount:
        return jsonify({'success': False, 'message': 'Saldo insuficiente.'}), 400
        
    try:
        # Descontar saldo
        current_user.tokens -= amount
        
        # Registrar transacción
        tx = Transaccion(
            user_id=current_user.id_usuario,
            amount=-amount,
            tipo='egreso',
            description=description
        )
        db.session.add(tx)
        db.session.commit()
        
        return jsonify({'success': True, 'new_balance': current_user.tokens, 'message': 'Transacción exitosa.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error procesando la transacción.'}), 500

@billetera_bp.route('/ganar', methods=['POST'])
@login_required
def ganar():
    if current_user.rol == 'invitado':
        flash('Regístrate para reclamar recompensas.', 'error')
        return redirect(url_for('jugador.dashboard'))

    hoy = date.today()
    if current_user.ultima_recompensa_diaria == hoy:
        flash('Ya reclamaste tu recompensa diaria hoy. Vuelve mañana.', 'warning')
        return redirect(url_for('billetera.index'))

    from datetime import datetime as dt
    inicio_hoy = dt.combine(hoy, dt.min.time())
    ya_tx = Transaccion.query.filter(
        Transaccion.user_id == current_user.id_usuario,
        Transaccion.description == 'Recompensa diaria',
        Transaccion.created_at >= inicio_hoy,
    ).first()
    if ya_tx:
        current_user.ultima_recompensa_diaria = hoy
        db.session.commit()
        flash('Ya reclamaste tu recompensa diaria hoy. Vuelve mañana.', 'warning')
        return redirect(url_for('billetera.index'))

    try:
        amount = 50
        current_user.tokens = (current_user.tokens or 0) + amount
        current_user.ultima_recompensa_diaria = hoy

        tx = Transaccion(
            user_id=current_user.id_usuario,
            amount=amount,
            tipo='ingreso',
            description='Recompensa diaria',
        )
        db.session.add(tx)
        db.session.commit()
        login_user(current_user)
        flash(f'¡Recompensa diaria reclamada! +{amount} RiftCoins.', 'success')
    except Exception:
        db.session.rollback()
        flash('Error al reclamar recompensa.', 'error')

    return redirect(url_for('billetera.index'))
