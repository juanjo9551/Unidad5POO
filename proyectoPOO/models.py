from __main__ import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class Trabajador(db.Model):
    __tablename__ = 'trabajador'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    dni = db.Column(db.String(80), nullable=False)
    correo = db.Column(db.String(120), nullable=False)
    legajo = db.Column(db.Integer, nullable=False)
    horas = db.Column(db.Integer)
    funcion = db.Column(db.String(50))
    #fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    registroHorario = db.relationship('RegistroHorario', backref='trabajador', cascade="all, delete-orphan")


class RegistroHorario(db.Model):
    __tablename__ = 'registroHorario'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable = False) 
    horaEntrada = db.Column(db.DateTime, nullable=False) 
    horaSalida = db.Column(db.DateTime, nullable=True) 
    dependencia = db.Column(db.String(10), nullable=False)
    trabajador_id = db.Column(db.Integer, db.ForeignKey('trabajador.id'), nullable=False)