from flask import Blueprint, jsonify
from db import get_db_connection

home_bp = Blueprint('home', __name__)

@home_bp.route('/api/home', methods=['GET'])
def get_home():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # категории
        cursor.execute("SELECT id, name, image FROM categories")
        categories = cursor.fetchall()

        # популярные товары (пока просто последние)
        cursor.execute("""
            SELECT id, name, price, images
            FROM products
            ORDER BY id DESC
            LIMIT 4
        """)
        products = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "categories": categories,
            "products": products
        })

    except Exception as e:
        print(e)
        return jsonify({"message": "Ошибка сервера"}), 500