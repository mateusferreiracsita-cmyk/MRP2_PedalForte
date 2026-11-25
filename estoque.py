"""Estoque: movimentações, saldo e kardex/histórico (RF04, RF05, RN02 e RN10).

O saldo de cada item fica em dados["estoque"] e cada movimentação é
guardada em dados["movimentos"] (o kardex). Movimentação nunca é apagada
(RN10): se algo foi lançado errado, a correção é feita com um AJUSTE.
"""

from itens import escolher_item
from persistencia import salvar_dados
from utils import (data_hoje, formatar_numero, ler_data, ler_decimal,
                   ler_opcao, ler_texto, linha, titulo)


def com_sinal(valor):
    # Coloca + para quem entra e - para quem sai.
    texto = formatar_numero(valor)
    if valor > 0:
        return "+" + texto
    return texto


def registrar_movimento(dados, codigo, tipo, quantidade, documento,
                        data=None):
    """Registra uma movimentação e atualiza o saldo (RF04).

    - ENTRADA e SAIDA: a quantidade vem positiva (a saída desconta sozinha)
    - AJUSTE: a quantidade vem com sinal (+ aumenta, - diminui)

    - Se o saldo ficasse negativo, levanta ValueError (RN02).

    Esta função NÃO grava no disco: quem chamou decide a hora de salvar.
    Assim o apontamento de produção pode lançar vários movimentos e
    gravar tudo de uma vez só.
    """
    if data is None:
        data = data_hoje()

    saldo = dados["estoque"].get(codigo, 0)# se não existir retorna 0
    if tipo == "ENTRADA":
        variacao = quantidade
    elif tipo == "SAIDA":
        variacao = -quantidade
    else:
        variacao = quantidade

    novo_saldo = round(saldo + variacao, 6)
    # o round evita sobras de conta com decimais 
    if novo_saldo < 0:
        unidade = dados["itens"][codigo]["unidade"]
        raise ValueError(f"saldo insuficiente (saldo atual: "
                         f"{formatar_numero(saldo)} {unidade})")

    dados["estoque"][codigo] = novo_saldo
    dados["movimentos"].append({
        "data": data,
        "item": codigo,
        "tipo": tipo,
        "quantidade": variacao,
        "saldo": novo_saldo,
        "documento": documento,
    })


def avisar_estoque_baixo(dados, codigo):
    #Mostra um alerta se o saldo estiver abaixo do estoque de segurança.
    item = dados["itens"][codigo]
    saldo = dados["estoque"].get(codigo, 0)
    seguranca = item["estoque_seguranca"]
    if saldo < seguranca:
        print(f"ALERTA: saldo ({formatar_numero(saldo)} {item['unidade']}) "
              f"abaixo do estoque de segurança "
              f"({formatar_numero(seguranca)} {item['unidade']}).")


def movimentar_estoque(dados):
    #Tela de movimentação: entrada, saída ou ajuste.
    titulo("MOVIMENTAR ESTOQUE")
    codigo = escolher_item(dados, "Código do item: ")
    if codigo is None:
        return

    letra = ler_opcao("Tipo E - entrada"
                          " S - saída"
                          " A - ajuste: "
                          , ["E", "S", "A"])
    if letra == "E":
        tipo = "ENTRADA"
    elif letra == "S":
        tipo = "SAIDA"
    else:
        tipo = "AJUSTE"

    if tipo == "AJUSTE":
        quantidade = ler_decimal("Quantidade do ajuste "
                                 "(use - para diminuir): ")
        if quantidade == 0:
            print("ERRO: o ajuste não pode ser zero.")
            return
    else:
        quantidade = ler_decimal("Quantidade: ", minimo=0.001)

    data = ler_data("Data (dd/mm/aaaa, ENTER = hoje): ")
    documento = ler_texto("Documento/motivo (ex.: NF 4521, Inventário): ")

    try:
        registrar_movimento(dados, codigo, tipo, quantidade, documento, data)
    except ValueError as erro:
        print(f"ERRO: {erro}. Operação cancelada!")
        return

    salvar_dados(dados, "estoque", "movimentos")
    unidade = dados["itens"][codigo]["unidade"]
    print(f"Movimentação registrada! Novo saldo de {codigo}: "
          f"{formatar_numero(dados['estoque'][codigo])} {unidade}")
    avisar_estoque_baixo(dados, codigo)#verificação


def consultar_kardex(dados):
    #Mostra o histórico (kardex) e o saldo de um item (RF05).
    titulo("SALDO E KARDEX")
    codigo = escolher_item(dados, "Código do item: ")
    if codigo is None:
        return

    item = dados["itens"][codigo]
    print(f"\nKARDEX - {codigo} {item['descricao']} ({item['unidade']})")
    print(f"{'Data':<12}{'Tipo':<9}{'Qtde':>9}{'Saldo':>9}  Documento")
    linha()

    achou = False
    for movimento in dados["movimentos"]:#procura movimentos no histórico
        if movimento["item"] == codigo:
            achou = True
            print(f"{movimento['data']:<12}{movimento['tipo']:<9}"
                  f"{com_sinal(movimento['quantidade']):>9}"
                  f"{formatar_numero(movimento['saldo']):>9}"
                  f"  {movimento['documento']}")
    if not achou:
        print("Nenhuma movimentação registrada para este item!")

    saldo = dados["estoque"].get(codigo, 0)
    print(f"\nSaldo atual: {formatar_numero(saldo)} {item['unidade']}")
    avisar_estoque_baixo(dados, codigo)


def exibir_posicao_estoque(dados):
    # Mostra o saldo de todos os itens e quem está abaixo da segurança.
    titulo("POSIÇÃO DE ESTOQUE")
    print(f"{'Código':<8}{'Descrição':<28}{'Saldo':>9}{'Segurança':>11}"
          f"  Situação")
    linha()
    for codigo in sorted(dados["itens"]):
        item = dados["itens"][codigo]
        saldo = dados["estoque"].get(codigo, 0)
        if saldo < item["estoque_seguranca"]:
            situacao = "ABAIXO"
        else:
            situacao = "OK"
        print(f"{codigo:<8}{item['descricao']:<28}"
              f"{formatar_numero(saldo):>9}"
              f"{formatar_numero(item['estoque_seguranca']):>11}"
              f"  {situacao}")
        
