# usar utf-8 para linguagem BR
"""Guarda e carrega os dados nos arquivos da pasta data/.

A ideia é simples: quando o sistema abre, carregar_dados() lê tudo e
devolve UM dicionário chamado "dados". Os outros módulos recebem esse
dicionário, mexem nele e chamam salvar_dados() para gravar no disco.
"""


import csv
import json
from pathlib import Path

# a pasta data/ fica ao lado deste arquivo, nao importa de onde rodamos
PASTA_DATA = Path(__file__).parent / "data"

#super importanta para a fluidez do programa ->
ARQUIVOS_JSON = {
    "itens": "itens.json",
    "estrutura": "estrutura.json",
    "estoque": "estoque.json",
    "centros": "centros.json",
    "roteiros": "roteiros.json",
    "mps": "mps.json",
    "ordens": "ordens.json",
    "mrp": "mrp.json",  # guarda o último cálculo do MRP
}

ARQUIVO_MOVIMENTOS = PASTA_DATA / "movimentos.csv"
CAMPOS_MOVIMENTO = ["data", "item", "tipo", "quantidade", "saldo",
                    "documento"]


def ler_json(nome_arquivo, valor_vazio):
    # lê arq Json
    caminho = PASTA_DATA / nome_arquivo
    if not caminho.exists():
        return valor_vazio  # return vazio caso nao exista o arquivo
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except json.JSONDecodeError as erro:
        raise ValueError(f"O arquivo {nome_arquivo} está com problema: "
                         f"{erro}") from erro


def gravar_json(nome_arquivo, conteudo):
    PASTA_DATA.mkdir(exist_ok=True)  # mkdir para abrir uma pasta data
    with open(PASTA_DATA / nome_arquivo, "w", encoding="utf-8") as arquivo:
        json.dump(conteudo, arquivo, ensure_ascii=False, indent=2)
        # dump para gravar conteudo em json, formatações dentro do ()


def para_numero(texto):
    # O CSV devolve tudo como texto, tem que voltar para número
    # Primeiro vira float, porque int("0.5") dá erro
    numero = float(texto)
    if numero.is_integer():
        return int(numero)
    return numero


def ler_movimentos():
    if not ARQUIVO_MOVIMENTOS.exists():
        return []
    movimentos = []
    with open(ARQUIVO_MOVIMENTOS, "r", encoding="utf-8",
              newline="") as arquivo:
        for movimento in csv.DictReader(arquivo):
            movimento["quantidade"] = para_numero(movimento["quantidade"])
            movimento["saldo"] = para_numero(movimento["saldo"])
            movimentos.append(movimento)
    return movimentos


def gravar_movimentos(movimentos):
    PASTA_DATA.mkdir(exist_ok=True)
    with open(ARQUIVO_MOVIMENTOS, "w", encoding="utf-8",
              newline="") as arquivo:
        # leitura formatado
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_MOVIMENTO)
        escritor.writeheader()
        escritor.writerows(movimentos)


def carregar_dados():
    # Lê todos os arquivos e monta o dicionário "dados".
    dados = {}
    for chave, arquivo in ARQUIVOS_JSON.items():
        # só as ordens são uma lista; o resto é dicionário
        if chave == "ordens":
            vazio = []
        else:
            vazio = {}
        dados[chave] = ler_json(arquivo, vazio)
    dados["movimentos"] = ler_movimentos()
    return dados


def salvar_dados(dados, *chaves):
    # se chaves nao tiver nada, grava os dados
    # se tiver algo, descobre o que é e grava no devido lugar
    if not chaves:
        chaves = list(ARQUIVOS_JSON) + ["movimentos"]
    for chave in chaves:
        if chave == "movimentos":
            gravar_movimentos(dados["movimentos"])
        else:
            gravar_json(ARQUIVOS_JSON[chave], dados[chave])