from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Nome do arquivo onde os dados serão salvos
CSV_FILE = "dados.csv"

# ===============================
# Rota inicial
# ===============================
@app.route("/")
def home():
    return "<h2>🌿 Servidor Monitor Arbor está rodando!</h2><p>Use /dados para enviar dados e /grafico para visualizar.</p>"

# ===============================
# Rota que recebe dados enviados via POST
# ===============================
@app.route("/dados", methods=["POST"])
def receber_dados():
    data = request.get_json()

    if not data or "sensor" not in data or "valor" not in data:
        return jsonify({"status": "erro", "msg": "JSON inválido"}), 400

    df = pd.DataFrame([data])

    # Se arquivo já existir, adiciona no final
    if os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, mode='a', header=False, index=False)
    else:
        df.to_csv(CSV_FILE, index=False)

    return jsonify({"status": "ok"}), 200

# ===============================
# Rota que exibe os dados em uma tabela estilizada
# ===============================
@app.route("/grafico")
def grafico():
    if not os.path.exists(CSV_FILE):
        return "<h3 style='font-family:sans-serif;text-align:center;'>Nenhum dado recebido ainda.</h3>"

    df = pd.read_csv(CSV_FILE)
    tabela_html = df.to_html(
        classes="tabela",
        index=False,
        justify="center",
        border=0
    )

    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>📊 Monitor Arbor - Dados Recebidos</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, sans-serif;
                background-color: #f4f6f9;
                color: #333;
                text-align: center;
                padding: 30px;
            }}
            h1 {{
                font-size: 2.2rem;
                color: #2e7d32;
                margin-bottom: 20px;
            }}
            .tabela {{
                margin: 0 auto;
                border-collapse: collapse;
                width: 70%;
                background-color: white;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border-radius: 8px;
                overflow: hidden;
            }}
            .tabela th {{
                background-color: #4CAF50;
                color: white;
                padding: 12px;
                font-size: 1rem;
            }}
            .tabela td {{
                padding: 10px;
                border-bottom: 1px solid #ddd;
                font-size: 0.95rem;
            }}
            .tabela tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .tabela tr:hover {{
                background-color: #f1f1f1;
            }}
        </style>
    </head>
    <body>
        <h1>📊 Dados Recebidos - Monitor Arbor</h1>
        {tabela_html}
    </body>
    </html>
    """

    return html

# ===============================
# Inicializa o servidor Flask
# ===============================
if __name__ == "__main__":
    # debug=True facilita testes locais
    app.run(host="0.0.0.0", port=5000, debug=True)
