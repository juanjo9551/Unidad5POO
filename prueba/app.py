from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Usuario, Comentario



@app.route("/")
def inicio():
    if session.get("name"):
        return render_template("inicio.html")
    else:
        return redirect("/login")

@app.route("/nuevo_usuario", methods = ["GET", "POST"])
def nuevo_usuario():
    if request.method == "POST":
        print("request_method_post")
        if request.form.get("nombre") and request.form.get("email") and request.form.get("password"):
            usuario_con_mismo_email = Usuario.query.filter_by(email=request.form["email"]).first()
            if usuario_con_mismo_email:
                error_message = f"Usuario ya registrado con email {request.form.get('email')}"
                return render_template(
                    "register.html",
                    error=error_message,
                    nombre=request.form.get("nombre"),
                    email=request.form.get("email")
                )

            else:
                nuevo_usuario = Usuario(nombre=request.form.get("nombre"), email=request.form.get("email"), clave= generate_password_hash(request.form.get("password")))
                db.session.add(nuevo_usuario)
                db.session.commit()
                session["nombre"] = request.form.get("nombre")
                return redirect("/")
    print("renderizando el register")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Usuario.query.filter_by(email=request.form["email"]).first()
        if user:
            if user.nombre == request.form.get("nombre") and user.email == request.form.get("email") and check_password_hash(user.clave, request.form.get("password")):
                session["nombre"] = request.form.get("nombre")
                return render_template("inicio.html")
            else: 
                error_message = "Nombre, correo y contraseña no coincidentes con un usuario existente"
                return render_template(
                "login.html", 
                error=error_message, 
                nombre=request.form.get("nombre"),
                email=request.form.get("email")
            )
            
        else:
            error_message = "Nombre, correo y contraseña no coincidentes con un usuario existente"
            return render_template(
                "login.html", 
                error=error_message, 
                nombre=request.form.get("nombre"),
                email=request.form.get("email")
            )

    else: 
        return render_template("login.html")

@app.route("/nuevo_comentario", methods=["GET", "POST"])
def nuevo_comentario():
    if request.method == "POST":
        if not request.form["email"] or not request.form["password"]:
            return render_template("error.html", error="Por favor ingrese los datos requeridos")
        else:
            usuario_actual = Usuario.query.filter_by(email=request.form["email"]).first()
            if usuario_actual is None:
                return render_template("error.html", error="El correo no está registrado")
            else:
                verificacion = check_password_hash(usuario_actual.clave, request.form["password"])
                if verificacion:
                    return render_template("ingresar_comentario.html", usuario=usuario_actual)
                else:
                    return render_template("error.html", error="La contraseña no es válida")
    else:
        return render_template("nuevo_comentario.html")

@app.route("/ingresar_comentario", methods=["GET", "POST"])
def ingresar_comentario():
    if request.method == "POST":
        if not request.form["contenido"]:
            return render_template("error.html", error="Contenido no ingresado...")
        else:
            nuevo_comentario = Comentario(fecha=datetime.now(), contenido=request.form["contenido"], usuario_id=request.form["userId"])
            db.session.add(nuevo_comentario)
            db.session.commit()
            return render_template("inicio.html")
    return render_template("inicio.html")

@app.route("/listar_comentarios")
def listar_comentarios():
    return render_template("listar_comentarios.html", comentarios = Comentario.query.all())

@app.route("/listar_comentarios_usuario", methods=["GET", "POST"])
def listar_comentarios_usuario():
    if request.method == "POST":
        if not request.form.get("usuarios"):
            #Pasa como parametro todos los usuarios
            return render_template("listar_comentarios_usuario.html", usuarios = Usuario.query.all(), usuario_selec = None)
        else:
            return render_template("listar_comentarios_usuario.html", usuarios = None, usuario_selec = Usuario.query.get(request.form["usuarios"]))
    else:
        return render_template("listar_comentarios_usuario.html", usuarios = Usuario.query.all(), usuario_selec = None)

@app.route("/logout")
def logout():
    session.pop(all, None)
    return redirect("/nuevo_usuario")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)