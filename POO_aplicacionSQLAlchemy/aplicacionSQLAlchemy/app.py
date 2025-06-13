from datetime import datetime
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db 
from models import Usuario, Comentario
		
@app.route('/')
def inicio():
	return render_template('inicio.html')	
@app.route('/nuevo_usuario', methods = ['GET','POST'])
def nuevo_usuario():   
    resultado= render_template('aviso.html', mensaje="No se pudo ejecutar la operación")
    if request.method == 'POST':
        if not request.form['nombre'] or not request.form['email'] or not request.form['password']:
            resultado=  render_template('error.html', error="Los datos ingresados no son correctos...")
        else:
            nuevo_usuario = Usuario(nombre=request.form['nombre'], correo = request.form['email'], clave=generate_password_hash(request.form['password']))       
            db.session.add(nuevo_usuario)
            db.session.commit()
            resultado=  render_template('aviso.html', mensaje="El usuario se registró exitosamente")
    else:
        resultado= render_template('nuevo_usuario.html')
    return resultado
	
@app.route('/nuevo_comentario', methods = ['GET','POST'])
def nuevo_comentario():
    resultado= render_template('aviso.html', mensaje="No se pudo ejecutar la operación")
    if request.method == 'POST':
        if  not request.form['email'] or not request.form['password']:
            reresultado= render_template('error.html', error="Por favor ingrese los datos requeridos")
        else:
            usuario_actual= Usuario.query.filter_by(correo= request.form['email']).first()
            if usuario_actual is None:
                resultado= render_template('error.html', error="El correo no está registrado")
            else:
                verificacion = check_password_hash(usuario_actual.clave, request.form['password'])
                if (verificacion):                    
                    resultado= render_template('ingresar_comentario.html', usuario = usuario_actual)
                else:
                    retresultado= render_template('error.html', error="La contraseña no es válida")
    else: # Cuando entro por GET
        resultado= render_template('nuevo_comentario.html')
    return resultado

@app.route('/ingresar_comentario', methods = ['GET', 'POST'])
def ingresar_comentario():
    resultado= render_template('aviso.html', mensaje="No se pudo ejecutar la operación")
    if request.method == 'POST':
        if not request.form['contenido']:
            resultado= render_template('error.html', error="Contenido no ingresado...")
        else:            
            nuevo_comentario= Comentario(fecha=datetime.now(), contenido=request.form['contenido'], usuario_id =request.form['userId'])    
            db.session.add(nuevo_comentario)
            db.session.commit()
            resultado= render_template('aviso.html', mensaje="Se ha registrado el comentario")
            #return render_template('inicio.html') 
    else:
        resultado= render_template('inicio.html') 
    return resultado

@app.route('/listar_comentarios')
def listar_comentarios():
   return render_template('listar_comentario.html', comentarios = Comentario.query.all())

@app.route('/listar_comentarios_usuario', methods = ['GET', 'POST'])
def listar_comentarios_usuario():  
    resultado= render_template('aviso.html', mensaje="No se pudo ejecutar la operación")
    if request.method == 'POST':
        if not request.form['usuarios']:
			#Pasa como parámetro todos los usuarios
            resultado= render_template('listar_comentario_usuario.html', usuarios = Usuario.query.all(), usuario_seleccionado = None )
        else:
            resultado= render_template('listar_comentario_usuario.html', usuarios= None, usuario_selec = Usuario.query.get(request.form['usuarios'])) 
    else:
        resultado= render_template('listar_comentario_usuario.html', usuarios = Usuario.query.all(), usuario_selec = None )   
    return resultado
        

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug = True)	