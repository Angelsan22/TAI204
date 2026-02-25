from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)

FASTAPI_URL = "http://localhost:5000"

@app.route("/")
def inicio():
    respuesta = requests.get(f"{FASTAPI_URL}/v1/usuarios/")
    data = respuesta.json()
    return render_template("index.html", usuarios=data["Usuarios"])


@app.route("/agregar", methods=["POST"])
def agregar():
    usuario = {
        "id": int(request.form["id"]),
        "nombre": request.form["nombre"],
        "edad": int(request.form["edad"])
    }

    requests.post(f"{FASTAPI_URL}/v1/usuarios/", json=usuario)
    return redirect("/")


@app.route("/eliminar/<int:id>")
def eliminar(id):
    requests.delete(f"{FASTAPI_URL}/v1/usuarios/{id}")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
