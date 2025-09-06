from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import os

app = Flask(__name__)

CSV_FILE = "dados.csv"

@app.route("/")
def home():
    return "Servidor MonitorArbor está rodando!"

@app.route("/dados", methods=["POST"])
def receber_dados():
    data = request.json
    if not data or "sensor" not in data or "valor" not in data:
        return jsonify({"status": "erro", "msg": "JSON inválido"}), 400

    df = pd.DataFrame([data])
    if os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(CSV_FILE, index=False)

    return jsonify({"status": "ok"}), 200

@app.route("/grafico")
def grafico():
    if not os.path.exists(CSV_FILE):
        return "Sem dados ainda!"

    df = pd.read_csv(CSV_FILE)
    if df.empty:
        return "Sem dados ainda!"

    html = """
    <h1>Dados recebidos</h1>
    {{ tabela|safe }}
    """
    return render_template_string(html, tabela=df.to_html())
