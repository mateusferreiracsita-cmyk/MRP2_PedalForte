"""Gráficos de gestão com matplotlib (RF16).

Cada gráfico aparece na tela e também é salvo em PNG na pasta
graficos_saida.
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from capacidade import calcular_carga, ler_codigo_centro
from itens import escolher_item
from mps import SEMANAS
from utils import titulo

PASTA_GRAFICOS = Path(__file__).parent / "graficos_saida"


def salvar_e_mostrar(figura, nome_arquivo):
    PASTA_GRAFICOS.mkdir(exist_ok=True)
    caminho = PASTA_GRAFICOS / nome_arquivo
    figura.savefig(caminho, dpi=120, bbox_inches="tight")
    print(f"Gráfico salvo em: {caminho}")
    plt.show()
    plt.close(figura)


def grafico_posicao_estoque(dados):
    # Saldo atual x estoque de segurança de cada item (barras).
    titulo("GRÁFICO: POSIÇÃO DE ESTOQUE")
    codigos = sorted(dados["itens"])
    if not codigos:
        print("Nenhum item cadastrado.")
        return

    saldos = []
    segurancas = []
    for codigo in codigos:
        saldos.append(dados["estoque"].get(codigo, 0))
        segurancas.append(dados["itens"][codigo]["estoque_seguranca"])

    # duas barras por item: uma ao lado da outra
    largura = 0.4
    esquerda = []
    direita = []
    for posicao in range(len(codigos)):
        esquerda.append(posicao - largura / 2)
        direita.append(posicao + largura / 2)

    figura, eixo = plt.subplots(figsize=(11, 5))
    eixo.bar(esquerda, saldos, largura, label="Saldo atual")
    eixo.bar(direita, segurancas, largura, label="Estoque de segurança")
    eixo.set_xticks(range(len(codigos)))
    eixo.set_xticklabels(codigos, rotation=45)
    eixo.set_yscale("symlog", linthresh=10)
    # escala "symlog" para os itens pequenos não sumirem ao lado dos grandes
    eixo.set_ylabel("Quantidade (escala logarítmica)")
    eixo.set_title("Posição de estoque: saldo atual x estoque de segurança")
    eixo.legend()
    salvar_e_mostrar(figura, "posicao_estoque.png")


def grafico_estoque_projetado(dados):
    """Estoque projetado de um item nas 8 semanas, com a linha do
    estoque de segurança."""
    titulo("GRÁFICO: ESTOQUE PROJETADO")
    if not dados["mrp"]:
        print("O MRP ainda não foi executado. Use a opção 4 do menu.")
        return
    codigo = escolher_item(dados, "Código do item: ")
    if codigo is None:
        return
    registro = dados["mrp"]["registros"].get(codigo)
    if registro is None:
        print(f"{codigo} não tem registro. Rode o MRP de novo.")
        return

    item = dados["itens"][codigo]
    semanas = list(range(1, SEMANAS + 1))

    figura, eixo = plt.subplots(figsize=(9, 5))
    eixo.plot(semanas, registro["ep"], marker="o", label="Estoque projetado")
    eixo.axhline(item["estoque_seguranca"], color="red", linestyle="--",
                 label="Estoque de segurança")
    eixo.set_xticks(semanas)
    eixo.set_xlabel("Semana")
    eixo.set_ylabel(f"Quantidade ({item['unidade']})")
    eixo.set_title(f"Estoque projetado - {codigo} {item['descricao']}")
    eixo.legend()
    salvar_e_mostrar(figura, f"estoque_projetado_{codigo}.png")


def grafico_ordens_por_semana(dados):
    """Ordens de produção e de compra por semana de entrega, empilhadas.
    Contamos ordens, porque somar peças com metros e
    litros não faria sentido."""
    titulo("GRÁFICO: ORDENS POR SEMANA DE ENTREGA")
    ops = [0] * SEMANAS
    ocs = [0] * SEMANAS
    for ordem in dados["ordens"]:
        if ordem["status"] == "ENCERRADA":
            continue
        semana = ordem["semana_entrega"]
        if 1 <= semana <= SEMANAS:
            if ordem["tipo"] == "OP":
                ops[semana - 1] += 1
            else:
                ocs[semana - 1] += 1
    if sum(ops) + sum(ocs) == 0:
        print("Não há ordens em aberto. Execute o MRP antes (opção 4).")
        return

    semanas = list(range(1, SEMANAS + 1))
    figura, eixo = plt.subplots(figsize=(9, 5))
    eixo.bar(semanas, ops, label="OP (produção)")
    eixo.bar(semanas, ocs, bottom=ops, label="OC (compra)")
    eixo.set_xticks(semanas)
    eixo.yaxis.set_major_locator(MaxNLocator(integer=True))
    eixo.set_xlabel("Semana de entrega")
    eixo.set_ylabel("Quantidade de ordens")
    eixo.set_title("Ordens em aberto por semana de entrega")
    eixo.legend()
    salvar_e_mostrar(figura, "ordens_por_semana.png")


def grafico_carga_capacidade(dados):
    # Carga x capacidade de um centro, destacando a sobrecarga.
    titulo("GRÁFICO: CARGA x CAPACIDADE")
    if not dados["centros"]:
        print("Nenhum centro cadastrado ainda.")
        return
    codigo = ler_codigo_centro("Código do centro (ex.: CT-01): ")
    if codigo not in dados["centros"]:
        print(f"ERRO: o centro {codigo} não está cadastrado.")
        return

    centro = dados["centros"][codigo]
    capacidade = centro["capacidade_horas_semana"]
    cargas, _ = calcular_carga(dados)

    # duas séries: as semanas normais e as semanas em sobrecarga (vermelho)
    normais = [0] * SEMANAS
    sobrecarregadas = [0] * SEMANAS
    for i in range(SEMANAS):
        if cargas[codigo][i] > capacidade:
            sobrecarregadas[i] = cargas[codigo][i]
        else:
            normais[i] = cargas[codigo][i]

    semanas = list(range(1, SEMANAS + 1))
    figura, eixo = plt.subplots(figsize=(9, 5))
    eixo.bar(semanas, normais, color="tab:blue", label="Dentro da capacidade")
    eixo.bar(semanas, sobrecarregadas, color="tab:red", label="Sobrecarga")
    eixo.axhline(capacidade, color="black", linestyle="--",
                 label="Capacidade")
    eixo.set_xticks(semanas)
    eixo.set_xlabel("Semana")
    eixo.set_ylabel("Horas")
    eixo.set_title(f"Carga x capacidade - {codigo} {centro['descricao']}")
    eixo.legend()
    salvar_e_mostrar(figura, f"carga_capacidade_{codigo}.png")
    