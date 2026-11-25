# Cadastro de itens (RF02): cadastrar, listar e alterar.


from persistencia import salvar_dados
from utils import (formatar_dinheiro, formatar_numero, ler_codigo_item,
                   ler_decimal, ler_inteiro, ler_texto, linha, titulo)

NOMES_TIPO = {
    "PA": "Produto acabado",
    "SA": "Semiacabado",
    "MP": "Matéria-prima",
}


def escolher_item(dados, mensagem="Código do item: "):#mensagem padrão mas modificável.
    #pergunta um código e confere se o item existe.
    #Devolve o código, ou None (com aviso) se não estiver cadastrado.
    codigo = ler_codigo_item(mensagem)
    if codigo not in dados["itens"]:
        print(f"ERRO: o item {codigo} não está cadastrado.")
        return None
    return codigo


def listar_itens(dados):
    #funcao que lista de forma organizada montando uma tabela
    titulo("ITENS CADASTRADOS")
    if not dados["itens"]:
        print("Nenhum item cadastrado ainda.")
        return

    print(f"{'Código':<8}{'Descrição':<28}{'Un':<5}{'Custo un.':>12}"
          f"{'LT':>4}{'ES':>7}{'Lote':>7}")
    linha()
    for codigo in sorted(dados["itens"]):
        item = dados["itens"][codigo]
        # PA e SA não têm custo digitado: ele sai do custo padrão (RF13)
        if item["tipo"] == "MP":
            custo = formatar_dinheiro(item["custo_unitario"])
        else:
            custo = "-"
        print(f"{codigo:<8}{item['descricao']:<28}{item['unidade']:<5}"
              f"{custo:>12}{item['lead_time']:>4}"
              f"{formatar_numero(item['estoque_seguranca']):>7}"
              f"{formatar_numero(item['lote_minimo']):>7}")
    print("\nLT = lead time (semanas) | ES = estoque de segurança")


def cadastrar_item(dados):
    titulo("CADASTRAR ITEM")
    codigo = ler_codigo_item("Código (ex.: PA-001, SA-020, MP-201): ")
    if codigo in dados["itens"]:
        print(f"ERRO: o código {codigo} já existe (cada código é único).")
        return

    tipo = codigo[:2]
    print(f"Tipo: {NOMES_TIPO[tipo]}")
    descricao = ler_texto("Descrição: ")
    unidade = ler_texto("Unidade de medida (un, m, L...): ")

    if tipo == "MP":
        custo = ler_decimal("Custo unitário (R$): ", minimo=0)
    else:
        # quem é fabricado tem o custo calculado pela estrutura
        custo = 0.0
        print("Custo: será calculado pelo custo de materiais e mão de obra.")

    lead_time = ler_inteiro("Lead time (semanas): ", minimo=0)
    estoque_seguranca = ler_decimal("Estoque de segurança: ", minimo=0)
    lote_minimo = ler_decimal("Lote mínimo: ", minimo=0)

    dados["itens"][codigo] = {
        "descricao": descricao,
        "tipo": tipo,
        "unidade": unidade,
        "custo_unitario": custo,
        "lead_time": lead_time,
        "estoque_seguranca": estoque_seguranca,
        "lote_minimo": lote_minimo,
    }
    # todo item novo já nasce com saldo zero no estoque
    dados["estoque"][codigo] = 0
    salvar_dados(dados, "itens", "estoque")
    print(f"Item {codigo} cadastrado!")


def alterar_item(dados):
    titulo("ALTERAR ITEM")
    codigo = escolher_item(dados)

    item = dados["itens"][codigo]
    print("ENTER em qualquer campo mantém o valor atual.")
    print("O código e o tipo não podem ser mudados")

    item["descricao"] = ler_texto(f"Descrição [{item['descricao']}]: ",
                                  padrao=item["descricao"])
    item["unidade"] = ler_texto(f"Unidade [{item['unidade']}]: ",
                                padrao=item["unidade"])
    # se não digitar nada, vai continuar igual
    
    if item["tipo"] == "MP":
        item["custo_unitario"] = ler_decimal(
            f"Custo unitário [{formatar_numero(item['custo_unitario'])}]: ",
            minimo=0, padrao=item["custo_unitario"])
        
    item["lead_time"] = ler_inteiro(
        f"Lead time [{item['lead_time']}]: ",
        minimo=0, padrao=item["lead_time"])
    
    item["estoque_seguranca"] = ler_decimal(
        "Estoque de segurança "
        f"[{formatar_numero(item['estoque_seguranca'])}]: ",
        minimo=0, padrao=item["estoque_seguranca"])
    
    item["lote_minimo"] = ler_decimal(
        f"Lote mínimo [{formatar_numero(item['lote_minimo'])}]: ",
        minimo=0, padrao=item["lote_minimo"])

    salvar_dados(dados, "itens")
    print(f"Item {codigo} alterado!")