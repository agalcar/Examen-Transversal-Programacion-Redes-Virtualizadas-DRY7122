import sqlite3

from flask import Flask, redirect, render_template, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
BASE_DATOS = "usuarios.db"


def obtener_conexion():
    conexion = sqlite3.connect(BASE_DATOS)
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_base_datos():
    conexion = obtener_conexion()

    conexion.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )

    conexion.commit()
    conexion.close()


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    mensaje = ""

    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        usuario = request.form["usuario"].strip()
        password = request.form["password"]

        if not nombre or not usuario or not password:
            mensaje = "Todos los campos son obligatorios."
        else:
            password_hash = generate_password_hash(password)

            try:
                conexion = obtener_conexion()

                conexion.execute(
                    """
                    INSERT INTO usuarios (nombre, usuario, password)
                    VALUES (?, ?, ?)
                    """,
                    (nombre, usuario, password_hash)
                )

                conexion.commit()
                conexion.close()

                mensaje = "Usuario registrado correctamente."

            except sqlite3.IntegrityError:
                mensaje = "El nombre de usuario ya se encuentra registrado."

    return render_template("registro.html", mensaje=mensaje)


@app.route("/login", methods=["POST"])
def login():
    usuario = request.form["usuario"].strip()
    password = request.form["password"]

    conexion = obtener_conexion()

    registro = conexion.execute(
        "SELECT * FROM usuarios WHERE usuario = ?",
        (usuario,)
    ).fetchone()

    conexion.close()

    if registro and check_password_hash(registro["password"], password):
        mensaje = f"Acceso correcto. Bienvenido, {registro['nombre']}."
    else:
        mensaje = "Usuario o contraseña incorrectos."

    return render_template("index.html", mensaje=mensaje)


if __name__ == "__main__":
    crear_base_datos()
    app.run(host="0.0.0.0", port=7500, debug=True)
