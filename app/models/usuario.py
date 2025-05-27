import os
from .. import db
from dotenv import load_dotenv

load_dotenv()  

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.LargeBinary(128), nullable=False)

def inicializar_usuarios():
    Usuario.query.delete()

    usuarios = [
        {
            'username': os.getenv('USER_1_USERNAME'),
            'senha_hash': os.getenv('USER_1_HASH').encode()  
        },
        {
            'username': os.getenv('USER_2_USERNAME'),
            'senha_hash': os.getenv('USER_2_HASH').encode()
        }
    ]

    for usuario in usuarios:
        if usuario["username"] and usuario["senha_hash"]:  
            if not Usuario.query.filter_by(username=usuario['username']).first():
                db.session.add(Usuario(
                    username=usuario['username'],
                    senha_hash=usuario['senha_hash']
                ))

    db.session.commit()