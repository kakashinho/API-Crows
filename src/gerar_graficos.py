import os
import pandas as pd
import plotly.express as px


from plotly.subplots import make_subplots
import plotly.graph_objects as go

# ------------------------- Funções --------------------------------------------
# Função adiciona coluna de ano
def adicionar_ano(df):
    df['DATA'] = pd.to_datetime(df['DATA'])
    df['ANO'] = df['DATA'].dt.year
    return df

# Função agrupa por colunas com operação de soma ou média
def agrupar_df(df, colunas, coluna_valor, operacao='sum'):
    if operacao == 'sum':
        return df.groupby(colunas)[coluna_valor].sum().reset_index()
    elif operacao == 'mean':
        return df.groupby(colunas)[coluna_valor].mean().reset_index()

# Função Mescla dois DataFrames
def mesclar_df(df1, df2, colunas, how='left'):
    return pd.merge(df1, df2, on=colunas, how=how)

# Cria uma nova coluna a partir da diferença de outras duas
def calcular_diferenca(df, col1, col2, nova_coluna):
    df[nova_coluna] = df[col1] - df[col2]
    return df

# Seleciona top N cidades com maior valor em uma coluna
def selecionar_top_cidades(df, coluna_valor, n=5):
    top = (
        df.groupby('NO_MUN_MIN')[coluna_valor]
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .index
    )
    return df[df['NO_MUN_MIN'].isin(top)]

# Padroniza adição de ano e mês no df
def adicionar_mes_ano(df):
    df['DATA'] = pd.to_datetime(df['DATA'])
    df['ANO'] = df['DATA'].dt.year
    df['MES'] = df['DATA'].dt.month
    df['ANO_MES'] = df['DATA'].dt.to_period('M').astype(str)
    return df

def quebrar_texto(texto, largura=30):
    return '<br>'.join([texto[i:i+largura] for i in range(0, len(texto), largura)])

# ------------------------- Método que faz o Gráfico de Balança Comercial -------------------------------------------
# Função principal da balança comercial
def balanca_comercial(df_exp, df_imp, df_mun, retorno):
    df_exp = adicionar_mes_ano(df_exp)
    df_imp = adicionar_mes_ano(df_imp)

    # Verfica o periodo está dentre um ano
    coluna = 'ANO'
    qtd_exp, qtd_imp = df_exp['ANO'].nunique(), df_imp['ANO'].nunique()
    if qtd_exp == 1 and qtd_imp == 1:
        coluna = 'MES'

    # Agrupamento
    exp_anos = agrupar_df(df_exp, ['CO_MUN', coluna], 'VL_FOB', 'sum')
    exp_anos.rename(columns={'VL_FOB': 'EXPORTACAO'}, inplace=True)

    imp_anos = agrupar_df(df_imp, ['CO_MUN', coluna], 'VL_FOB', 'sum')
    imp_anos.rename(columns={'VL_FOB': 'IMPORTACAO'}, inplace=True)

    # Mescla exportação e importação
    balanca = mesclar_df(exp_anos, imp_anos, ['CO_MUN', coluna], how='outer').fillna(0)

    # Calcula a balança
    balanca = calcular_diferenca(balanca, 'EXPORTACAO', 'IMPORTACAO', 'BALANCA')

    # Adiciona o nome dos municípios
    balanca = mesclar_df(balanca, df_mun[['CO_MUN', 'NO_MUN_MIN']], ['CO_MUN'])

    # Top cidades
    top_cidades = selecionar_top_cidades(balanca, 'BALANCA', n=5)

    # Paleta
    paleta_de_cores = [
        "#003d80",   # azul bem escuro
        "#0059b3",  # azul escuro
        "#0073e6",  # azul intenso
        "#3399ff",  # azul
        "#66b2ff",  # azul médio
        "#99ccff",  # azul claro
        "#cce5ff"  # azul bem claro  
    ]

    # Gráfico
    fig = px.line(
        top_cidades,
        x=coluna,
        y='BALANCA',
        color='NO_MUN_MIN',
        markers=True,
        title='Balança Comercial por Município (Exportação - Importação)',
        labels={'NO_MUN_MIN': 'Município', 'BALANCA': 'Balança Comercial (US$)'},
        line_shape='linear',
        hover_data={'NO_MUN_MIN': True, 'BALANCA': ':.2f'},
        color_discrete_sequence=paleta_de_cores
    )

    # Se for gráfico por mês, ajustar eixo X com os nomes corretos
    if coluna == 'MES':
        meses_nomes = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        fig.update_xaxes(
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=meses_nomes
        )

    # Anotações nos pontos
    for trace in fig.data:
        textos = []
        for y in trace['y']:
            if y >= 1e9:
                textos.append(f'US$ {y / 1e9:.1f}B')
            elif y >= 1e6:
                textos.append(f'US$ {y / 1e6:.1f}M')
            elif abs(y) >= 1e9:
                textos.append(f'US$ {"-" if y < 0 else ""}{abs(y) / 1e9:.1f}B')
            elif abs(y) >= 1e6:
                textos.append(f'US$ {"-" if y < 0 else ""}{abs(y) / 1e6:.1f}M')
            else:
                textos.append(f'US$ {y:,.2f}')
            
        # Atribui os textos ao trace para que apareçam como labels
        trace.text = textos
        trace.textposition = 'top center'
        trace.mode = 'lines+markers+text'
        trace.textfont = dict(size=10, color='black', family='Arial')
        trace.hovertemplate = (
        '<b>%{text}</b><br>' +
        'Ano/Mês: %{x}<br>' +
        'Valor: US$ %{y:,.2f}<extra></extra>'
        )
        trace.text = textos

    # Layout geral
    fig.update_layout(
        title={'text': 'Balança Comercial por Município (Exportação - Importação)', 'x': 0.5, 'xanchor': 'center'},
        xaxis_title='Mês' if coluna == 'MES' else 'Ano',
        yaxis_title='Balança Comercial (US$)',
        legend_title='Município',
        font=dict(family='Arial', size=12),
        hoverlabel=dict(bgcolor="white", font_size=13, font_family="Rockwell"),
        plot_bgcolor='white',
        margin=dict(l=60, r=60, t=100, b=60),
        showlegend=True,
    )

    # Grade de fundo com linhas cinza claro
    fig.update_xaxes(
        showgrid=True,
        gridcolor='#eeeeee',
        gridwidth=1
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor='#eeeeee',
        gridwidth=1
    )

    # Linha de base
    fig.add_shape(
        type="line",
        x0=top_cidades[coluna].min(), x1=top_cidades[coluna].max(),
        y0=0, y1=0,
        line=dict(color="black", width=2, dash="dashdot"),
    )
    if retorno == 'fig': return fig

    # Salvar HTML
    pasta_graficos = 'graficos-dinamicos'
    os.makedirs(pasta_graficos, exist_ok=True)
    caminho_arquivo = os.path.join(pasta_graficos, 'balanca_comercial.html')
    fig.write_html(caminho_arquivo)

    return caminho_arquivo


# ------------------------- Método que faz o Gráfico de Todas as Cargas --------------------------------------------

# Função principal da balança comercial por produto
def funil_por_produto(df, df_sh4, tipo, metrica, retorno):

    # Agrupa por produto (SH4), somando ou tirando média de acordo com a coluna
    if metrica == 'VL_FOB':
        df_total = agrupar_df(df, ['SH4'], metrica, 'sum')
    elif metrica == 'VALOR AGREGADO':
        df_total = agrupar_df(df, ['SH4'], metrica, 'mean')
    elif metrica == 'KG_LIQUIDO':
        df_total = agrupar_df(df, ['SH4'], metrica, 'sum')

    # Ordena pelo metrica (maior saldo)
    df_total = df_total.sort_values(by=f'{metrica}', ascending=False)

    # Garante que SH4 tenha um único produto associado
    df_sh4_resumo = df_sh4[['SH4', 'PRODUTO']].drop_duplicates(subset='SH4')

    # Mescla com o total de cargas
    df_total = mesclar_df(df_total, df_sh4_resumo, ['SH4'], how='left')

    # Agrupa por SH4 e PRODUTO para evitar duplicação de barras
    df_total = df_total.groupby(['SH4', 'PRODUTO'], as_index=False)[metrica].sum()

    # Cria nome de produto limitado apenas para o eixo Y
    df_total['PRODUTO_LIMITADO'] = df_total['PRODUTO'].str.slice(0, 20) + '...'

    # Seleciona top 20 produtos
    df_total = df_total.sort_values(by=metrica, ascending=False).head(20)

    # Agrupa novamente por PRODUTO_LIMITADO para evitar erro de barras duplicadas
    df_total = df_total.groupby('PRODUTO_LIMITADO', as_index=False).agg({
        metrica: 'sum',
        'PRODUTO': 'first'  # Pega um nome completo representativo
    })

    # Reordena para visualização crescente
    df_total = df_total.sort_values(by=metrica, ascending=True)

    # Paleta de cores
    paleta_de_cores = [
        "#3399ff",  # azul
        "#66b2ff",  # azul médio
        "#99ccff",  # azul claro
        "#cce5ff",  # azul bem claro  
        "#003d80",   # azul bem escuro
        "#0059b3",  # azul escuro
        "#0073e6"  # azul intenso
    ]

    df_total['hover_text'] = (
    "Descrição: " + df_total['PRODUTO'].apply(lambda x: quebrar_texto(x, 60))
    )

    tipo_lower = tipo.lower()
    # Gera gráfico de funil com nome completo no hover
    fig = px.funnel(
        df_total,
        y='PRODUTO_LIMITADO',
        x=f'{metrica}',
        title=f'TOP 20 Produtos em {tipo_lower} por {metrica} dos municípios',
        labels={f'{metrica}': f'{tipo} (US$)', 'PRODUTO_LIMITADO': 'Produto'},
        color='PRODUTO_LIMITADO',
        hover_name='hover_text',  # Mostra nome completo no tooltip
        hover_data={
            'PRODUTO_LIMITADO': False,  # Remove o truncado do hover
            f'{metrica}': True
        },
        color_discrete_sequence=paleta_de_cores
    )

    # Layout
    fig.update_layout(
        title_x=0.5,
        font=dict(family='Arial', size=12),
        # hoverlabel=dict(bgcolor="white", font_size=13, font_family="Rockwell"),
        # plot_bgcolor='white',
        margin=dict(l=60, r=60, t=100, b=60),
        showlegend=False,
    )

    # Formatação dos valores dentro do funil
    fig.update_traces(texttemplate='US$ %{x:,.0f}', textposition='inside')

    # Retorno em figura ou como caminho do HTML
    if retorno == 'fig':
        return fig

    pasta_graficos = 'graficos-dinamicos'
    os.makedirs(pasta_graficos, exist_ok=True)
    caminho_arquivo = os.path.join(pasta_graficos, 'funil_por_produto.html')
    fig.write_html(caminho_arquivo)

    return caminho_arquivo

# ------------------------- Método que faz o Gráfico de Ranking de Municípios --------------------------------------------

def ranking_municipios(df_mun,df_exp,df_imp, tipo,metrica,df_prod,retorno):
    
    if(tipo == 'Exportacões'):
        df = adicionar_ano(df_exp)

    elif(tipo == 'Importacões'):
        df = adicionar_ano(df_imp)
    else:
        raise ValueError(f"Tipo inválido: {tipo}")
    
    # Garante que SH4 tenha um único produto associado
    df_sh4_resumo = df_prod[['SH4', 'PRODUTO']].drop_duplicates(subset='SH4')
    df_comp = mesclar_df(df,df_sh4_resumo, ['SH4'])

    # agrupamento
    if(metrica == 'VALOR AGREGADO'):
        tipo_anos = agrupar_df(df_comp,['CO_MUN'], 'VALOR AGREGADO', 'mean')
        tipo_anos.rename(columns={'VALOR AGREGADO':'VALOR_AGREGADO'}, inplace=True)
        metrica = 'VALOR_AGREGADO'
        # Adiciona o nome dos municípios
        municipios = mesclar_df(tipo_anos, df_mun[['CO_MUN', 'NO_MUN_MIN']], ['CO_MUN'])
        municipios_top10 = municipios.sort_values(by="VALOR_AGREGADO", ascending=False).head(10)  

        cargas = df_comp.groupby(['CO_MUN', 'SH4','PRODUTO'],as_index=False)['VALOR AGREGADO'].mean()

        cargas_top5 = cargas.sort_values(['CO_MUN','VALOR AGREGADO'], ascending=False)
        cargas_top5 = cargas_top5.groupby('CO_MUN').head(5)

        cargas_top5['PRODUTO_LIMITADO'] = cargas_top5['PRODUTO'].str.slice(0, 30) + '...'

        cargas_top5['descricao'] = cargas_top5['SH4'].astype(str) + ' - ' + cargas_top5['PRODUTO_LIMITADO'] + ' - (Valor Agregado da Carga:' + cargas_top5['VALOR AGREGADO'].round(2).astype(str) + ')'
        carga_agrupada = cargas_top5.groupby('CO_MUN')['descricao'].apply(lambda x: '<br>'.join(x)).reset_index()

        
        municipios_total = pd.merge(municipios_top10, carga_agrupada, on='CO_MUN', how='left')

    elif(metrica == 'VL_FOB'):
        tipo_anos = agrupar_df(df_comp,['CO_MUN'], 'VL_FOB', 'sum')

        # Adiciona o nome dos municípios
        municipios = mesclar_df(tipo_anos, df_mun[['CO_MUN', 'NO_MUN_MIN']], ['CO_MUN'])
        municipios_top10 = municipios.sort_values(by="VL_FOB", ascending=False).head(10)  

        cargas = df_comp.groupby(['CO_MUN', 'SH4','PRODUTO'],as_index=False)['VL_FOB'].sum()
        cargas.rename(columns={'VL_FOB': 'VL FOB'}, inplace=True)

        cargas_top5 = cargas.sort_values(['CO_MUN','VL FOB'], ascending=False)
        cargas_top5 = cargas_top5.groupby('CO_MUN').head(5)

        cargas_top5['PRODUTO_LIMITADO'] = cargas_top5['PRODUTO'].str.slice(0, 30) + '...'

        cargas_top5['descricao'] = cargas_top5['SH4'].astype(str) + ' - ' + cargas_top5['PRODUTO_LIMITADO'] + ' - (Valor Fob:' + cargas_top5['VL FOB'].round(2).astype(str) + ')'
        carga_agrupada = cargas_top5.groupby('CO_MUN')['descricao'].apply(lambda x: '<br>'.join(x)).reset_index()

        
        municipios_total = pd.merge(municipios_top10, carga_agrupada, on='CO_MUN', how='left')

    elif(metrica == 'KG_LIQUIDO'):
        tipo_anos = agrupar_df(df_comp,['CO_MUN'], 'KG_LIQUIDO', 'sum')

        # Adiciona o nome dos municípios
        municipios = mesclar_df(tipo_anos, df_mun[['CO_MUN', 'NO_MUN_MIN']], ['CO_MUN'])
        municipios_top10 = municipios.sort_values(by="KG_LIQUIDO", ascending=False).head(10)  

        cargas = df_comp.groupby(['CO_MUN', 'SH4','PRODUTO'],as_index=False)['KG_LIQUIDO'].sum()
        cargas.rename(columns={'KG_LIQUIDO': 'KG LIQUIDO'}, inplace=True)

        cargas_top5 = cargas.sort_values(['CO_MUN','KG LIQUIDO'], ascending=False)
        cargas_top5 = cargas_top5.groupby('CO_MUN').head(5)

        cargas_top5['PRODUTO_LIMITADO'] = cargas_top5['PRODUTO'].str.slice(0, 30) + '...'

        cargas_top5['descricao'] = cargas_top5['SH4'].astype(str) + ' - ' + cargas_top5['PRODUTO_LIMITADO'] + ' - (Valor Por KG LIQUIDO:' + cargas_top5['KG LIQUIDO'].round(2).astype(str) + ')'
        carga_agrupada = cargas_top5.groupby('CO_MUN')['descricao'].apply(lambda x: '<br>'.join(x)).reset_index() 

        
        municipios_total = pd.merge(municipios_top10, carga_agrupada, on='CO_MUN', how='left')


    # Paleta
    paleta_de_cores = [
        "#26517f",
        "#003d80",   # azul bem escuro
        "#0059b3",  # azul escuro
        "#0073e6",  # azul intenso
        "#3399ff",  # azul
        "#00bdf2",
        "#71b2e1",
        "#66b2ff",  # azul médio
        "#99ccff",  # azul claro
        "#cce5ff"  # azul bem claro  
    ]

    # Gráfico
    fig = px.bar(
        municipios_total,
        x='NO_MUN_MIN',
        y=f'{metrica}',
        color='NO_MUN_MIN',
        title=f'Top 10 municípios por {metrica} de {tipo}',
        labels={'NO_MUN_MIN': 'Município'},
        hover_data = {'CO_MUN': False,f'{metrica}':True,'NO_MUN_MIN':True, 'descricao':True},
        color_discrete_sequence=paleta_de_cores,
    )
    if retorno == 'fig': return fig

    # Salvar HTML
    pasta_graficos = 'graficos-dinamicos'
    os.makedirs(pasta_graficos, exist_ok=True)
    caminho_arquivo = os.path.join(pasta_graficos, 'ranking_municipios.html')
    fig.write_html(caminho_arquivo)

    return caminho_arquivo
    


def ranking_municipios_cargas(df_mun,df_exp,df_imp, tipo,metrica,df_prod,retorno):
    
    if(tipo == 'Exportacões'):
        df = adicionar_ano(df_exp)

    elif(tipo == 'Importacões'):
        df = adicionar_ano(df_imp)
    else:
        raise ValueError(f"Tipo inválido: {tipo}")
    
    # Garante que SH4 tenha um único produto associado
    df_sh4_resumo = df_prod[['SH4', 'PRODUTO']].drop_duplicates(subset='SH4')
    df_comp = mesclar_df(df,df_sh4_resumo, ['SH4'])

    # agrupamento
    if(metrica == 'VALOR AGREGADO'):
        # nessa estou separando por cargas
        tipo_ano = agrupar_df(df_comp,['CO_MUN'], 'VALOR AGREGADO', 'mean')
        tipo_ano.rename(columns={'VALOR AGREGADO':'VALOR_AGREGADO'}, inplace=True)
        metrica = 'VALOR_AGREGADO'
        # Adiciona o nome dos municípios
        municipios = mesclar_df(tipo_ano, df_mun[['CO_MUN', 'NO_MUN_MIN']], ['CO_MUN'])
        municipios_10 = municipios.sort_values(by="VALOR_AGREGADO", ascending=False).head(10)  

        carga = df_comp.groupby(['CO_MUN', 'SH4','PRODUTO'],as_index=False)['VALOR AGREGADO'].mean()

        cargas = carga.sort_values(['CO_MUN','VALOR AGREGADO'], ascending=False)
        # cargas= cargas.groupby('CO_MUN')

        cargas['PRODUTO_LIMITADO'] = cargas['PRODUTO'].str.lower().str.slice(0, 10) + '...'

        cargas['descricao'] = cargas['SH4'].astype(str) + ' - ' + cargas['PRODUTO_LIMITADO'] + ' - (Valor :' + cargas['VALOR AGREGADO'].round(2).astype(str) + ')'
        # carga_agrupada = cargas.groupby('CO_MUN')['descricao'].apply(lambda x: '<br>'.join(x)).reset_index()

        
        municipios_total = pd.merge(municipios_10, cargas, on='CO_MUN', how='left')

    elif(metrica == 'VL_FOB'):
        # nesse está o hover com 30 cargas
        tipo_anos = agrupar_df(df_comp,['CO_MUN'], 'VL_FOB', 'sum')

        # Adiciona o nome dos municípios
        municipios = mesclar_df(tipo_anos, df_mun[['CO_MUN', 'NO_MUN_MIN']], ['CO_MUN'])
        municipios_top10 = municipios.sort_values(by="VL_FOB", ascending=False).head(10)  

        cargas = df_comp.groupby(['CO_MUN', 'SH4','PRODUTO'],as_index=False)['VL_FOB'].sum()
        cargas.rename(columns={'VL_FOB': 'VL FOB'}, inplace=True)

        cargas_top5 = cargas.sort_values(['CO_MUN','VL FOB'], ascending=False)
        cargas_top5 = cargas_top5.groupby('CO_MUN').head(30)

        cargas_top5['PRODUTO_LIMITADO'] = cargas_top5['PRODUTO'].str.slice(0, 30) + '...'

        cargas_top5['descricao'] = cargas_top5['SH4'].astype(str) + ' - ' + cargas_top5['PRODUTO_LIMITADO'] + ' - (Valor Fob:' + cargas_top5['VL FOB'].round(2).astype(str) + ')'
        carga_agrupada = cargas_top5.groupby('CO_MUN')['descricao'].apply(lambda x: '<br>'.join(x)).reset_index()

        
        municipios_total = pd.merge(municipios_top10, carga_agrupada, on='CO_MUN', how='left')

    elif(metrica == 'KG_LIQUIDO'):
        # neste está igual o grafico só de ranking municipios, não tinha mexido nesse
        tipo_anos = agrupar_df(df_comp,['CO_MUN'], 'KG_LIQUIDO', 'sum')

        # Adiciona o nome dos municípios
        municipios = mesclar_df(tipo_anos, df_mun[['CO_MUN', 'NO_MUN_MIN']], ['CO_MUN'])
        municipios_top10 = municipios.sort_values(by="KG_LIQUIDO", ascending=False).head(10)  

        cargas = df_comp.groupby(['CO_MUN', 'SH4','PRODUTO'],as_index=False)['KG_LIQUIDO'].sum()
        cargas.rename(columns={'KG_LIQUIDO': 'KG LIQUIDO'}, inplace=True)

        cargas_top5 = cargas.sort_values(['CO_MUN','KG LIQUIDO'], ascending=False)
        cargas_top5 = cargas_top5.groupby('CO_MUN').head(5)

        cargas_top5['PRODUTO_LIMITADO'] = cargas_top5['PRODUTO'].str.slice(0, 30) + '...'

        cargas_top5['descricao'] = cargas_top5['SH4'].astype(str) + ' - ' + cargas_top5['PRODUTO_LIMITADO'] + ' - (Valor Por KG LIQUIDO:' + cargas_top5['KG LIQUIDO'].round(2).astype(str) + ')'
        carga_agrupada = cargas_top5.groupby('CO_MUN')['descricao'].apply(lambda x: '<br>'.join(x)).reset_index() 

        
        municipios_total = pd.merge(municipios_top10, carga_agrupada, on='CO_MUN', how='left')


    # Paleta
    paleta_de_cores = [
        "#26517f",
        "#003d80",   # azul bem escuro
        "#0059b3",  # azul escuro
        "#0073e6",  # azul intenso
        "#3399ff",  # azul
        "#00bdf2",
        "#71b2e1",
        "#66b2ff",  # azul médio
        "#99ccff",  # azul claro
        "#cce5ff"  # azul bem claro  
    ]

    # Gráfico
    fig = px.bar(
        municipios_total,
        x='NO_MUN_MIN',
        y=f'{metrica}',
        color='descricao',
        title=f'Top 10 municípios por {metrica} de {tipo}',
        labels={'NO_MUN_MIN': 'Município'},
        hover_data = {'CO_MUN': False,f'{metrica}':True,'NO_MUN_MIN':True, 'descricao':True},
        color_discrete_sequence=paleta_de_cores,
    )


    # fig = make_subplots(
    #     rows = 10,
    #     cols = 1,
    #     subplot_titles = municipios_total["NO_MUN_MIN"].unique()
    # )

    # mun = municipios_total["NO_MUN_MIN"].unique()

    # for i in range(len(mun)):
    #     dados_mun = municipios_total[municipios_total['NO_MUN_MIN'] == mun[i]]
    #     dados_mun = dados_mun.sort_values(by=f'{metrica}', ascending=False)
    #     row = (i // 1) + 1
    #     col = (i % 1) + 1

    #     fig.add_trace(
    #         go.Funnel(
    #             y=dados_mun['descricao'],
    #             x=dados_mun[f'{metrica}'],
                
    #             name = mun[i]
    #         ),
    #         row = row,
    #         col = col
    #     )
    # fig.update_layout(
    #     title_text="Top cargas por Município (Gráfico de Funil)", 
    #     height=1200,
    #     funnelmode="stack",
        
    #     )
    
    if retorno == 'fig': return fig

    # Salvar HTML
    pasta_graficos = 'graficos-dinamicos'
    os.makedirs(pasta_graficos, exist_ok=True)
    caminho_arquivo = os.path.join(pasta_graficos, 'ranking_municipios_cargas.html')
    fig.write_html(caminho_arquivo)

    return caminho_arquivo
