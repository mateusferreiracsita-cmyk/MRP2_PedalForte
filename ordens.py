"""Ordens de produção (OP) e de compra (OC): listar, firmar, liberar,
encerrar e apontar a produção (RF09, RF10 e RF11).

O caminho de uma ordem é: PLANEJADA -> FIRME -> LIBERADA -> ENCERRADA.
As ordens PLANEJADAS nascem do MRP e podem sumir quando o MRP roda de
novo. Depois de firmada, a ordem fica protegida.
"""

from estoque import registrar_movimento
from persistencia import salvar_dados
from utils import formatar_numero, ler_texto, linha, titulo


def nome_do_status(ordem):
    # Ordem planejada que já nasceu atrasada aparece como ATRASADA.
    if ordem["status"] == "PLANEJADA" and ordem.get("atrasada"):
        return "ATRASADA"
    return ordem["status"]


def listar_ordens(dados):
    titulo("ORDENS DE PRODUÇÃO E DE COMPRA")
    if not dados["ordens"]:
        print("Nenhuma ordem ainda. Execute o MRP (opção 4) para gerá-las.")
        return

    if dados["mrp"]:
        print(f"Execução do MRP em {dados['mrp']['data_execucao']}\n")
    print(f"{'Ordem':<9}{'Tipo':<6}{'Item':<8}{'Qtde':>8}{'Liberar':>9}"
          f"{'Entregar':>10}  Status")
    linha()

    atrasadas = 0 # contar o numero de atrasadas
    for ordem in dados["ordens"]:
        liberar = "S" + str(ordem["semana_liberacao"])
        entregar = "S" + str(ordem["semana_entrega"])
        status = nome_do_status(ordem)
        if status == "ATRASADA":
            atrasadas += 1
        print(f"{ordem['numero']:<9}{ordem['tipo']:<6}{ordem['item']:<8}"
              f"{formatar_numero(ordem['quantidade']):>8}"
              f"{liberar:>9}{entregar:>10}  {status}")

    if atrasadas > 0:
        print(f"\n{atrasadas} mensagens de exceção: ordens com liberação "
              f"antes da semana 1.")


def escolher_ordem(dados, mensagem="Número da ordem (ex.: OP-0010): "):
    """Pergunta o número e devolve a ordem, ou None (com aviso) se não
    existir"""
    numero = ler_texto(mensagem).upper()
    for ordem in dados["ordens"]:
        if ordem["numero"] == numero:
            return ordem
    print(f"ERRO: a ordem {numero} não existe.")
    return None


def avancar_ordem(dados, status_atual, novo_status, acao):
    # Muda o status de uma ordem se ela estiver no status certo
    titulo(f"{acao.upper()} ORDEM")
    ordem = escolher_ordem(dados)
    if ordem is None:
        return

    if ordem["status"] != status_atual:
        print(f"ERRO: só dá para {acao} ordens com status {status_atual}. "
              f"A {ordem['numero']} está {ordem['status']}.")
        return

    ordem["status"] = novo_status
    salvar_dados(dados, "ordens")
    print(f"Ordem {ordem['numero']} agora está {novo_status}.")


def firmar_ordem(dados):
    avancar_ordem(dados, "PLANEJADA", "FIRME", "firmar")


def liberar_ordem(dados):
    avancar_ordem(dados, "FIRME", "LIBERADA", "liberar")


def encerrar_ordem(dados):
    """Encerra uma OC liberada: o material chegou, então entra no estoque.
    A OP não se encerra aqui: ela se encerra no apontamento de produção."""
    titulo("ENCERRAR ORDEM")
    ordem = escolher_ordem(dados)
    if ordem is None:
        return

    if ordem["tipo"] == "OP":
        print("ERRO: a OP é encerrada pelo apontamento de produção.")
        return
    if ordem["status"] != "LIBERADA":
        print(f"ERRO: só dá para encerrar ordens LIBERADAS. "
              f"A {ordem['numero']} está {ordem['status']}.")
        return

    registrar_movimento(dados, ordem["item"], "ENTRADA", ordem["quantidade"],
                        ordem["numero"] + " (recebimento)")
    ordem["status"] = "ENCERRADA"
    salvar_dados(dados, "estoque", "movimentos", "ordens")
    print(f"Ordem {ordem['numero']} encerrada e material dado como "
          f"entrada no estoque.")


def apontar_producao(dados):
    """Aponta a produção de uma OP liberada pela quantidade total (RF11):
    baixa os componentes, dá entrada no item produzido e encerra a OP."""
    titulo("APONTAR PRODUÇÃO")
    ordem = escolher_ordem(dados, "Número da OP a apontar (ex.: OP-0010): ")
    if ordem is None:
        return
    if ordem["tipo"] != "OP":
        print("ERRO: só ordens de produção (OP) podem ser apontadas.")
        return
    if ordem["status"] != "LIBERADA":
        print(f"ERRO: a OP precisa estar LIBERADA. "
              f"A {ordem['numero']} está {ordem['status']}.")
        return

    item = ordem["item"]

    # Primeiro conferimos TODOS os componentes, antes de mexer em qualquer
    # saldo. Se faltar um só, rejeitamos tudo e nada fica pela metade.
    consumos = []
    faltas = []
    for componente in dados["estrutura"].get(item, []):
        codigo = componente["componente"]
        necessario = round(componente["quantidade"] * ordem["quantidade"], 6)
        saldo = dados["estoque"].get(codigo, 0)
        consumos.append((codigo, necessario))
        if saldo < necessario:
            unidade = dados["itens"][codigo]["unidade"]
            faltas.append(f"  - {codigo}: precisa de "
                          f"{formatar_numero(necessario)} {unidade}, "
                          f"saldo {formatar_numero(saldo)} {unidade}")

    if faltas:
        print("ERRO: faltam componentes no estoque:")
        for falta in faltas:
            print(falta)
        print("Apontamento rejeitado.")
        return

    documento = f"{ordem['numero']} ({item})"
    for codigo, necessario in consumos:
        registrar_movimento(dados, codigo, "SAIDA", necessario, documento)
    registrar_movimento(dados, item, "ENTRADA", ordem["quantidade"],
                        ordem["numero"] + " (produção)")

    ordem["status"] = "ENCERRADA"
    salvar_dados(dados, "estoque", "movimentos", "ordens")
    unidade = dados["itens"][item]["unidade"]
    print(f"Produção apontada! {formatar_numero(ordem['quantidade'])} "
          f"{unidade} de {item} entraram no estoque e a "
          f"{ordem['numero']} foi encerrada.")