from flask import Blueprint, request, jsonify
from app.models import User, db
from werkzeug.security import generate_password_hash, check_password_hash


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data or not all(key in data for key in ('nome', 'email', 'senha', 'data_nascimento')):
        return jsonify({'error': 'Dados incompletos'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'E-mail já cadastrado'}), 400

    hashed_password = generate_password_hash(data['senha'])
    user = User(
        nome=data['nome'],
        email=data['email'],
        senha=hashed_password,
        data_nascimento=data['data_nascimento']
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Usuário criado com sucesso!'}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not all(key in data for key in ('email', 'senha')):
        return jsonify({'error': 'Dados incompletos'}), 400


    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.senha, data['senha']):
        return jsonify({'error': 'E-mail ou senha inválidos'}), 401

    return jsonify({'message': 'Login realizado com sucesso!'}), 200
