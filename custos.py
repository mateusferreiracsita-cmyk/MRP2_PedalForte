"""Custo padrão dos itens fabricados (RF13).

Custo padrão = materiais + mão de obra.
  - Matéria-prima: é o custo unitário cadastrado.
  - Item fabricado: soma (quantidade x custo de cada componente) e depois
    soma a mão de obra do roteiro (horas por unidade x custo-hora).
Como um PA tem SA dentro, e o SA tem MP dentro, a conta precisa descer
pela estrutura: por isso a função chama a si mesma (recursão).
"""

from utils import (codigo_valido, formatar_dinheiro, formatar_numero,
                   ler_texto, linha, titulo)


def custo_mao_de_obra(dados, codigo):
    # Horas por unidade x custo-hora do centro que fabrica o item.
    roteiro = dados["roteiros"].get(codigo)
    if roteiro is None:
        return 0
    centro = dados["centros"][roteiro["centro"]]
    return roteiro["tempo_unitario"] * centro["custo_hora"]


def custo_padrao(dados, codigo):
    # Calcula o custo padrão de uma unidade do item.
    item = dados["itens"][codigo]
    if item["tipo"] == "MP":
        return item["custo_unitario"]

    materiais = 0
    for componente in dados["estrutura"].get(codigo, []):
        #recursão: o custo do componente pode depender dos componentes dele
        custo_do_componente = custo_padrao(dados, componente["componente"])
        materiais += componente["quantidade"] * custo_do_componente
    return materiais + custo_mao_de_obra(dados, codigo)


def exibir_custo_padrao(dados):
    """Mostra o custo padrão dos itens fabricados e, se quiser, o
    detalhamento de um deles."""
    titulo("CUSTO PADRÃO DOS PRODUTOS")
    print(f"{'Item':<8}{'Descrição':<28}{'Custo padrão':>15}")
    linha()
    achou = False
    for codigo in sorted(dados["itens"]):
        item = dados["itens"][codigo]
        if item["tipo"] != "MP":
            achou = True
            print(f"{codigo:<8}{item['descricao']:<28}"
                  f"{formatar_dinheiro(custo_padrao(dados, codigo)):>15}")
    if not achou:
        print("Nenhum item fabricado cadastrado.")
        return

    codigo = ler_texto("\nCódigo para detalhar (ENTER para voltar): ",
                       padrao="").upper()
    if codigo == "":
        return
    if not codigo_valido(codigo) or codigo not in dados["itens"]:
        print(f"ERRO: o item {codigo} não está cadastrado.")
        return
    if dados["itens"][codigo]["tipo"] == "MP":
        print("Matéria-prima não tem custo padrão calculado: o custo "
              "é o cadastrado.")
        return
    detalhar_custo(dados, codigo)


def detalhar_custo(dados, codigo):
    #Imprime o custo do item componente por componente.
    item = dados["itens"][codigo]
    print(f"\nCUSTO PADRÃO - {codigo} {item['descricao']}")
    print(f"{'Item':<8}{'Descrição':<28}{'Qtde':>7}{'Custo un.':>14}"
          f"{'Total':>14}")
    linha()

    for componente in dados["estrutura"].get(codigo, []):
        filho = componente["componente"]
        custo_un = custo_padrao(dados, filho)
        total = componente["quantidade"] * custo_un
        print(f"{filho:<8}{dados['itens'][filho]['descricao']:<28}"
              f"{formatar_numero(componente['quantidade']):>7}"
              f"{formatar_dinheiro(custo_un):>14}"
              f"{formatar_dinheiro(total):>14}")

    roteiro = dados["roteiros"].get(codigo)
    if roteiro is None:
        print("(sem roteiro cadastrado: mão de obra não considerada)")
    else:
        centro = dados["centros"][roteiro["centro"]]
        mao_de_obra = custo_mao_de_obra(dados, codigo)
        print(f"{'Mão de obra ' + roteiro['centro']:<36}"
              f"{formatar_numero(roteiro['tempo_unitario']) + ' h':>7}"
              f"{formatar_dinheiro(centro['custo_hora']):>14}"
              f"{formatar_dinheiro(mao_de_obra):>14}")

    linha()
    total = custo_padrao(dados, codigo)
    print(f"CUSTO PADRÃO TOTAL {formatar_dinheiro(total)}")

    