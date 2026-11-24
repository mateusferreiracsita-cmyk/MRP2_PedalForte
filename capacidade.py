"""Centros de trabalho e roteiros (RF06).

Centro de trabalho = onde as coisas são fabricadas (soldagem, montagem...).
Roteiro = diz qual centro fabrica cada item e quanto tempo leva por unidade.

Mais pra frente este módulo também vai calcular a carga x capacidade (CRP).
"""


from itens import escolher_item
from persistencia import salvar_dados
from utils import (formatar_dinheiro, formatar_numero, ler_decimal,
                   ler_texto, linha, titulo)


def codigo_centro_valido(codigo):
    #Confere se o código é CT-01, CT-02... (CT, hífen e 2 números).
    if len(codigo) != 5:
        return False
    if codigo[:3] != "CT-":
        return False
    return codigo[3:].isdigit()


def ler_codigo_centro(mensagem):
    #Lê um código de centro validado
    while True:
        codigo = input(mensagem).strip().upper()
        if codigo_centro_valido(codigo):
            return codigo
        print("ERRO: código inválido. Use o formato CT-01, CT-02...")


def dica(valor):
    # Mostra o valor atual na pergunta de função de alteração de dados,
    #  se existir.
    if valor is None:
        return ""
    if isinstance(valor, (int, float)):
        valor = formatar_numero(valor)
    return f" [{valor}]"


def listar_centros(dados):
    titulo("CENTROS DE TRABALHO")
    if not dados["centros"]:
        print("Nenhum centro cadastrado ainda.")
        return

    print(f"{'Código':<8}{'Descrição':<32}{'Capac. (h/sem)':>16}"
          f"{'Custo/hora':>13}")
    linha()
    for codigo in sorted(dados["centros"]):
        centro = dados["centros"][codigo]
        print(f"{codigo:<8}{centro['descricao']:<32}"
              f"{formatar_numero(centro['capacidade_horas_semana']):>16}"
              f"{formatar_dinheiro(centro['custo_hora']):>13}")


def cadastrar_centro(dados):
    """Cadastra um centro novo. Se o código já existir, vira alteração
    (ENTER mantém o valor que já estava)."""
    titulo("CADASTRAR / ALTERAR CENTRO DE TRABALHO")
    codigo = ler_codigo_centro("Código do centro (ex.: CT-01): ")

    atual = dados["centros"].get(codigo, {})
    if atual:
        print("Esse centro já existe, então vamos alterar. "
              "ENTER mantém o valor atual.")

    descricao = ler_texto(
        "Descrição" + dica(atual.get("descricao")) + ": ",
        padrao=atual.get("descricao"))
    capacidade = ler_decimal(
        "Capacidade (horas por semana)"
        + dica(atual.get("capacidade_horas_semana")) + ": ",
        minimo=0.1, padrao=atual.get("capacidade_horas_semana"))
    custo_hora = ler_decimal(
        "Custo por hora (R$)" + dica(atual.get("custo_hora")) + ": ",
        minimo=0, padrao=atual.get("custo_hora"))

    dados["centros"][codigo] = {
        "descricao": descricao,
        "capacidade_horas_semana": capacidade,
        "custo_hora": custo_hora,
    }
    salvar_dados(dados, "centros")
    print(f"Centro {codigo} salvo!")


def listar_roteiros(dados):
    titulo("ROTEIROS DE OPERAÇÃO")
    if not dados["roteiros"]:
        print("Nenhum roteiro cadastrado ainda.")
        return

    print(f"{'Item':<8}{'Descrição':<28}{'Centro':<8}{'Horas/un':>10}")
    linha()
    for codigo in sorted(dados["roteiros"]):
        roteiro = dados["roteiros"][codigo]
        descricao = dados["itens"][codigo]["descricao"]
        print(f"{codigo:<8}{descricao:<28}{roteiro['centro']:<8}"
              f"{formatar_numero(roteiro['tempo_unitario']):>10}")


def definir_roteiro(dados):
    #Diz qual centro fabrica um item e quantas horas leva cada unidade
    
    titulo("ROTEIRO DE OPERAÇÃO")
    if not dados["centros"]:
        print("ERRO: cadastre um centro de trabalho antes.")
        return

    codigo = escolher_item(dados, "Código do item fabricado: ")
    if codigo is None:
        return
    if dados["itens"][codigo]["tipo"] == "MP":
        print("ERRO: matéria-prima é comprada, não precisa de roteiro.")
        return

    listar_centros(dados)
    centro = ler_codigo_centro("\nCentro que fabrica este item: ")
    if centro not in dados["centros"]:
        print(f"ERRO: o centro {centro} não está cadastrado.")
        return

    atual = dados["roteiros"].get(codigo, {})
    tempo = ler_decimal(
        "Tempo por unidade (horas)" + dica(atual.get("tempo_unitario"))
        + ": ", minimo=0.01, padrao=atual.get("tempo_unitario"))

    dados["roteiros"][codigo] = {"centro": centro, "tempo_unitario": tempo}
    salvar_dados(dados, "roteiros")
    print(f"Roteiro de {codigo} salvo!")