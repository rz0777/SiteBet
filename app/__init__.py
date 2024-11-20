from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import auth, events, bets, wallet
    app.register_blueprint(auth.bp)
    app.register_blueprint(events.bp)
    app.register_blueprint(bets.bp)
    app.register_blueprint(wallet.bp)

    return app
