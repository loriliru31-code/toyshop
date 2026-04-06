from flask import Blueprint, session, jsonify, render_template
from db import mysql
from MySQLdb.cursors import DictCursor

cart = Blueprint("cart", __name__)

def get_user_id():
    return session.get("user_id")


# ================= ПРОСМОТР КОРЗИНЫ =================
@cart.route("/cart")
def view_cart():
    user_id = get_user_id()

    if not user_id:
        return render_template("cart.html", cart_items=[], total_price=0)

    cur = mysql.connection.cursor(DictCursor)

    cur.execute("""
        SELECT ci.product_id, ci.quantity,
               p.name, p.price, p.images
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.user_id=%s
    """, (user_id,))

    items = cur.fetchall()
    cur.close()

    total_price = 0

    for item in items:
        if not item["images"]:
            item["images"] = "img/products/default_product.jpg"

        item["id"] = item["product_id"]  # важно для фронта
        total_price += item["price"] * item["quantity"]

    return render_template("cart.html",
                           cart_items=items,
                           total_price=total_price)


# ================= ДОБАВЛЕНИЕ =================
@cart.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    user_id = get_user_id()

    if not user_id:
        return jsonify({"success": False}), 401

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT quantity FROM cart_items
        WHERE user_id=%s AND product_id=%s
    """, (user_id, product_id))

    row = cur.fetchone()

    if row:
        cur.execute("""
            UPDATE cart_items
            SET quantity = quantity + 1
            WHERE user_id=%s AND product_id=%s
        """, (user_id, product_id))
    else:
        cur.execute("""
            INSERT INTO cart_items(user_id, product_id, quantity)
            VALUES(%s, %s, 1)
        """, (user_id, product_id))

    mysql.connection.commit()

    # счетчик
    cur.execute("""
        SELECT SUM(quantity)
        FROM cart_items
        WHERE user_id=%s
    """, (user_id,))

    count = cur.fetchone()[0] or 0
    cur.close()

    return jsonify({"success": True, "cart_count": count})


# ================= УДАЛЕНИЕ / МИНУС =================
@cart.route("/remove_from_cart/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    user_id = get_user_id()

    if not user_id:
        return jsonify({"success": False}), 401

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT quantity FROM cart_items
        WHERE user_id=%s AND product_id=%s
    """, (user_id, product_id))

    row = cur.fetchone()

    if row:
        if row[0] > 1:
            cur.execute("""
                UPDATE cart_items
                SET quantity = quantity - 1
                WHERE user_id=%s AND product_id=%s
            """, (user_id, product_id))
        else:
            cur.execute("""
                DELETE FROM cart_items
                WHERE user_id=%s AND product_id=%s
            """, (user_id, product_id))

        mysql.connection.commit()

    # пересчет
    cur.execute("""
        SELECT SUM(ci.quantity), SUM(ci.quantity * p.price)
        FROM cart_items ci
        JOIN products p ON ci.product_id = p.id
        WHERE ci.user_id=%s
    """, (user_id,))

    result = cur.fetchone()
    cur.close()

    return jsonify({
        "success": True,
        "cart_count": result[0] or 0,
        "total_price": float(result[1] or 0)
    })


# ================= ОЧИСТКА =================
@cart.route("/clear_cart", methods=["POST"])
def clear_cart():
    user_id = get_user_id()

    if not user_id:
        return jsonify({"success": False}), 401

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM cart_items WHERE user_id=%s", (user_id,))
    mysql.connection.commit()
    cur.close()

    return jsonify({
        "success": True,
        "cart_count": 0,
        "total_price": 0
    })