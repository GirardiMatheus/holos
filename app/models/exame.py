from .. import db

class Exame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.String(50), nullable=False)