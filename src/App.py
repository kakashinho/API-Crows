#--------------------------- Imports ----------------------
import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort
from gerar_graficos import balanca_comercial,ranking_municipios,funil_por_produto  # Função que gera o HTML do gráfico

#----------------- Criação da Aplicação Flask -------------
app = Flask(__name__,
            template_folder=os.path.join(os.getcwd(), 'templates'),
            static_folder=os.path.join(os.getcwd(), 'static'))

#---------------------- Página Inicial --------------------
@app.route('/')
def home():
    return render_template('home.html')

#---------------------- Página Feedback --------------------
@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

caminhos = []

#---------------------- Página Gráficos --------------------
@app.route('/graficos', methods=['GET', 'POST'])
def graficos():
    mostrar_grafico = False

    #Limpa os caminhos antes de gerar novos gráficos
    caminhos.clear()

#------------ Se o usuário enviou o formulário--------------
    if request.method == 'POST':
        # Recupera os índices (0 a 74)
        index_inicial = int(request.form['data_inicial'])
        index_final = int(request.form['data_final'])

        # Cria a lista de meses possíveis
        meses = pd.date_range(start='2019-01', end='2025-03', freq='MS').strftime('%Y-%m').tolist()       

        # Converte os índices para datas reais
        data_inicial = meses[index_inicial]
        data_final = meses[index_final]

        # Converte para int se quiser usar como ano
        ano_inicial = int(data_inicial[:4])
        ano_final = int(data_final[:4])

        #pegando o filtro do front
        tipo = request.form['exp-imp']
        metrica = request.form['metrica']

        # Converte para datetime se precisar
        data_inicial_dt = pd.to_datetime(data_inicial)
        data_final_dt = pd.to_datetime(data_final)
        
        # Caminho para o CSV de municípios
        base_path = os.path.dirname(os.path.abspath(__file__))
        caminho_mun = os.path.join(base_path, 'tabelas-relacionais', 'df_mun.csv')
        df_mun = pd.read_csv(caminho_mun) if os.path.exists(caminho_mun) else pd.DataFrame()
        caminho_sh4 = os.path.join(base_path, 'tabelas-relacionais', 'df_sh4.csv')
        df_sh4 = pd.read_csv(caminho_sh4) if os.path.exists(caminho_sh4) else pd.DataFrame()

        #Função para carregar dados por ano
        def carregar_dados_dataframe(ano, tipo):
            caminho = os.path.join(base_path, 'arquivos-brutos-csv', 'exportacoes' if tipo == 'exp' else 'importacoes', f'df_{tipo}_{ano}.csv')
            return pd.read_csv(caminho) if os.path.exists(caminho) else pd.DataFrame()

        #Concatena dados de vários anos
        df_completo_exp, df_completo_imp = pd.DataFrame(), pd.DataFrame()
        for ano in range(ano_final, ano_inicial - 1, -1):
            df_completo_exp = pd.concat([df_completo_exp, carregar_dados_dataframe(ano, 'exp')], ignore_index=True)
            df_completo_imp = pd.concat([df_completo_imp, carregar_dados_dataframe(ano, 'imp')], ignore_index=True)
        
        data_inicial = f'{data_inicial}-01'
        data_final = f'{data_final}-01'

        # Converte as datas selecionadas também
        data_inicial_dt = pd.to_datetime(data_inicial)
        data_final_dt = pd.to_datetime(data_final)

        # Filtrar os dados com base no intervalo de datas
        df_filtrado_exp, df_filtrado_imp = pd.DataFrame(), pd.DataFrame()
        df_filtrado_exp = df_completo_exp[(df_completo_exp['DATA'] >= data_inicial) & (df_completo_exp['DATA'] <= data_final)]
        df_filtrado_imp = df_completo_imp[(df_completo_imp['DATA'] >= data_inicial) & (df_completo_imp['DATA'] <= data_final)]

        #Se dados existem, gera os gráficos
        if not df_completo_exp.empty and not df_completo_imp.empty:
            caminhos.append(balanca_comercial(df_completo_exp, df_completo_imp, df_mun,''))
            caminhos.append(funil_por_produto(df_completo_exp, df_sh4, tipo, metrica,''))
            caminhos.append(ranking_municipios(df_mun,df_completo_exp,df_completo_imp,tipo,metrica,''))
            mostrar_grafico = True

    #Renderiza a página de gráficos
    return render_template('graficos.html', mostrar_grafico=mostrar_grafico)

#------ Rotas para exibir os arquivos HTML dos gráficos ----
@app.route('/grafico_primeiro')
def grafico_primeiro():
    if len(caminhos) < 1 or not os.path.exists(caminhos[0]):
        return abort(404, description="Gráfico não encontrado.")
    pasta, nome_arquivo = os.path.split(caminhos[0])
    return send_from_directory(pasta, nome_arquivo)

@app.route('/grafico_segundo')
def grafico_segundo():
    if len(caminhos) < 2 or not os.path.exists(caminhos[1]):
        return abort(404, description="Gráfico não encontrado.")
    pasta, nome_arquivo = os.path.split(caminhos[1])
    return send_from_directory(pasta, nome_arquivo)

@app.route('/grafico_terceiro')
def grafico_terceiro():
    if len(caminhos) < 3 or not os.path.exists(caminhos[2]):
        return abort(404, description="Gráfico não encontrado.")
    pasta, nome_arquivo = os.path.split(caminhos[2])
    return send_from_directory(pasta, nome_arquivo)


#----------------- Inicia o servidor Flask ---------------
#Roda a aplicação localmente com debug=True (útil durante o desenvolvimento).
if __name__ == '__main__':
    app.run(debug=True)


