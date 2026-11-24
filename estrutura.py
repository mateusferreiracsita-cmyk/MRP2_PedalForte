"""Estrutura de produto, a "BOM" (RF03 e RN03).
Cada item fabricado guarda a lista dos seus componentes, e cada
componente tem a quantidade necessária para fazer uma unidade do pai.
"""

from itens import escolher_item
from persistencia import salvar_dados
from utils import formatar_numero, ler_decimal, titulo

# Quem pode ser componente de quem (RN03):
#   PA aceita SA e MP | SA aceita só MP | MP não tem estrutura.
# Com essa regra a estrutura só "desce" (PA -> SA -> MP), então nunca
# existe ciclo e nunca passa de 3 níveis.



def cadastrar_componente(dados):
    """Adiciona um componente a um item pai (ou muda a quantidade, se o
    componente já estiver na lista)."""
    titulo("CADASTRAR COMPONENTE DA ESTRUTURA")
    pai = escolher_item(dados, "Código do item pai: ")
    if pai is None:
        return

    tipo_pai = dados["itens"][pai]["tipo"]
    if tipo_pai == "MP":
        print("ERRO: matéria-prima é comprada, então não tem estrutura.")
        return

    filho = escolher_item(dados, "Código do componente: ")
    if filho is None:
        return

    tipo_filho = dados["itens"][filho]["tipo"]
    if tipo_pai == "PA" and tipo_filho not in ("SA", "MP"):
        print(f"ERRO: um PA só aceita componentes do tipo SA ou MP. "
              f"{filho} é {tipo_filho}.")
        return
    if tipo_pai == "SA" and tipo_filho != "MP":
        print(f"ERRO: um SA só aceita componentes do tipo MP. "
              f"{filho} é {tipo_filho}.")
        return

    quantidade = ler_decimal("Quantidade por unidade do pai: ",
                             minimo=0.001)

    componentes = dados["estrutura"].setdefault(pai, [])
    for componente in componentes:
        if componente["componente"] == filho:
            componente["quantidade"] = quantidade
            print(f"{filho} já estava na estrutura: quantidade atualizada.")
            break
    else:
        componentes.append({"componente": filho, "quantidade": quantidade})
        print(f"{filho} adicionado à estrutura de {pai}.")

    salvar_dados(dados, "estrutura")


def remover_componente(dados):  
    titulo("REMOVER COMPONENTE DA ESTRUTURA")
    # Para o retirar pai, retire todos os componentes
    pai = escolher_item(dados, "Código do item pai: ")
    if pai is None:
        return

    componentes = dados["estrutura"].get(pai, [])
    if not componentes:
        print(f"{pai} não tem componentes cadastrados.")
        return

    filho = escolher_item(dados, "Código do componente a remover: ")
    if filho is None:
        return

    novos = [c for c in componentes if c["componente"] != filho]
    """cria uma cópia da lista dos componentes a fim de verificar 
    se o que o usuário digitou participa da estrutura do pai"""
    if len(novos) == len(componentes):
        print(f"ERRO: {filho} não faz parte da estrutura de {pai}.")
        return

    if novos:
        dados["estrutura"][pai] = novos
    else:
        del dados["estrutura"][pai]  # sem componentes, some a entrada
    salvar_dados(dados, "estrutura")
    print(f"{filho} removido da estrutura de {pai}.")


def desenhar_arvore(dados, codigo, prefixo, nivel, niveis):
    """Imprime os componentes de "codigo" em forma de árvore.
    igual a árvore apresentada no pdf
    É recursiva: para cada componente que também tem componentes (um SA),
    ela chama a si mesma para desenhar o próximo nível.
    """
    componentes = dados["estrutura"].get(codigo, [])
    for posicao, componente in enumerate(componentes):
        ultimo = posicao == len(componentes) - 1
        conector = "└── " if ultimo else "├── "
        filho = componente["componente"]
        item = dados["itens"][filho]

        esquerda = f"{prefixo}{conector}{filho} {item['descricao']} "
        quantidade = formatar_numero(componente["quantidade"])
        print(f"{esquerda.ljust(52, '.')} {quantidade} {item['unidade']}")
        # pontinhos para alinhar

        lista = niveis.setdefault(nivel, [])
        if filho not in lista:
            lista.append(filho)

        # se esse era o último, a linha vertical não continua 
        novo_prefixo = prefixo + ("    " if ultimo else "│   ")
        desenhar_arvore(dados, filho, novo_prefixo, nivel + 1, niveis)


def exibir_estrutura(dados):
    """Mostra a estrutura da BOM, indentada e com o nível de cada item."""
    titulo("ESTRUTURA DE PRODUTO (BOM)")
    codigo = escolher_item(dados, "Código do produto: ")
    if codigo is None:
        return

    item = dados["itens"][codigo]
    if item["tipo"] == "MP":
        print("Matéria-prima não tem estrutura.")
        return
    if not dados["estrutura"].get(codigo):
        print(f"{codigo} ainda não tem componentes cadastrados.")
        return

    print(f"\n{codigo} {item['descricao']}")
    niveis = {}
    desenhar_arvore(dados, codigo, "", 1, niveis)

    resumo = [f"0 = {codigo}"]
    for nivel in sorted(niveis):
        resumo.append(f"{nivel} = " + ", ".join(niveis[nivel]))
    print("\nNíveis: " + " | ".join(resumo))