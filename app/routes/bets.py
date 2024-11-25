from flask import Blueprint, request, jsonify, render_template
from app.models import User, Event, Bet, db
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('bets', __name__, url_prefix='/bets')


@bp.route('/place', methods=['POST'])
@jwt_required()
def place_bet():
    current_user_id = get_jwt_identity()  
    print(f"Identidade do usuário: {current_user_id}")  

    data = request.get_json()

    
    if not current_user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    required_fields = ['evento_id', 'valor', 'tipo_aposta']
    if not data or not all(key in data for key in required_fields):
        return jsonify({'error': 'Dados incompletos'}), 400

    try:
        valor = float(data['valor'])
        evento = Event.query.get(data['evento_id'])

        if not evento or evento.status != 'aprovado':
            return jsonify({'error': 'Evento não encontrado ou não aprovado'}), 404

        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        if valor <= 0 or user.saldo < valor:
            return jsonify({'error': 'Saldo insuficiente ou valor inválido'}), 400

        user.saldo -= valor

        aposta = Bet(
            usuario_id=user.id,
            evento_id=evento.id,
            valor=valor,
            tipo_aposta=data['tipo_aposta']
        )
        db.session.add(aposta)
        db.session.commit()

        return jsonify({'message': 'Aposta realizada com sucesso!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@bp.route('/finish', methods=['POST'])
@jwt_required
def finish_event():
    data = request.get_json()
    required_fields = ['evento_id', 'resultado']


    if not data or not all(key in data for key in required_fields):
        return jsonify({'error': 'Dados incompletos'}), 400

    try:
        evento = Event.query.get(data['evento_id'])
        resultado = data['resultado']

        if not evento:
            return jsonify({'error': 'Evento não encontrado'}), 404
        if evento.status != 'aprovado':
            return jsonify({'error': 'Somente eventos aprovados podem ser finalizados'}), 400
        if resultado not in ['sim', 'não']:
            return jsonify({'error': 'Resultado inválido'}), 400

        evento.resultado = resultado
        evento.status = 'finalizado'

        apostas = Bet.query.filter_by(evento_id=evento.id).all()
        vencedores = [aposta for aposta in apostas if aposta.tipo_aposta == resultado]
        total_apostado = sum(aposta.valor for aposta in apostas)
        total_vencedores = sum(aposta.valor for aposta in vencedores)

        for aposta in vencedores:
            proporcao = aposta.valor / total_vencedores
            ganho = proporcao * total_apostado
            usuario = User.query.get(aposta.usuario_id)
            usuario.saldo += ganho

        db.session.commit()

        return jsonify({'message': 'Evento finalizado com sucesso!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500