from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, time, timedelta
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Trabajador, RegistroHorario




def getDifHoras(entrada, salida):
    base_date = datetime.today().date()
    dt_entrada = datetime.combine(base_date, entrada)
    dt_salida = datetime.combine(base_date, salida)

    diferencia = dt_salida - dt_entrada
    return diferencia
app.jinja_env.globals.update(getDifHoras=getDifHoras)

def sum_times(times):
    total_seconds = [t.total_seconds() for t in times]
    hours = sum(total_seconds) // 3600
    print((sum(total_seconds) - hours*3600), sum(total_seconds), hours)
    minutes = (sum(total_seconds) - hours*3600) // 60
    seconds = sum(total_seconds) - hours*3600 - minutes*60
    print(hours, minutes, seconds)
    return (int(hours),int(minutes),int(seconds))
app.jinja_env.globals.update(sum_times=sum_times)

def registros_filtrados(trabajador, dependencia, fechainicio, fechafin):
    registros_filtrados = [
    r for r in trabajador.registroHorario
    if r.horasalida and
       (dependencia == 'Todas' or r.dependencia == dependencia) and
       fechainicio <= r.fecha <= fechafin
    ]
    return bool(registros_filtrados)
app.jinja_env.globals.update(registros_filtrados=registros_filtrados)

@app.route("/")
def inicio():
    return render_template("inicio.html")




@app.route("/registrar_entrada", methods=["GET", "POST"])
def registrar_entrada():
    if request.method == "POST":
        if not request.form["legajo"] or not request.form["ultimosdni"]:
            return render_template("registrar_entrada.html",
                                        legajo=request.form.get("legajo"),
                                        ultimosdni=request.form.get("ultimosdni"),
                                        error="Por favor, complete los campos restantes",
                                        exito=None)
        else:
            ultimosdni = request.form["ultimosdni"]
            trabajador = Trabajador.query.filter(Trabajador.dni.endswith(ultimosdni)).first()
            if trabajador is None:
                return render_template("registrar_entrada.html",
                                        legajo=request.form.get("legajo"),
                                        ultimosdni=request.form.get("ultimosdni"),
                                        error="No hay coincidencias. Intente nuevamente",
                                        exito=None)
            else:
                if trabajador.legajo == request.form.get("legajo"):
                    existe = RegistroHorario.query.filter(
                        RegistroHorario.idtrabajador == trabajador.id,
                        db.func.date(RegistroHorario.fecha) == datetime.now().date(),
                        RegistroHorario.horasalida == None
                    ).first()   
                    if not existe:
                        nuevo_registro_horario = RegistroHorario(fecha=datetime.now().date(), horaentrada=datetime.now().replace(microsecond=0).time(), horasalida=None, dependencia=request.form.get("dependencia"), idtrabajador=trabajador.id)
                        db.session.add(nuevo_registro_horario)
                        db.session.commit()
                        return render_template("registrar_entrada.html",
                                        legajo=request.form.get("legajo"),
                                        ultimosdni=request.form.get("ultimosdni"),
                                        error=None,
                                        exito="La entrada ha sido registrada correctamente")
                    else:
                        return render_template("registrar_entrada.html",
                                        legajo=request.form.get("legajo"),
                                        ultimosdni=request.form.get("ultimosdni"),
                                        error="Ya existe una entrada para la fecha actual",
                                        exito=None)
                else:
                    return render_template("registrar_entrada.html",
                                        legajo=request.form.get("legajo"),
                                        ultimosdni=request.form.get("ultimosdni"),
                                        error="El legajo no coincide con un trabajador con el dni ingresado",
                                        exito=None)
    else:
        return render_template("registrar_entrada.html")




@app.route("/registrar_salida", methods=["GET", "POST"])
def registrar_salida():
    if request.method == "POST":
        if not request.form["legajo"] or not request.form["ultimosdni"]:
            return render_template("registrar_salida.html",
                                        legajo=request.form.get("legajo"),
                                        ultimosdni=request.form.get("ultimosdni"),
                                        dependencia=request.form.get("dependencia"),
                                        error="Por favor, complete los campos restantes",
                                        exito=None)
        else:
            ultimosdni = request.form["ultimosdni"]
            trabajador = Trabajador.query.filter(Trabajador.dni.endswith(ultimosdni)).first()
            if trabajador is None:
                return render_template("registrar_salida.html",
                                        legajo=request.form.get("legajo"),
                                        ultimosdni=request.form.get("ultimosdni"),
                                        dependencia=request.form.get("dependencia"),
                                        error="No hay coincidencias. Intente nuevamente",
                                        exito=None)
            else:
                if trabajador.legajo == request.form.get("legajo"):
                    
                    registro = RegistroHorario.query.filter(
                        RegistroHorario.idtrabajador == trabajador.id,
                        db.func.date(RegistroHorario.fecha) == datetime.now().date(),
                        RegistroHorario.horasalida == None
                    ).first()
                    if registro: 
                        registro.horasalida = datetime.now().replace(microsecond=0).time()
                        db.session.commit()
                        return render_template("registrar_salida.html",
                                        legajo=request.form.get("legajo"),
                                        ultimosdni=request.form.get("ultimosdni"),
                                        dependencia=request.form.get("dependencia"),
                                        error=None,
                                        exito="La salida ha sido registrada correctamente")
                    else:
                        return render_template("registrar_salida.html",
                                        legajo=request.form.get("legajo"),
                                        ultimosdni=request.form.get("ultimosdni"),
                                        dependencia=request.form.get("dependencia"),
                                        error="No existe una entrada para la fecha actual sin salida correspondiente",
                                        exito=None)
                else:
                    return render_template("registrar_salida.html",
                                        legajo=request.form.get("legajo"),
                                        ultimosdni=request.form.get("ultimosdni"),
                                        dependencia=request.form.get("dependencia"),
                                        error="El legajo no coincide con un trabajador con el dni ingresado",
                                        exito=None)
    else:
        return render_template("registrar_salida.html")




@app.route("/consultar_registros", methods=["GET", "POST"])
def consultar_registros():
    if request.method == "POST":
        if not request.form["legajo"] or not request.form["ultimosdni"] or not request.form["fechainicio"] or not request.form["fechafin"]:
            return render_template("consultar_registros.html",
                                        legajo=request.form.get("legajo"),
                                        ultimosdni=request.form.get("ultimosdni"),
                                        fechainicio=request.form.get("fechainicio"),
                                        fechafin=request.form.get("fechafin"),
                                        error="Por favor, complete los campos restantes",
                                        exito=None)
        else:
            ultimosdni = request.form["ultimosdni"]
            trabajador = Trabajador.query.filter(Trabajador.dni.endswith(ultimosdni), Trabajador.legajo == request.form.get("legajo")).first()
            if trabajador is None:
                return render_template("consultar_registros.html",
                                        legajo=request.form.get("legajo"),
                                        ultimosdni=request.form.get("ultimosdni"),
                                        fechainicio=request.form.get("fechainicio"),
                                        fechafin=request.form.get("fechafin"),
                                        error="No hay coincidencias. Intente nuevamente",
                                        exito=None)
            
            else:
                if trabajador.legajo == request.form.get("legajo"):
                    registros = RegistroHorario.query.filter(
                        RegistroHorario.idtrabajador == trabajador.id,
                        db.func.date(RegistroHorario.fecha).between(datetime.strptime(request.form.get("fechainicio"), "%Y-%m-%d").date(), datetime.strptime(request.form.get("fechafin"), "%Y-%m-%d").date()),
                    )
                    
                    print(registros)
                    return render_template("consultar_registros.html",
                                        legajo=request.form.get("legajo"),
                                        ultimosdni=request.form.get("ultimosdni"),
                                        fechainicio=request.form.get("fechainicio"),
                                        fechafin=request.form.get("fechafin"),
                                        registros=list(registros),
                                        mostrar_registros=True,
                                        error=None,
                                        exito=None)
                else:
                    return render_template("consultar_registros.html",
                                        legajo=request.form.get("legajo"),
                                        ultimosdni=request.form.get("ultimosdni"),
                                        fechainicio=request.form.get("fechainicio"),
                                        fechafin=request.form.get("fechafin"),
                                        error="El legajo no coincide con un trabajador con el dni ingresado",
                                        exito=None)
    else:
        return render_template("consultar_registros.html")

    


@app.route("/gen_inf_general", methods=["GET", "POST"])
def gen_inf_general():
    if request.method == "POST":
        if not session.get("name"):
            if not request.form.get("legajo") or not request.form.get("ultimosdni"):
                return render_template("gen_inf_general.html",
                                        legajo=request.form.get("legajo"),
                                        ultimosdni=request.form.get("ultimosdni"),
                                        error="Por favor, complete los campos restantes",
                                        exito=None)
            else:
                trabajador = Trabajador.query.filter(Trabajador.dni.endswith(request.form.get("ultimosdni")),
                                                     Trabajador.legajo == request.form.get("legajo"),
                                                     Trabajador.funcion == "AD").first()
                if trabajador:
                    session["dni"] = trabajador.dni
                    session["legajo"] = request.form.get("legajo")
                    session["ultimosdni"] = request.form.get("ultimosdni")
                    session["dependencia"] = request.form.get("dependencia")
                    session["funcion"] = request.form.get("funcion")
                    
                    return redirect("/gen_inf_general/consultar_datos")
                else:
                    return render_template("gen_inf_general.html",
                                        legajo=request.form.get("legajo"),
                                        ultimosdni=request.form.get("ultimosdni"),
                                        error="No es un trabajador con funcion de administrador",
                                        exito=None)
        else:
            return render_template("gen_inf_general.html")
    else:
        return render_template("gen_inf_general.html")




@app.route("/gen_inf_general/consultar_datos", methods=["GET", "POST"])
def consultar_datos():
    if request.method == "GET":
        return render_template("gen_inf_general.html",
                                        legajo=session.get("legajo"),
                                        ultimosdni=session.get("ultimosdni"),
                                        fechainicio = session.get("fechainicio"),
                                        fechafin = session.get("fechafin"),
                                        funcion = session.get("funcion"),
                                        dependencia = session.get("dependencia"),
                                        admin=True,
                                        error=None,
                                        exito=None)
    elif request.method == "POST":
        fechainicio = request.form.get("fechainicio")
        fechafin = request.form.get("fechafin")
        try:
            fechainicio = datetime.strptime(fechainicio, "%Y-%m-%d").date()
            fechafin = datetime.strptime(fechafin, "%Y-%m-%d").date()
        except ValueError:
            fechainicio = ''
            fechafin = ''
        funcion = request.form.get("funcion")
        dependencia = request.form.get("dependencia")
        if fechainicio and fechafin and funcion and dependencia:
            if funcion == "Todas":
                trabajadores = Trabajador.query.order_by(Trabajador.nombre.asc()).all()
            elif funcion in ("AD", "DO", "TE"):
                trabajadores = Trabajador.query.order_by(Trabajador.nombre.asc()).filter(Trabajador.funcion == funcion).all()
            hay_registros_por_trabajador = [True if t.registroHorario else False for t in trabajadores]
            return render_template("gen_inf_general.html",
                                        legajo=session.get("legajo"),
                                        ultimosdni=session.get("ultimosdni"),
                                        fechainicio=fechainicio,
                                        fechafin=fechafin,
                                        funcion=funcion,
                                        dependencia=dependencia,
                                        trabajadores=trabajadores,
                                        admin=True,
                                        hay_registros_por_trabajador=hay_registros_por_trabajador,
                                        error=None,
                                        exito=None)
        else:
            return render_template("gen_inf_general.html",
                                        legajo=session.get("legajo"),
                                        ultimosdni=session.get("ultimosdni"),
                                        fechainicio=fechainicio,
                                        fechafin=fechafin,
                                        funcion=funcion,
                                        dependencia=dependencia,
                                        admin=True,
                                        error="Por favor, complete los campos restantes",
                                        exito=None)




@app.route("/gen_inf_personal", methods=["GET", "POST"])
def gen_inf_personal():
    if request.method == "POST":
        if not session.get("name"):
            if not request.form.get("legajo") or not request.form.get("ultimosdni"):
                return render_template("gen_inf_personal.html",
                                        legajo=request.form.get("legajo"),
                                        ultimosdni=request.form.get("ultimosdni"),
                                        error="Por favor, complete los campos restantes",
                                        exito=None)
            else:
                trabajador = Trabajador.query.filter(Trabajador.dni.endswith(request.form.get("ultimosdni")),
                                                     Trabajador.legajo == request.form.get("legajo"),
                                                     Trabajador.funcion == "AD").first()
                if trabajador:
                    session["dni"] = trabajador.dni
                    session["legajo"] = request.form.get("legajo")
                    session["ultimosdni"] = request.form.get("ultimosdni")
                    return redirect("/gen_inf_personal/consultar_datos")
                else:
                    return render_template("gen_inf_personal.html",
                                        legajo=request.form.get("legajo"),
                                        ultimosdni=request.form.get("ultimosdni"),
                                        error="No es un trabajador con funcion de administrador",
                                        exito=None)
        else:
            return render_template("gen_inf_personal.html")
    else:
        return render_template("gen_inf_personal.html")




@app.route("/gen_inf_personal/consultar_datos", methods=["GET", "POST"])
def gen_inf_personal_consultar_datos():
    if request.method == "GET":
        return render_template("gen_inf_personal.html",
                                        legajo=session.get("legajo"),
                                        ultimosdni=session.get("ultimosdni"),
                                        admin=True,
                                        error=None,
                                        exito=None)
    elif request.method == "POST":
        fechainicio = request.form.get("fechainicio")
        fechafin = request.form.get("fechafin")
        dni = request.form.get("dni")
        print(fechainicio, fechafin, dni)
        if fechainicio and fechafin and dni:
            try:
                fechainicio = datetime.strptime(fechainicio, "%Y-%m-%d").date()
                fechafin = datetime.strptime(fechafin, "%Y-%m-%d").date()
                trabajador = Trabajador.query.filter(Trabajador.dni == dni).first()
                registros_periodo = RegistroHorario.query.filter(
                        RegistroHorario.idtrabajador == trabajador.id,
                        db.func.date(RegistroHorario.fecha).between(datetime.strptime(request.form.get("fechainicio"), "%Y-%m-%d").date(), datetime.strptime(request.form.get("fechafin"), "%Y-%m-%d").date()),
                    )
                total_time = sum_times([getDifHoras(reg.horaentrada, reg.horasalida) for reg in registros_periodo if reg.horasalida])
            except ValueError:
                return render_template("gen_inf_personal.html",
                                        legajo=session.get("legajo"),
                                        ultimosdni=session.get("ultimosdni"),
                                        fechainicio=fechainicio,
                                        fechafin=fechafin,
                                        dni=dni,
                                        admin=True,
                                        error="Por favor, ingrese los datos de las fechas",
                                        exito=None)
            
            return render_template("gen_inf_personal.html",
                                        legajo=session.get("legajo"),
                                        ultimosdni=session.get("ultimosdni"),
                                        fechainicio=fechainicio,
                                        fechafin=fechafin,
                                        dni=dni,
                                        trabajador=trabajador,
                                        admin=True,
                                        total_time=total_time,
                                        registros_periodo=registros_periodo,
                                        error=None,
                                        exito=None)
        else:
            return render_template("gen_inf_personal.html",
                                        legajo=session.get("legajo"),
                                        ultimosdni=session.get("ultimosdni"),
                                        fechainicio=fechainicio,
                                        fechafin=fechafin,
                                        dni=dni,
                                        admin=True,
                                        error="Por favor, complete los campos restantes",
                                        exito=None)




if __name__ == "__main__":
    app.run(debug=True, port=5000)