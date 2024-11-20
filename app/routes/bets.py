from flask import Blueprint, request, jsonify
from app.models import User, Event, Bet, db

bp = Blueprint('bets', __name__, url_prefix='/bets')


@bp.route('/place', methods=['POST'])
def place_bet():
    data = request.get_json()
    required_fields = ['usuario_id', 'evento_id', 'valor', 'tipo_aposta']

    if not data or not all(key in data for key in required_fields):
        return jsonify({'error': 'Dados incompletos'}), 400

    try:
        usuario = User.query.get(data['usuario_id'])
        evento = Event.query.get(data['evento_id'])
        valor = float(data['valor'])
        tipo_aposta = data['tipo_aposta']

        if not usuario:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        if not evento:
            return jsonify({'error': 'Evento não encontrado'}), 404
        if valor <= 0:
            return jsonify({'error': 'O valor deve ser maior que zero'}), 400
        if evento.status != 'aprovado':
            return jsonify({'error': 'Apostas só são permitidas em eventos aprovados'}), 400
        if usuario.saldo < valor:
            return jsonify({'error': 'Saldo insuficiente'}), 400
        if tipo_aposta not in ['sim', 'não']:
            return jsonify({'error': 'Tipo de aposta inválido'}), 400


        usuario.saldo -= valor


        aposta = Bet(
            usuario_id=usuario.id,
            evento_id=evento.id,
            valor=valor,
            tipo_aposta=tipo_aposta
        )
        db.session.add(aposta)
        db.session.commit()

        return jsonify({'message': 'Aposta realizada com sucesso!', 'novo_saldo': usuario.saldo}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/finish', methods=['POST'])
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
