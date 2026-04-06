from flask import Blueprint, session, redirect, render_template, request
from db import mysql
from datetime import datetime
from MySQLdb.cursors import DictCursor

orders = Blueprint("orders", __name__)

# ---------------- Получение текущего пользователя ----------------
def get_user_id():
    return session.get("user_id")


# =================== СТРАНИЦА ВСЕХ ЗАКАЗОВ ===================
@orders.route("/orders")
def orders_page():
    user_id = get_user_id()
    if not user_id:
        return redirect("/register")

    cur = mysql.connection.cursor(DictCursor)
    cur.execute("""
        SELECT id, total_price, created_at
        FROM orders
        WHERE user_id=%s
        ORDER BY created_at DESC
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()

    # Преобразуем даты в объекты datetime
    for r in rows:
        if isinstance(r['created_at'], str):
            r['created_at'] = datetime.strptime(r['created_at'], "%Y-%m-%d %H:%M:%S")

    return render_template("orders.html", orders=rows)


# =================== ПРОСМОТР ТОВАРОВ В ЗАКАЗЕ ===================
@orders.route("/order_items/<int:order_id>")
def order_items(order_id):
    user_id = get_user_id()
    if not user_id:
        return redirect("/register")

    cur = mysql.connection.cursor(DictCursor)
    # Проверка владельца заказа
    cur.execute("SELECT user_id FROM orders WHERE id=%s", (order_id,))
    order = cur.fetchone()
    if not order or order['user_id'] != user_id:
        cur.close()
        return redirect("/orders")

    # Товары в заказе
    cur.execute("""
        SELECT p.name, oi.price, oi.quantity
        FROM order_items oi
        JOIN products p ON p.id = oi.product_id
        WHERE oi.order_id=%s
    """, (order_id,))
    items = cur.fetchall()
    cur.close()

    return render_template("order_items.html", items=items)


# =================== СОЗДАНИЕ ЗАКАЗА ===================
@orders.route("/create_order", methods=["POST"])
def create_order():
    user_id = get_user_id()
    if not user_id:
        return redirect("/register")

    cur = mysql.connection.cursor(DictCursor)

    cur.execute("""
        SELECT ci.product_id, ci.quantity, p.price
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.user_id=%s
    """, (user_id,))
    cart_items = cur.fetchall()
    if not cart_items:
        cur.close()
        return redirect("/cart")

    total = sum(item['price'] * item['quantity'] for item in cart_items)

    cur.execute(
        "INSERT INTO orders(user_id, total_price, created_at) VALUES(%s, %s, NOW())",
        (user_id, total)
    )
    order_id = cur.lastrowid

    for item in cart_items:
        cur.execute("""
            INSERT INTO order_items(order_id, product_id, quantity, price)
            VALUES(%s, %s, %s, %s)
        """, (order_id, item['product_id'], item['quantity'], item['price']))

    cur.execute("DELETE FROM cart_items WHERE user_id=%s", (user_id,))
    mysql.connection.commit()
    cur.close()

    return redirect("/orders")


# =================== СТРАНИЦА ОФОРМЛЕНИЯ ЗАКАЗА ===================
@orders.route("/checkout")
def checkout():
    user_id = get_user_id()
    if not user_id:
        return redirect("/register")

    cur = mysql.connection.cursor(DictCursor)
    cur.execute("""
        SELECT ci.product_id, ci.quantity, p.name, p.price, p.images
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.user_id=%s
    """, (user_id,))
    cart_items = cur.fetchall()
    cur.close()

    if not cart_items:
        return redirect("/cart")

    # Подсчёт общей суммы
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)

    # Дефолтная картинка для товаров без изображения
    for item in cart_items:
        if not item['images']:
            item['images'] = "img/default_product.jpg"

    return render_template("checkout.html", cart_items=cart_items, total_price=total_price)