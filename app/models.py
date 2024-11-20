from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Modelo de Usuário
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(128), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    saldo = db.Column(db.Float, default=0.0)
    is_moderador = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.nome}>'

# Modelo de Evento
class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(150), nullable=False)
    valor_cota = db.Column(db.Float, nullable=False)
    data_inicio_apostas = db.Column(db.DateTime, nullable=False)
    data_fim_apostas = db.Column(db.DateTime, nullable=False)
    data_ocorrencia = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pendente')  # pendente, aprovado, rejeitado
    resultado = db.Column(db.String(10), default='indefinido')  # sim, não, indefinido
    criado_por = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    criador = db.relationship('User', backref=db.backref('eventos', lazy=True))

    def __repr__(self):
        return f'<Event {self.titulo}>'

# Modelo de Aposta
class Bet(db.Model):
    __tablename__ = 'bets'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    evento_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tipo_aposta = db.Column(db.String(10), nullable=False)  # sim ou não

    usuario = db.relationship('User', backref=db.backref('apostas', lazy=True))
    evento = db.relationship('Event', backref=db.backref('apostas', lazy=True))

    def __repr__(self):
        return f'<Bet User {self.usuario_id} Event {self.evento_id}>'

# Modelo de Transação
class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # adicionar, sacar
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    detalhes = db.Column(db.String(150))

    usuario = db.relationship('User', backref=db.backref('transacoes', lazy=True))

    def __repr__(self):
        return f'<Transaction {self.tipo} {self.valor}>'
