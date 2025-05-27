import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua_chave_secreta_aqui'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@db:5432/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False