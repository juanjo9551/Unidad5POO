from flask import Flask
from models import db, Producto

app = Flask(__name__)
app.config.from_pyfile("config.py")  # o configura manualmente DATABASE_URI

db.init_app(app)

with app.app_context():
    Producto.__table__.create(db.engine)
