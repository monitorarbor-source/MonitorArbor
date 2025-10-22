@app.route("/grafico")
def grafico():
    # Verifica se já existe CSV com dados
    if not os.path.exists(CSV_FILE):
        return "<h3 style='font-family:sans-serif;text-align:center;'>Nenhum dado recebido ainda.</h3>"

    # Lê dados do CSV
    df = pd.read_csv(CSV_FILE)

    # Converte para HTML com classes CSS personalizadas
    tabela_html = df.to_html(
        classes="tabela",
        index=False,
        justify="center",
        border=0
    )

    # HTML estilizado
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


