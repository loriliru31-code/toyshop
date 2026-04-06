from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask import redirect, session

# Подключаем SQLAlchemy (ОДИН экземпляр на всё приложение)
db = SQLAlchemy()

# ==================== МОДЕЛИ ====================
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(150))
    password_hash = db.Column(db.Text)
    address = db.Column(db.Text)
    role = db.Column(db.String(20))

    def __str__(self):
        return self.email


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    price = db.Column(db.Integer)
    images = db.Column(db.String(255))
    category_id = db.Column(db.Integer)

    def __str__(self):
        return self.name


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    images = db.Column(db.String(255))

    def __str__(self):
        return self.name


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    total_price = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)

    def __str__(self):
        return f"Order {self.id}"


class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)

    def __str__(self):
        return f"Item {self.id}"


class CartItem(db.Model):
    __tablename__ = "cart_items"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer)

    def __str__(self):
        return f"Cart {self.id}"


# ==================== ЗАЩИТА АДМИНКИ ====================
class AdminModelView(ModelView):
    can_export = True
    page_size = 50

    def is_accessible(self):
        return session.get("role") == "admin"

    def inaccessible_callback(self, name, **kwargs):
        return redirect("/admin/login")


# ==================== ИНИЦИАЛИЗАЦИЯ ====================
def init_admin(app):
    # ❌ НИКАКОГО db.init_app ЗДЕСЬ!

    admin = Admin(app, name="Shop Admin")

    admin.add_view(AdminModelView(User, db.session, category="Пользователи"))
    admin.add_view(AdminModelView(Product, db.session, category="Каталог"))
    admin.add_view(AdminModelView(Category, db.session, category="Каталог"))
    admin.add_view(AdminModelView(Order, db.session, category="Заказы"))
    admin.add_view(AdminModelView(OrderItem, db.session, category="Заказы"))
    admin.add_view(AdminModelView(CartItem, db.session, category="Корзина"))

    return admin