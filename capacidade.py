"""Centros de trabalho e roteiros (RF06).

Centro de trabalho = onde as coisas são fabricadas (soldagem, montagem...).
Roteiro = diz qual centro fabrica cada item e quanto tempo leva por unidade.

"""

from mps import SEMANAS
from persistencia import salvar_dados
from itens import escolher_item
from persistencia import salvar_dados
from utils import (formatar_dinheiro, formatar_numero, ler_decimal,
                   ler_texto, linha, titulo)

STATUS_NA_CARGA = ("PLANEJADA", "FIRME", "LIBERADA")

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


def formatar_horas(valor):
    #Horas com uma casa decimal e vírgula: 15 -> 15,0.
    return f"{valor:.1f}".replace(".", ",")


def calcular_carga(dados):
    """Calcula a carga de cada centro, semana a semana (RN09).

    Carga da semana = soma de (quantidade da OP x tempo por unidade do
    roteiro) das OPs que são liberadas naquela semana.
    Devolve ({centro: [carga das 8 semanas]}, [avisos]).
    """
    cargas = {}
    for codigo in dados["centros"]:
        cargas[codigo] = [0] * SEMANAS

    avisos = []
    for ordem in dados["ordens"]:
        if ordem["tipo"] != "OP":
            continue
        if ordem["status"] not in STATUS_NA_CARGA:
            continue

        roteiro = dados["roteiros"].get(ordem["item"])
        if roteiro is None:
            aviso = f"O item {ordem['item']} não tem roteiro: fora da carga."
            if aviso not in avisos:
                avisos.append(aviso)
            continue

        # ordem atrasada (liberação antes da semana 1) pesa na semana 1
        semana = ordem["semana_liberacao"]
        if semana < 1:
            semana = 1
        if semana > SEMANAS:
            continue

        horas = ordem["quantidade"] * roteiro["tempo_unitario"]
        cargas[roteiro["centro"]][semana - 1] += horas

    # arredonda para não aparecer sobra de conta com decimais
    for codigo in cargas:
        for i in range(SEMANAS):
            cargas[codigo][i] = round(cargas[codigo][i], 4)
    return cargas, avisos


def exibir_crp(dados):
    """Mostra a carga x capacidade de cada centro, semana a semana
    (RF12), e avisa as semanas com sobrecarga."""
    titulo("CARGA x CAPACIDADE (CRP)")
    if not dados["centros"]:
        print("Nenhum centro cadastrado ainda.")
        return
    if not dados["ordens"]:
        print("Ainda não há ordens. Execute o MRP antes (opção 4).")
        return

    cargas, avisos = calcular_carga(dados)

    for codigo in sorted(dados["centros"]):
        centro = dados["centros"][codigo]
        capacidade = centro["capacidade_horas_semana"]
        print(f"\nCARGA x CAPACIDADE - {codigo} {centro['descricao']} "
              f"({formatar_horas(capacidade)} h/semana)")
        print(f"{'Sem':<5}{'Carga(h)':>9}{'Uso(%)':>8}")
        linha()

        semanas_em_sobrecarga = []
        for semana in range(1, SEMANAS + 1):
            carga = cargas[codigo][semana - 1]
            uso = carga / capacidade * 100
            barras = "#" * round(uso / 10)  # cada # vale 10% de uso
            alerta = ""
            if carga > capacidade:
                alerta = " SOBRECARGA"
                semanas_em_sobrecarga.append(str(semana))
            print(f"{semana:<5}{formatar_horas(carga):>9}{round(uso):>8}"
                  f"  {barras}{alerta}")

        if semanas_em_sobrecarga:
            if len(semanas_em_sobrecarga) == 1:
                onde = "na semana "
            else:
                onde = "nas semanas "
            print("Sugestão: antecipar OPs ou programar hora extra "
                  + onde + ", ".join(semanas_em_sobrecarga) + ".")

    for aviso in avisos:
        print("\nAVISO: " + aviso)