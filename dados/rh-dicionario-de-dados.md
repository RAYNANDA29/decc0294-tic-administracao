# Dicionario de dados - base simulada de RH da Coca-Cola

Base ficticia gerada por `simulacao-rh.py`, semente 20260929, data de
referencia 29/09/2026. Nenhum registro corresponde a pessoa real.

Separador `;`, codificacao UTF-8 com BOM, decimal brasileiro.

## Como as tabelas se ligam

```
rh-funcionarios  1 --- N  rh-avaliacoes     (chave: matricula)
rh-funcionarios  1 --- N  rh-treinamentos   (chave: matricula)
rh-funcionarios  1 --- N  rh-ausencias      (chave: matricula)
rh-funcionarios  N --- 1  rh-departamentos  (chave: departamento)
rh-funcionarios  N --- 1  rh-cargos         (chave: cargo)
rh-funcionarios  N --- 1  rh-unidades       (chave: unidade_negocio)
rh-funcionarios  N --- 1  rh-funcionarios  (chave: gestor_matricula)
```

As tres tabelas de referencia sao geradas antes dos defeitos, e por
isso ficam limpas. E por isso que 6 linhas de funcionario, com o
departamento em caixa alta, e 3 linhas, com o cargo em caixa baixa,
nao acham par na juncao. A quebra e o defeito, nao o script.

## rh-funcionarios.csv

201 linhas, 43 colunas.

| Coluna | O que registra |
|---|---|
| `matricula` | Identificador do funcionario, unico e estavel. Chave primaria da tabela. |
| `nome_completo` | Nome do funcionario como consta no cadastro. |
| `cpf` | CPF no formato 000.000.000-00. Dado pessoal, so pode circular no ambiente restrito. |
| `data_nascimento` | Data de nascimento no formato aaaa-mm-dd. |
| `idade` | Idade em anos completos na data de referencia. |
| `sexo` | F ou M, como registrado no sistema. |
| `estado_civil` | Situacao registrada no cadastro. |
| `escolaridade` | Escolaridade formal informada pela pessoa. |
| `dependentes` | Numero de dependentes usados no calculo do plano de saude. |
| `email_corporativo` | E-mail de trabalho. Deveria ser o mesmo dominio em toda a base. |
| `departamento` | Area da empresa a que o funcionario pertence. |
| `cargo` | Nome do cargo exercido. |
| `nivel` | Faixa do plano de cargos: Estagiario a Presidente. |
| `familia_cargo` | Agrupamento do cargo para efeito de carreira. |
| `unidade_negocio` | Unidade onde a pessoa trabalha. |
| `cidade` | Cidade da unidade. |
| `uf` | Unidade da federacao da unidade. |
| `regiao` | Regiao geografica da unidade. |
| `centro_custo` | Centro de custo usado na contabilidade. |
| `modelo_contrato` | Regime de contratacao. CLT na base inteira. |
| `jornada_horas` | Jornada semanal em horas. 30 para estagiario, 40 para os demais. |
| `data_admissao` | Data de entrada na empresa, em aaaa-mm-dd. |
| `data_demissao` | Data de saida. Vazio para quem continua na empresa. |
| `tempo_empresa_anos` | Tempo de empresa em anos, com uma casa decimal. |
| `gestor_matricula` | Matricula do gestor imediato. Vazio para o Presidente. |
| `gestor_nome` | Nome do gestor imediato. Campo redundante: repete o que a juncao entrega. |
| `status` | Ativo, Ativo em periodo de experiencia, Afastado, Aviso previo, Desligado. |
| `salario_base` | Salario mensal base em reais, com duas casas. |
| `bonus_anual` | Bonus anual provisionado, em reais. |
| `remuneracao_total` | Salario base mais bonus. Deveria ser sempre maior que o salario base. |
| `valor_plano_saude` | Custeio mensal do plano de saude da empresa com a familia. |
| `valor_vale_alimentacao` | Vale alimentacao mensal, em reais. |
| `valor_vale_transporte` | Vale transporte mensal. Zero nos niveis de gestao. |
| `plano_saude` | sim ou nao. |
| `previdencia_complementar` | sim ou nao. |
| `nota_desempenho` | Nota de desempenho do ciclo 2025-S2, de 1 a 5. |
| `meta_cumprida_percentual` | Percentual de meta cumprida no ciclo 2025-S2. |
| `e_nps` | eNPS de -100 a 100, medido na pesquisa de engajamento. |
| `horas_treinamento_2025` | Horas de treinamento concluidas em 2025. |
| `faltas_2025` | Faltas injustificadas e justificadas no ano de 2025. |
| `dias_afastamento_2025` | Dias de afastamento no ano de 2025. |
| `turnover_12m` | sim quando a pessoa saiu nos 12 meses de referencia. |
| `origem_recrutamento` | Canal pelo qual a pessoa foi recruited. |

## rh-departamentos.csv

13 linhas, 8 colunas.

| Coluna | O que registra |
|---|---|
| `departamento` | Area da empresa a que o funcionario pertence. |
| `descricao` | Texto livre de identificacao da area, unidade ou curso. |
| `responsavel` | Pessoa responsavel pela area. |
| `orcamento_anual` | Orcamento anual aprovado da area, em reais. |
| `headcount_efetivo` | Pessoas hoje na area, contadas na base. |
| `headcount_orcado` | Pessoas previstas no quadro aprovado da area. |
| `criado_em` | Data de criacao do departamento. |
| `centro_custo` | Centro de custo usado na contabilidade. |

## rh-cargos.csv

78 linhas, 9 colunas.

| Coluna | O que registra |
|---|---|
| `cargo` | Nome do cargo exercido. |
| `nivel` | Faixa do plano de cargos: Estagiario a Presidente. |
| `familia_cargo` | Agrupamento do cargo para efeito de carreira. |
| `departamento_referencial` | Departamento de referencia do cargo. |
| `escolaridade_minima` | Escolaridade minima exigida para o cargo. |
| `faixa_salarial_minima` | Piso salarial do cargo, em reais. |
| `faixa_salarial_maxima` | Teto salarial do cargo, em reais. |
| `vale_refeicao` | sim ou nao. |
| `cargo_de_confianca` | sim ou nao. |

## rh-unidades.csv

18 linhas, 10 colunas.

| Coluna | O que registra |
|---|---|
| `unidade_negocio` | Unidade onde a pessoa trabalha. |
| `descricao` | Texto livre de identificacao da area, unidade ou curso. |
| `cidade` | Cidade da unidade. |
| `uf` | Unidade da federacao da unidade. |
| `regiao` | Regiao geografica da unidade. |
| `centro_custo` | Centro de custo usado na contabilidade. |
| `cnpj` | CNPJ da unidade, com digito verificador valido e sem correspondencia real. |
| `matricula_gestor` | Matricula do gestor da unidade. |
| `headcount_orcado` | Pessoas previstas no quadro aprovado da area. |
| `data_inauguracao` | Data de inauguracao da unidade. |

## rh-avaliacoes.csv

760 linhas, 12 colunas.

| Coluna | O que registra |
|---|---|
| `id_avaliacao` | Identificador da avaliacao. |
| `matricula` | Identificador do funcionario, unico e estavel. Chave primaria da tabela. |
| `ciclo` | Semestre de referencia da avaliacao. |
| `data_avaliacao` | Data de realizacao da avaliacao. |
| `tipo_avaliacao` | Avaliacao do Gestor, Autoavaliacao ou Calibracao 360. |
| `avaliador_matricula` | Matricula de quem avaliou. Vazio na autoavaliacao. |
| `avaliador_nome` | Nome de quem avaliou. |
| `nota` | Nota de 1 a 5 dada na avaliacao. |
| `meta_percentual` | Percentual de meta considerado na avaliacao. |
| `peso` | Peso da avaliacao no resultado. Zero quando nao pesa na nota final. |
| `principais_entregas` | Texto semiestruturado com as entregas do ciclo. |
| `status_registro` | Concluida ou Pendente. |

## rh-treinamentos.csv

602 linhas, 11 colunas.

| Coluna | O que registra |
|---|---|
| `id_treinamento` | Identificador da inscricao. |
| `matricula` | Identificador do funcionario, unico e estavel. Chave primaria da tabela. |
| `codigo_curso` | Codigo do curso no catalogo. |
| `titulo_curso` | Nome do curso. |
| `categoria` | Area do catalogo de cursos. |
| `data_inscricao` | Data de inscricao no curso. |
| `data_conclusao` | Data de conclusao. Vazio enquanto o curso nao termina. |
| `carga_horaria` | Carga horaria do curso, em horas. |
| `status_curso` | Concluido, Em andamento, Nao iniciado ou Cancelado. |
| `nota_avaliacao` | Nota do curso, de 0 a 10. Vazio se nao concluido. |
| `investimento` | Custo do curso por pessoa, em reais. |

## rh-ausencias.csv

481 linhas, 9 colunas.

| Coluna | O que registra |
|---|---|
| `id_ausencia` | Identificador do registro de ausencia. |
| `matricula` | Identificador do funcionario, unico e estavel. Chave primaria da tabela. |
| `data_inicio` | Data de inicio do afastamento. |
| `data_fim` | Data de termino do afastamento. |
| `tipo_ausencia` | Ferias, Atestado medico, Licenca maternidade, Licenca paternal, Falta nao justificada, Banco de horas compensada ou Afastamento por doenca. |
| `dias_utilis` | Dias uteis do afastamento. |
| `motivo` | Texto com a justificativa registrada. |
| `comprovacao` | sim quando houve comprovacao apresentada. |
| `abono` | 1 quando a falta foi abonada, 0 quando nao foi. |

## Defeitos conhecidos

A base tem 53 defeitos inseridos de proposito, para a atividade de
qualidade de dados. Os tipos sao: unidade trocada, erro de registro,
salario sem acrescimo, ausente por regra, ausente ao acaso, caixa
inconsistente, formato de data, formato de texto, duplicidade de chave,
valor repetido, contrato entre colunas, data impossivel, atipico por
escala e duplicata exata. A lista completa, com linha e coluna, sai
do comando `defeitos`.

## Limites declarados

- Os 200 registros sao uma amostra. Nao representam a empresa real.
- Salarios, notas e engajamento sao sorteados, nao medidos.
- CPF e CNPJ passam no digito verificador e nao identificam ninguem.
- Nao ha dado de historico anterior a 12 meses, nem de historico
  posterior a data de referencia.