"""Plano Mestre de Produção, o MPS (RF07).

O MPS diz quantos produtos acabados (PA) o cliente (demanda externa) 
quer em cada semana.
A partir disso, o MRP calcula tudo o que precisa produzir e comprar.
"""

from itens import escolher_item
from persistencia import salvar_dados
from utils import ler_inteiro, linha, titulo

SEMANAS = 8  # o horizonte do planejamento


def listar_mps(dados):
    #faz uma mini tabebla de mps
    titulo("PLANO MESTRE DE PRODUÇÃO (demanda por semana)")
    cabecalho = f"{'Item':<8}"
    for semana in range(1, SEMANAS + 1):
        cabecalho += f"{'S' + str(semana):>6}"
    print(cabecalho)
    linha()

    for codigo in sorted(dados["itens"]):
        if dados["itens"][codigo]["tipo"] != "PA":
            continue
        demanda = dados["mps"].get(codigo, [0] * SEMANAS)
        texto = f"{codigo:<8}"
        for quantidade in demanda:
            texto += f"{quantidade:>6}"
        print(texto)


def cadastrar_mps(dados):
    # Cadastra (ou altera) a demanda das 8 semanas de um produto acabado.
    # ENTER mantém o valor que já estava.
    titulo("CADASTRAR / ALTERAR MPS")
    codigo = escolher_item(dados, "Código do produto acabado: ")
    if codigo is None:
        return
    if dados["itens"][codigo]["tipo"] != "PA":
        print("ERRO: o MPS é só para produto acabado (PA).")
        return

    atual = dados["mps"].get(codigo, [0] * SEMANAS)
    print(f"Demanda de {codigo} - {dados['itens'][codigo]['descricao']}")
    print("ENTER mantém o valor atual.")

    nova = []
    for semana in range(1, SEMANAS + 1):
        quantidade = ler_inteiro(f"  Semana {semana} [{atual[semana - 1]}]: ",
                                 minimo=0, padrao=atual[semana - 1])
        nova.append(quantidade)

    dados["mps"][codigo] = nova
    salvar_dados(dados, "mps")
    print("MPS salvo! Rode o MRP de novo para atualizar as ordens.")