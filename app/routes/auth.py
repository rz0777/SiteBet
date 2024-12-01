from flask import Blueprint, request, jsonify, render_template, make_response, redirect, url_for
from app.models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required, create_access_token
from datetime import timedelta, datetime
from app.routes.home import home_view


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login')
def login_view():
    return render_template('login.html')

@bp.route('/signup')
def signup_view():
    return render_template('signup.html')

@bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data or not all(key in data for key in ('nome', 'email', 'senha', 'data_nascimento')):
        return jsonify({'error': 'Dados incompletos'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'E-mail já cadastrado'}), 400

    hashed_password = generate_password_hash(data['senha'])
    data_nascimento_str = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
    user = User(
        nome=data['nome'],
        email=data['email'],
        senha=hashed_password,
        data_nascimento=data_nascimento_str
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

    token = create_access_token(
        identity=str(user.id),
        expires_delta=timedelta(hours=1)
    )

    response = make_response(jsonify({"message": "Login bem-sucedido!"}))
    response.set_cookie('token', token, httponly=True, secure=False, samesite='Strict')

    return response, 200


@bp.route('/logout', methods=['GET'])
def logout():
    response = make_response(jsonify({"message": "Logout bem-sucedido!"}))
    
    response.delete_cookie('token')
    
    return response, 200

@bp.route('/session', methods=['GET'])
@jwt_required()
def session_info():
    current_user = get_jwt_identity()
    return jsonify(current_user), 200
