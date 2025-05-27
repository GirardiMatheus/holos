from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    from .routes.auth import auth_bp
    from .routes.exames import exames_bp
    from .routes.orcamentos import orcamentos_bp
    from .routes.main import main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(exames_bp)
    app.register_blueprint(orcamentos_bp)
    app.register_blueprint(main_bp)
    
    with app.app_context():
        db.create_all()
        from .models.usuario import inicializar_usuarios
        inicializar_usuarios()
    
    return app