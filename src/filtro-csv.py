# Importa as bibliotecas necessárias: pandas para manipulação de dados e csv para controlar aspas ao salvar arquivos
import pandas as pd
import csv

# URLs dos arquivos CSV fornecidos pelo site do governo (dados de municípios, SH4 e países)
mun = 'https://balanca.economia.gov.br/balanca/bd/tabelas/UF_MUN.csv'
sh4 = 'https://balanca.economia.gov.br/balanca/bd/tabelas/NCM_SH.csv'
pais = 'https://balanca.economia.gov.br/balanca/bd/tabelas/PAIS.csv'

# Leitura dos arquivos CSV em DataFrames
# separador é ";" e o encoding "latin1" garante que acentos e caracteres especiais sejam lidos corretamente
df_mun = pd.read_csv(mun, sep=";", encoding="latin1")
df_sh4 = pd.read_csv(sh4, sep=";", encoding="latin1")
df_pais = pd.read_csv(pais, sep=";", encoding="latin1")


# ---------------------------------------------------------
# Geração do CSV de Municípios de SP
# ---------------------------------------------------------

# Filtra os dados para incluir apenas os municípios do estado de São Paulo
df_mun_resumo = df_mun[df_mun['SG_UF'] == 'SP']

# Cria uma nova coluna 'OPCOES_MUN' com a formatação "código - nome", linha por linha
df_mun_resumo['OPCOES_MUN'] = [f"{row['CO_MUN_GEO']} - {row['NO_MUN_MIN']}" for _, row in df_mun_resumo.iterrows()]

# Ordena os municípios pelo nome em ordem alfabética
df_mun_resumo = df_mun_resumo.sort_values(by='NO_MUN_MIN')

# Seleciona apenas a coluna 'OPCOES_MUN' para exportar
df_mun_resumo = df_mun_resumo['OPCOES_MUN']

# Salva o resultado em CSV com todas as células entre aspas
df_mun_resumo.to_csv('./opcoes-csv/df_mun.csv', index=False, quoting=csv.QUOTE_ALL)

# ---------------------------------------------------------
# Geração do CSV de Cargas (Produtos SH4)
# ---------------------------------------------------------

# Pega apenas as colunas essenciais: código SH4 e descrição do produto
df_sh4_resumo = df_sh4[['CO_SH4', 'NO_SH4_POR']]

# Remove linhas duplicadas e reseta o índice
df_sh4_resumo = df_sh4_resumo.drop_duplicates().reset_index(drop=True)

# Limita o texto do nome do produto a 40 caracteres e adiciona "..." para deixar mais legível em menus
df_sh4_resumo['PRODUTO_LIMITADO'] = df_sh4_resumo['NO_SH4_POR'].str.slice(0, 40) + '...'

# Cria a coluna formatada "SH4 - produto" para uso em filtros ou menus
df_sh4_resumo['OPCOES_CARGA'] = [f"{row['CO_SH4']} - {row['PRODUTO_LIMITADO']}" for _, row in df_sh4_resumo.iterrows()]

# Seleciona apenas a coluna formatada para exportação
df_sh4_resumo = df_sh4_resumo['OPCOES_CARGA']

# Salva como CSV com aspas em todos os campos
df_sh4_resumo.to_csv('./opcoes-csv/df_sh4.csv', index=False, quoting=csv.QUOTE_ALL)


# ---------------------------------------------------------
# Geração do CSV de Países
# ---------------------------------------------------------

# Ordena os países pelo nome em ordem alfabética
df_pais = df_pais.sort_values(by='CO_PAIS')

# Seleciona apenas essa nova coluna formatada para exportar
df_pais_resumo = df_pais['NO_PAIS']
#remover: "Não Definido" , "Sem informação", "Não Declarados"

# Salva como CSV com aspas em tudo
df_pais_resumo.to_csv('./opcoes-csv/df_pais.csv', index=False, quoting=csv.QUOTE_ALL)