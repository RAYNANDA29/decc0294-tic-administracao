#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
 SIMULACAO DE DADOS DE RECURSOS HUMANOS - COCA-COLA - 200 FUNCIONARIOS
 DECC0294 - Tecnologia da Informacao e Comunicacao Aplicada a Administracao
 UFMA - Curso de Administracao - 2026.2
=============================================================================

O QUE ESTE ARQUIVO E
    Um gerador de base de dados de RH ficticia. Sao 200 funcionarios, sete
    tabelas relacionadas e um conjunto de defeitos de qualidade inseridos de
    proposito, para uso nas praticas dos modulos 5 a 8 da disciplina.

    AVISO
    Nenhum registro corresponde a pessoa real. Nome, CPF, CNPJ, salario,
    avaliacao e historico profissional sao sinteticos, gerados por sorteio com
    semente fixa. A base serve para treino de analise. Nao use, e nao reutilize,
    estes numeros para decidir sobre gente.

COMO USAR (peca ao agente, no opencode desktop)

    1) "execute simulacao-rh.py com o comando gerar"
       Cria as sete tabelas em dados/ e mostra um resumo no terminal.

    2) "execute simulacao-rh.py com o comando dicionario"
       Grava dados/rh-dicionario-de-dados.md com o significado de cada coluna.

    3) "execute simulacao-rh.py com o comando ficha EMP0042"
       Mostra a ficha completa de um funcionario, com avaliacoes, treinamentos
       e ausencias.

    4) "execute simulacao-rh.py com o comando defeitos"
       Lista os defeitos que foram inseridos de proposito, com arquivo, linha e
       coluna. Use depois de entregar a atividade, para conferir o que achou.

    Sem nenhum comando, o script imprime estas instrucoes.

O QUE O SCRIPT NAO FAZ
    Nao usa rede, nao instala nada, nao le dado de fora e nao sobrescreve arquivo
    sem avisar. A semente e fixa e a data de referencia e fixa: rodar duas vezes
    devolve sempre os mesmos 200 funcionarios, e por isso qualquer numero da
    analise fica reproduzivel.

AS TABELAS QUE ELE CRIA
    dados/rh-funcionarios.csv    201 linhas para 200 pessoas, uma linha e uma
                                  pessoa. A linha a mais e uma duplicata exata.
    dados/rh-departamentos.csv   13 departamentos, com orcamento e quadro
    dados/rh-cargos.csv          78 cargos, com familia e faixa salarial
    dados/rh-unidades.csv        18 unidades de negocio, com centro de custo
    dados/rh-avaliacoes.csv      avaliacoes de dois ciclos, de gestor, de
                                  autoavaliacao e de calibracao
    dados/rh-treinamentos.csv    inscricoes em cursos de 2025
    dados/rh-ausencias.csv       ferias, atestados e faltas de 12 meses

ONDE ISSO ENTRA NA DISCIPLINA
    Modulo 5  as sete tabelas sao as fontes do mapa de dados
    Modulo 6  "perfil dados/rh-funcionarios.csv" e "atipicos" ja com defeito
    Modulo 7  "banco" com varias tabelas e "juntar" pela chave matricula
    Modulo 8  painel de rotatividade, salario por area e headcount por unidade

Nao precisa instalar nada. Roda com o Python que ja vem com o ambiente.
=============================================================================
"""

import csv
import os
import random
import statistics
import sys
from datetime import date, timedelta

PASTA = "dados"
SEP = ";"
COD = "utf-8-sig"
QTD = 200
SEMENTE = 20260929
HOJE = date(2026, 9, 29)
DOMINIO = "coca-cola.com.br"


# ---------------------------------------------------------------- utilidades

def titulo(t):
    print()
    print("=" * 74)
    print(" " + t)
    print("=" * 74)


def brl(v):
    """Grava numero no formato brasileiro, com duas casas."""
    v = round(float(v), 2)
    sinal = "-" if v < 0 else ""
    v = abs(v)
    inteiro = int(v)
    centavos = int(round((v - inteiro) * 100))
    if centavos >= 100:
        inteiro += 1
        centavos -= 100
    return "%s%s,%02d" % (sinal, "{:,}".format(inteiro).replace(",", "."), centavos)


def num(v, casas=1):
    """Grava decimal no formato brasileiro, sem separador de milhar."""
    return ("%%.%df" % casas % float(v)).replace(".", ",")


def para_iso(d):
    return d.strftime("%Y-%m-%d")


def para_br(d):
    return d.strftime("%d/%m/%Y")


def idade_de(d, ref=HOJE):
    return ref.year - d.year - ((ref.month, ref.day) < (d.month, d.day))


def cpf_sintetico(rnd):
    """Monta um CPF que passa no digito verificador. Nao e de ninguem real."""
    d = [rnd.randint(0, 9) for _ in range(9)]
    for _ in range(2):
        s = sum(d[i] * (10 - i) for i in range(len(d)))
        r = (s * 10) % 11
        d.append(0 if r == 10 else r)
    b = "".join(str(x) for x in d)
    return "%s.%s.%s-%s" % (b[0:3], b[3:6], b[6:9], b[9:11])


def cnpj_sintetico(rnd):
    """Monta um CNPJ que passa no digito verificador."""
    d = [rnd.randint(0, 9) for _ in range(8)] + [0, 0, 0, 1]
    for pesos in ([5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2],
                  [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]):
        s = sum(d[i] * pesos[i] for i in range(len(pesos)))
        r = s % 11
        d.append(0 if r < 2 else 11 - r)
    b = "".join(str(x) for x in d)
    return "%s.%s.%s/%s-%s" % (b[0:2], b[2:5], b[5:8], b[8:12], b[12:14])


def email_de(nome, sobrenomes):
    return "%s.%s@%s" % (nome.split()[0].lower(), sobrenomes[-1].lower(), DOMINIO)


def valor_brl_para_float(t):
    """Le o valor gravado em formato brasileiro e devolve float."""
    t = str(t).strip()
    if not t:
        return None
    t = t.replace("R$", "").strip()
    if t.count(",") == 1:
        t = t.replace(".", "").replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None


# ------------------------------------------------------------------ catalogos

NIVEL = {
    1: ("Estagiario", 1600.0, 2400.0, "Ensino medio"),
    2: ("Assistente", 2100.0, 3400.0, "Ensino medio"),
    3: ("Analista", 3800.0, 6800.0, "Ensino superior"),
    4: ("Especialista", 6200.0, 10500.0, "Ensino superior"),
    5: ("Coordenador", 10500.0, 17500.0, "Ensino superior"),
    6: ("Gerente", 17000.0, 29000.0, "Ensino superior"),
    7: ("Diretor", 32000.0, 48000.0, "Pos-graduacao"),
    8: ("Presidente", 85000.0, 120000.0, "Pos-graduacao"),
}

QUANTIDADE = {1: 12, 2: 32, 3: 78, 4: 34, 5: 25, 6: 14, 7: 4, 8: 1}

# nivel: (cargo, departamento, peso no sorteio)
CARGOS_POR_NIVEL = {
    8: [("Presidente", "Presidencia", 1)],
    7: [("Diretor de Vendas", "Vendas", 1),
        ("Diretor de Marketing", "Marketing", 1),
        ("Diretor de Distribuicao e Logistica", "Logistica", 1),
        ("Diretor de Recursos Humanos", "Recursos Humanos", 1),
        ("Diretor Financeiro", "Financeiro", 1),
        ("Diretor de Tecnologia da Informacao", "Tecnologia da Informacao", 1)],
    6: [("Gerente de Vendas Regional", "Vendas", 2),
        ("Gerente de Grandes Contas", "Vendas", 1),
        ("Gerente de Trade Marketing", "Marketing", 2),
        ("Gerente de Distribuicao", "Logistica", 2),
        ("Gerente de Producao e Qualidade", "Qualidade", 2),
        ("Gerente de Recursos Humanos", "Recursos Humanos", 1),
        ("Gerente Financeiro", "Financeiro", 1),
        ("Gerente de Tecnologia da Informacao", "Tecnologia da Informacao", 1),
        ("Gerente de Comunicacao Corporativa", "Comunicacao", 1),
        ("Gerente de Sustentabilidade", "Sustentabilidade", 1),
        ("Gerente de Customer Service", "Atendimento", 1),
        ("Gerente de Assuntos Corporativos e Juridico", "Juridico", 1),
        ("Gerente de Compra e Suprimentos", "Compras", 1)],
    5: [("Coordenador de Vendas", "Vendas", 3),
        ("Coordenador de Distribuicao", "Logistica", 2),
        ("Coordenador de Trade Marketing", "Marketing", 2),
        ("Coordenador de Producao", "Qualidade", 1),
        ("Coordenador de Qualidade", "Qualidade", 1),
        ("Coordenador de Recrutamento e Selecao", "Recursos Humanos", 1),
        ("Coordenador de Desenvolvimento Organizacional", "Recursos Humanos", 1),
        ("Coordenador de Folha e Beneficios", "Recursos Humanos", 1),
        ("Coordenador de Controle Financeiro", "Financeiro", 2),
        ("Coordenador de Sistemas", "Tecnologia da Informacao", 2),
        ("Coordenador de Logistica", "Logistica", 1),
        ("Coordenador de Atendimento ao Consumidor", "Atendimento", 1),
        ("Coordenador de Comunicacao", "Comunicacao", 1),
        ("Coordenador de Sustentabilidade", "Sustentabilidade", 1),
        ("Coordenador de Compras", "Compras", 1)],
    4: [("Especialista em Trade Marketing", "Marketing", 3),
        ("Especialista em Dados e Analytics", "Tecnologia da Informacao", 3),
        ("Especialista em Recrutamento", "Recursos Humanos", 2),
        ("Especialista em Qualidade", "Qualidade", 2),
        ("Especialista em Logistica", "Logistica", 2),
        ("Especialista em Marketing Digital", "Marketing", 2),
        ("Especialista em Customer Service", "Atendimento", 2),
        ("Especialista em Financas", "Financeiro", 2),
        ("Especialista em Saude e Seguranca do Trabalho", "Qualidade", 2),
        ("Especialista em Assuntos Regulatorios", "Juridico", 2),
        ("Especialista em Comunicacao", "Comunicacao", 2),
        ("Especialista em Sustentabilidade", "Sustentabilidade", 2),
        ("Especialista em Compras", "Compras", 2),
        ("Especialista em Governanca de Dados", "Tecnologia da Informacao", 2)],
    3: [("Analista de Vendas", "Vendas", 10),
        ("Analista de Marketing", "Marketing", 3),
        ("Analista Financeiro", "Financeiro", 3),
        ("Analista de Dados", "Tecnologia da Informacao", 3),
        ("Analista de Sistemas", "Tecnologia da Informacao", 3),
        ("Analista de RH", "Recursos Humanos", 3),
        ("Analista de Qualidade", "Qualidade", 2),
        ("Analista de Distribuicao", "Logistica", 3),
        ("Analista de Comunicacao", "Comunicacao", 1),
        ("Analista de Compras", "Compras", 1),
        ("Analista Juridico", "Juridico", 1),
        ("Analista de Atendimento ao Consumidor", "Atendimento", 2),
        ("Analista de Sustentabilidade", "Sustentabilidade", 1),
        ("Analista de Logistica", "Logistica", 2)],
    2: [("Assistente Administrativo", "Vendas", 2),
        ("Assistente de Vendas", "Vendas", 6),
        ("Assistente de RH", "Recursos Humanos", 2),
        ("Assistente Financeiro", "Financeiro", 2),
        ("Assistente de Logistica", "Logistica", 2),
        ("Assistente de Comunicacao", "Comunicacao", 1),
        ("Assistente de Atendimento ao Consumidor", "Atendimento", 2),
        ("Assistente de Compras", "Compras", 1),
        ("Assistente de Qualidade", "Qualidade", 1)],
    1: [("Estagiario de Administracao", "Vendas", 2),
        ("Estagiario de Marketing", "Marketing", 2),
        ("Estagiario de Vendas", "Vendas", 3),
        ("Estagiario de Producao", "Qualidade", 2),
        ("Estagiario de TI", "Tecnologia da Informacao", 2),
        ("Estagiario de Logistica", "Logistica", 1)],
}

MULT_DEP = {
    "Presidencia": 1.00,
    "Vendas": 1.10,
    "Marketing": 1.04,
    "Logistica": 0.93,
    "Qualidade": 0.95,
    "Recursos Humanos": 1.00,
    "Financeiro": 1.09,
    "Tecnologia da Informacao": 1.19,
    "Comunicacao": 1.02,
    "Sustentabilidade": 0.98,
    "Atendimento": 0.86,
    "Juridico": 1.15,
    "Compras": 1.03,
}

MULT_UF = {
    "SP": 1.10, "RJ": 1.08, "DF": 1.06, "PR": 1.03, "RS": 1.03, "SC": 1.00,
    "MG": 0.98, "ES": 0.98, "GO": 0.97, "MT": 0.95, "PE": 0.96, "BA": 0.96,
    "CE": 0.96, "MA": 0.94, "PA": 0.94, "AM": 0.98,
}

# unidade, cidade, uf, regiao, centro de custo, peso no sorteio
UNIDADES = [
    ("Matriz - Sao Paulo", "Sao Paulo", "SP", "Sudeste", "CC-1000", 14),
    ("Grande Sao Paulo", "Sao Paulo", "SP", "Sudeste", "CC-1100", 13),
    ("Interior de Sao Paulo", "Campinas", "SP", "Sudeste", "CC-1200", 9),
    ("Rio de Janeiro", "Rio de Janeiro", "RJ", "Sudeste", "CC-2100", 9),
    ("Minas Gerais", "Belo Horizonte", "MG", "Sudeste", "CC-2200", 8),
    ("Espirito Santo", "Vitoria", "ES", "Sudeste", "CC-2300", 4),
    ("Brasilia e Entorno", "Brasilia", "DF", "Centro-Oeste", "CC-3100", 9),
    ("Goias", "Goiania", "GO", "Centro-Oeste", "CC-3200", 6),
    ("Mato Grosso", "Cuiaba", "MT", "Centro-Oeste", "CC-3300", 4),
    ("Parana", "Curitiba", "PR", "Sul", "CC-4100", 8),
    ("Rio Grande do Sul", "Porto Alegre", "RS", "Sul", "CC-4200", 7),
    ("Santa Catarina", "Florianopolis", "SC", "Sul", "CC-4300", 4),
    ("Pernambuco", "Recife", "PE", "Nordeste", "CC-5100", 6),
    ("Bahia", "Salvador", "BA", "Nordeste", "CC-5200", 7),
    ("Ceara", "Fortaleza", "CE", "Nordeste", "CC-5300", 5),
    ("Maranhao", "Sao Luis", "MA", "Nordeste", "CC-5400", 4),
    ("Para", "Belem", "PA", "Norte", "CC-6100", 4),
    ("Amazonas", "Manaus", "AM", "Norte", "CC-6200", 3),
]

PRIMEIROS_F = [
    "Alice", "Ana", "Beatriz", "Bianca", "Camila", "Carolina", "Clara", "Daniela",
    "Debora", "Eduarda", "Eliane", "Fernanda", "Francisca", "Gabriela", "Helena",
    "Heloisa", "Ingrid", "Isabel", "Isabelly", "Josefa", "Juliana", "Larissa",
    "Leticia", "Luana", "Luiza", "Mariana", "Marina", "Michele", "Natalia",
    "Olivia", "Patricia", "Paula", "Rafaela", "Renata", "Sabrina", "Sandra", "Sara",
    "Sofia", "Talita", "Tatiana", "Ursula", "Valentina", "Vanessa", "Vitoria",
    "Yasmin", "Zilda", "Aline", "Bruna", "Cristina", "Ester", "Fatima", "Giliane",
    "Isadora", "Laurinha", "Marcela", "Nubia", "Olvia", "Priscila", "Rosana",
]

PRIMEIROS_M = [
    "Alan", "Andre", "Antonio", "Bruno", "Caio", "Carlos", "Daniel", "Diego",
    "Douglas", "Edson", "Eduardo", "Elias", "Emerson", "Everton", "Fabio",
    "Felipe", "Fernando", "Flavio", "Francisco", "Gabriel", "Geraldo", "Gustavo",
    "Heitor", "Helio", "Henrique", "Ivo", "Joao", "Jonas", "Jose", "Leandro",
    "Luciano", "Lucas", "Luiz", "Marcelo", "Marcos", "Mateus", "Miguel", "Murilo",
    "Nilton", "Otavio", "Paulo", "Pedro", "Rafael", "Ricardo", "Roberto",
    "Rodrigo", "Samuel", "Sergio", "Thiago", "Vinicius", "Vitor", "Wagner",
    "Wallace", "Wellington",
]

SOBRENOMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves",
    "Pereira", "Lima", "Gomes", "Ribeiro", "Martins", "Carvalho", "Almeida",
    "Lopes", "Soares", "Fernandes", "Vieira", "Barbosa", "Rocha", "Dias",
    "Nascimento", "Andrade", "Moreira", "Nunes", "Marques", "Machado", "Mendes",
    "Freitas", "Cardoso", "Ramos", "Goncalves", "Santana", "Teixeira", "Correia",
    "Azevedo", "Pinto", "Cunha", "Farias", "Melo", "Araujo", "Monteiro",
    "Fonseca", "Macedo", "Duarte", "Pinheiro", "Bezerra", "Moura", "Xavier",
    "Bastos", "Campos", "Guimaraes", "Medeiros", "Aparecida", "Cardoso", "Castro",
]

ESTADO_CIVIL = ["Solteiro(a)", "Casado(a)", "Uniao estavel", "Divorciado(a)",
                "Viuvo(a)"]

ORIGEM = ["Portal de carreiras", "Indicacao de colega", "Banco de talentos",
          "Universidade", "Agencia de recrutamento", "Processo seletivo interno",
          "Feira de carreiras"]

CURSOS = [
    ("TRN-101", "Seguranca do Trabalho e Uso de EPI", "Seguranca do Trabalho", 8),
    ("TRN-102", "Direitos Trabalhistas na Pratica", "Juridico", 12),
    ("TRN-103", "Excel Aplicado a Gestao", "Dados e Tecnologia", 16),
    ("TRN-104", "Analise de Dados com Python", "Dados e Tecnologia", 24),
    ("TRN-105", "Power BI para Decisao Gerencial", "Dados e Tecnologia", 16),
    ("TRN-106", "Negocio de Bebidas e Canais", "Comercial", 12),
    ("TRN-107", "Trade Marketing e Execucao no PDV", "Comercial", 16),
    ("TRN-108", "Gestao de Equipe e Feedback", "Lideranca", 20),
    ("TRN-109", "Lideranca para Coordenadores", "Lideranca", 24),
    ("TRN-110", "Sucessao e Plano de Carreira", "Lideranca", 12),
    ("TRN-111", "Atendimento ao Cliente com Qualidade", "Atendimento", 12),
    ("TRN-112", "Logistica de Distribuicao e Rota", "Operacao", 20),
    ("TRN-113", "Manutencao Autonoma de Equipamentos", "Operacao", 16),
    ("TRN-114", "Gestao de Contratos e Compras", "Administracao", 12),
    ("TRN-115", "Orcamento e Controle de Custos", "Administracao", 16),
    ("TRN-116", "Comunicacao Corporativa e Midia", "Comunicacao", 12),
    ("TRN-117", "Sustentabilidade e Coleta Seletiva", "Sustentabilidade", 8),
    ("TRN-118", "LGPD e Protecao de Dados", "Juridico", 8),
    ("TRN-119", "Diversidade, Inclusao e Conduta", "Pessoas", 8),
    ("TRN-120", "Integridade e Compliance", "Juridico", 8),
    ("TRN-121", "Negociacao para Grandes Contas", "Comercial", 20),
    ("TRN-122", "Gestao de Mudanca", "Lideranca", 12),
    ("TRN-123", "Ciclo de Vendas com CRM", "Dados e Tecnologia", 12),
    ("TRN-124", "Primeiros Socorros", "Seguranca do Trabalho", 16),
]

ENTREGAS = [
    "Aumento de {n}% no volume da regiao apos a campanha de verao",
    "Reduziu {n} dias de estoque parado no centro de distribuicao",
    "Concluiu a migracao de {n} usuarios para o novo sistema de vendas",
    "Renegociou {n} contratos de foodservice no setor de mineracao",
    "Premiacao da equipe como melhor resultado trimestral do ano",
    "Reduziu o indice de ruptura de {n}% para menos de 3%",
    "Implantou a rota de entrega {n} no interior da unidade",
    "Treinou {n} novos profissionais e reduziu o turnover da regiao",
    "Abriu {n} novos pontos de venda no canal de foodservice",
    "Adequou o processo ao checklist de auditoria, com {n} nao conformidades",
    "Entregou o planejamento de demanda com {n} semanas de antecipacao",
    "Recuperou R$ {n} mil de contas a receber em atraso",
]

# (indice da linha de dados, coluna, tipo do defeito, descricao do que foi gravado)
# O indice 0 e a primeira linha depois do cabecalho, ou seja, a linha 2 do arquivo.
DEFEITOS = [
    (34, "salario_base", "unidade trocada",
     "salario gravado em milhar: o valor da linha foi dividido por mil"),
    (111, "salario_base", "unidade trocada",
     "salario gravado em milhar: o valor da linha foi dividido por mil"),
    (176, "salario_base", "unidade trocada",
     "salario gravado em milhar: o valor da linha foi dividido por mil"),
    (88, "salario_base", "erro de registro",
     "salario negativo: -4.500,00"),
    (30, "bonus_anual", "salario sem acrescimo",
     "remuneracao_total ficou menor que salario_base, porque o bonus saiu negativo"),
    (5, "escolaridade", "ausente por regra",
     "campo obrigatorio do cadastro ficou vazio"),
    (66, "escolaridade", "ausente por regra",
     "campo obrigatorio do cadastro ficou vazio"),
    (141, "escolaridade", "ausente por regra",
     "campo obrigatorio do cadastro ficou vazio"),
    (12, "horas_treinamento_2025", "ausente ao acaso",
     "campo de horas de treinamento ficou vazio"),
    (45, "horas_treinamento_2025", "ausente ao acaso",
     "campo de horas de treinamento ficou vazio"),
    (78, "horas_treinamento_2025", "ausente ao acaso",
     "campo de horas de treinamento ficou vazio"),
    (133, "horas_treinamento_2025", "ausente ao acaso",
     "campo de horas de treinamento ficou vazio"),
    (190, "horas_treinamento_2025", "ausente ao acaso",
     "campo de horas de treinamento ficou vazio"),
    (91, "bonus_anual", "ausente ao acaso", "campo de bonus ficou vazio"),
    (152, "bonus_anual", "ausente ao acaso", "campo de bonus ficou vazio"),
    (23, "e_nps", "ausente ao acaso", "campo de engajamento ficou vazio"),
    (108, "e_nps", "ausente ao acaso", "campo de engajamento ficou vazio"),
    (21, "departamento", "caixa inconsistente",
     "departamento gravado em caixa alta"),
    (57, "departamento", "caixa inconsistente",
     "departamento gravado em caixa alta"),
    (93, "departamento", "caixa inconsistente",
     "departamento gravado em caixa alta"),
    (129, "departamento", "caixa inconsistente",
     "departamento gravado em caixa alta"),
    (165, "departamento", "caixa inconsistente",
     "departamento gravado em caixa alta"),
    (198, "departamento", "caixa inconsistente",
     "departamento gravado em caixa alta"),
    (40, "cargo", "caixa inconsistente", "cargo gravado em caixa baixa"),
    (84, "cargo", "caixa inconsistente", "cargo gravado em caixa baixa"),
    (150, "cargo", "caixa inconsistente", "cargo gravado em caixa baixa"),
    (3, "data_nascimento", "formato de data",
     "data em dd/mm/aaaa, com o resto da coluna em aaaa-mm-dd"),
    (17, "data_nascimento", "formato de data",
     "data em dd/mm/aaaa, com o resto da coluna em aaaa-mm-dd"),
    (44, "data_nascimento", "formato de data",
     "data em dd/mm/aaaa, com o resto da coluna em aaaa-mm-dd"),
    (71, "data_nascimento", "formato de data",
     "data em dd/mm/aaaa, com o resto da coluna em aaaa-mm-dd"),
    (99, "data_nascimento", "formato de data",
     "data em dd/mm/aaaa, com o resto da coluna em aaaa-mm-dd"),
    (122, "data_nascimento", "formato de data",
     "data em dd/mm/aaaa, com o resto da coluna em aaaa-mm-dd"),
    (160, "data_nascimento", "formato de data",
     "data em dd/mm/aaaa, com o resto da coluna em aaaa-mm-dd"),
    (185, "data_nascimento", "formato de data",
     "data em dd/mm/aaaa, com o resto da coluna em aaaa-mm-dd"),
    (9, "data_admissao", "formato de data",
     "data em dd/mm/aaaa, com o resto da coluna em aaaa-mm-dd"),
    (61, "data_admissao", "formato de data",
     "data em dd/mm/aaaa, com o resto da coluna em aaaa-mm-dd"),
    (118, "data_admissao", "formato de data",
     "data em dd/mm/aaaa, com o resto da coluna em aaaa-mm-dd"),
    (172, "data_admissao", "formato de data",
     "data em dd/mm/aaaa, com o resto da coluna em aaaa-mm-dd"),
    (7, "cpf", "formato de texto", "CPF gravado so com digitos, sem pontos e hifen"),
    (55, "cpf", "formato de texto", "CPF gravado so com digitos, sem pontos e hifen"),
    (137, "cpf", "formato de texto",
     "CPF gravado so com digitos, sem pontos e hifen"),
    (168, "cpf", "duplicidade de chave",
     "mesmo CPF do funcionario da linha 14, com matricula e historico diferentes"),
    (181, "cpf", "duplicidade de chave",
     "mesmo CPF do funcionario da linha 40, com matricula e historico diferentes"),
    (26, "email_corporativo", "erro de registro",
     "e-mail pessoal gravado no campo de e-mail corporativo"),
    (143, "email_corporativo", "erro de registro",
     "e-mail pessoal gravado no campo de e-mail corporativo"),
    (99, "email_corporativo", "valor repetido",
     "e-mail corporativo igual ao da linha 102, com nome diferente"),
    (36, "idade", "contrato entre colunas",
     "idade nao bate com a data de nascimento da propria linha"),
    (70, "jornada_horas", "erro de registro", "jornada gravada com 0 hora"),
    (84, "meta_cumprida_percentual", "atipico por escala",
     "meta cumprida em 320% no ciclo, contra menos de 100% na maior parte da base"),
    (115, "faltas_2025", "atipico por escala",
     "47 faltas em 12 meses, contra 1 ou 2 na maior parte da base"),
    (128, "data_demissao", "data impossivel",
     "data de demissao anterior a data de admissao"),
    (45, "tempo_empresa_anos", "contrato entre colunas",
     "tempo de empresa nao bate com a data de admissao da propria linha"),
    (30, "linha inteira", "duplicata exata",
     "a linha 32 foi repetida no fim do arquivo, sem matricula nova"),
]

COLS_FUNCIONARIOS = [
    "matricula", "nome_completo", "cpf", "data_nascimento", "idade", "sexo",
    "estado_civil", "escolaridade", "dependentes", "email_corporativo",
    "departamento", "cargo", "nivel", "familia_cargo", "unidade_negocio",
    "cidade", "uf", "regiao", "centro_custo", "modelo_contrato", "jornada_horas",
    "data_admissao", "data_demissao", "tempo_empresa_anos", "gestor_matricula",
    "gestor_nome", "status", "salario_base", "bonus_anual", "remuneracao_total",
    "valor_plano_saude", "valor_vale_alimentacao", "valor_vale_transporte",
    "plano_saude", "previdencia_complementar", "nota_desempenho",
    "meta_cumprida_percentual", "e_nps", "horas_treinamento_2025", "faltas_2025",
    "dias_afastamento_2025", "turnover_12m", "origem_recrutamento",
]

COLS_DEPARTAMENTOS = [
    "departamento", "descricao", "responsavel", "orcamento_anual",
    "headcount_efetivo", "headcount_orcado", "criado_em", "centro_custo",
]

COLS_CARGOS = [
    "cargo", "nivel", "familia_cargo", "departamento_referencial",
    "escolaridade_minima", "faixa_salarial_minima", "faixa_salarial_maxima",
    "vale_refeicao", "cargo_de_confianca",
]

COLS_UNIDADES = [
    "unidade_negocio", "descricao", "cidade", "uf", "regiao", "centro_custo",
    "cnpj", "matricula_gestor", "headcount_orcado", "data_inauguracao",
]

COLS_AVALIACOES = [
    "id_avaliacao", "matricula", "ciclo", "data_avaliacao", "tipo_avaliacao",
    "avaliador_matricula", "avaliador_nome", "nota", "meta_percentual", "peso",
    "principais_entregas", "status_registro",
]

COLS_TREINAMENTOS = [
    "id_treinamento", "matricula", "codigo_curso", "titulo_curso", "categoria",
    "data_inscricao", "data_conclusao", "carga_horaria", "status_curso",
    "nota_avaliacao", "investimento",
]

COLS_AUSENCIAS = [
    "id_ausencia", "matricula", "data_inicio", "data_fim", "tipo_ausencia",
    "dias_utilis", "motivo", "comprovacao", "abono",
]

TABELAS = [
    ("rh-funcionarios.csv", COLS_FUNCIONARIOS),
    ("rh-departamentos.csv", COLS_DEPARTAMENTOS),
    ("rh-cargos.csv", COLS_CARGOS),
    ("rh-unidades.csv", COLS_UNIDADES),
    ("rh-avaliacoes.csv", COLS_AVALIACOES),
    ("rh-treinamentos.csv", COLS_TREINAMENTOS),
    ("rh-ausencias.csv", COLS_AUSENCIAS),
]


# --------------------------------------------------------------- construcao

def sorteia_cargos(rnd):
    """Escolhe 200 cargos, na ordem do nivel mais alto para o mais baixo."""
    escolhidos = []
    for rank in sorted(QUANTIDADE, reverse=True):
        pool = []
        for cargo, dep, peso in CARGOS_POR_NIVEL[rank]:
            pool.extend([(rank, cargo, dep)] * peso)
        if len(pool) < QUANTIDADE[rank]:
            pool = pool * (QUANTIDADE[rank] // len(pool) + 1)
        rnd.shuffle(pool)
        escolhidos.extend(pool[:QUANTIDADE[rank]])
    return escolhidos


def escolhe_unidade(rnd, rank):
    """Lideranca fica concentrada na matriz, operacao se distribui no pais."""
    if rnd.random() < {8: 0.90, 7: 0.70, 6: 0.45, 5: 0.28, 4: 0.18}.get(rank, 0.12):
        return UNIDADES[0]
    pool = []
    for u in UNIDADES[1:]:
        pool.extend([u] * u[5])
    return rnd.choice(pool)


def sorteia_nome(rnd, usados):
    for _ in range(500):
        sexo = "F" if rnd.random() < 0.48 else "M"
        primeiro = rnd.choice(PRIMEIROS_F if sexo == "F" else PRIMEIROS_M)
        quantos = 1 if rnd.random() < 0.55 else 2
        sobrenomes = []
        for _ in range(quantos):
            s = rnd.choice(SOBRENOMES)
            if s not in sobrenomes:
                sobrenomes.append(s)
        nome = " ".join([primeiro] + sobrenomes)
        if nome not in usados:
            usados.add(nome)
            return nome, sexo, sobrenomes
    raise RuntimeError("nao foi possivel sortear nome unico")


def sorteia_admissao(rnd, nascimento):
    """Admissao valida: maior de 21 anos na data, com tempo de empresa sorteado."""
    minimo = date(nascimento.year + 21, nascimento.month, min(nascimento.day, 28))
    faixa = rnd.random()
    if faixa < 0.18:
        anos = rnd.randint(0, 1)
    elif faixa < 0.55:
        anos = rnd.randint(2, 6)
    elif faixa < 0.85:
        anos = rnd.randint(7, 13)
    else:
        anos = rnd.randint(14, 20)
    fim = date(HOJE.year - anos, HOJE.month, 1)
    inicio = date(HOJE.year - anos - 1, HOJE.month, 1)
    if fim <= minimo:
        fim = date(HOJE.year, HOJE.month, 1)
    if inicio < minimo:
        inicio = minimo
    if fim <= inicio:
        return minimo
    return inicio + timedelta(days=rnd.randint(0, (fim - inicio).days))


def construir_funcionarios(rnd):
    escolhidos = sorteia_cargos(rnd)
    usados = set()
    pessoas = []

    for i, (rank, cargo, departamento) in enumerate(escolhidos):
        nome, sexo, sobrenomes = sorteia_nome(rnd, usados)
        # de 22 a 60 anos: com 21 anos ja e possivel ter sido admitida
        nascimento = HOJE - timedelta(days=rnd.randint(8040, 22000))
        admissao = sorteia_admissao(rnd, nascimento)
        unidade, cidade, uf, regiao, centro, _ = escolhe_unidade(rnd, rank)
        salario = rnd.uniform(NIVEL[rank][1], NIVEL[rank][2])
        salario *= MULT_DEP.get(departamento, 1.0)
        salario *= MULT_UF.get(uf, 0.96)
        salario *= rnd.uniform(0.94, 1.08)
        salario = round(salario / 10.0) * 10.0

        if rank == 1:
            bonus = 0.0
        elif rank == 2:
            bonus = 0.0
        elif rank == 3:
            bonus = salario * rnd.uniform(0.04, 0.12)
        elif rank == 4:
            bonus = salario * rnd.uniform(0.08, 0.18)
        elif rank == 5:
            bonus = salario * rnd.uniform(0.15, 0.30)
        else:
            bonus = salario * rnd.uniform(0.25, 0.60)
        bonus = round(bonus / 10.0) * 10.0

        dependentes = rnd.choice([0, 0, 0, 1, 1, 1, 2, 2, 3])
        plano = "nao" if rnd.random() < 0.12 else "sim"
        desempenho = int(min(5, max(1, round(rnd.gauss(3.3, 0.7) + (rank - 3) * 0.10))))
        # vale transporte so existe nas capitais e nos niveis de execucao
        vale_transporte = 0.0
        if rank <= 3 and uf in ("SP", "RJ", "DF", "MG", "BA", "PE", "CE"):
            vale_transporte = rnd.randrange(22000, 40000, 500) / 100.0

        pessoas.append({
            "_rank": rank,
            "matricula": "EMP%04d" % (i + 1),
            "nome_completo": nome,
            "cpf": cpf_sintetico(rnd),
            "data_nascimento": para_iso(nascimento),
            "idade": idade_de(nascimento),
            "sexo": sexo,
            "estado_civil": rnd.choice(ESTADO_CIVIL),
            "escolaridade": (NIVEL[rank][3] if rank >= 3
                             else rnd.choice(["Ensino medio", "Ensino superior"])),
            "dependentes": dependentes,
            "email_corporativo": email_de(nome, sobrenomes),
            "departamento": departamento,
            "cargo": cargo,
            "nivel": NIVEL[rank][0],
            "familia_cargo": ("Diretoria" if rank >= 7 else
                              "Gestao" if rank in (5, 6) else
                              "Tecnica" if rank == 4 else
                              "Analise" if rank == 3 else "Apoio"),
            "unidade_negocio": unidade,
            "cidade": cidade,
            "uf": uf,
            "regiao": regiao,
            "centro_custo": centro,
            "modelo_contrato": "CLT",
            "jornada_horas": 30 if rank == 1 else 40,
            "data_admissao": para_iso(admissao),
            "data_demissao": "",
            "tempo_empresa_anos": num((HOJE - admissao).days / 365.25, 1),
            "gestor_matricula": "",
            "gestor_nome": "",
            "status": "Ativo",
            "salario_base": brl(salario),
            "bonus_anual": brl(bonus),
            "remuneracao_total": brl(salario + bonus),
            "valor_plano_saude": brl(0.0 if plano == "nao" else
                                    rnd.randrange(42000, 98000, 500) / 100.0
                                    * (1 + 0.35 * dependentes)),
            "valor_vale_alimentacao": brl(rnd.randrange(900, 1500, 50)
                                         if rank >= 3 else 800),
            "valor_vale_transporte": brl(vale_transporte),
            "plano_saude": plano,
            "previdencia_complementar": "sim" if (
                (rank >= 5 and rnd.random() < 0.85)
                or (rank == 4 and rnd.random() < 0.45)) else "nao",
            "nota_desempenho": desempenho,
            "meta_cumprida_percentual": num(min(240.0, max(28.0, rnd.gauss(
                98.0, 21.0) + (rank - 3) * 3.0)), 1),
            "e_nps": int(max(-100, min(100, round(rnd.gauss(21, 26)
                                                      + (rank - 3) * 4)))),
            "horas_treinamento_2025": int(max(0, min(160, round(
                rnd.gauss(34, 20) + rank * 4)))),
            "faltas_2025": max(0, int(round(rnd.gauss(2.2, 1.8)
                                             + (1.2 if rank <= 2 else 0)))),
            "dias_afastamento_2025": 0,
            "turnover_12m": "nao",
            "origem_recrutamento": rnd.choice(ORIGEM),
            "_salario": salario,
        })

    montar_hierarquia(rnd, pessoas)
    montar_movimentacao(rnd, pessoas)
    return pessoas


def montar_hierarquia(rnd, pessoas):
    """O gestor vem sempre do nivel imediatamente acima, nunca do mesmo nivel."""
    por_rank = {}
    for p in pessoas:
        por_rank.setdefault(p["_rank"], []).append(p)
    for rank in sorted(QUANTIDADE, reverse=True):
        for p in por_rank[rank]:
            if rank == 8:
                continue
            # estagiario responde a um assistente do proprio departamento
            candidatos = por_rank[2 if rank == 1 else rank - 1]
            mesmos = [c for c in candidatos
                      if c["departamento"] == p["departamento"]]
            if not mesmos:
                mesmos = [c for c in candidatos
                          if c["unidade_negocio"] == p["unidade_negocio"]]
            if not mesmos:
                mesmos = candidatos
            chefe = rnd.choice(mesmos)
            p["gestor_matricula"] = chefe["matricula"]
            p["gestor_nome"] = chefe["nome_completo"]


def montar_movimentacao(rnd, pessoas):
    """15 desligamentos, alguns afastamentos, periodo de experiencia e aviso previo."""
    for p in pessoas:
        admissao = date(*[int(x) for x in p["data_admissao"].split("-")])
        if (HOJE - admissao).days <= 90:
            p["status"] = "Ativo em periodo de experiencia"

    candidatos = [p for p in pessoas if p["status"] == "Ativo"]
    desligados = rnd.sample(candidatos, 15)
    for p in desligados:
        demissao = HOJE - timedelta(days=rnd.randint(20, 340))
        adm = date(*[int(x) for x in p["data_admissao"].split("-")])
        if demissao < adm + timedelta(days=180):
            demissao = adm + timedelta(days=180)
        p["data_demissao"] = para_iso(demissao)
        p["status"] = "Desligado"
        p["turnover_12m"] = "sim"

    for p in rnd.sample([x for x in pessoas if x["status"] == "Ativo"], 4):
        p["status"] = "Aviso previo"
        p["data_demissao"] = para_iso(HOJE + timedelta(days=rnd.randint(10, 45)))

    for p in rnd.sample([x for x in pessoas if x["status"] == "Ativo"], 9):
        p["status"] = "Afastado"


def construir_departamentos(rnd, pessoas):
    """Uma linha por departamento, com o quadro orcado e o efetivo da base."""
    responsavel = {}
    for p in pessoas:
        responsavel.setdefault(p["departamento"], p)
    linhas = []
    for nome in sorted(responsavel):
        efetivo = sum(1 for p in pessoas
                      if p["departamento"] == nome and p["status"] != "Desligado")
        orcado = efetivo + rnd.choice([-2, -1, 0, 0, 1, 1, 2, 3])
        base = rnd.uniform(1.8, 26.0)
        linhas.append({
            "departamento": nome,
            "descricao": "Area de %s do Sistema Coca-Cola" % nome,
            "responsavel": responsavel[nome]["nome_completo"],
            "orcamento_anual": brl(round(base * efetivo * 1000 / 10.0) * 10.0),
            "headcount_efetivo": efetivo,
            "headcount_orcado": max(1, orcado),
            "criado_em": para_iso(HOJE - timedelta(days=rnd.randint(900, 6500))),
            "centro_custo": "CC-" + nome[:2].upper() + "00",
        })
    return linhas


def construir_cargos():
    linhas = []
    for rank in sorted(CARGOS_POR_NIVEL):
        nome_nivel, mini, maxi, escolaridade = NIVEL[rank]
        for cargo, departamento, _ in CARGOS_POR_NIVEL[rank]:
            fator = MULT_DEP.get(departamento, 1.0)
            linhas.append({
                "cargo": cargo,
                "nivel": nome_nivel,
                "familia_cargo": ("Diretoria" if rank >= 7 else
                                  "Gestao" if rank in (5, 6) else
                                  "Tecnica" if rank == 4 else
                                  "Analise" if rank == 3 else "Apoio"),
                "departamento_referencial": departamento,
                "escolaridade_minima": escolaridade,
                "faixa_salarial_minima": brl(mini * fator),
                "faixa_salarial_maxima": brl(maxi * fator),
                "vale_refeicao": "sim",
                "cargo_de_confianca": "sim" if rank >= 5 else "nao",
            })
    return linhas


def construir_unidades(rnd, pessoas):
    linhas = []
    for unidade, cidade, uf, regiao, centro, _ in UNIDADES:
        na_unidade = [p for p in pessoas if p["unidade_negocio"] == unidade]
        gestores = [p for p in na_unidade if p["_rank"] >= 6]
        if not gestores:
            gestores = na_unidade
        gestor = min(gestores, key=lambda p: -p["_rank"]) if gestores else None
        linhas.append({
            "unidade_negocio": unidade,
            "descricao": "Unidade de negocio %s" % unidade,
            "cidade": cidade,
            "uf": uf,
            "regiao": regiao,
            "centro_custo": centro,
            "cnpj": cnpj_sintetico(rnd),
            "matricula_gestor": gestor["matricula"] if gestor else "",
            "headcount_orcado": max(1, len(na_unidade) + rnd.choice([-2, -1, 0, 1, 2])),
            "data_inauguracao": para_iso(HOJE - timedelta(days=rnd.randint(1200, 9000))),
        })
    return linhas


def construir_avaliacoes(rnd, pessoas):
    linhas = []
    n = 0
    for p in pessoas:
        if p["status"] == "Desligado":
            continue
        for ciclo, data in (("2025-S1", date(2025, 7, 10)),
                            ("2025-S2", date(2026, 1, 15))):
            for tipo in ("Avaliacao do Gestor", "Autoavaliacao"):
                n += 1
                gestor = p["gestor_matricula"]
                if tipo == "Avaliacao do Gestor":
                    nota = p["nota_desempenho"]
                    if ciclo == "2025-S1":
                        nota = int(min(5, max(1, nota + rnd.choice([-1, 0, 0, 1]))))
                else:
                    nota = int(min(5, max(1, p["nota_desempenho"]
                                           + rnd.choice([-1, -1, 0, 0, 0, 1, 1]))))
                linhas.append({
                    "id_avaliacao": "AVL%05d" % n,
                    "matricula": p["matricula"],
                    "ciclo": ciclo,
                    "data_avaliacao": para_iso(data),
                    "tipo_avaliacao": tipo,
                    "avaliador_matricula": gestor if tipo == "Avaliacao do Gestor" else "",
                    "avaliador_nome": (p["gestor_nome"]
                                       if tipo == "Avaliacao do Gestor" else ""),
                    "nota": nota,
                    # no ciclo 2025-S2 a avaliacao do gestor fecha com a ficha
                    "meta_percentual": (p["meta_cumprida_percentual"]
                                        if tipo == "Avaliacao do Gestor"
                                        and ciclo == "2025-S2" else
                                        num(max(20.0, min(260.0, rnd.gauss(
                                            float(p["meta_cumprida_percentual"]
                                                  .replace(",", "."))
                                            + (3.0 if tipo == "Autoavaliacao" else 0.0),
                                            18.0))), 1)),
                    "peso": 100 if tipo == "Avaliacao do Gestor" else 0,
                    "principais_entregas": " e ".join(
                        e.replace("{n}", str(rnd.randint(4, 28)))
                        for e in rnd.sample(ENTREGAS, rnd.randint(1, 2))),
                    "status_registro": "Concluida" if rnd.random() < 0.94 else "Pendente",
                })
        if p["_rank"] >= 5 and rnd.random() < 0.55:
            n += 1
            linhas.append({
                "id_avaliacao": "AVL%05d" % n,
                "matricula": p["matricula"],
                "ciclo": "2025-S2",
                "data_avaliacao": para_iso(date(2026, 2, 20)),
                "tipo_avaliacao": "Calibracao 360",
                "avaliador_matricula": "",
                "avaliador_nome": "Comite de calibracao",
                "nota": int(min(5, max(1, p["nota_desempenho"] + rnd.choice([-1, 0, 1])))),
                "meta_percentual": p["meta_cumprida_percentual"],
                "peso": 0,
                "principais_entregas": "Avaliacao cruzada com pares do nivel",
                "status_registro": "Concluida",
            })
    return linhas


def construir_treinamentos(rnd, pessoas):
    linhas = []
    n = 0
    for p in pessoas:
        quantos = rnd.choice([1, 2, 2, 3, 3, 3, 4, 4, 5])
        for _ in range(quantos):
            n += 1
            codigo, titulo, categoria, horas = rnd.choice(CURSOS)
            inscricao = HOJE - timedelta(days=rnd.randint(200, 700))
            status = rnd.choices(
                ["Concluido", "Em andamento", "Nao iniciado", "Cancelado"],
                weights=[0.70, 0.12, 0.10, 0.08])[0]
            if status == "Em andamento":
                conclusao = ""
            else:
                conclusao = para_iso(inscricao + timedelta(days=rnd.randint(7, 90)))
            linhas.append({
                "id_treinamento": "TRN%05d" % n,
                "matricula": p["matricula"],
                "codigo_curso": codigo,
                "titulo_curso": titulo,
                "categoria": categoria,
                "data_inscricao": para_iso(inscricao),
                "data_conclusao": conclusao,
                "carga_horaria": horas,
                "status_curso": status,
                "nota_avaliacao": (int(min(10, max(0, round(rnd.gauss(8.0, 1.4)))))
                                  if status == "Concluido" else ""),
                "investimento": brl(rnd.randrange(0, 160) * 50),
            })
    return linhas


def construir_ausencias(rnd, pessoas):
    """Ferias, atestados e faltas de 12 meses. Soma os dias na propria ficha."""
    linhas = []
    n = 0
    motivos = {
        "Atestado medico": "Atestado apresentado ao gestor",
        "Ferias": "Programacao anual de ferias",
        "Licenca maternidade": "Licenca prevista em lei",
        "Licenca paternal": "Licenca prevista em lei",
        "Falta nao justificada": "Sem comunicacao previa",
        "Banco de horas compensada": "Compensacao de horas extras",
        "Afastamento por doenca": "Afastamento de longo prazo",
    }
    for p in pessoas:
        if p["status"] == "Desligado":
            continue
        eventos = []
        if rnd.random() < 0.86:
            inicio = rnd.choice([date(2025, 1, 6), date(2025, 7, 7),
                                 date(2025, 12, 22)])
            eventos.append(("Ferias", inicio, rnd.randint(12, 25)))
        for _ in range(rnd.choice([0, 0, 1, 1, 1, 2, 2, 3])):
            inicio = HOJE - timedelta(days=rnd.randint(10, 355))
            eventos.append(("Atestado medico", inicio, rnd.randint(1, 9)))
        for _ in range(rnd.choice([0, 0, 0, 0, 0, 0, 1, 2])):
            inicio = HOJE - timedelta(days=rnd.randint(10, 355))
            eventos.append(("Banco de horas compensada", inicio, rnd.randint(1, 2)))
        if p["sexo"] == "F" and p["_rank"] <= 5 and rnd.random() < 0.06:
            inicio = HOJE - timedelta(days=rnd.randint(20, 200))
            eventos.append(("Licenca maternidade", inicio, 120))
        if p["sexo"] == "M" and rnd.random() < 0.04:
            inicio = HOJE - timedelta(days=rnd.randint(20, 300))
            eventos.append(("Licenca paternal", inicio, 20))
        if p["faltas_2025"] >= 5 and rnd.random() < 0.5:
            inicio = HOJE - timedelta(days=rnd.randint(10, 200))
            eventos.append(("Falta nao justificada", inicio, 1))
        if p["status"] == "Afastado" and rnd.random() < 0.7:
            inicio = HOJE - timedelta(days=rnd.randint(40, 300))
            eventos.append(("Afastamento por doenca", inicio, rnd.randint(30, 90)))

        for tipo, inicio, dias in eventos:
            n += 1
            fim = min(inicio + timedelta(days=dias * 2), HOJE)
            linhas.append({
                "id_ausencia": "AUS%05d" % n,
                "matricula": p["matricula"],
                "data_inicio": para_iso(inicio),
                "data_fim": para_iso(fim),
                "tipo_ausencia": tipo,
                "dias_utilis": dias,
                "motivo": motivos[tipo],
                "comprovacao": "nao" if tipo == "Falta nao justificada" else "sim",
                "abono": 1 if tipo in ("Falta nao justificada", "Atestado medico") else 0,
            })
        p["dias_afastamento_2025"] = sum(
            l["dias_utilis"] for l in linhas if l["matricula"] == p["matricula"])
    return linhas


# ------------------------------------------------------------------ defeitos

def aplicar_defeitos(pessoas):
    """Grava os erros de proposito e devolve a lista do que foi alterado."""
    aplicados = []
    for idx, coluna, tipo, descricao in DEFEITOS:
        if coluna == "linha inteira":
            aplicados.append((idx, coluna, tipo, descricao))
            continue
        p = pessoas[idx]
        if coluna == "salario_base" and tipo == "unidade trocada":
            alvo = p["salario_base"]
            p["salario_base"] = num(float(alvo.replace(".", "").replace(",", ".")) / 1000.0, 1)
        elif coluna == "salario_base":
            p["salario_base"] = "-4.500,00"
            p["remuneracao_total"] = "-4.500,00"
        elif coluna == "bonus_anual" and tipo == "salario sem acrescimo":
            p["bonus_anual"] = "-1.200,00"
            p["remuneracao_total"] = brl(
                p["_salario"] - 1200.0)
        elif coluna in ("escolaridade", "horas_treinamento_2025", "bonus_anual",
                        "e_nps"):
            p[coluna] = ""
        elif coluna == "departamento":
            p[coluna] = p[coluna].upper()
        elif coluna == "cargo":
            p[coluna] = p[coluna].lower()
        elif coluna in ("data_nascimento", "data_admissao"):
            d = date(*[int(x) for x in p[coluna].split("-")])
            p[coluna] = para_br(d)
        elif coluna == "cpf" and tipo == "formato de texto":
            p[coluna] = p[coluna].replace(".", "").replace("-", "")
        elif coluna == "cpf":
            p["_cpf_duplicado_de"] = DEFEITOS_ESPELHO[idx]
            p[coluna] = pessoas[DEFEITOS_ESPELHO[idx]]["cpf"]
            p["nome_completo"] = pessoas[DEFEITOS_ESPELHO[idx]]["nome_completo"]
        elif coluna == "email_corporativo" and tipo == "erro de registro":
            p[coluna] = p["nome_completo"].split()[0].lower() + "@gmail.com"
        elif coluna == "email_corporativo":
            p[coluna] = pessoas[100]["email_corporativo"]
        elif coluna == "idade":
            p[coluna] = p[coluna] + 12
        elif coluna == "jornada_horas":
            p[coluna] = 0
        elif coluna == "meta_cumprida_percentual":
            p[coluna] = "320,0"
        elif coluna == "faltas_2025":
            p[coluna] = 47
        elif coluna == "data_demissao":
            p[coluna] = "2019-03-04"
            p["status"] = "Desligado"
            p["turnover_12m"] = "sim"
        elif coluna == "tempo_empresa_anos":
            p[coluna] = num(p["_salario"] / 100.0, 1)
        aplicados.append((idx, coluna, tipo, descricao))
    return aplicados


DEFEITOS_ESPELHO = {168: 12, 181: 38}


# ------------------------------------------------------------------ escrita

def gravar(nome, colunas, linhas):
    caminho = os.path.join(PASTA, nome)
    with open(caminho, "w", newline="", encoding=COD) as f:
        w = csv.writer(f, delimiter=SEP)
        w.writerow(colunas)
        for linha in linhas:
            w.writerow(["" if linha.get(c) is None else linha.get(c) for c in colunas])
    return caminho

def construir_tudo():
    """Monta as sete tabelas em memoria. Sempre devolve o mesmo resultado.

    As tabelas de departamento, cargo e unidade sao montadas antes dos
    defeitos, e por isso ficam limpas. E por isso que seis linhas de
    funcionario, com o departamento em caixa alta, nao acham par na juncao.
    """
    rnd = random.Random(SEMENTE)
    pessoas = construir_funcionarios(rnd)

    departamentos = construir_departamentos(rnd, pessoas)
    cargos = construir_cargos()
    unidades = construir_unidades(rnd, pessoas)

    aplicar_defeitos(pessoas)
    avaliacoes = construir_avaliacoes(rnd, pessoas)
    treinamentos = construir_treinamentos(rnd, pessoas)
    ausencias = construir_ausencias(rnd, pessoas)

    # a duplicata exata vem por ultimo, depois de todas as somas
    funcionarios = list(pessoas) + [dict(pessoas[30])]

    return {
        "rh-funcionarios.csv": (COLS_FUNCIONARIOS, funcionarios),
        "rh-departamentos.csv": (COLS_DEPARTAMENTOS, departamentos),
        "rh-cargos.csv": (COLS_CARGOS, cargos),
        "rh-unidades.csv": (COLS_UNIDADES, unidades),
        "rh-avaliacoes.csv": (COLS_AVALIACOES, avaliacoes),
        "rh-treinamentos.csv": (COLS_TREINAMENTOS, treinamentos),
        "rh-ausencias.csv": (COLS_AUSENCIAS, ausencias),
    }


def mostrar_resumo(tabelas, linhas_func):
    titulo("RESUMO DA BASE SIMULADA")
    print()
    print("Referencia: %s   Semente: %d" % (para_br(HOJE), SEMENTE))
    print()
    # a distribuicao conta pessoas, e nao linhas: a 201 linha e a duplicata
    pessoas = list({p["matricula"]: p for p in linhas_func}.values())
    print("%-24s %8s %8s" % ("TABELA", "LINHAS", "COLUNAS"))
    print("-" * 42)
    for nome, (colunas, linhas) in tabelas.items():
        print("%-24s %8d %8d" % (nome, len(linhas), len(colunas)))
    print("-" * 42)
    print("%-24s %8d %8s" % ("TOTAL", sum(len(l) for _, l in tabelas.values()), ""))
    print("%-24s %8d %8s" % ("PESSOAS", len(pessoas), ""))

    print()
    print("HEADCOUNT POR DEPARTAMENTO")
    print()
    contagem = {}
    for p in pessoas:
        contagem[p["departamento"]] = contagem.get(p["departamento"], 0) + 1
    for k in sorted(contagem, key=lambda x: -contagem[x]):
        barra = "#" * contagem[k]
        print("  %-24s %3d  %s" % (k, contagem[k], barra))

    print()
    print("SALARIO BASE, EM REAIS")
    print()
    print("  %-22s %6s" % ("Nivel", "Pessoas"))
    for nivel in ["Estagiario", "Assistente", "Analista", "Especialista",
                  "Coordenador", "Gerente", "Diretor", "Presidente"]:
        quantos = sum(1 for p in pessoas if p["nivel"] == nivel)
        print("  %-22s %6d" % (nivel, quantos))
    validos = [p["_salario"] for p in pessoas]
    print()
    print("  minimo      %s" % brl(min(validos)))
    print("  mediana     %s" % brl(statistics.median(validos)))
    print("  media       %s" % brl(statistics.mean(validos)))
    print("  maximo      %s" % brl(max(validos)))
    folha = sum(p["_salario"] for p in pessoas)
    print()
    print("  folha de salario base mensal, sem proventos: %s" % brl(folha))
    print("  verificacao: soma das linhas x headcount x media = %s"
          % brl(len(pessoas) * statistics.mean(validos)))

    print()
    print("MOVIMENTACAO E ABSENTEISMO")
    print()
    print("  desligados em 12 meses      %d" % sum(
        1 for p in pessoas if p["status"] == "Desligado"))
    print("  turnover de 12 meses        %.1f%%" % (
        100.0 * sum(1 for p in pessoas if p["turnover_12m"] == "sim") / QTD))
    print("  afastados hoje             %d" % sum(
        1 for p in pessoas if p["status"] == "Afastado"))
    print("  em periodo de experiencia  %d" % sum(
        1 for p in pessoas if p["status"] == "Ativo em periodo de experiencia"))
    print("  em aviso previo           %d" % sum(
        1 for p in pessoas if p["status"] == "Aviso previo"))
    print("  horas de treinamento       %d" % sum(
        p["horas_treinamento_2025"] for p in pessoas
        if p["horas_treinamento_2025"] != ""))
    print("  faltas registradas         %d" % sum(
        p["faltas_2025"] for p in pessoas if p["faltas_2025"] != ""))
    print("  media de e_nps             %.1f" % statistics.mean(
        float(p["e_nps"]) for p in pessoas if p["e_nps"] != ""))

    print()
    print("DEFEITOS DE QUALIDADE INSERIDOS")
    print()
    print("  %d alteracoes em %d linhas de dados" % (
        len(DEFEITOS), len({d[0] for d in DEFEITOS})))
    print(" rode 'defeitos' para ver a lista com arquivo, linha e coluna")
    conferir_chaves(tabelas, pessoas)


def conferir_chaves(tabelas, pessoas):
    """Confere se as chaves fecham. As que nao fecham, fecham de proposito."""
    titulo("CONFERENCIA DE CHAVES")
    print()
    mat = [p["matricula"] for p in pessoas]
    print("  linhas em rh-funcionarios            %d" % len(pessoas))
    print("  matriculas distintas                 %d" % len(set(mat)))
    print("  linhas a mais que pessoas            %d  (a duplicata exata)"
          % (len(pessoas) - len(set(mat))))

    sem_par = 0
    for tabela, chave in (("rh-avaliacoes.csv", "matricula"),
                          ("rh-treinamentos.csv", "matricula"),
                          ("rh-ausencias.csv", "matricula")):
        linhas = tabelas[tabela][1]
        orfas = [l for l in linhas if l[chave] not in set(mat)]
        print("  %-34s %d linha(s) sem matricula correspondente"
              % (tabela, len(orfas)))

    deps = {l["departamento"] for l in tabelas["rh-departamentos.csv"][1]}
    cargos = {l["cargo"] for l in tabelas["rh-cargos.csv"][1]}
    unid = {l["unidade_negocio"] for l in tabelas["rh-unidades.csv"][1]}
    print("  %-34s %d" % ("funcionarios sem departamento", sum(
        1 for p in pessoas if p["departamento"] not in deps)))
    print("  %-34s %d" % ("funcionarios sem cargo", sum(
        1 for p in pessoas if p["cargo"] not in cargos)))
    print("  %-34s %d" % ("funcionarios sem unidade", sum(
        1 for p in pessoas if p["unidade_negocio"] not in unid)))
    print("  %-34s %d" % ("funcionarios sem gestor valido", sum(
        1 for p in pessoas if p["gestor_matricula"] and p["gestor_matricula"] not in set(mat))))
    print()
    print("  As tres primeiras linhas quebram de proposito. A causa e o mesmo")
    print("  defeito: o departamento gravado em caixa alta nao casa com a")
    print("  tabela de departamentos. E o que o comando juntar do modulo 7")
    print("  mostra quando conta os registros sem par.")


# ------------------------------------------------------------------ comandos

def cmd_gerar():
    titulo("SIMULACAO DE RH - COCA-COLA - GERACAO DA BASE")
    os.makedirs(PASTA, exist_ok=True)
    tabelas = construir_tudo()
    for nome, (colunas, linhas) in tabelas.items():
        gravar(nome, colunas, linhas)
    mostrar_resumo(tabelas, tabelas["rh-funcionarios.csv"][1])
    print()
    print("PROXIMO PASSO")
    print("  1) 'execute simulacao-rh.py com o comando dicionario'")
    print("  2) 'execute atividade_modulo6.py com o comando perfil"
          " dados/rh-funcionarios.csv'")
    print("  3) 'execute atividade_modulo7.py com o comando banco"
          " dados/rh-funcionarios.csv dados/rh-avaliacoes.csv'")
    return 0


def cmd_defeitos():
    titulo("DEFEITOS INSERIDOS DE PROPOSITO")
    print()
    print("Estes sao os erros que o script gravou em dados/rh-funcionarios.csv.")
    print("A base tem 200 pessoas e 201 linhas. Nenhum destes erros e erro seu:")
    print("sao o objeto da analise. A coluna VALOR mostra o que esta no arquivo.")
    print()
    print("%-6s %-9s %-24s %-22s %-16s %s"
          % ("LINHA", "MATRICULA", "COLUNA", "TIPO", "VALOR", "O QUE FOI GRAVADO"))
    print("-" * 132)
    pessoas = construir_tudo()["rh-funcionarios.csv"][1]
    for idx, coluna, tipo, descricao in DEFEITOS:
        if coluna == "linha inteira":
            print("%-6d %-9s %-24s %-22s %-16s %s"
                  % (idx + 2, pessoas[idx]["matricula"], "linha inteira", tipo,
                     "linha repetida", descricao))
            continue
        print("%-6d %-9s %-24s %-22s %-16s %s"
              % (idx + 2, pessoas[idx]["matricula"], coluna, tipo,
                 str(pessoas[idx].get(coluna, ""))[:16], descricao))
    print("-" * 132)
    print()
    print("Total: %d alteracoes, em %d linhas" % (
        len(DEFEITOS), len({d[0] for d in DEFEITOS})))
    print()
    print("Como usar: primeiro entregue a atividade do modulo 6 sem olhar esta")
    print("lista. Depois volte aqui e confira quantos dos %d voce achou."
          % len(DEFEITOS))
    print()
    print("UM AVISO SOBRE O METODO")
    print()
    print("O comando atipicos do modulo 6 aponta mais casos que estes, porque")
    print("usa intervalo entre quartis. Salario, bonus e carga horaria sobem")
    print("com o nivel do cargo, e o alto da distribuicao fica fora do")
    print("intervalo sem que haja erro. falso positivo e o caso comum, e")
    print("classificar um caso como realidade e parte do trabalho.")
    return 0


def cmd_dicionario():
    titulo("DICIONARIO DE DADOS")
    caminho = os.path.join(PASTA, "rh-dicionario-de-dados.md")
    tabelas = construir_tudo()
    L = []
    L.append("# Dicionario de dados - base simulada de RH da Coca-Cola")
    L.append("")
    L.append("Base ficticia gerada por `simulacao-rh.py`, semente %d, data de" % SEMENTE)
    L.append("referencia %s. Nenhum registro corresponde a pessoa real." % para_br(HOJE))
    L.append("")
    L.append("Separador `%s`, codificacao UTF-8 com BOM, decimal brasileiro." % SEP)
    L.append("")
    L.append("## Como as tabelas se ligam")
    L.append("")
    L.append("```")
    L.append("rh-funcionarios  1 --- N  rh-avaliacoes     (chave: matricula)")
    L.append("rh-funcionarios  1 --- N  rh-treinamentos   (chave: matricula)")
    L.append("rh-funcionarios  1 --- N  rh-ausencias      (chave: matricula)")
    L.append("rh-funcionarios  N --- 1  rh-departamentos  (chave: departamento)")
    L.append("rh-funcionarios  N --- 1  rh-cargos         (chave: cargo)")
    L.append("rh-funcionarios  N --- 1  rh-unidades       (chave: unidade_negocio)")
    L.append("rh-funcionarios  N --- 1  rh-funcionarios  (chave: gestor_matricula)")
    L.append("```")
    L.append("")
    L.append("As tres tabelas de referencia sao geradas antes dos defeitos, e por")
    L.append("isso ficam limpas. E por isso que 6 linhas de funcionario, com o")
    L.append("departamento em caixa alta, e 3 linhas, com o cargo em caixa baixa,")
    L.append("nao acham par na juncao. A quebra e o defeito, nao o script.")
    L.append("")
    for nome, (colunas, linhas) in tabelas.items():
        L.append("## %s" % nome)
        L.append("")
        L.append("%d linhas, %d colunas." % (len(linhas), len(colunas)))
        L.append("")
        L.append("| Coluna | O que registra |")
        L.append("|---|---|")
        for c in colunas:
            L.append("| `%s` | %s |" % (c, DESCRICOES.get(c, "")))
        L.append("")
    L.append("## Defeitos conhecidos")
    L.append("")
    L.append("A base tem %d defeitos inseridos de proposito, para a atividade de" % len(DEFEITOS))
    L.append("qualidade de dados. Os tipos sao: unidade trocada, erro de registro,")
    L.append("salario sem acrescimo, ausente por regra, ausente ao acaso, caixa")
    L.append("inconsistente, formato de data, formato de texto, duplicidade de chave,")
    L.append("valor repetido, contrato entre colunas, data impossivel, atipico por")
    L.append("escala e duplicata exata. A lista completa, com linha e coluna, sai")
    L.append("do comando `defeitos`.")
    L.append("")
    L.append("## Limites declarados")
    L.append("")
    L.append("- Os 200 registros sao uma amostra. Nao representam a empresa real.")
    L.append("- Salarios, notas e engajamento sao sorteados, nao medidos.")
    L.append("- CPF e CNPJ passam no digito verificador e nao identificam ninguem.")
    L.append("- Nao ha dado de historico anterior a 12 meses, nem de historico")
    L.append("  posterior a data de referencia.")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print()
    print("Dicionario gravado em: " + caminho)
    return 0


def cmd_ficha(matricula):
    titulo("FICHA DO FUNCIONARIO " + matricula)
    tabelas = construir_tudo()
    pessoas = tabelas["rh-funcionarios.csv"][1]
    alvo = None
    for p in pessoas:
        if p["matricula"].upper() == matricula.upper():
            alvo = p
            break
    if alvo is None:
        print()
        print("Nao achei a matricula " + matricula + " entre os 200 funcionarios.")
        print("Exemplos validos: EMP0001, EMP0042, EMP0137, EMP0200")
        return 1
    print()
    for c in COLS_FUNCIONARIOS:
        print("  %-26s %s" % (c, alvo.get(c, "")))
    for tabela in ("rh-avaliacoes.csv", "rh-treinamentos.csv", "rh-ausencias.csv"):
        linhas = tabelas[tabela][1]
        minhas = [l for l in linhas if l["matricula"] == alvo["matricula"]]
        print()
        print("%s  (%d registro(s))" % (tabela, len(minhas)))
        print("-" * 74)
        for l in minhas:
            print("  " + " | ".join(str(l.get(c, "")) for c in linhas[0].keys()))
    return 0


DESCRICOES = {
    "matricula": "Identificador do funcionario, unico e estavel. Chave primaria da tabela.",
    "nome_completo": "Nome do funcionario como consta no cadastro.",
    "cpf": "CPF no formato 000.000.000-00. Dado pessoal, so pode circular no ambiente restrito.",
    "data_nascimento": "Data de nascimento no formato aaaa-mm-dd.",
    "idade": "Idade em anos completos na data de referencia.",
    "sexo": "F ou M, como registrado no sistema.",
    "estado_civil": "Situacao registrada no cadastro.",
    "escolaridade": "Escolaridade formal informada pela pessoa.",
    "dependentes": "Numero de dependentes usados no calculo do plano de saude.",
    "email_corporativo": "E-mail de trabalho. Deveria ser o mesmo dominio em toda a base.",
    "departamento": "Area da empresa a que o funcionario pertence.",
    "cargo": "Nome do cargo exercido.",
    "nivel": "Faixa do plano de cargos: Estagiario a Presidente.",
    "familia_cargo": "Agrupamento do cargo para efeito de carreira.",
    "unidade_negocio": "Unidade onde a pessoa trabalha.",
    "cidade": "Cidade da unidade.",
    "uf": "Unidade da federacao da unidade.",
    "regiao": "Regiao geografica da unidade.",
    "centro_custo": "Centro de custo usado na contabilidade.",
    "modelo_contrato": "Regime de contratacao. CLT na base inteira.",
    "jornada_horas": "Jornada semanal em horas. 30 para estagiario, 40 para os demais.",
    "data_admissao": "Data de entrada na empresa, em aaaa-mm-dd.",
    "data_demissao": "Data de saida. Vazio para quem continua na empresa.",
    "tempo_empresa_anos": "Tempo de empresa em anos, com uma casa decimal.",
    "gestor_matricula": "Matricula do gestor imediato. Vazio para o Presidente.",
    "gestor_nome": "Nome do gestor imediato. Campo redundante: repete o que a juncao entrega.",
    "status": "Ativo, Ativo em periodo de experiencia, Afastado, Aviso previo, Desligado.",
    "salario_base": "Salario mensal base em reais, com duas casas.",
    "bonus_anual": "Bonus anual provisionado, em reais.",
    "remuneracao_total": "Salario base mais bonus. Deveria ser sempre maior que o salario base.",
    "valor_plano_saude": "Custeio mensal do plano de saude da empresa com a familia.",
    "valor_vale_alimentacao": "Vale alimentacao mensal, em reais.",
    "valor_vale_transporte": "Vale transporte mensal. Zero nos niveis de gestao.",
    "plano_saude": "sim ou nao.",
    "previdencia_complementar": "sim ou nao.",
    "nota_desempenho": "Nota de desempenho do ciclo 2025-S2, de 1 a 5.",
    "meta_cumprida_percentual": "Percentual de meta cumprida no ciclo 2025-S2.",
    "e_nps": "eNPS de -100 a 100, medido na pesquisa de engajamento.",
    "horas_treinamento_2025": "Horas de treinamento concluidas em 2025.",
    "faltas_2025": "Faltas injustificadas e justificadas no ano de 2025.",
    "dias_afastamento_2025": "Dias de afastamento no ano de 2025.",
    "turnover_12m": "sim quando a pessoa saiu nos 12 meses de referencia.",
    "origem_recrutamento": "Canal pelo qual a pessoa entrou na empresa.",
    "descricao": "Texto livre de identificacao da area, unidade ou curso.",
    "responsavel": "Pessoa responsavel pela area.",
    "orcamento_anual": "Orcamento anual aprovado da area, em reais.",
    "headcount_efetivo": "Pessoas hoje na area, contadas na base.",
    "headcount_orcado": "Pessoas previstas no quadro aprovado da area.",
    "criado_em": "Data de criacao do departamento.",
    "nivel_referencial": "Nivel do cargo.",
    "departamento_referencial": "Departamento de referencia do cargo.",
    "escolaridade_minima": "Escolaridade minima exigida para o cargo.",
    "faixa_salarial_minima": "Piso salarial do cargo, em reais.",
    "faixa_salarial_maxima": "Teto salarial do cargo, em reais.",
    "vale_refeicao": "sim ou nao.",
    "cargo_de_confianca": "sim ou nao.",
    "cnpj": "CNPJ da unidade, com digito verificador valido e sem correspondencia real.",
    "matricula_gestor": "Matricula do gestor da unidade.",
    "headcount_orcado_unidade": "Quadro aprovado da unidade.",
    "data_inauguracao": "Data de inauguracao da unidade.",
    "id_avaliacao": "Identificador da avaliacao.",
    "ciclo": "Semestre de referencia da avaliacao.",
    "data_avaliacao": "Data de realizacao da avaliacao.",
    "tipo_avaliacao": "Avaliacao do Gestor, Autoavaliacao ou Calibracao 360.",
    "avaliador_matricula": "Matricula de quem avaliou. Vazio na autoavaliacao.",
    "avaliador_nome": "Nome de quem avaliou.",
    "nota": "Nota de 1 a 5 dada na avaliacao.",
    "meta_percentual": "Percentual de meta considerado na avaliacao.",
    "peso": "Peso da avaliacao no resultado. Zero quando nao pesa na nota final.",
    "principais_entregas": "Texto semiestruturado com as entregas do ciclo.",
    "status_registro": "Concluida ou Pendente.",
    "id_treinamento": "Identificador da inscricao.",
    "codigo_curso": "Codigo do curso no catalogo.",
    "titulo_curso": "Nome do curso.",
    "categoria": "Area do catalogo de cursos.",
    "data_inscricao": "Data de inscricao no curso.",
    "data_conclusao": "Data de conclusao. Vazio enquanto o curso nao termina.",
    "carga_horaria": "Carga horaria do curso, em horas.",
    "status_curso": "Concluido, Em andamento, Nao iniciado ou Cancelado.",
    "nota_avaliacao": "Nota do curso, de 0 a 10. Vazio se nao concluido.",
    "investimento": "Custo do curso por pessoa, em reais.",
    "id_ausencia": "Identificador do registro de ausencia.",
    "data_inicio": "Data de inicio do afastamento.",
    "data_fim": "Data de termino do afastamento.",
    "tipo_ausencia": "Ferias, Atestado medico, Licenca maternidade, Licenca paternal, Falta nao justificada, Banco de horas compensada ou Afastamento por doenca.",
    "dias_utilis": "Dias uteis do afastamento.",
    "motivo": "Texto com a justificativa registrada.",
    "comprovacao": "sim quando houve comprovacao apresentada.",
    "abono": "1 quando a falta foi abonada, 0 quando nao foi.",
}


def instrucoes():
    print()
    print("=" * 74)
    print(" SIMULACAO DE DADOS DE RH - COCA-COLA - 200 FUNCIONARIOS")
    print(" DECC0294 - UFMA - Curso de Administracao - 2026.2")
    print("=" * 74)
    print()
    print("O QUE ESTE ARQUIVO FAZ")
    print("    Gera uma base ficticia de recursos humanos com 200 funcionarios,")
    print("    sete tabelas relacionadas e defeitos de qualidade inseridos de")
    print("    proposito, para as praticas dos modulos 5 a 8.")
    print()
    print("    AVISO: nenhum registro e de pessoa real. Dado sintetico, sorteado")
    print("    com semente fixa. Nao use estes numeros para decidir sobre gente.")
    print()
    print("COMANDOS")
    print()
    print("    gerar         cria as sete tabelas em dados/ e mostra o resumo")
    print("    dicionario    grava dados/rh-dicionario-de-dados.md")
    print("    ficha EMP0042 mostra a ficha completa de um funcionario")
    print("    defeitos      lista os defeitos inseridos, com linha e coluna")
    print()
    print("COMO PEDIR AO AGENTE")
    print()
    print('    "execute simulacao-rh.py com o comando gerar"')
    print('    "execute simulacao-rh.py com o comando dicionario"')
    print('    "execute simulacao-rh.py com o comando ficha EMP0042"')
    print('    "execute simulacao-rh.py com o comando defeitos"')
    print()
    print("DEPOIS DE GERAR, O CAMINHO NA DISCIPLINA")
    print()
    print("    modulo 5  as sete tabelas sao as fontes do mapa de dados")
    print("    modulo 6  perfil dados/rh-funcionarios.csv, depois atipicos")
    print("    modulo 7  banco com varias tabelas e juntar por matricula")
    print("    modulo 8  painel de rotatividade, salario e headcount")
    print()
    print("Nao precisa instalar nada. Roda com o Python que ja vem com o ambiente.")


def principal():
    if len(sys.argv) < 2:
        instrucoes()
        return 0
    comando = sys.argv[1].lower()
    if comando in ("gerar", "gerar-base"):
        return cmd_gerar()
    if comando in ("defeitos", "defeito"):
        return cmd_defeitos()
    if comando in ("dicionario", "dic"):
        return cmd_dicionario()
    if comando in ("ficha",):
        if len(sys.argv) < 3:
            print()
            print("Faltou a matricula. Uso: ficha EMP0042")
            return 1
        return cmd_ficha(sys.argv[2])
    if comando in ("ajuda", "help", "-h", "--help"):
        instrucoes()
        return 0
    print()
    print("Comando desconhecido: " + comando)
    instrucoes()
    return 1


if __name__ == "__main__":
    sys.exit(principal())
