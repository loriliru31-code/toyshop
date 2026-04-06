from flask import Blueprint, render_template, request, redirect, session
from db import mysql
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)

# ------------------- Вход пользователя -------------------
@auth.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, password_hash, role
            FROM users WHERE email=%s
        """, (email,))
        user = cur.fetchone()
        cur.close()

        if not user or not check_password_hash(user[1], password):
            error = "Неверный email или пароль"
        else:
            session["user_id"] = user[0]
            session["role"] = user[2]

            return redirect("/")

    return render_template("login.html", error=error)


# ------------------- Отдельный вход для админа -------------------
@auth.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            error = "Введите email и пароль"
        else:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id, password_hash, role FROM users WHERE email=%s", (email,))
            user = cur.fetchone()
            cur.close()

            if not user or user[2] != "admin":
                error = "Нет доступа"
            else:
                stored_password = user[1] or ""
                if stored_password.startswith(("pbkdf2:sha256:", "scrypt:")):
                    valid = check_password_hash(stored_password, password)
                else:
                    valid = stored_password == password

                if valid:
                    session["user_id"] = user[0]
                    session["role"] = "admin"
                    return redirect("/admin")
                else:
                    error = "Нет доступа"

    return render_template("admin_login.html", error=error)


# ------------------- Регистрация -------------------
@auth.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            error = "Заполните все поля"

        elif len(password) < 6:
            error = "Пароль должен быть минимум 6 символов"

        else:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id FROM users WHERE email=%s", (email,))
            if cur.fetchone():
                error = "Пользователь уже существует"
                cur.close()
            else:
                hashed = generate_password_hash(password)

                cur.execute("""
                    INSERT INTO users(name, email, password_hash)
                    VALUES(%s, %s, %s)
                """, (name, email, hashed))

                mysql.connection.commit()

                # 🔥 авто логин
                session["user_id"] = cur.lastrowid
                session["role"] = "user"

                cur.close()
                return redirect("/")

    return render_template("register.html", error=error)


# ------------------- Профиль -------------------
@auth.route("/profile")
def profile():
    user_id = session.get("user_id")

    if not user_id:
        return redirect("/login")

    cur = mysql.connection.cursor()
    cur.execute("SELECT name, email, address FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    cur.close()

    return render_template("profile.html", user={
    "fullname": user[0],
    "email": user[1],
    "address": user[2]
})

def get_user_id():
    return session.get("user_id")

@auth.route("/update_address", methods=["POST"])
def update_address():
    user_id = get_user_id()
    if not user_id:
        return redirect("/login")  # если не авторизован

    # Получаем адрес из формы
    new_address = request.form.get("address", "").strip()
    if not new_address:
        # можно добавить flash сообщение или редирект с ошибкой
        return redirect("/profile")

    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET address=%s WHERE id=%s", (new_address, user_id))
    mysql.connection.commit()
    cur.close()

    return redirect("/profile")

@auth.route("/update_profile", methods=["POST"])
def update_profile():
    user_id = get_user_id()
    if not user_id:
            return redirect("/login")

    # Получаем данные из формы
    new_name = request.form.get("name", "").strip()
    new_email = request.form.get("email", "").strip()

    if not new_name and not new_email:
        # ничего не менять
        return redirect("/profile")

    cur = mysql.connection.cursor()
    if new_name:
        cur.execute("UPDATE users SET name=%s WHERE id=%s", (new_name, user_id))
    if new_email:
        cur.execute("UPDATE users SET email=%s WHERE id=%s", (new_email, user_id))
    mysql.connection.commit()
    cur.close()

    return redirect("/profile")

# ------------------- Выход -------------------
@auth.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("role", None)
    return redirect("/")