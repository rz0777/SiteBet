from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.routes import auth, events, bets, wallet
    app.register_blueprint(auth.bp)
    app.register_blueprint(events.bp)
    app.register_blueprint(bets.bp)
    app.register_blueprint(wallet.bp)

    return app
