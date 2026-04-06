from flask import Flask
from config import *
from db import mysql
from admin import init_admin, db
from routes.auth import auth
from routes.products import products
from routes.cart import cart
from routes.orders import orders

app = Flask(__name__)

app.config["MYSQL_HOST"] = MYSQL_HOST
app.config["MYSQL_USER"] = MYSQL_USER
app.config["MYSQL_PASSWORD"] = MYSQL_PASSWORD
app.config["MYSQL_DB"] = MYSQL_DB
app.secret_key = SECRET_KEY

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


mysql.init_app(app)
db.init_app(app)
init_admin(app)

app.register_blueprint(auth)
app.register_blueprint(products)
app.register_blueprint(cart)
app.register_blueprint(orders)

# =========================
# Запуск приложения
# =========================
if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)