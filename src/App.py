import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from gerar_graficos import balanca_comercial  # Função que gera o HTML do gráfico

app = Flask(__name__,
            template_folder=os.path.join(os.getcwd(), 'templates'),
            static_folder=os.path.join(os.getcwd(), 'static'))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/graficos', methods=['GET', 'POST'])
def graficos():
    mostrar_grafico = False

    if request.method == 'POST':
        data_inicial = request.form['data_inicial']
        data_final = request.form['data_final']
        ano_inicial = int(data_inicial[:4])
        ano_final = int(data_final[:4])

        base_path = os.path.dirname(os.path.abspath(__file__))
        caminho_mun = os.path.join(base_path, 'tabelas-relacionais', 'df_mun.csv')
        df_mun = pd.read_csv(caminho_mun) if os.path.exists(caminho_mun) else pd.DataFrame()

        def carregar_dados_dataframe(ano, tipo):
            caminho = os.path.join(base_path, 'arquivos-brutos-csv', 'exportacoes' if tipo == 'exp' else 'importacoes', f'df_{tipo}_{ano}.csv')
            return pd.read_csv(caminho) if os.path.exists(caminho) else pd.DataFrame()

        df_completo_exp, df_completo_imp = pd.DataFrame(), pd.DataFrame()
        for ano in range(ano_final, ano_inicial - 1, -1):
            df_completo_exp = pd.concat([df_completo_exp, carregar_dados_dataframe(ano, 'exp')], ignore_index=True)
            df_completo_imp = pd.concat([df_completo_imp, carregar_dados_dataframe(ano, 'imp')], ignore_index=True)

        if not df_completo_exp.empty and not df_completo_imp.empty:
            balanca_comercial(df_completo_exp, df_completo_imp, df_mun)
            mostrar_grafico = True

    return render_template('graficos.html', mostrar_grafico=mostrar_grafico)

@app.route('/grafico_resultado')
def grafico_resultado():
    caminho = os.path.join(os.getcwd(), 'graficos-dinamicos')  # ou use src/graficos-dinamicos se estiver dentro da pasta src
    return send_from_directory(caminho, 'balanca_comercial.html')

if __name__ == '__main__':
    app.run(debug=True)
