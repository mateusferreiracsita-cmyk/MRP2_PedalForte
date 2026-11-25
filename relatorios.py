"""Exportação de relatórios em CSV (RF14).

Os arquivos vão para a pasta exportacoes/. Usamos ponto e vírgula e
vírgula decimal, que é o jeito que o Excel em português abre sem bagunça.
"""

import csv
from pathlib import Path

from utils import formatar_numero, titulo

PASTA_EXPORTACAO = Path(__file__).parent / "exportacoes"


def gravar_csv(nome_arquivo, cabecalho, linhas):
    PASTA_EXPORTACAO.mkdir(exist_ok=True)
    caminho = PASTA_EXPORTACAO / nome_arquivo
    # utf-8-sig deixa o Excel reconhecer os acentos
    with open(caminho, "w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow(cabecalho)
        escritor.writerows(linhas)
    return caminho


def exportar_posicao_estoque(dados):
    linhas = []
    for codigo in sorted(dados["itens"]):
        item = dados["itens"][codigo]
        saldo = dados["estoque"].get(codigo, 0)
        if saldo < item["estoque_seguranca"]:
            situacao = "ABAIXO DA SEGURANÇA"
        else:
            situacao = "OK"
        linhas.append([codigo, item["descricao"], item["tipo"],
                       item["unidade"], formatar_numero(saldo),
                       formatar_numero(item["estoque_seguranca"]),
                       situacao])
    cabecalho = ["Código", "Descrição", "Tipo", "Unidade", "Saldo",
                 "Estoque de segurança", "Situação"]
    return gravar_csv("posicao_estoque.csv", cabecalho, linhas)


def exportar_ordens(dados):
    linhas = []
    for ordem in dados["ordens"]:
        descricao = dados["itens"][ordem["item"]]["descricao"]
        status = ordem["status"]
        if status == "PLANEJADA" and ordem.get("atrasada"):
            status = "ATRASADA"
        linhas.append([ordem["numero"], ordem["tipo"], ordem["item"],
                       descricao, formatar_numero(ordem["quantidade"]),
                       ordem["semana_liberacao"], ordem["semana_entrega"],
                       status])
    cabecalho = ["Ordem", "Tipo", "Item", "Descrição", "Quantidade",
                 "Semana de liberação", "Semana de entrega", "Status"]
    return gravar_csv("ordens.csv", cabecalho, linhas)


def exportar_csv(dados):
    # Exporta a posição de estoque e a lista de ordens.
    titulo("EXPORTAR RELATÓRIOS (CSV)")
    caminho_estoque = exportar_posicao_estoque(dados)
    caminho_ordens = exportar_ordens(dados)
    print(f"Posição de estoque: {caminho_estoque}")
    print(f"Lista de ordens:    {caminho_ordens}")
    if not dados["ordens"]:
        print("(Ainda não há ordens: execute o MRP para gerá-las.)")