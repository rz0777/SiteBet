from flask import Blueprint, request, jsonify
from app.models import Event, db
from datetime import datetime

bp = Blueprint('events', __name__, url_prefix='/events')

@bp.route('/create', methods=['POST'])
def create_event():
    data = request.get_json()
    required_fields = ['titulo', 'descricao', 'valor_cota', 'data_inicio_apostas', 'data_fim_apostas', 'data_ocorrencia', 'criado_por']
    
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
            criado_por=data['criado_por']  # ID do usuário que criou o evento
        )
        db.session.add(event)
        db.session.commit()

        return jsonify({'message': 'Evento criado com sucesso!', 'event_id': event.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/list', methods=['GET'])
def list_events():
    status = request.args.get('status', 'aprovado')
    events = Event.query.filter_by(status=status).all()

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
    } for event in events]), 200


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

