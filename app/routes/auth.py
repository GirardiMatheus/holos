from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
import bcrypt
from ..models.usuario import Usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        senha = request.form.get('senha')

        usuario = Usuario.query.filter_by(username=username).first()
        if usuario:
            stored_hash = usuario.senha_hash
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')
            
            if bcrypt.checkpw(senha.encode('utf-8'), stored_hash):
                session['username'] = username
                return jsonify({"status": "success", "message": "Login realizado com sucesso!"})
        
        return jsonify({"status": "error", "message": "Credenciais inválidas"}), 401

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.login'))