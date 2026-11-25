from menu import menu_principal
from persistencia import carregar_dados


def main():
    # RF15: os dados da pasta data/ são carregados assim que o sistema abre
    try:
        dados = carregar_dados()
    except ValueError as erro:
        print(f"ERRO ao carregar os dados: {erro}")
        return

    try:
        menu_principal(dados)
    except (KeyboardInterrupt, EOFError):
        print("\nSistema encerrado.")


if __name__ == "__main__":
    main()