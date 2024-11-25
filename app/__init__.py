from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.routes import auth, events, wallet, home, bets
    app.register_blueprint(auth.bp)
    app.register_blueprint(events.bp)
    app.register_blueprint(wallet.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(bets.bp)

    from app.models import User

    @app.before_request
    def load_user():
        try:
            verify_jwt_in_request()  
            user_id = get_jwt_identity()  
            print(f"Usuário autenticado com ID: {user_id}")

            g.current_user = User.query.get(int(user_id)) if user_id else None
            if g.current_user:
                print(f"Usuário carregado: {g.current_user.nome}")
            else:
                print("Nenhum usuário encontrado")
        except Exception as e:
            g.current_user = None
            print(f"Erro ao verificar o token: {e}")

    return app
