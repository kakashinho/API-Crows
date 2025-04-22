import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Layout largo para melhor visualização
st.set_page_config(layout="wide")

# Botão para resetar o app
if st.button('Resetar App'):
    st.session_state.clear()
    st.rerun()

# Caminho base para os arquivos CSV
base_path = os.path.dirname(os.path.abspath(__file__))

# ----------------------------
# Função para carregar tabelas relacionais
# ----------------------------
@st.cache_data
def carregar_dados():
    caminho_mun = os.path.join(base_path, 'tabelas-relacionais', 'df_mun.csv')
    caminho_sh4 = os.path.join(base_path, 'tabelas-relacionais', 'df_sh4.csv')
    caminho_pais = os.path.join(base_path, 'tabelas-relacionais', 'df_pais.csv')
    
    df_mun, df_sh4, df_pais = None, None, None

    if os.path.exists(caminho_mun):
        df_mun = pd.read_csv(caminho_mun)
    if os.path.exists(caminho_sh4):
        df_sh4 = pd.read_csv(caminho_sh4)
    if os.path.exists(caminho_pais):
        df_pais = pd.read_csv(caminho_pais)
    
    return df_mun, df_sh4, df_pais

df_mun, df_sh4, df_pais = carregar_dados()

# ----------------------------
# Criando DataFrame de regiões
# ----------------------------
cidades_txt = '''
Campos do Jordão
Monteiro Lobato
Santo Antônio do Pinhal
São Bento do Sapucaí
Caçapava
Igaratá
Jacareí
Pindamonhangaba
Santa Branca
São José dos Campos
Taubaté
Tremembé
Aparecida
Cachoeira Paulista
Canas
Cruzeiro
Guaratinguetá
Lavrinhas
Lorena
Piquete
Potim
Queluz
Roseira
Arapeí
Areias
Bananal
São José do Barreiro
Silveiras
Cunha
Jambeiro
Lagoinha
Natividade da Serra
Paraibuna
Redenção da Serra
São Luiz do Paraitinga
Caraguatatuba
Ilhabela
São Sebastião
Ubatuba
'''
#Está pulando São Luiz do Paraitinga 

lista_cidades = [cidade.strip() for cidade in cidades_txt.strip().split('\n')]
regioes = pd.DataFrame({'Cidades': lista_cidades, 'Regiao': 'São José dos Campos'})

# ----------------------------
# Seleção de período
# ----------------------------

# Obter o ano e o mês atual
ano_atual = pd.to_datetime('today').year
mes_atual = pd.to_datetime('today').month

# Adicionar widgets para selecionar ano e mês
ano_inicial = st.sidebar.slider("Ano inicial", min_value=2019, max_value=ano_atual, value=2019)
mes_inicial = st.sidebar.slider("Mês inicial", min_value=1, max_value=12, value=1)
ano_final = st.sidebar.slider("Ano final", min_value=2019, max_value=ano_atual, value=ano_atual)
mes_final = st.sidebar.slider("Mês final", min_value=1, max_value=12, value=mes_atual)

# ----------------------------
# Filtros do usuário
# ----------------------------
st.title("Tipos de Filtros")

# Inicializa variáveis para os filtros
regiao = None
cidade = None
carga = None

filtro = st.radio("Filtrar por:", ['Municípios SP', 'Microrregião', 'Portes Semelhantes', 'Filtro por Carga'])

if filtro == 'Microrregião':
    regiao = st.sidebar.selectbox("Região", ["", *regioes['Regiao'].unique()])

elif filtro == 'Portes Semelhantes':
    cidade = st.sidebar.selectbox("Cidade", ["", *df_mun['NO_MUN_MIN'].sort_values().unique()])

elif filtro == 'Filtro por Carga':
    df_sh4['PRODUTO_LIMITADO'] = df_sh4['PRODUTO'].str.slice(0, 50) + '...'
    opcoes_carga = [""] + [
        f"{row['SH4']} - {row['PRODUTO_LIMITADO']}" for _, row in df_sh4.iterrows()
    ]
    carga_str = st.sidebar.selectbox("Código SH4", opcoes_carga)
    if carga_str:
        carga = carga_str.split(" - ")[0]

# ----------------------------
# Carregar dados anuais
# ----------------------------
@st.cache_data
def carregar_dados_dataframe_exp(ano):
    caminho = os.path.join(base_path, 'arquivos-brutos-csv', 'exportacoes', f'df_exp_{ano}.csv')
    if os.path.exists(caminho):
        return pd.read_csv(caminho)
    return pd.DataFrame()

@st.cache_data
def carregar_dados_dataframe_imp(ano):
    caminho = os.path.join(base_path, 'arquivos-brutos-csv', 'importacoes', f'df_imp_{ano}.csv')
    if os.path.exists(caminho):
        return pd.read_csv(caminho)
    return pd.DataFrame()

# ----------------------------
# Botão "Filtrar"
# ----------------------------

if st.sidebar.button('Filtrar') or True:
    if ano_final < ano_inicial:
        st.sidebar.error("O ano final não pode ser anterior ao ano inicial!")
    else:
        # Carregar e juntar os dados por ano
        df_completo_exp = pd.DataFrame()
        df_completo_imp = pd.DataFrame()
        for ano in range(ano_final, ano_inicial - 1, -1):
            df_ano = carregar_dados_dataframe_exp(ano)
            df_completo_exp = pd.concat([df_completo_exp, df_ano], ignore_index=True)

            df_ano = carregar_dados_dataframe_imp(ano)
            df_completo_imp = pd.concat([df_completo_imp, df_ano], ignore_index=True)

        data_inicial = f'{ano_inicial}-{mes_inicial}-01'
        data_final = f'{ano_final}-{mes_final}-01'

        # Filtrar os dados com base no intervalo de datas
        df_completo_exp = df_completo_exp[(df_completo_exp['DATA'] >= data_inicial) & (df_completo_exp['DATA'] <= data_final)]
        df_completo_imp = df_completo_imp[(df_completo_imp['DATA'] >= data_inicial) & (df_completo_imp['DATA'] <= data_final)]

        # Inicializa os dois dataframes
        df_filtrado_exp = df_completo_exp.copy()
        df_filtrado_imp = df_completo_imp.copy()

        # -------------------- Filtro por Microrregião --------------------
        if regiao:
            st.subheader("Filtrados regiao")
            cidades_regiao = regioes[regioes['Regiao'] == regiao]['Cidades']
            cods_mun = df_mun[df_mun['NO_MUN_MIN'].isin(cidades_regiao)][['NO_MUN_MIN','CO_MUN']].reset_index(drop=True)

            df_filtrado_exp = df_filtrado_exp[df_filtrado_exp['CO_MUN'].isin(cods_mun['CO_MUN'])]
            df_filtrado_exp.reset_index(drop=True, inplace=True)

            df_filtrado_imp = df_filtrado_imp[df_filtrado_imp['CO_MUN'].isin(cods_mun['CO_MUN'])]
            df_filtrado_imp.reset_index(drop=True, inplace=True)


        # -------------------- Filtro por Cidade (Ranking de porte) --------------------
        elif cidade:
            st.subheader("Filtrados cidade")
            # Supondo que 'df_completo_exp' e 'df_completo_imp' já sejam seus dataframes de exportação e importação

            # Calcular o valor FOB total (exportações e importações)
            df_exp = df_completo_exp.groupby('CO_MUN')['VL_FOB'].sum().reset_index(name='EXPORTACAO')
            df_imp = df_completo_imp.groupby('CO_MUN')['VL_FOB'].sum().reset_index(name='IMPORTACAO')

            # Junta os dataframes de exportação e importação
            df_balanca = pd.merge(df_exp, df_imp, on='CO_MUN', how='outer').fillna(0)

            # Adiciona a coluna de "Força Comercial" (diferente entre exportações e importações)
            df_balanca['FORCA_COMERCIAL'] = df_balanca['EXPORTACAO'] - df_balanca['IMPORTACAO']

            # Ordena os municípios pela "força comercial"
            df_balanca = df_balanca.sort_values(by='FORCA_COMERCIAL', ascending=False).reset_index(drop=True)

            # Encontra o município desejado (cidade)
            cod_mun = df_mun.loc[df_mun['NO_MUN_MIN'] == cidade, 'CO_MUN'].values[0]

            # Encontrar a posição do município desejado na lista
            posicao = df_balanca[df_balanca['CO_MUN'] == cod_mun].index[0]

            # Definir o intervalo para pegar os municípios vizinhos
            start = max(posicao - 2, 0)
            end = min(posicao + 4, len(df_balanca))

            # Seleciona os códigos dos municípios vizinhos
            cods_vizinhos = df_balanca.iloc[start:end]['CO_MUN']

            # Filtra os dataframes de exportação e importação para esses municípios vizinhos
            df_filtrado_exp = df_completo_exp[df_completo_exp['CO_MUN'].isin(cods_vizinhos)].reset_index(drop=True)
            df_filtrado_imp = df_completo_imp[df_completo_imp['CO_MUN'].isin(cods_vizinhos)].reset_index(drop=True)


        # -------------------- Filtro por Carga (Produto SH4) --------------------
        elif carga:
            st.subheader("Filtrados carga")
            # Se for string tipo "1101 - CAFÉ"
            if isinstance(carga, str):
                carga = carga.split(" - ")[0].strip()

            # Agora transforma em inteiro (se possível)
            try:
                carga = int(carga)
            except ValueError:
                st.error("Erro ao interpretar o código SH4.")
                    
            df_filtrado_exp = df_completo_exp[df_completo_exp['SH4'] == carga]
            df_agrupado = df_filtrado_exp.groupby('CO_MUN')['VL_FOB'].sum().reset_index()
            df_agrupado = df_agrupado.sort_values(by='VL_FOB', ascending=False)

            cods_carga = df_agrupado['CO_MUN']

            df_filtrado_exp = df_filtrado_exp[df_filtrado_exp['CO_MUN'].isin(cods_carga)]
            df_filtrado_exp.reset_index(drop=True, inplace=True)

            df_filtrado_imp = df_completo_imp[df_completo_imp['CO_MUN'].isin(cods_carga)]
            df_filtrado_imp.reset_index(drop=True, inplace=True)

        # -------------------- Exibir resultado final -----------------------------
        st.subheader("Dados Filtrados")
        st.write(df_filtrado_exp)

        # -------------------- Geração do Gráfico ---------------------------------
        from gerar_graficos import balanca_comercial
        from gerar_graficos import funil_por_produto

        fig_1 = balanca_comercial(df_filtrado_exp, df_filtrado_imp, df_mun)
        informacao = 'Exportação'
        fig_2 = funil_por_produto(df_filtrado_exp, df_sh4, informacao, 'VALOR AGREGADO')
        fig_3 = funil_por_produto(df_filtrado_exp, df_sh4, informacao, 'VL_FOB')
        fig_4 = funil_por_produto(df_filtrado_exp, df_sh4, informacao, 'KG_LIQUIDO')
        informacao = 'Importação'
        fig_5 = funil_por_produto(df_filtrado_imp, df_sh4, informacao, 'VALOR AGREGADO')
        fig_6 = funil_por_produto(df_filtrado_imp, df_sh4, informacao, 'VL_FOB')
        fig_7 = funil_por_produto(df_filtrado_imp, df_sh4, informacao, 'KG_LIQUIDO')

        # Divisão de colunas no Streamlit
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        col5, col6 = st.columns(2)
        col7, col8 = st.columns(2)

        # Exibe o gráfico no Streamlit
        col1.plotly_chart(fig_1)
        col2.plotly_chart(fig_2)
        col3.plotly_chart(fig_3)
        col4.plotly_chart(fig_4)
        col5.plotly_chart(fig_5)
        col6.plotly_chart(fig_6)
        col7.plotly_chart(fig_7)

else:
    st.sidebar.write("Escolha os filtros e clique em 'Filtrar'")
