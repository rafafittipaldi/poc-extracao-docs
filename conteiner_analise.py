import streamlit as st
import json

# Carregar dados JSON
def carregar_dados_json(caminho):
    print('comecei')
    with open(caminho, 'r', encoding='utf-8') as arquivo:
        dados = json.load(arquivo)
    return dados

# Função para criar um contêiner para cada documento
def criar_container(documento):
    # Extraindo as duas primeiras informações do documento
    primeiras_info = list(documento.items())[:2]
    # print(primeiras_info)

    # Criando o contêiner expansível
    with st.expander(f"{primeiras_info[0][0]}: {primeiras_info[0][1]}, {primeiras_info[1][0]}: {primeiras_info[1][1]}"):
        # Exibindo as informações restantes
        for chave, valor in documento.items():
            if chave not in [primeiras_info[0][0], primeiras_info[1][0]]:
                st.write(f"{chave}: {valor}")

# Caminho do arquivo JSON
caminho_json = 'c:\\projects\\gestao-de-conteudos-1\\poc-gestao-conteudo\\documentos.json'

# Carregando os dados
# dados_documentos = carregar_dados_json(caminho_json)
string_json = '{"documentos": [{"tipo": "RG", "numero": "49.151.623-4", "nome": "DANIELZ COELHO DA COSTA", "nome_pai": "EDIVALDO DA COSTA", "nome_mae": "ROSA COELHO DA COSTA", "naturalidade": "SÃO PAULO - SP", "data_nascimento": "19/DEZ/1980", "data_expedicao": "21/DEZ/2012", "cpf": "342.002.171-42"}, {"tipo": "CPF", "numero": "000.000.000-00", "nome": "NOME DA PESSOA", "data_nascimento": "01/01/1990", "data_inscricao": "01/2000"}]}'
dados_documentos = json.loads(string_json)
for doc in dados_documentos['documentos']:
    criar_container(doc)
    st.checkbox("Selecionar", key=doc['numero'])

print(dados_documentos)