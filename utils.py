"""Funções de apoio que o sistema inteiro usa. 
Pura formatação!
Aqui ficam duas coisas: as perguntas ao usuário (que insistem até a
resposta ser válida) e a formatação dos números com ",".
"""

import re
from datetime import datetime




def formatar_numero(valor):
    """Mostra o número sem zeros sobrando e com vírgula: 3 -> 3, 0.5 -> 0,5."""
    texto = f"{valor:.3f}".rstrip("0").rstrip(".")
    return texto.replace(".", ",")


def formatar_dinheiro(valor):
    # formatação com . de milhar e , para centavos ( R$ também )
    texto = f"{valor:,.2f}"
    # o Python usa o padrão americano, então trocamos vírgula por ponto
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return "R$ " + texto


def data_hoje():
    #Data de hoje no formato dd/mm/aaaa.
    return datetime.now().strftime("%d/%m/%Y")


def linha(simbolo="-"):
    print(simbolo * 50)


def titulo(texto):
    # Cabeçalho bonitinho para cada tela.
    print()
    linha("=")
    print(texto)
    linha("=")


def pausar():
    input("\nPressione ENTER para continuar...")


def codigo_valido(codigo):
    # Confere se o código é Tipo-Número, tipo PA-001, SA-020 ou MP-201.
    # o código tem sempre 6 caracteres: 2 letras, um hífen e 3 números
    if len(codigo) != 6:
        return False

    tipo = codigo[:2]      # as duas primeiras letras (PA, SA ou MP)
    hifen = codigo[2]      # o terceiro caractere
    numero = codigo[3:]    # os três últimos caracteres

    if tipo not in ("PA", "SA", "MP"):
        return False
    if hifen != "-":
        return False
    if not numero.isdigit():
        return False
    return True


def data_valida(texto):
    #validação da data, 31/02 não existe por ex.
    try:
        datetime.strptime(texto, "%d/%m/%Y")
        return True
    except ValueError:
        return False

# validação de texto, número, decimal e opção ( pedir ajuda a IA )


def ler_texto(mensagem, padrao=None):
    while True:
        texto = input(mensagem).strip()
        if texto:
            return texto
        if padrao is not None:
            return padrao
        print("ERRO: esse campo não pode ficar vazio.")


def ler_inteiro(mensagem, minimo=None, padrao=None):
    while True:
        texto = input(mensagem).strip()
        if texto == "" and padrao is not None:
            return padrao
        try:
            numero = int(texto)
        except ValueError:
            print("ERRO: digite um número inteiro.")
            continue
        if minimo is not None and numero < minimo:
            print(f"ERRO: o valor mínimo é {minimo}.")
            continue
        return numero


def ler_decimal(mensagem, minimo=None, padrao=None):
    while True:
        texto = input(mensagem).strip()
        if texto == "" and padrao is not None:
            return padrao
        try:
            # aceita 0,5 e 0.5
            numero = float(texto.replace(",", "."))
        except ValueError:
            print("ERRO: digite um número (ex.: 12,5).")
            continue
        if minimo is not None and numero < minimo:
            print(f"ERRO: o valor mínimo é {formatar_numero(minimo)}.")
            continue
        return numero


def ler_opcao(mensagem, opcoes):
    #Lê uma das opções da lista, ex.: ler_opcao("E/S/A: ", ["E","S","A"]).
    while True:
        texto = input(mensagem).strip().upper()
        if texto in opcoes:
            return texto
        print("ERRO: opção inválida. Use: " + ", ".join(opcoes) + ".")


def ler_codigo_item(mensagem):
    while True:
        codigo = input(mensagem).strip().upper()
        if codigo_valido(codigo):
            return codigo
        print("ERRO: código inválido. Use o formato PA-001, SA-020, MP-201.")


def ler_data(mensagem):
    while True:
        texto = input(mensagem).strip()
        if texto == "":# para caso de ENTER usar data de hoje
            return data_hoje()
        if data_valida(texto):
            return texto
        print("ERRO: data inválida. Use dd/mm/aaaa.")


def confirmar(mensagem): # S OU N 
    return ler_opcao(mensagem + " [S/N]: ", ["S", "N"]) == "S"
