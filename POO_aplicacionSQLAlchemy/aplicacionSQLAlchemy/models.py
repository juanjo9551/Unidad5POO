from __main__ import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class Usuario(db.Model):
    __tablename__= 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    clave = db.Column(db.String(120), nullable=False)    
    comentario = db.relationship('Comentario', backref='usuario', cascade="all, delete-orphan")
	
class Comentario(db.Model):
    __tablename__= "comentario"
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime)
    contenido = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))        
    