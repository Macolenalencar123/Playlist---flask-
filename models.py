from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def get_user(user_id):
    return User.query.filter_by(id=user_id).first()

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(40))
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email  
        self.password = generate_password_hash( password)
    
    def verify_password (self, password):
        return check_password_hash(self.password, password)
    
    def __str__(self):
        return self.username

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String)
    status = db.Column(db.Boolean)
    avaliacao = db.Column(db.String)
    favorito = db.Column(db.Boolean)
    usuario = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, titulo, status, avaliacao, favorito, usuario ):
        self.titulo = titulo
        self.status = status
        self.avaliacao = avaliacao
        self.favorito = favorito
        self.usuario = usuario