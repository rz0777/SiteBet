from app import db
from app.models import User
from werkzeug.security import generate_password_hash
from datetime import datetime

moderador = User.query.filter_by(email="moderador@exemplo.com").first()

if not moderador:
    moderador = User(
        nome="Moderador",
        email="moderador@exemplo.com",
        senha=generate_password_hash("123"),
        is_moderador=True,
        saldo=0.0,
        data_nascimento=datetime.strptime("2000-01-01", "%Y-%m-%d").date()
    )
    db.session.add(moderador)
    db.session.commit()
    print("Moderador criado com sucesso!")
else:
    print("Moderador já existe.")
