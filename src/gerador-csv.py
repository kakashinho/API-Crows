# imports, dados e dataframes
import pandas as pd

mun = 'https://balanca.economia.gov.br/balanca/bd/tabelas/UF_MUN.csv'
sh4 = 'https://balanca.economia.gov.br/balanca/bd/tabelas/NCM_SH.csv'
pais = 'https://balanca.economia.gov.br/balanca/bd/tabelas/PAIS.csv'

df_mun = pd.read_csv(mun, sep=";", encoding="latin1")
df_sh4 = pd.read_csv(sh4, sep=";", encoding="latin1")
df_pais = pd.read_csv(pais, sep=";", encoding="latin1")

# Limpando Colunas SH4:

# Renomear coluna para compatibilidade com a base de produtos
df_sh4 = df_sh4.rename(columns={"CO_SH4": "SH4", "NO_SH4_POR": "PRODUTO"})

# Selecionando as colunas SH4 e PRODUTO:
df_sh4_resumo = df_sh4[['SH4', 'PRODUTO']]

# Remover linhas duplicadas
df_sh4_resumo  = df_sh4_resumo.drop_duplicates().reset_index(drop=True)

# Salvando o DataFrame em um arquivo CSV
df_sh4_resumo.to_csv(f'./tabelas-relacionais//df_sh4.csv', index=False)


# Limpando Colunas Cidades:

# Renomear coluna para compatibilidade com a base de municípios
df_mun = df_mun.rename(columns={"CO_MUN_GEO": "CO_MUN"})

df_mun = df_mun[df_mun['SG_UF'] == 'SP']

# Remover as colunas que não sejam o Código e o Nome do Município em Minusculo:
df_mun_resumo = df_mun.drop( ['SG_UF','NO_MUN'], axis=1)

# Salvando o DataFrame em um arquivo CSV
df_mun_resumo.to_csv(f'./tabelas-relacionais//df_mun.csv', index=False)

# Limpando Colunas Países:

# Renomear coluna para compatibilidade com a base de produtos
df_pais = df_pais.rename(columns={"CO_PAIS_ISOA3": "SGL_PAIS"})

# Remover as colunas que não sejam o SH4 e o Produto:
df_pais_resumo = df_pais.drop( ['CO_PAIS_ISON3','NO_PAIS_ING','NO_PAIS_ESP'], axis=1)

# Salvando o DataFrame em um arquivo CSV
df_pais_resumo.to_csv(f'./tabelas-relacionais//df_pais.csv', index=False)

df_exp = pd.DataFrame()
urls_baixadas = []
for year in range(2019,2026):
    try:
        url = f'https://balanca.economia.gov.br/balanca/bd/comexstat-bd/mun/EXP_{year}_MUN.csv'
        df = pd.read_csv(url, sep=";", encoding="latin1")

        df = df[df['SG_UF_MUN'] == 'SP']
        df = df[df['KG_LIQUIDO'] > 0]
        df = df[df['VL_FOB'] > 0]
        df['VALOR AGREGADO'] = df['VL_FOB'] / df['KG_LIQUIDO']

        # Gerando uma nova coluna 'DATA' com o primeiro dia do mês
        df['DATA'] = pd.to_datetime(df['CO_ANO'].astype(str) + '-' + df['CO_MES'].astype(str) + '-01')
        df = df.drop( ['CO_ANO','CO_MES'], axis=1)

        # Especificando a nova ordem das colunas
        nova_ordem = ['DATA', 'SG_UF_MUN', 'CO_MUN','SH4','VL_FOB','KG_LIQUIDO','VALOR AGREGADO','CO_PAIS']

        # Reorganizando as colunas
        df_exp = df[nova_ordem]

        #Ordenand a coluna DATA do mais recente para o mais antigo (ordem decrescente):
        df_exp = df_exp.sort_values(by='DATA', ascending=False).reset_index(drop=True)

        # Salvando o DataFrame em um arquivo CSV
        df_exp.to_csv(f'./arquivos-brutos-csv/exportacoes//df_exp_{year}.csv', index=False)


        urls_baixadas.append(url)
    except Exception as Ex:
        print(f"Erro ao baixar {url}: {Ex}")



df_imp = pd.DataFrame()
urls_baixadas = []
for year in range(2019,2026):
    try:
        url = f'https://balanca.economia.gov.br/balanca/bd/comexstat-bd/mun/IMP_{year}_MUN.csv'
        df = pd.read_csv(url, sep=";", encoding="latin1")

        df = df[df['SG_UF_MUN'] == 'SP']
        df = df[df['KG_LIQUIDO'] > 0]
        df = df[df['VL_FOB'] > 0]
        df['VALOR AGREGADO'] = df['VL_FOB'] / df['KG_LIQUIDO']

        # Gerando uma nova coluna 'DATA' com o primeiro dia do mês
        df['DATA'] = pd.to_datetime(df['CO_ANO'].astype(str) + '-' + df['CO_MES'].astype(str) + '-01')
        df = df.drop( ['CO_ANO','CO_MES'], axis=1)
        
        # Especificando a nova ordem das colunas
        nova_ordem = ['DATA', 'SG_UF_MUN', 'CO_MUN','SH4','VL_FOB','KG_LIQUIDO','VALOR AGREGADO','CO_PAIS']

        # Reorganizando as colunas
        df_imp = df[nova_ordem]

        #Ordenand a coluna DATA do mais recente para o mais antigo (ordem decrescente):
        df_imp = df_imp.sort_values(by='DATA', ascending=False).reset_index(drop=True)

        # Salvando o DataFrame em um arquivo CSV
        df_imp.to_csv(f'./arquivos-brutos-csv/importacoes//df_imp_{year}.csv', index=False)


        urls_baixadas.append(url)
    except Exception as Ex:
        print(f"Erro ao baixar {url}: {Ex}")
