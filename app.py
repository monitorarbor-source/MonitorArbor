# ===========================================
# 1️⃣  Importações e configurações iniciais
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
# 2️⃣  Função de backup para o Google Drive
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

        print(f"✅ Backup feito no Google Drive: {filename}")
    except Exception as e:
        print("⚠️ Erro ao enviar para o Google Drive:", e)

# ===========================================
# 3️⃣  Rota Flask para receber e salvar dados
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
# 4️⃣  Rota para exibir dados em tabela HTML
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
# 5️⃣  Rota inicial (teste)
# ===========================================
@app.route("/")
def home():
    return "Servidor MonitorArbor está rodando!"

# ===========================================
# 6️⃣  Execução local (Render usa Gunicorn)
# ===========================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
