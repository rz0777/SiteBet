from flask import Blueprint, request, jsonify, render_template
from app.models import Event, db, User
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity


bp = Blueprint('events', __name__, url_prefix='/events')

@bp.route('/')
def list_events_view():
    return render_template('events.html')

@bp.route('/create')
def create_event_view():
    return render_template('create_event.html')

@bp.route('/moderation')
def moderation_view():
    return render_template('moderation.html')


@bp.route('/approve/<int:event_id>', methods=['POST'])
@jwt_required()
def approve_event(event_id):
    current_user_id = get_jwt_identity()  

    
    user = User.query.get(current_user_id)
    if not user or not user.is_moderador:
        return jsonify({'error': 'Acesso negado. Apenas moderadores podem aceitar eventos.'}), 403


    evento = Event.query.get(event_id)
    if not evento:
        return jsonify({'error': 'Evento não encontrado'}), 404
    if evento.status != 'pendente':
        return jsonify({'error': 'Apenas eventos pendentes podem ser aprovados'}), 400

    evento.status = 'aprovado'
    db.session.commit()

    return jsonify({'message': f'Evento {event_id} aprovado com sucesso!'}), 200

@bp.route('/reject/<int:event_id>', methods=['POST'])
@jwt_required()
def reject_event(event_id):
    data = request.get_json()
    motivo = data.get('motivo', '').strip()

    current_user_id = get_jwt_identity()  


    user = User.query.get(current_user_id)
    if not user or not user.is_moderador:
        return jsonify({'error': 'Acesso negado. Apenas moderadores podem aceitar eventos.'}), 403

    if not motivo:
        return jsonify({'error': 'É necessário fornecer um motivo para rejeitar o evento'}), 400

    evento = Event.query.get(event_id)
    if not evento:
        return jsonify({'error': 'Evento não encontrado'}), 404
    if evento.status != 'pendente':
        return jsonify({'error': 'Apenas eventos pendentes podem ser rejeitados'}), 400


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


    titulo = data['titulo']
    descricao = data['descricao']
    valor_cota = data['valor_cota']

    user = User.query.get(current_user)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    try:
        data_inicio_apostas = datetime.strptime(data['data_inicio_apostas'], '%Y-%m-%dT%H:%M')
        data_fim_apostas = datetime.strptime(data['data_fim_apostas'], '%Y-%m-%dT%H:%M')
        data_ocorrencia = datetime.strptime(data['data_ocorrencia'], '%Y-%m-%d').date()
    except Exception as e:
        print(f"Erro ao converter datas: {e}")
        return jsonify({'error': 'Formato de data inválido!'}), 400

    try:
        event = Event(
            titulo=titulo,
            descricao=descricao,
            valor_cota=valor_cota,
            data_inicio_apostas=data_inicio_apostas,
            data_fim_apostas=data_fim_apostas,
            data_ocorrencia=data_ocorrencia,
            criado_por=user.id
        )
        db.session.add(event)
        db.session.commit()
        return jsonify({'message': 'Evento criado com sucesso!', 'event_id': event.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/list', methods=['GET'])
def list_events():
    current_user_id = get_jwt_identity()

   
    user = User.query.get(current_user_id)
    try:
        if user and user.is_moderador:
        
            events = Event.query.all()
        else:
       
            events = Event.query.filter_by(status='aprovado').all()
        event_list = [{
            'id': event.id,
            'titulo': event.titulo,
            'descricao': event.descricao,
            'valor_cota': event.valor_cota,
            'data_inicio_apostas': event.data_inicio_apostas,
            'data_fim_apostas': event.data_fim_apostas,
            'data_ocorrencia': event.data_ocorrencia,
            'status': event.status,
        } for event in events]

        return jsonify({'events': event_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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

@bp.route('/<int:event_id>', methods=['GET'])
def event_view(event_id):
    try:
       
        event = Event.query.get_or_404(event_id)
        
       
        return render_template('events_details.html', event=event)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/finalize/<int:event_id>',methods=['GET'])
def event_fim_view(event_id):
    try:
        
        event = Event.query.get_or_404(event_id)
        
        
        return render_template('event_finalize.html', event=event)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/finalize/<int:event_id>', methods=['POST'])
@jwt_required()
def finalize_event(event_id):
    current_user = get_jwt_identity()
    user = User.query.get(current_user['id'])

    
    if not user or not user.is_moderador:
        return jsonify({'error': 'Acesso restrito a moderadores'}), 403

   
    evento = Event.query.get(event_id)
    if not evento:
        return jsonify({'error': 'Evento não encontrado'}), 404
    if evento.status != 'aprovado':
        return jsonify({'error': 'O evento precisa estar aprovado para ser finalizado'}), 400

    data = request.get_json()
    if not data or 'resultado' not in data:
        return jsonify({'error': 'Resultado do evento não especificado'}), 400
    
    
    evento.resultado = data['resultado'] 
    evento.status = 'finalizado'
    db.session.commit()

    
    distribute_bets(evento)

    return jsonify({'message': 'Evento finalizado com sucesso'}), 200


def distribute_bets(evento):
    
    apostas = Bet.query.filter_by(evento_id=evento.id).all()

    if not apostas:
        return

    total_apostado = sum([aposta.valor for aposta in apostas])
    
   
    vencedores = []
    for aposta in apostas:
        if (aposta.tipo_aposta == 'sim' and evento.resultado == 'sim') or \
           (aposta.tipo_aposta == 'não' and evento.resultado == 'não'):
            vencedores.append(aposta)
    
    if not vencedores:
        return jsonify({'error': 'Não há vencedores para este evento'}), 400

    
    for vencedor in vencedores:
        percentual_vencedor = vencedor.valor / total_apostado
        valor_ganho = percentual_vencedor * total_apostado
        usuario = User.query.get(vencedor.usuario_id)
        usuario.saldo += valor_ganho
        db.session.commit()

    return jsonify({'message': 'Distribuição de apostas realizada com sucesso'}), 200

