# MRP II - Pedal Forte Bicicletas

Sistema de Planejamento dos Recursos de Manufatura (MRP II) em Python, em
modo texto, para a fábrica fictícia **Pedal Forte Bicicletas** (Divinópolis-MG).

- **Curso:** Engenharia de Computação, CEFET-MG Campus Divinópolis
- **Disciplina:** Programação em Python
- **Professor:** Guido Pantuza
- **Trabalho:** 2º Sistema MRP II (individual)
- **Aluno:** Mateus Ferreira Carvalho Silva
- **Vídeo de demonstração do sistema:** [cole o link aqui]
- **Vídeo de demonstração do código:** [cole o link aqui]

---

## Aviso sobre o uso de Inteligência Artificial

- **A base de demonstração** da pasta `data/` (itens, estrutura de produto,
  centros de trabalho, roteiros, MPS, estoque inicial e movimentos) foi
  gerada e validada por  IA (Claude e Gemini). Eu copiei esses dados
  e colei nos arquivos da pasta `data/`. Os valores seguem os exemplos do
  enunciado (por exemplo, o custo padrão do PA-001 dá R$ 792,60).

- **O código** foi desenvolvido com o apoio de IA, em um passo a
  passo em que cada módulo foi sendo feito em um ciclo de execução, suporte, 
  discussão, entendimento e implementação.

---

## Como executar

**Requisitos**

- Python 3.10 ou superior (desenvolvido no Windows com Python 3.14; a
  execução também foi verificada em Linux com Python 3.12).
- Biblioteca `matplotlib`, usada somente nos gráficos (opção 9 do menu).

**Passo a passo**

```bash
# 1. entre na pasta do projeto
cd MRP2_PedalForte

# 2. instale a dependência dos gráficos
pip install -r requirements.txt

# 3. rode o sistema
python main.py
```

Se o `matplotlib` não estiver instalado, o sistema funciona normalmente. Só a
opção 9 (gráficos) avisa que a biblioteca está faltando.

---

## Estrutura do projeto

```
MRP2_PedalForte/
├── main.py            # ponto de entrada
├── menu.py            # menus e navegação
├── itens.py           # cadastro de itens
├── estrutura.py       # BOM e árvore indentada
├── estoque.py         # movimentações, saldo e kardex
├── mps.py             # plano mestre de produção
├── mrp.py             # cálculo do MRP
├── ordens.py          # OPs, OCs e apontamento
├── capacidade.py      # centros, roteiros e CRP
├── custos.py          # custo padrão
├── relatorios.py      # exportação CSV
├── graficos.py        # gráficos de gestão (matplotlib)
├── persistencia.py    # leitura e gravação de arquivos
├── utils.py           # validações e formatação
├── requirements.txt   # dependências (matplotlib)
├── data/              # arquivos de dados (JSON e CSV)
├── exportacoes/       # CSVs gerados pelo sistema
├── graficos_saida/    # PNGs gerados pelo sistema
└── docs/
    └── README.md
```

---

## Requisitos funcionais

| Requisito | Onde está | Como acessar no menu |
|-----------|-----------|----------------------|
| RF01 - Menu principal | `menu.py`, `main.py` | Tela inicial |
| RF02 - Cadastrar, listar e alterar itens | `itens.py` | 1 > opções 1, 2 e 3 |
| RF03 - Estrutura de produto (BOM) e explosão indentada | `estrutura.py` | 1 > opções 4, 5 e 6 |
| RF04 - Movimentações de estoque | `estoque.py` | 2 > opção 1 |
| RF05 - Saldo, kardex e alerta de estoque de segurança | `estoque.py` | 2 > opções 2 e 3 |
| RF06 - Centros de trabalho e roteiros | `capacidade.py` | 1 > opções 7, 8, 9 e 10 |
| RF07 - Plano Mestre de Produção (8 semanas) | `mps.py` | 3 |
| RF08 - Cálculo MRP e registro de um item | `mrp.py` | 4 > opções 1 e 2 |
| RF09 - Ordens planejadas (OP e OC) | `mrp.py`, `ordens.py` | 4 (gera) e 5 (lista) |
| RF10 - Firmar, liberar e encerrar ordens | `ordens.py` | 5 > F, L e E |
| RF11 - Apontamento de produção | `ordens.py` | 5 > A |
| RF12 - Carga x capacidade (CRP) | `capacidade.py` | 6 |
| RF13 - Custo padrão | `custos.py` | 7 |
| RF14 - Exportação em CSV | `relatorios.py` | 8 |
| RF15 - Persistência em `data/` | `persistencia.py` | Automático |
| RF16 - Gráficos com matplotlib | `graficos.py` | 9 |

## Regras de negócio

| Regra | Como foi implementada |
|-------|-----------------------|
| RN01 - Código `Tipo-Número`, único | `utils.codigo_valido` confere o formato. `itens.cadastrar_item` recusa código repetido. O tipo do item é tirado do próprio código. |
| RN02 - Saldo nunca negativo | `estoque.registrar_movimento` recusa a operação com mensagem explicativa. |
| RN03 - Estrutura em no máximo 3 níveis | O dicionário `COMPONENTES_PERMITIDOS` em `estrutura.py` define que PA aceita SA e MP, SA aceita só MP e MP não tem estrutura. Isso também impede ciclos. |
| RN04 - MRP processa PA, depois SA, depois MP | `mrp.ORDEM_DOS_TIPOS` e `somar_demanda_dos_componentes`. |
| RN05 - Necessidade líquida | Fórmula aplicada em `mrp.calcular_mrp`. |
| RN06 - Recebimento planejado = maior entre necessidade líquida e lote mínimo | `mrp.calcular_mrp`. |
| RN07 - Liberação = entrega - lead time; atrasada se antes da semana 1 | `mrp.calcular_mrp` marca a ordem como atrasada e gera mensagem de exceção. |
| RN08 - Só ordens firmes e liberadas são recebimentos programados | `mrp.calcular_mrp` apaga as PLANEJADAS e recalcula. |
| RN09 - Carga do centro | `capacidade.calcular_carga`. |
| RN10 - Kardex nunca é excluído | Nenhuma função apaga movimentos. Correções são feitas por AJUSTE. |

---

## Como usar (ciclo completo)

1. **Cadastros (1):** itens, estrutura de produto, centros e roteiros. A base de
   demonstração já vem pronta.
2. **Estoque (2):** dê entrada nos materiais (opção 1, tipo E, informando o
   documento, por exemplo "NF 1234").
3. **MPS (3):** cadastre ou altere a demanda dos produtos acabados para as 8
   semanas.
4. **Executar MRP (4 > 1):** o sistema calcula e gera as ordens planejadas.
   Depois é possível ver o registro de qualquer item (4 > 2).
5. **Ordens (5):** firmar (F), liberar (L) e depois apontar a produção (A).
   Ordens de compra são encerradas com E, que dá entrada do material no estoque.
6. **Conferir (2 > 2):** o kardex mostra o estoque atualizado.
7. **CRP (6), custo padrão (7), CSV (8) e gráficos (9)** podem ser usados a
   qualquer momento depois do MRP.

Para voltar a base de demonstração ao estado original, use
`git checkout data` (restaura os arquivos da pasta `data/` do último commit).

---

## Base de demonstração (RNF09)

| Tipo | Itens |
|------|-------|
| Produtos acabados | PA-001 Bicicleta Aro 29 MTB, PA-002 Bicicleta Aro 29 Urbana |
| Semiacabados | SA-010 Quadro aro 29 soldado, SA-020 Roda aro 29 montada |
| Matérias-primas | MP-100, MP-101, MP-200, MP-201, MP-202, MP-300, MP-301, MP-302 |
| Centros de trabalho | CT-01 Soldagem e pintura, CT-02 Montagem de rodas, CT-03 Montagem final |

## Arquivos de dados (`data/`)

| Arquivo | Conteúdo |
|---------|----------|
| `itens.json` | Cadastro dos itens |
| `estrutura.json` | Componentes de cada item pai e quantidade por unidade |
| `estoque.json` | Saldo atual de cada item |
| `movimentos.csv` | Kardex: data, item, tipo, quantidade, saldo e documento |
| `centros.json` | Capacidade (h/semana) e custo-hora de cada centro |
| `roteiros.json` | Centro que fabrica cada item e tempo por unidade |
| `mps.json` | Demanda semanal de cada produto acabado |
| `ordens.json` | Ordens de produção e de compra |
| `mrp.json` | Último cálculo do MRP (registro de cada item) |

---

## Decisões de projeto

- **Programação estruturada, sem classes.** Cada módulo é um conjunto de
  funções que trabalham sobre listas e dicionários.
- **Um dicionário único chamado `dados`.** `persistencia.carregar_dados()` lê
  todos os arquivos ao iniciar. Os módulos recebem esse dicionário, alteram e
  gravam só a parte que mudou com `salvar_dados(dados, "estoque")`. Assim,
  cada operação já fica salva no disco.
- **Separação entre menu e regra de negócio.** O `menu.py` só pergunta e chama
  funções. As regras ficam nos módulos de cada assunto.
- **Recursão** na árvore indentada da BOM (`estrutura.desenhar_arvore`) e no
  custo padrão (`custos.custo_padrao`).
- **Validação de entradas** em `utils.py`: as funções `ler_*` repetem a
  pergunta até a resposta ser válida.
- **Custo de PA e SA:** não é digitado no cadastro. O custo é calculado pelo
  custo padrão (materiais mais mão de obra), percorrendo a estrutura.
- **Ordens atrasadas:** ficam com status PLANEJADA e uma marca de atraso. A
  tela mostra "ATRASADA", e a ordem ainda pode ser firmada.
- **Ordens firmes e liberadas pesam nos componentes.** Além de entrarem como
  recebimentos programados, elas ainda vão consumir material, então entram na
  necessidade bruta dos componentes. Ordem atrasada conta na semana 1.
- **Encerrar uma OC** dá entrada do material no estoque (o recebimento). Uma OP
  só é encerrada pelo apontamento de produção.
- **Apontamento seguro:** confere todos os componentes antes de alterar
  qualquer saldo. Se faltar um, rejeita tudo.
- **CRP:** conta as OPs em aberto (planejadas, firmes e liberadas) pela semana
  de liberação, para enxergar a sobrecarga antes de liberar. A constante
  `STATUS_NA_CARGA` em `capacidade.py` permite mudar isso.
- **Gráfico de ordens:** conta ordens por semana, e não quantidades, porque
  somar peças com metros e litros não faz sentido.
- **CSV:** usa ponto e vírgula e vírgula decimal, para abrir direito no Excel
  em português.

## Limitações e melhorias futuras

- Roteiro de operação única, como pede o enunciado.
- Não há interface gráfica nem previsão de demanda com IA.
- Possíveis melhorias: interface gráfica (Tkinter ou Streamlit), previsão de
  demanda e controle de fornecedores.