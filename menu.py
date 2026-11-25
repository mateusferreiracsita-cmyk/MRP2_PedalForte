# Menus e navegação do sistema (RF01).


from capacidade import (cadastrar_centro, definir_roteiro, exibir_crp,
                        listar_centros, listar_roteiros)
from custos import exibir_custo_padrao
from estoque import (consultar_kardex, exibir_posicao_estoque,
                     movimentar_estoque)
from estrutura import (cadastrar_componente, exibir_estrutura,
                       remover_componente)
from itens import alterar_item, cadastrar_item, listar_itens
from mps import cadastrar_mps, listar_mps
from mrp import executar_mrp, exibir_registro_mrp
from ordens import (apontar_producao, encerrar_ordem, firmar_ordem,
                    liberar_ordem, listar_ordens)
from relatorios import exportar_csv
from utils import ler_opcao, linha, pausar, titulo


def executar_acao(funcao, dados):
    """Roda uma função do sistema. Se algo inesperado acontecer, mostra o
    erro em vez de fechar o programa no meio de uma operação."""
    try:
        funcao(dados)
    except (ValueError, KeyError, OSError) as erro:
        print(f"ERRO inesperado: {erro}")


def mostrar_submenu(dados, nome, opcoes):
    #Monta um submenu que repete até a pessoa escolher voltar (template).
    # "opcoes" é uma lista de nome e função.
    validas = ["0"]
    for numero in range(1, len(opcoes) + 1):
        validas.append(str(numero))

    while True:
        titulo(nome)
        for numero, (texto, funcao) in enumerate(opcoes, start=1):
            print(f"{numero}. {texto}")
        print("0. Voltar")
        linha()

        escolha = ler_opcao("Escolha uma opção: ", validas)
        if escolha == "0":
            return
        funcao = opcoes[int(escolha) - 1][1]
        executar_acao(funcao, dados)
        pausar()


def menu_cadastros(dados):
    mostrar_submenu(dados, "CADASTROS", [
        ("Listar itens", listar_itens),
        ("Cadastrar item", cadastrar_item),
        ("Alterar item", alterar_item),
        ("Cadastrar componente da estrutura (BOM)", cadastrar_componente),
        ("Remover componente da estrutura", remover_componente),
        ("Exibir estrutura de produto", exibir_estrutura),
        ("Listar centros de trabalho", listar_centros),
        ("Cadastrar/alterar centro de trabalho", cadastrar_centro),
        ("Definir roteiro de um item", definir_roteiro),
        ("Listar roteiros", listar_roteiros),
    ])


def menu_estoque(dados):
    mostrar_submenu(dados, "ESTOQUE", [
        ("Movimentar estoque (entrada, saída, ajuste)", movimentar_estoque),
        ("Consultar saldo e kardex de um item", consultar_kardex),
        ("Posição de estoque de todos os itens", exibir_posicao_estoque),
    ])


def menu_mps(dados):
    mostrar_submenu(dados, "PLANO MESTRE DE PRODUÇÃO (MPS)", [
        ("Listar MPS", listar_mps),
        ("Cadastrar/alterar MPS de um produto", cadastrar_mps),
    ])


def menu_mrp(dados):
    mostrar_submenu(dados, "MRP", [
        ("Executar MRP", executar_mrp),
        ("Ver registro MRP de um item", exibir_registro_mrp),
    ])


def menu_ordens(dados):
    """Mostra a lista de ordens e as ações possíveis sobre elas."""
    acoes = {
        "F": firmar_ordem,
        "L": liberar_ordem,
        "E": encerrar_ordem,
        "A": apontar_producao,
    }
    while True:
        listar_ordens(dados)
        print()
        print("[F] Firmar  [L] Liberar  [E] Encerrar OC  "
              "[A] Apontar produção  [V] Voltar")
        escolha = ler_opcao("Escolha: ", ["F", "L", "E", "A", "V"])
        if escolha == "V":
            return
        executar_acao(acoes[escolha], dados)
        pausar()


def menu_graficos(dados):
    try:
        import graficos
    except ImportError:
        print("ERRO: a biblioteca matplotlib não está instalada.")
        pausar()
        return

    mostrar_submenu(dados, "GRÁFICOS DE GESTÃO", [
        ("Posição de estoque (saldo x segurança)",
         graficos.grafico_posicao_estoque),
        ("Estoque projetado de um item",
         graficos.grafico_estoque_projetado),
        ("Ordens por semana de entrega (OP x OC)",
         graficos.grafico_ordens_por_semana),
        ("Carga x capacidade de um centro",
         graficos.grafico_carga_capacidade),
    ])


def mostrar_menu_principal():
    print()
    print("=" * 50)
    print("MRP II - PEDAL FORTE BICICLETAS")
    print("=" * 50)
    print("1. Cadastros (itens, estrutura, centros, roteiros)")
    print("2. Estoque (movimentar, saldo, kardex)")
    print("3. Plano Mestre de Produção (MPS)")
    print("4. Executar MRP")
    print("5. Ordens de produção e de compra")
    print("6. Carga x capacidade (CRP)")
    print("7. Custo padrão dos produtos")
    print("8. Relatórios (exportar CSV)")
    print("9. Gráficos de gestão")
    print("0. Sair")
    linha()


def menu_principal(dados):
    #Loop principal: repete até a pessoa escolher sair.
    while True:
        mostrar_menu_principal()
        escolha = ler_opcao("Escolha uma opção: ",
                            ["0", "1", "2", "3", "4", "5", "6", "7", "8",
                             "9"])
        if escolha == "0":
            print("Até logo!")
            return
        elif escolha == "1":
            menu_cadastros(dados)
        elif escolha == "2":
            menu_estoque(dados)
        elif escolha == "3":
            menu_mps(dados)
        elif escolha == "4":
            menu_mrp(dados)
        elif escolha == "5":
            menu_ordens(dados)
        elif escolha == "6":
            executar_acao(exibir_crp, dados)
            pausar()
        elif escolha == "7":
            executar_acao(exibir_custo_padrao, dados)
            pausar()
        elif escolha == "8":
            executar_acao(exportar_csv, dados)
            pausar()
        elif escolha == "9":
            menu_graficos(dados)