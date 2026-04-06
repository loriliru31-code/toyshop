from flask import Blueprint, render_template, url_for, request, session, jsonify
from db import mysql

# возвращаем прежнее имя Blueprint
products = Blueprint("products", __name__)


# ================= ВСПОМОГАТЕЛЬНОЕ =================
def get_cart_ids(user_id):
    """Получаем список id товаров в корзине для текущего пользователя"""
    if not user_id:
        return []

    cur = mysql.connection.cursor()
    cur.execute("SELECT product_id FROM cart_items WHERE user_id=%s", (user_id,))
    rows = cur.fetchall()
    cur.close()
    return [r[0] for r in rows]


# ================= ГЛАВНАЯ =================
@products.route("/")
def index():
    cur = mysql.connection.cursor()

    user_id = session.get("user_id")
    cart_ids = get_cart_ids(user_id)

    # Получаем категории
    cur.execute("SELECT id, name FROM categories")
    categories_rows = cur.fetchall()

    categories = [
        {
            "id": c[0],
            "name": c[1],
            "images": None
        }
        for c in categories_rows
    ]

    # Получаем последние 6 товаров
    cur.execute("SELECT id, name, price, images, category_id FROM products ORDER BY id DESC LIMIT 6")
    rows = cur.fetchall()
    cur.close()

    products_list = []
    for r in rows:
        products_list.append({
            "id": r[0],
            "name": r[1],
            "price": float(r[2]),
            "images": url_for('static', filename=f"img/products/{r[3]}") if r[3]
                      else url_for('static', filename="img/products/default_product.jpg"),
            "category_id": r[4]
        })

    return render_template(
        "index.html",
        products=products_list,
        categories=categories,
        cart_ids=cart_ids
    )


# ================= КАТАЛОГ =================
@products.route("/catalog")
def catalog():
    cur = mysql.connection.cursor()

    user_id = session.get("user_id")
    cart_ids = get_cart_ids(user_id)

    # Получаем категории
    cur.execute("SELECT id, name FROM categories")
    categories_rows = cur.fetchall()

    categories = [
        {
            "id": c[0],
            "name": c[1],
            "images": None
        }
        for c in categories_rows
    ]
    # Получаем все товары
    cur.execute("SELECT id, name, price, images, category_id FROM products ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()

    products_list = []
    for r in rows:
        products_list.append({
            "id": r[0],
            "name": r[1],
            "price": float(r[2]),
            "images": url_for('static', filename=f"img/products/{r[3]}") if r[3]
                      else url_for('static', filename="img/products/default_product.jpg"),
            "category_id": r[4]
        })

    return render_template(
        "catalog.html",
        products=products_list,
        categories=categories,
        cart_ids=cart_ids
    )


# ================= API ФИЛЬТР =================
@products.route("/api/products")
def api_products():
    category_id = request.args.get("category_id", type=int)
    cur = mysql.connection.cursor()

    if category_id:
        cur.execute("""
            SELECT id, name, price, images, category_id
            FROM products
            WHERE category_id=%s
            ORDER BY id DESC
        """, (category_id,))
    else:
        cur.execute("SELECT id, name, price, images, category_id FROM products ORDER BY id DESC")

    rows = cur.fetchall()
    cur.close()

    products_list = []
    for r in rows:
        products_list.append({
            "id": r[0],
            "name": r[1],
            "price": float(r[2]),
            "images": url_for('static', filename=f"img/products/{r[3]}") if r[3]
                      else url_for('static', filename="img/products/default_product.jpg"),
            "category_id": r[4]
        })

    return jsonify(products_list)


# ================= СТРАНИЦА ТОВАРА =================
@products.route("/product/<int:product_id>")
def product_page(product_id):
    cur = mysql.connection.cursor()
    user_id = session.get("user_id")
    cart_ids = get_cart_ids(user_id)

    cur.execute("""
        SELECT id, name, price, images, category_id
        FROM products
        WHERE id=%s
    """, (product_id,))
    p = cur.fetchone()
    cur.close()

    if not p:
        return "Товар не найден", 404

    product = {
        "id": p[0],
        "name": p[1],
        "price": float(p[2]),
        "images": url_for('static', filename=f"img/products/{p[3]}") if p[3]
                  else url_for('static', filename="img/products/default_product.jpg"),
        "category_id": p[4]
    }

    return render_template(
        "product.html",
        product=product,
        cart_ids=cart_ids
    )