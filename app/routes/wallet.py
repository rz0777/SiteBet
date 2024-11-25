from flask import Blueprint, request, jsonify, render_template
from app.models import User, Transaction, db
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('wallet', __name__, url_prefix='/wallet')

@bp.route('/')
def wallet_view():
    return render_template('wallet.html')

@bp.route('/addFunds', methods=['POST'])
@jwt_required()
def add_funds():
    current_user_id = get_jwt_identity()  
    data = request.get_json()

    if not current_user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    try:
        valor = float(data['valor'])
        if valor <= 0:
            return jsonify({'error': 'O valor deve ser maior que zero'}), 400

        usuario = User.query.get(current_user_id)
        if not usuario:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        usuario.saldo += valor  

        transacao = Transaction(
            usuario_id=usuario.id,
            tipo='adicionar',
            valor=valor,
            detalhes='Recarga de créditos'
        )
        db.session.add(transacao)
        db.session.commit()

        return jsonify({'message': 'Fundos adicionados com sucesso!', 'novo_saldo': usuario.saldo}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/withdrawFunds', methods=['POST'])
@jwt_required()
def withdraw_funds():
    current_user_id = get_jwt_identity() 
    data = request.get_json()

    if not data or 'valor' not in data or 'conta' not in data:
        return jsonify({'error': 'Dados incompletos'}), 400

    try:
        valor = float(data['valor'])
        if valor <= 0:
            return jsonify({'error': 'O valor deve ser maior que zero'}), 400

        usuario = User.query.get(current_user_id) 
        if not usuario:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        if usuario.saldo < valor:
            return jsonify({'error': 'Saldo insuficiente'}), 400

       
        taxa = 0.04 if valor <= 100 else 0.03 if valor <= 1000 else 0.02 if valor <= 5000 else 0.01
        taxa_total = valor * taxa
        valor_liquido = valor - taxa_total

        usuario.saldo -= valor  

        transacao = Transaction(
            usuario_id=usuario.id,
            tipo='sacar',
            valor=valor,
            detalhes=f'Saque para conta: {data["conta"]} (Taxa aplicada: R$ {taxa_total:.2f})'
        )
        db.session.add(transacao)
        db.session.commit()

        return jsonify({'message': 'Saque realizado com sucesso!', 'valor_liquido': valor_liquido, 'novo_saldo': usuario.saldo}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/transactions', methods=['GET'])
@jwt_required()
def list_transactions():
    current_user = get_jwt_identity()
    transactions = Transaction.query.filter_by(usuario_id=current_user).all()

    return jsonify([{
        'id': t.id,
        'tipo': t.tipo,
        'valor': t.valor,
        'detalhes': t.detalhes,
        'data': t.data.isoformat()
    } for t in transactions]), 200
