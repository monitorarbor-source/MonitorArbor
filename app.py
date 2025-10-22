# ===========================================
#Importações e configurações iniciais
# ===========================================
from flask import Flask, request, jsonify, render_template_string, send_file
import pandas as pd
import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

app = Flask(__name__)

# Nome do arquivo CSV local (Render usa disco temporário)
CSV_FILE = "dados.csv"

# Se o Render tiver a variável de ambiente com as credenciais do Google Drive
# (armazenada como GDRIVE_CREDENTIALS), recria o arquivo de credenciais.
if "GDRIVE_CREDENTIALS" in os.environ:
    with open("credentials.json", "w") as f:
        f.write(os.environ["GDRIVE_CREDENTIALS"])

# ===========================================
#Função de backup para o Google Drive
# ===========================================
def upload_to_drive(filename):
    """Faz backup automático do arquivo CSV no Google Drive"""
    try:
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile("credentials.json")
        if gauth.credentials is None:
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()

        drive = GoogleDrive(gauth)

        # Verifica se já existe um arquivo com o mesmo nome no Drive
        file_list = drive.ListFile({'q': f"title='{filename}'"}).GetList()
        if file_list:
            file_drive = file_list[0]
            file_drive.SetContentFile(filename)
            file_drive.Upload()
        else:
            file_drive = drive.CreateFile({'title': filename})
            file_drive.SetContentFile(filename)
            file_drive.Upload()

        print(f"Backup feito no Google Drive: {filename}")
    except Exception as e:
        print("Erro ao enviar para o Google Drive:", e)

# ===========================================
#Rota Flask para receber e salvar dados
# ===========================================
@app.route("/dados", methods=["POST"])
def receber_dados():
    """Recebe dados JSON, salva no CSV e envia para o Drive"""
    data = request.json
    if not data or "sensor" not in data or "valor" not in data:
        return jsonify({"status": "erro", "msg": "JSON inválido"}), 400

    df = pd.DataFrame([data])

    # Salva no CSV local (no Render)
    if os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(CSV_FILE, index=False)

    print("📥 Dado recebido e salvo:", data)

    # Faz backup no Google Drive
    upload_to_drive(CSV_FILE)

    return jsonify({"status": "ok"}), 200

# ===========================================
# Rota para exibir dados em tabela HTML
# ===========================================
@app.route("/grafico")
def grafico():
    """Mostra tabela com dados salvos"""
    if not os.path.exists(CSV_FILE):
        return "Sem dados ainda!"

    df = pd.read_csv(CSV_FILE)
    if df.empty:
        return "Sem dados ainda!"

    html = """
    <h1>📊 Dados recebidos</h1>
    {{ tabela|safe }}
    """
    return render_template_string(html, tabela=df.to_html())

# ===========================================
# Rota inicial (teste)
# ===========================================
@app.route("/")
def home():
    return "Servidor MonitorArbor está rodando!"

# ===========================================
# Execução local (Render usa Gunicorn)
# ===========================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
@app.route("/grafico")
def grafico():
    if not os.path.exists(CSV_FILE):
        return "<h3>Nenhum dado recebido ainda.</h3>"

    df = pd.read_csv(CSV_FILE)

    # Converte DataFrame em tabela HTML com classes CSS
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
                width: 60%;
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


