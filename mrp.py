"""Cálculo do MRP (RF08 e RN04 a RN08).

Para cada item, semana a semana, o MRP responde: quanto vamos precisar
(necessidade bruta), quanto já temos ou vai chegar, e quanto falta
(necessidade líquida). Se falta, ele gera uma ordem planejada.

O resultado do cálculo fica em dados["mrp"] e as ordens novas entram em
dados["ordens"].
"""

from itens import escolher_item
from persistencia import salvar_dados
from utils import confirmar, data_hoje, formatar_numero, linha, titulo

# RN04: processamos primeiro os PA, depois os SA e por último as MP.
"""Assim, quando chega a vez de um componente, todos os pais dele já
disseram quanto vão precisar."""
ORDEM_DOS_TIPOS = ("PA", "SA", "MP")

SEMANAS = 8  # o horizonte do planejamento

LINHAS_DO_REGISTRO = [
    ("Necessidade bruta", "nb"),
    ("Receb. programados", "rp"),
    ("Estoque projetado", "ep"),
    ("Necessidade líquida", "nl"),
    ("Receb. planejados", "rpl"),
    ("Liberação planejada", "lib"),
]


def ajustar_semana(semana):
    """Ordem atrasada (semana antes da 1) conta como semana 1, porque o
    material já é necessário desde o começo."""
    if semana < 1:
        return 1
    return semana


def somar_demanda_dos_componentes(dados, necessidade, pai, semana,
                                  quantidade):
    """Soma na necessidade bruta de cada componente o que a ordem do pai
    vai consumir: quantidade do pai x quantidade por unidade (RN04)."""
    if semana > SEMANAS:
        #calcular somente para 8 semanas
        return
    for componente in dados["estrutura"].get(pai, []):
        filho = componente["componente"]
        consumo = round(quantidade * componente["quantidade"], 6)
        necessidade[filho][semana - 1] += consumo # atualiza a demanda


def proximo_numero(ordens, tipo):
    #Acha o próximo número livre (OP ou OC) olhando as ordens que ficam
    # Serve para não ter reaproveitamento/uso duplicado de mesmo número
    maior = 0
    for ordem in ordens:
        if ordem["tipo"] == tipo:
            numero = int(ordem["numero"][3:])
            if numero > maior:
                maior = numero
    return maior + 1


def calcular_mrp(dados):
    """Faz o cálculo do MRP para todos os itens. Devolve a lista de
    mensagens de exceção (ordens com liberação antes da semana 1)."""
    itens = dados["itens"]

    # RN08: as ordens PLANEJADAS são apagadas e recalculadas.
    # As FIRMES, LIBERADAS e ENCERRADAS ficam.
    ordens_mantidas = []
    for ordem in dados["ordens"]:
        if ordem["status"] != "PLANEJADA":
            ordens_mantidas.append(ordem)

    # Uma lista de 8 semanas para cada item, começando zerada
    recebimentos = {} # o que já vai chegar (ordens firmes/liberadas)
    necessidade = {} #demanda que os pais geram sobre cada componente
    for codigo in itens:
        recebimentos[codigo] = [0] * SEMANAS
        necessidade[codigo] = [0] * SEMANAS

    # Ordens firmes e liberadas: o que elas entregam vira recebimento
    #programado, e o que elas ainda vão consumir já pesa nos componentes
    for ordem in ordens_mantidas:
        if ordem["status"] not in ("FIRME", "LIBERADA"):
            continue
        semana = ajustar_semana(ordem["semana_entrega"])
        if semana <= SEMANAS:
            recebimentos[ordem["item"]][semana - 1] += ordem["quantidade"]
        if ordem["tipo"] == "OP":
            semana = ajustar_semana(ordem["semana_liberacao"])
            somar_demanda_dos_componentes(dados, necessidade, ordem["item"],
                                          semana, ordem["quantidade"])

    novas_ordens = []
    registros = {}

    for tipo in ORDEM_DOS_TIPOS:# fazer na ordem certa
        for codigo in sorted(itens):
            item = itens[codigo]
            if item["tipo"] != tipo:
                continue

            # PA: a necessidade bruta vem do MPS. SA e MP: vem dos pais.
            if tipo == "PA":
                bruta = list(dados["mps"].get(codigo, [0] * SEMANAS))
            else:
                bruta = necessidade[codigo]

            estoque_inicial = dados["estoque"].get(codigo, 0)
            seguranca = item["estoque_seguranca"]
            lote = item["lote_minimo"]
            prazo = item["lead_time"]

            # cria uma lista de 8 zeros
            projetado = [0] * SEMANAS
            liquida = [0] * SEMANAS
            planejado = [0] * SEMANAS
            liberacao = [0] * SEMANAS

            estoque_anterior = estoque_inicial
            for i in range(SEMANAS):
                # RN05: NL = máx(0, NB + ES - (EP anterior + recebimentos))
                disponivel = estoque_anterior + recebimentos[codigo][i]
                falta = round(bruta[i] + seguranca - disponivel, 6)
                if falta < 0:
                    falta = 0

                # RN06: se falta, recebemos o maior entre a falta e o lote
                recebimento = 0
                if falta > 0:
                    if falta > lote:
                        recebimento = falta
                    else:
                        recebimento = lote

                projetado[i] = round(disponivel + recebimento - bruta[i], 6)
                estoque_anterior = projetado[i]
                liquida[i] = falta
                planejado[i] = recebimento

                if recebimento == 0:
                    continue

                # RN07: liberar = semana do recebimento - lead time
                semana_entrega = i + 1
                semana_liberacao = semana_entrega - prazo
                if semana_liberacao >= 1:
                    liberacao[semana_liberacao - 1] += recebimento

                # item fabricado gera OP; matéria-prima gera OC
                if tipo == "MP":
                    tipo_ordem = "OC"
                else:
                    tipo_ordem = "OP"

                novas_ordens.append({
                    "numero": "",
                    "tipo": tipo_ordem,
                    "item": codigo,
                    "quantidade": recebimento,
                    "semana_liberacao": semana_liberacao,
                    "semana_entrega": semana_entrega,
                    "status": "PLANEJADA",
                    "atrasada": semana_liberacao < 1,
                })

                # a OP planejada já cria demanda para os componentes
                if tipo_ordem == "OP":
                    semana_demanda = ajustar_semana(semana_liberacao)
                    somar_demanda_dos_componentes(
                        dados, necessidade, codigo, semana_demanda,
                        recebimento)

            registros[codigo] = {
                "estoque_inicial": estoque_inicial,
                "nb": bruta,
                "rp": recebimentos[codigo],
                "ep": projetado,
                "nl": liquida,
                "rpl": planejado,
                "lib": liberacao,
            }

    # Dá o número de cada ordem nova, continuando de onde as outras pararam
    contadores = {
        "OP": proximo_numero(ordens_mantidas, "OP"),
        "OC": proximo_numero(ordens_mantidas, "OC"),
    }
    excecoes = []
    for ordem in novas_ordens:
        tipo_ordem = ordem["tipo"]
        ordem["numero"] = f"{tipo_ordem}-{contadores[tipo_ordem]:04d}"
        contadores[tipo_ordem] += 1
        if ordem["atrasada"]:
            excecoes.append(
                f"{ordem['numero']} ({ordem['item']}): liberação na semana "
                f"{ordem['semana_liberacao']}, antes da semana 1.")

    dados["ordens"] = ordens_mantidas + novas_ordens
    dados["mrp"] = {"data_execucao": data_hoje(), "registros": registros}
    return excecoes


def executar_mrp(dados):
    #Tela de execução do MRP: calcula, resume e oferece ver um item.
    titulo("EXECUTAR MRP")
    if not dados["mps"]:
        print("ERRO: o MPS está vazio. Cadastre a demanda dos produtos "
              "acabados antes (opção 3).")
        return

    excecoes = calcular_mrp(dados)
    salvar_dados(dados, "ordens", "mrp")

    ops = 0
    ocs = 0
    for ordem in dados["ordens"]:
        if ordem["status"] == "PLANEJADA":
            if ordem["tipo"] == "OP":
                ops += 1
            else:
                ocs += 1

    print(f"MRP executado em {dados['mrp']['data_execucao']}.")
    print(f"{ops + ocs} ordens planejadas geradas: {ops} OP e {ocs} OC.")
    if excecoes:
        print(f"\n{len(excecoes)} mensagens de exceção:")
        for mensagem in excecoes:
            print("  - " + mensagem)

    if confirmar("\nVer o registro MRP de algum item agora?"):
        exibir_registro_mrp(dados)


def montar_linha(rotulo, valores):
    # Monta uma linha da tabela: o nome e um valor por semana
    texto = f"{rotulo:<22}"
    for valor in valores:
        texto += f"{formatar_numero(valor):>7}"
    return texto


def exibir_registro_mrp(dados):
    # RF08: Mostra o registro MRP de um item, semana por semana 
    titulo("REGISTRO MRP")
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
    print(f"\nREGISTRO MRP - {codigo} {item['descricao']}")
    print(f"Lead time: {item['lead_time']} sem | "
          f"Est. segurança: {formatar_numero(item['estoque_seguranca'])} | "
          f"Lote mín.: {formatar_numero(item['lote_minimo'])} | "
          f"Estoque: {formatar_numero(registro['estoque_inicial'])}")
    linha()
    print(montar_linha("Semana", list(range(1, SEMANAS + 1))))
    for rotulo, chave in LINHAS_DO_REGISTRO:
        print(montar_linha(rotulo, registro[chave]))