---
name: analise-turnover
description: Use when calcular turnover, taxa de rotatividade, analisar desligamentos mensal ou anual, headcount médio, retenção de talentos. Use ONLY when o pedido envolver turnover, rotatividade de pessoal ou análise de saídas e admissões.
---

# Análise de Turnover

Skill para calcular e interpretar turnover de forma comparável mês a mês.

## Entradas obrigatórias

Antes de calcular, obtenha:
1. Período de referência (mês ex: janeiro, ou ano ex: 2025).
2. Nº de desligamentos com data dentro do período.
3. Headcount no 1º dia e no último dia do período.
4. Nº de admissões, se for calcular movimentação geral.
5. Para cada saída: data de admissão, data de desligamento, tipo voluntário (pedido do colaborador) ou involuntário (decisão da empresa), motivo padronizado (remuneração, liderança, carreira, cultura/fit, carga).
6. Regra do que entra: estagiário, temporário, terceirizado, aprendiz entram? Transferência interna NÃO conta como desligamento. Afastado conta como ativo, salvo regra interna contrária. Documente a regra usada.

## Cálculo

Fórmula padrão de retenção (só saídas):

- Headcount médio = (HC início + HC fim) / 2
- Turnover (%) = (Desligamentos no período / Headcount médio) x 100

Mensal, nesta ordem:
1. Definir mês.
2. Contar desligamentos do mês.
3. Levantar HC dia 1 e dia 30/31.
4. Calcular HC médio.
5. Aplicar fórmula.

Anual, mesma lógica:
- Turnover anual (%) = (Desligamentos do ano / [(HC 01/01 + HC 31/12) / 2]) x 100

Fórmula geral de movimentação (Chiavenato / Convenia / FIA), quando pedir visão de giro:
- Turnover geral = [(Admitidos + Desligados) / 2] / Total de funcionários x 100

Separe sempre:
- Turnover voluntário = (Pedidos de demissão / HC médio) x 100
- Turnover involuntário = (Demissões pela empresa / HC médio) x 100

Mostre a conta com os números usados. Não arredonde antes do passo final.

## Segmentação obrigatória

Não entregue só o total. Calcule a mesma fórmula por:
- área, cargo, unidade e, se houver dado, por gestor;
- tempo de casa: 0-90 dias, 3-6 meses, 6-12 meses, 1 ano+.

## Interpretação

Responda em até 5 linhas por recorte:
- Subiu ou caiu vs período anterior? Onde concentra?
- 0-90 dias alto = recrutamento, expectativa, onboarding.
- Concentrado numa área/gestor = liderança ou sobrecarga.
- Voluntário alto = clima, remuneração, carreira, carga.
- Involuntário alto = seleção, desempenho, adaptação cultural.

Declare limitação: período curto, base pequena, regra de headcount adotada, dado faltante.
Não invente motivo de saída. Se não houver entrevista de desligamento, escreva "motivo não informado".

## Fontes de referência

- Sólides, Como calcular o turnover mensal e anual: https://solides.com.br/blog/turnover-mensal-e-anual
- Convenia, Como calcular Turnover - 5 tipos: https://blog.convenia.com.br/como-calcular-turnover
- Qandle, Attrition Analysis Step-by-Step: https://www.qandle.com/blog/attrition-analysis
