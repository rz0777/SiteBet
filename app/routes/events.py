from flask import Blueprint, request, jsonify
from app.models import Event, db
from datetime import datetime
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity


bp = Blueprint('events', __name__, url_prefix='/events')

def moderator_required(func):
    @wraps(func)
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user = get_jwt_identity()
        if not current_user['is_moderador']:
            return jsonify({'error': 'Acesso restrito a moderadores'}), 403
        return func(*args, **kwargs)
    return wrapper

@bp.route('/approve/<int:event_id>', methods=['POST'])
@moderator_required
def approve_event(event_id):
    evento = Event.query.get(event_id)
    if not evento:
        return jsonify({'error': 'Evento não encontrado'}), 404
    if evento.status != 'pendente':
        return jsonify({'error': 'Apenas eventos pendentes podem ser aprovados'}), 400

    evento.status = 'aprovado'
    db.session.commit()

    return jsonify({'message': f'Evento {event_id} aprovado com sucesso!'}), 200

@bp.route('/reject/<int:event_id>', methods=['POST'])
@moderator_required
def reject_event(event_id):
    data = request.get_json()
    motivo = data.get('motivo', '').strip()

    if not motivo:
        return jsonify({'error': 'É necessário fornecer um motivo para rejeitar o evento'}), 400

    evento = Event.query.get(event_id)
    if not evento:
        return jsonify({'error': 'Evento não encontrado'}), 404
    if evento.status != 'pendente':
        return jsonify({'error': 'Apenas eventos pendentes podem ser rejeitados'}), 400

    # Alterar o status do evento para "rejeitado"
    evento.status = 'rejeitado'
    evento.resultado = motivo
    db.session.commit()

    return jsonify({'message': f'Evento {event_id} rejeitado com sucesso!'}), 200

@bp.route('/create', methods=['POST'])
@jwt_required()
def create_event():
    current_user = get_jwt_identity()
    data = request.get_json()
    if not current_user:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    required_fields = ['titulo', 'descricao', 'valor_cota', 'data_inicio_apostas', 'data_fim_apostas', 'data_ocorrencia']
    if not data or not all(key in data for key in required_fields):
        return jsonify({'error': 'Dados incompletos'}), 400

    try:
        event = Event(
            titulo=data['titulo'],
            descricao=data['descricao'],
            valor_cota=float(data['valor_cota']),
            data_inicio_apostas=datetime.fromisoformat(data['data_inicio_apostas']),
            data_fim_apostas=datetime.fromisoformat(data['data_fim_apostas']),
            data_ocorrencia=datetime.fromisoformat(data['data_ocorrencia']).date(),
            criado_por=current_user['id']
        )
        db.session.add(event)
        db.session.commit()
        return jsonify({'message': 'Evento criado com sucesso!', 'event_id': event.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/list', methods=['GET'])
def list_events():
    status = request.args.get('status', 'aprovado')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    events = Event.query.filter_by(status=status).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'events': [{
            'id': event.id,
            'titulo': event.titulo,
            'descricao': event.descricao,
            'valor_cota': event.valor_cota,
            'data_inicio_apostas': event.data_inicio_apostas.isoformat(),
            'data_fim_apostas': event.data_fim_apostas.isoformat(),
            'data_ocorrencia': event.data_ocorrencia.isoformat(),
            'status': event.status,
            'resultado': event.resultado
        } for event in events.items],
        'total': events.total,
        'pages': events.pages,
        'current_page': events.page
    }), 200


@bp.route('/delete/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Evento não encontrado'}), 404

    if event.status != 'pendente':
        return jsonify({'error': 'Somente eventos pendentes podem ser excluídos'}), 400

    event.status = 'inativo'
    db.session.commit()

    return jsonify({'message': f'Evento {event_id} excluído com sucesso!'}), 200

@bp.route('/search', methods=['GET'])
def search_events():
    query = request.args.get('query', '').strip()
    status = request.args.get('status', 'aprovado')

    if not query:
        return jsonify({'error': 'Termo de busca não fornecido'}), 400

    results = Event.query.filter(
        Event.status == status,
        (Event.titulo.ilike(f'%{query}%') | Event.descricao.ilike(f'%{query}%'))
    ).all()

    return jsonify([{
        'id': event.id,
        'titulo': event.titulo,
        'descricao': event.descricao,
        'valor_cota': event.valor_cota,
        'data_inicio_apostas': event.data_inicio_apostas.isoformat(),
        'data_fim_apostas': event.data_fim_apostas.isoformat(),
        'data_ocorrencia': event.data_ocorrencia.isoformat(),
        'status': event.status,
        'resultado': event.resultado
    } for event in results]), 200

@bp.route('/details/<int:event_id>', methods=['GET'])
def event_details(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Evento não encontrado'}), 404

    return jsonify({
        'id': event.id,
        'titulo': event.titulo,
        'descricao': event.descricao,
        'valor_cota': event.valor_cota,
        'data_inicio_apostas': event.data_inicio_apostas.isoformat(),
        'data_fim_apostas': event.data_fim_apostas.isoformat(),
        'data_ocorrencia': event.data_ocorrencia.isoformat(),
        'status': event.status,
        'resultado': event.resultado
    }), 200
