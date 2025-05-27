import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua_chave_secreta_aqui'
    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@db:5432/postgres'
    SQLALCHEMY_DATABASE_URI = 'postgresql://holosdb_q7ws_user:N9tyzkJt3ArU5bsEvD2trrfphLhZsRM0@dpg-d0mt56d6ubrc73enkh0g-a/holosdb_q7ws'
    SQLALCHEMY_TRACK_MODIFICATIONS = False