from .. import db

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.LargeBinary(128), nullable=False)

def inicializar_usuarios():
    # Limpa usuários existentes para evitar duplicatas
    Usuario.query.delete()
    
    # Adiciona os usuários com os hashes gerados
    usuarios = [
        {
            'username': 'velorin',
            'senha_hash': b'$2b$12$2gYAxX0YXlZeq6FMKgSktOE5ezsxtMrJBtzJ26asBIeq0Drdh.FIy'  
        },
        {
            'username': 'r.souza',
            'senha_hash': b'$2b$12$dqO.B7Zs.EywgyjnH3xjYuMxZHb/Yur4JQYtj9WnOA77pI6mNxNJ2'  
        }
    ]
    
    for usuario in usuarios:
        if not Usuario.query.filter_by(username=usuario['username']).first():
            db.session.add(Usuario(
                username=usuario['username'],
                senha_hash=usuario['senha_hash']
            ))
    
    db.session.commit()