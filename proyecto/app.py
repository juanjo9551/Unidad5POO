from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)

app.secret_key = "CLAVE_SECRETA"

@app.route("/")
def index():
    if not session.get("name"):
        return redirect("/login")
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("nombre")
        if name:
            session["name"] = name
            return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("name", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
    