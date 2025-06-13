from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Trabajador, RegistroHorario


@app.route("/")
def inicio():
    return render_template("inicio.html")

@app.route("/registrar_entrada", methods=["GET", "POST"])
def registrar_entrada():
    if request.method == "POST":
        if not request.form["legajo"] or not request.form["ultimosdni"]:
            return render_template("error.html", error="Por favor ingrese los datos requeridos")
        else:
            ultimos4 = request.form["ultimosdni"]
            trabajador = Trabajador.query.filter(Trabajador.dni.endswith(ultimos4)).first()
            if trabajador is None:
                return render_template("error.html", error="No hay coincidencias. Intente nuevamente")
            else:
                if trabajador.legajo == request.form.get("legajo"):
                    
                    existe = RegistroHorario.query.filter(
                        RegistroHorario.trabajador_id == trabajador.id,
                        db.func.date(RegistroHorario.fecha) == datetime.now().date()
                    ).first()   


                    nuevo_registro_horario = RegistroHorario(fecha=datetime.now(), horaEntrada=datetime.now(), horaSalida=None, trabajador_id=trabajador.id)
                    db.session.add(nuevo_registro_horario)
                    db.session.commit()
                    return redirect("/inicio")
                else:
                    return render_template("error.html", error="El legajo no coincide con un trabajador con el dni ingresado")
       
    else:
        return render_template("registrar_entrada.html")
@app.route("/registrar_salida")
def registrar_entrada():
    return render_template("registrar_salida.html")
@app.route("/consultar_registros")
def registrar_entrada():
    return render_template("consultar_registros.html")
@app.route("/gen_inf_general")
def registrar_entrada():
    return render_template("gen_inf_general.html")
@app.route("/gen_inf_personal1")
def registrar_entrada():
    return render_template("gen_inf_personal1.html")



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)