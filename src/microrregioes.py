import pandas as pd
import unicodedata
import os

municipios_sao_jose_rio_preto = [
    # Microrregião de Jales
    "Aparecida d'Oeste", "Aspásia", "Dirce Reis", "Dolcinópolis", "Jales",
    "Marinópolis", "Mesópolis", "Nova Canaã Paulista", "Palmeira d'Oeste",
    "Paranapuã", "Pontalinda", "Populina", "Rubineia", "Santa Albertina",
    "Santa Clara d'Oeste", "Santa Fé do Sul", "Santa Rita d'Oeste",
    "Santa Salete", "Santana da Ponte Pensa", "São Francisco", "Três Fronteiras",
    "Urânia", "Vitória Brasil",

    # Microrregião de Fernandópolis
    "Estrela d'Oeste", "Fernandópolis", "Guarani d'Oeste", "Indiaporã",
    "Macedônia", "Meridiano", "Mira Estrela", "Ouroeste", "Pedranópolis",
    "São João das Duas Pontes", "Turmalina",

    # Microrregião de Votuporanga
    "Álvares Florence", "Américo de Campos", "Cardoso", "Cosmorama",
    "Parisi", "Pontes Gestal", "Riolândia", "Valentim Gentil", "Votuporanga",

    # Microrregião de São José do Rio Preto
    "Adolfo", "Altair", "Bady Bassitt", "Bálsamo", "Cedral", "Guapiaçu",
    "Guaraci", "Ibirá", "Icém", "Ipiguá", "Jaci", "José Bonifácio", "Mendonça",
    "Mirassol", "Mirassolândia", "Nova Aliança", "Nova Granada", "Olímpia",
    "Onda Verde", "Orindiúva", "Palestina", "Paulo de Faria", "Planalto",
    "Potirendaba", "São José do Rio Preto", "Tanabi", "Ubarana", "Uchoa", "Zacarias",

    # Microrregião de Catanduva
    "Ariranha", "Cajobi", "Catanduva", "Catiguá", "Elisiário", "Embaúba",
    "Novais", "Palmares Paulista", "Paraíso", "Pindorama", "Santa Adélia",
    "Severínia", "Tabapuã",

    # Microrregião de Auriflama
    "Auriflama", "Floreal", "Gastão Vidigal", "General Salgado", "Guzolândia",
    "Magda", "Nova Castilho", "Nova Luzitânia", "São João de Iracema",

    # Microrregião de Nhandeara
    "Macaubal", "Monções", "Monte Aprazível", "Neves Paulista", "Nhandeara",
    "Nipoã", "Poloni", "Sebastianópolis do Sul", "União Paulista",

    # Microrregião de Novo Horizonte
    "Irapuã", "Itajobi", "Marapoama", "Novo Horizonte", "Sales", "Urupês"
]

municipios_ribeirao_preto = [
    # Microrregião de Barretos
    "Barretos", "Colina", "Colômbia",
    
    # Microrregião de São Joaquim da Barra
    "Guaíra", "Ipuã", "Jaborandi", "Miguelópolis", "Morro Agudo",
    "Nuporanga", "Orlândia", "Sales Oliveira", "São Joaquim da Barra",
    
    # Microrregião de Ituverava
    "Aramina", "Buritizal", "Guará", "Igarapava", "Ituverava",
    
    # Microrregião de Franca
    "Cristais Paulista", "Franca", "Itirapuã", "Jeriquara",
    "Patrocínio Paulista", "Pedregulho", "Restinga",
    "Ribeirão Corrente", "Rifaina", "São José da Bela Vista",
    
    # Microrregião de Jaboticabal
    "Bebedouro", "Cândido Rodrigues", "Fernando Prestes", "Guariba",
    "Jaboticabal", "Monte Alto", "Monte Azul Paulista", "Pirangi",
    "Pitangueiras", "Santa Ernestina", "Taiaçu", "Taiuva", "Taquaral",
    "Taquaritinga", "Terra Roxa", "Viradouro", "Vista Alegre do Alto",
    
    # Microrregião de Ribeirão Preto
    "Barrinha", "Brodowski", "Cravinhos", "Dumont", "Guatapará",
    "Jardinópolis", "Luís Antônio", "Pontal", "Pradópolis",
    "Ribeirão Preto", "Santa Rita do Passa Quatro", "Santa Rosa de Viterbo",
    "São Simão", "Serra Azul", "Serrana", "Sertãozinho",
    
    # Microrregião de Batatais
    "Altinópolis", "Batatais", "Cajuru", "Cássia dos Coqueiros",
    "Santa Cruz da Esperança", "Santo Antônio da Alegria"
]

municipios_aracatuba = [
    # Microrregião de Andradina
    "Andradina", "Castilho", "Guaraçaí", "Ilha Solteira", "Itapura",
    "Mirandópolis", "Murutinga do Sul", "Nova Independência", 
    "Pereira Barreto", "Sud Mennucci", "Suzanápolis",
    
    # Microrregião de Araçatuba
    "Araçatuba", "Bento de Abreu", "Guararapes", "Lavínia",
    "Rubiácea", "Santo Antônio do Aracanguá", "Valparaíso",
    
    # Microrregião de Birigui
    "Alto Alegre", "Avanhandava", "Barbosa", "Bilac", "Birigui",
    "Braúna", "Brejo Alegre", "Buritama", "Clementina", "Coroados",
    "Gabriel Monteiro", "Glicério", "Lourdes", "Luiziânia",
    "Penápolis", "Piacatu", "Santópolis do Aguapeí", "Turiúba"
]

municipios_bauru = [
    # Microrregião de Lins
    "Cafelândia", "Getulina", "Guaiçara", "Guaimbê", "Júlio Mesquita",
    "Lins", "Promissão", "Sabino",

    # Microrregião de Bauru
    "Agudos", "Arealva", "Areiópolis", "Avaí", "Balbinos", "Bauru", "Borebi",
    "Cabrália Paulista", "Duartina", "Guarantã", "Iacanga", "Lençóis Paulista",
    "Lucianópolis", "Paulistânia", "Pirajuí", "Piratininga", "Pongaí",
    "Presidente Alves", "Reginópolis", "Ubirajara", "Uru",

    # Microrregião de Jaú
    "Bariri", "Barra Bonita", "Bocaina", "Boraceia", "Dois Córregos",
    "Igaraçu do Tietê", "Itaju", "Itapuí", "Jaú", "Macatuba", "Mineiros do Tietê",
    "Pederneiras",

    # Microrregião de Botucatu
    "Anhembi", "Bofete", "Botucatu", "Conchas", "Pardinho", "Pratânia", "São Manuel"
]

municipios_araraquara = [
    # Microrregião de Araraquara
    "Américo Brasiliense", "Araraquara", "Boa Esperança do Sul", "Borborema", "Dobrada",
    "Gavião Peixoto", "Ibitinga", "Itápolis", "Matão", "Motuca", "Nova Europa",
    "Rincão", "Santa Lúcia", "Tabatinga", "Trabiju",

    # Microrregião de São Carlos
    "Analândia", "Descalvado", "Dourado", "Ibaté", "Ribeirão Bonito", "São Carlos"
]

municipios_piracicaba = [
    # Microrregião de Rio Claro
    "Brotas", "Corumbataí", "Ipeúna", "Itirapina", "Rio Claro", "Torrinha",

    # Microrregião de Limeira
    "Araras", "Conchal", "Cordeirópolis", "Iracemápolis", "Leme", "Limeira",
    "Santa Cruz da Conceição", "Santa Gertrudes",

    # Microrregião de Piracicaba
    "Águas de São Pedro", "Capivari", "Charqueada", "Jumirim", "Mombuca",
    "Piracicaba", "Rafard", "Rio das Pedras", "Saltinho", "Santa Maria da Serra",
    "São Pedro", "Tietê"
]

municipios_campinas = [
    # Microrregião de Pirassununga
    "Aguaí", "Pirassununga", "Porto Ferreira", "Santa Cruz das Palmeiras",

    # Microrregião de São João da Boa Vista
    "Águas da Prata", "Caconde", "Casa Branca", "Divinolândia",
    "Espírito Santo do Pinhal", "Itobi", "Mococa", "Santo Antônio do Jardim",
    "São João da Boa Vista", "São José do Rio Pardo", "São Sebastião da Grama",
    "Tambaú", "Tapiratiba", "Vargem Grande do Sul",

    # Microrregião de Mogi Mirim
    "Artur Nogueira", "Engenheiro Coelho", "Estiva Gerbi", "Itapira",
    "Mogi Guaçu", "Mogi-Mirim", "Santo Antônio de Posse",

    # Microrregião de Campinas
    "Americana", "Campinas", "Cosmópolis", "Elias Fausto", "Holambra",
    "Hortolândia", "Indaiatuba", "Jaguariúna", "Monte Mor", "Nova Odessa",
    "Paulínia", "Pedreira", "Santa Bárbara d'Oeste", "Sumaré",
    "Valinhos", "Vinhedo",

    # Microrregião de Amparo
    "Águas de Lindóia", "Amparo", "Lindoia", "Monte Alegre do Sul",
    "Pedra Bela", "Pinhalzinho", "Serra Negra", "Socorro"
]

municipios_presidente_prudente = [
    # Microrregião de Dracena
    "Dracena", "Junqueirópolis", "Monte Castelo", "Nova Guataporanga",
    "Ouro Verde", "Panorama", "Paulicéia", "Santa Mercedes",
    "São João do Pau d'Alho", "Tupi Paulista",

    # Microrregião de Adamantina
    "Adamantina", "Flora Rica", "Flórida Paulista", "Inúbia Paulista",
    "Irapuru", "Lucélia", "Mariápolis", "Osvaldo Cruz", "Pacaembu",
    "Parapuã", "Pracinha", "Rinópolis", "Sagres", "Salmourão",

    # Microrregião de Presidente Prudente
    "Alfredo Marcondes", "Álvares Machado", "Anhumas", "Caiabu", "Caiuá",
    "Emilianópolis", "Estrela do Norte", "Euclides da Cunha Paulista",
    "Indiana", "João Ramalho", "Marabá Paulista", "Martinópolis",
    "Mirante do Paranapanema", "Narandiba", "Piquerobi", "Pirapozinho",
    "Presidente Bernardes", "Presidente Epitácio", "Presidente Prudente",
    "Presidente Venceslau", "Rancharia", "Regente Feijó",
    "Ribeirão dos Índios", "Rosana", "Sandovalina", "Santo Anastácio",
    "Santo Expedito", "Taciba", "Tarabai", "Teodoro Sampaio"
]

municipios_marilia_assis = [
    # Mesorregião de Marília
    # Microrregião de Tupã
    "Arco-Íris", "Bastos", "Herculândia", "Iacri", "Queiroz", "Quintana", "Tupã",

    # Microrregião de Marília
    "Álvaro de Carvalho", "Alvinlândia", "Echaporã", "Fernão", "Gália",
    "Garça", "Lupércio", "Marília", "Ocauçu", "Oriente", "Oscar Bressane",
    "Pompeia", "Vera Cruz",

    # Mesorregião de Assis
    # Microrregião de Assis
    "Assis", "Borá", "Campos Novos Paulista", "Cândido Mota", "Cruzália",
    "Florínia", "Ibirarema", "Iepê", "Lutécia", "Maracaí", "Nantes",
    "Palmital", "Paraguaçu Paulista", "Pedrinhas Paulista", "Platina",
    "Quatá", "Tarumã",

    # Microrregião de Ourinhos
    "Bernardino de Campos", "Canitar", "Chavantes", "Espírito Santo do Turvo",
    "Fartura", "Ipaussu", "Manduri", "Óleo", "Ourinhos", "Piraju",
    "Ribeirão do Sul", "Salto Grande", "Santa Cruz do Rio Pardo",
    "São Pedro do Turvo", "Sarutaiá", "Taguaí", "Tejupá", "Timburi"
]

municipios_sorocaba = [
    # Mesorregião de Itapetininga
    # Microrregião de Avaré
    "Águas de Santa Bárbara", "Arandu", "Avaré", "Cerqueira César", "Iaras",
    "Itaí", "Itatinga", "Paranapanema",

    # Microrregião de Itapeva
    "Barão de Antonina", "Bom Sucesso de Itararé", "Buri", "Coronel Macedo",
    "Itaberá", "Itapeva", "Itaporanga", "Itararé", "Nova Campina", 
    "Riversul", "Taquarituba", "Taquarivaí",

    # Microrregião de Itapetininga
    "Alambari", "Angatuba", "Campina do Monte Alegre", "Guareí", "Itapetininga",

    # Microrregião de Tatuí
    "Boituva", "Cerquilho", "Cesário Lange", "Laranjal Paulista",
    "Pereiras", "Porangaba", "Quadra", "Tatuí", "Torre de Pedra",

    # Microrregião de Capão Bonito
    "Apiaí", "Barra do Chapéu", "Capão Bonito", "Guapiara", "Iporanga", 
    "Itaóca", "Itapirapuã Paulista", "Ribeira", "Ribeirão Branco", "Ribeirão Grande",

    # Mesorregião Macro Metropolitana Paulista
    # Microrregião de Piedade
    "Ibiúna", "Piedade", "Pilar do Sul", "São Miguel Arcanjo", "Tapiraí",

    # Microrregião de Sorocaba
    "Alumínio", "Araçariguama", "Araçoiaba da Serra", "Cabreúva", "Capela do Alto",
    "Iperó", "Itu", "Mairinque", "Porto Feliz", "Salto", "Salto de Pirapora",
    "São Roque", "Sarapuí", "Sorocaba", "Votorantim",

    # Mesorregião do Litoral Sul Paulista
    # Microrregião de Registro
    "Barra do Turvo", "Cajati", "Cananéia", "Eldorado", "Iguape", "Ilha Comprida",
    "Jacupiranga", "Juquiá", "Miracatu", "Pariquera-Açu", "Registro", "Sete Barras"
]

municipios_sao_jose_dos_campos = [
    # Mesorregião do Vale do Paraíba Paulista

    # Microrregião de Campos do Jordão
    "Campos do Jordão", "Monteiro Lobato", "Santo Antônio do Pinhal",

    # Microrregião de São José dos Campos
    "São Bento do Sapucaí", "Caçapava", "Igaratá", "Jacareí", 
    "Pindamonhangaba", "Santa Branca", "São José dos Campos", "Taubaté",

    # Microrregião de Guaratinguetá
    "Tremembé", "Aparecida", "Cachoeira Paulista", "Canas", "Cruzeiro", 
    "Guaratinguetá", "Lavrinhas", "Lorena", "Piquete", "Potim", "Queluz",

    # Microrregião de Bananal
    "Roseira", "Arapeí", "Areias", "Bananal", "São José do Barreiro", "Silveiras",

    # Microrregião de Paraibuna/Paraitinga
    "Cunha", "Jambeiro", "Lagoinha", "Natividade da Serra", "Paraibuna", 
    "Redenção da Serra", "São Luís do Paraitinga",

    # Microrregião de Caraguatatuba
    "Caraguatatuba", "Ilhabela", "São Sebastião", "Ubatuba",
    
    # Mesorregião do Litoral Sul Paulista

    # Microrregião de Registro
    "Barra do Turvo", "Cajati", "Cananéia", "Eldorado", "Iguape", 
    "Ilha Comprida", "Jacupiranga", "Juquiá", "Miracatu", "Pariquera-Açu", "Registro",

    # Microrregião de Itanhaém
    "Sete Barras", "Itanhaém", "Itariri", "Mongaguá", "Pedro de Toledo", "Peruíbe"
]

municipios_sao_paulo = [
    # Mesorregião Metropolitana de São Paulo
    # Microrregião de Osasco
    "Barueri", "Cajamar", "Carapicuíba", "Itapevi", "Jandira", "Osasco", 
    "Pirapora do Bom Jesus", "Santana de Parnaíba",

    # Microrregião de Franco da Rocha
    "Caieiras", "Francisco Morato", "Franco da Rocha",

    # Microrregião de Guarulhos
    "Arujá", "Guarulhos", 

    # Microrregião de Itapecerica da Serra
    "Cotia", "Embu", "Embu-Guaçu", "Itapecerica da Serra", 
    "Juquitiba", "São Lourenço da Serra", "Taboão da Serra",

    # Microrregião de São Paulo
    "Vargem Grande Paulista", "Diadema", "Mauá", "Ribeirão Pires", 
    "Rio Grande da Serra", "Santo André", "São Bernardo do Campo", 
    "São Caetano do Sul", "São Paulo",

    # Microrregião de Mogi das Cruzes
    "Biritiba-Mirim", "Ferraz de Vasconcelos", "Guararema", "Itaquaquecetuba", 
    "Mogi das Cruzes", "Poá", "Salesópolis", "Suzano",

    # Microrregião de Santos
    "Bertioga", "Cubatão", "Guarujá", "Praia Grande", "Santos", "São Vicente"
]

# Contando o total de municípios
listas_municipios = [
    municipios_sao_jose_rio_preto, municipios_ribeirao_preto, municipios_aracatuba,
    municipios_bauru, municipios_araraquara, municipios_piracicaba, municipios_campinas,
    municipios_presidente_prudente, municipios_marilia_assis, municipios_sorocaba, 
    municipios_sao_jose_dos_campos, municipios_sao_paulo
]
print(sum(len(lista) for lista in listas_municipios))

# Caminho base para os arquivos CSV
base_path = os.path.dirname(os.path.abspath(__file__))

caminho_mun = os.path.join(base_path, 'tabelas-relacionais', 'df_mun.csv')
if os.path.exists(caminho_mun):
    df_mun = pd.read_csv(caminho_mun)

print(f"Total de municípios no DataFrame: {df_mun['NO_MUN_MIN'].nunique()}")


# Função para normalizar os nomes (remove acentos e coloca tudo em minúsculas)
def normalizar_nome(nome):
    if not isinstance(nome, str):  # Verifica se é uma string
        return nome  # Se não for, retorna o valor original
    nome = nome.strip()  # Remove espaços extras
    nome = nome.lower()  # Coloca tudo em minúsculas
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')  # Remove acentos e caracteres especiais
    return nome

# Suponha que você tenha a lista de municípios e o DataFrame com as colunas dos municípios
todos_municipios = sum(listas_municipios, [])  # Concatenando todas as listas de municípios

# Normalizando os dados da lista
df_lista_municipios = pd.DataFrame([normalizar_nome(mun) for mun in todos_municipios], columns=["municipio"])

# Normalizando os dados do DataFrame
df_mun['NO_MUN_MIN_NORMALIZADO'] = df_mun['NO_MUN_MIN'].apply(normalizar_nome)

# Verificando quais municípios da lista não estão no DataFrame
faltando = df_lista_municipios[~df_lista_municipios["municipio"].isin(df_mun['NO_MUN_MIN_NORMALIZADO'])]

# Verificando quais municípios do DataFrame não estão na lista
extra_na_lista = df_mun[~df_mun['NO_MUN_MIN_NORMALIZADO'].isin(df_lista_municipios['municipio'])]

# Exibindo os resultados
from IPython.display import display

display('municípios da lista não estão no DataFrame:')
display(faltando["municipio"])

display('municípios do DataFrame não estão na lista:')
display(extra_na_lista["NO_MUN_MIN"])

# 18 + 639 = 657
