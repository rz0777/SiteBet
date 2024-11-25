from flask import Blueprint, render_template, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token

bp = Blueprint('home', __name__)

@bp.route('/')
def home_view():
    return render_template('home.html')

@bp.route('/debug_token', methods=['GET'])
def debug_token():
    token = request.cookies.get('token')  
    print(f"Token recebido no cookie: {token}")

    try:
        decoded = decode_token(token)
        print(f"Token decodificado: {decoded}")
        return jsonify(decoded), 200
    except Exception as e:
        print(f"Erro ao decodificar o token: {e}")
        return jsonify({"error": str(e)}), 400
