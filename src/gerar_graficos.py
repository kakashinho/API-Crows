import os
import pandas as pd
import plotly.express as px

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

# ------------------------- Método que faz o Gráfico de Balança Comercial --------------------------------------------
# Função principal da balança comercial
def balanca_comercial(df_exp, df_imp, df_mun):
    df_exp = adicionar_ano(df_exp)
    df_imp = adicionar_ano(df_imp)

    # Agrupamento
    exp_anos = agrupar_df(df_exp, ['CO_MUN', 'ANO'], 'VL_FOB', 'sum')
    exp_anos.rename(columns={'VL_FOB': 'EXPORTACAO'}, inplace=True)

    imp_anos = agrupar_df(df_imp, ['CO_MUN', 'ANO'], 'VL_FOB', 'sum')
    imp_anos.rename(columns={'VL_FOB': 'IMPORTACAO'}, inplace=True)

    # Mescla exportação e importação
    balanca = mesclar_df(exp_anos, imp_anos, ['CO_MUN', 'ANO'], how='outer').fillna(0)

    # Calcula a balança
    balanca = calcular_diferenca(balanca, 'EXPORTACAO', 'IMPORTACAO', 'BALANCA')

    # Adiciona o nome dos municípios
    balanca = mesclar_df(balanca, df_mun[['CO_MUN', 'NO_MUN_MIN']], ['CO_MUN'])

    # Top cidades
    top_cidades = selecionar_top_cidades(balanca, 'BALANCA', n=5)

    # Paleta
    paleta_de_cores = px.colors.qualitative.Set1

    # Gráfico
    fig = px.line(
        top_cidades,
        x='ANO',
        y='BALANCA',
        color='NO_MUN_MIN',
        markers=True,
        title='Balança Comercial por Município (Exportação - Importação)',
        labels={'NO_MUN_MIN': 'Município', 'BALANCA': 'Balança Comercial (US$)'},
        line_shape='linear',
        hover_data={'NO_MUN_MIN': True, 'BALANCA': ':.2f'},
        color_discrete_sequence=paleta_de_cores,
    )

    # Anotações
    for trace in fig.data:
        for x, y in zip(trace['x'], trace['y']):
            if y >= 1e9:
                label = f'R$ {y / 1e9:.1f}B'
            elif y >= 1e6:
                label = f'R$ {y / 1e6:.1f}M'
            else:
                label = f'R$ {y:.2f}'
            fig.add_annotation(
                x=x, y=y,
                text=label,
                showarrow=True,
                arrowhead=2,
                ax=0, ay=-15,
                font=dict(size=10, color='black'),
                bgcolor='white',
                borderpad=2,
                bordercolor='black',
                borderwidth=1,
                opacity=0.8
            )

    # Layout
    fig.update_layout(
        title={'text': 'Balança Comercial por Município (Exportação - Importação)', 'x': 0.5, 'xanchor': 'center'},
        xaxis_title='Ano',
        yaxis_title='Balança Comercial (R$)',
        legend_title='Município',
        font=dict(family='Arial', size=12),
        hoverlabel=dict(bgcolor="white", font_size=13, font_family="Rockwell"),
        plot_bgcolor='white',
        margin=dict(l=60, r=60, t=100, b=60),
        showlegend=True,
    )

    # Eixos
    fig.update_xaxes(tickmode='linear', dtick=1)
    fig.update_yaxes(tickprefix="R$ ", tickformat=",.0s", ticksuffix="B")

    # Linha de base
    fig.add_shape(
        type="line",
        x0=top_cidades['ANO'].min(), x1=top_cidades['ANO'].max(),
        y0=0, y1=0,
        line=dict(color="black", width=2, dash="dashdot"),
    )

    # Salvar HTML
    pasta_graficos = 'graficos-dinamicos'
    os.makedirs(pasta_graficos, exist_ok=True)
    caminho_arquivo = os.path.join(pasta_graficos, 'balanca_comercial.html')
    fig.write_html(caminho_arquivo)

    return fig
