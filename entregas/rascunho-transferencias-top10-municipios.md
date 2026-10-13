# RASCUNHO - Top 10 municipios que mais receberam transferencias constitucionais (dez/2024)

> NAO ENTREGAR ASSIM: isso e rascunho pro teu trampo de Administracao 6o periodo UFMA. Tu tem que decidir: [1] periodo - eu usei dez/2024; [2] soma tudo ou so FPM; [3] como tratar DEDU do FUNDEB.

## Passo a passo (analise)

1. Fui na doc oficial da API: https://apiapex.tesouro.gov.br/aria/v1/transferencias_constitucionais/docs - vista via https://sisweb.tesouro.gov.br/apex/f?p=10250:7:111022482372737::NO:7:P7_ID_PROJETO:1586
2. Testei `/transferencias` - voltou 18 tipos, codigo 3 = FPM, 10 = FUNDEB, 12 = Royalties. Numero veio da API na hora.
3. Testei `/estados` - voltou 27 UFs, codigo 26 = Sao Paulo. Numero veio da API na hora.
4. Fui no CKAN: https://www.tesourotransparente.gov.br/ckan/api/3/action/package_show?id=transferencias-constitucionais-para-municipios - la diz que tem 146 recursos - numero veio desse JSON.
5. Baixei o arquivo `Transferencia_Mensal_Municipios_202412.csv`, resource `2403f2d8-1659-45cd-a6c9-83393ce6c3c8`, 79.343 linhas - numeros vieram desse download. Colunas: Municipio;UF;ANO;Mes;1o Decendio;2o Decendio;3o Decendio;Item transferencia;Transferencia. Somei os 3 decendios por municipio.
6. Cruzei com a API viva: `.../por_estado_municipio?p_estado=26&p_municipio=7107&p_ano=2024&p_mes=12&p_sn_detalhar=sim` deu soma R$ 808.641.870,87 - numero veio dessa chamada.

## Interpretacao - top 10 dez/2024

Todos os valores abaixo vieram da soma dos 3 decendios do CSV de dez/2024 citado acima. Valor nominal do mes, nao deflacionado.

1. Sao Paulo/SP | TOTAL R$ 820.825.104,52 | FPM R$ 74.585.238,63 | FUNDEB R$ 741.596.373,59 | Royalties R$ 1.766.574,80
2. Rio de Janeiro/RJ | TOTAL R$ 552.078.517,45 | FPM R$ 85.240.272,73 | FUNDEB R$ 437.567.979,12 | Royalties R$ 28.662.719,97
3. Fortaleza/CE | TOTAL R$ 428.202.864,55 | FPM R$ 213.100.681,76 | FUNDEB R$ 211.591.754,13 | Royalties R$ 3.317.078,94
4. Salvador/BA | TOTAL R$ 328.778.007,26 | FPM R$ 191.790.613,61 | FUNDEB R$ 133.624.752,20 | Royalties R$ 3.028.579,94
5. Manaus/AM | TOTAL R$ 309.000.855,49 | FPM R$ 134.253.429,53 | FUNDEB R$ 172.531.771,61 | Royalties R$ 1.919.218,82
6. Belo Horizonte/MG | TOTAL R$ 266.212.185,65 | FPM R$ 106.550.340,91 | FUNDEB R$ 154.806.989,81 | Royalties R$ 4.130.663,66
7. Marica/RJ | TOTAL R$ 257.726.869,26 | FPM R$ 15.023.861,65 | FUNDEB R$ 20.227.069,00 | Royalties R$ 222.250.623,57
8. Sao Luis/MA | TOTAL R$ 225.466.124,69 | FPM R$ 133.187.926,12 | FUNDEB R$ 86.525.770,82 | Royalties R$ 5.256.403,62
9. Recife/PE | TOTAL R$ 222.048.991,64 | FPM R$ 134.253.429,53 | FUNDEB R$ 85.682.765,18 | Royalties R$ 1.964.184,04
10. Teresina/PI | TOTAL R$ 214.503.806,32 | FPM R$ 133.187.926,12 | FUNDEB R$ 79.356.539,58 | Royalties R$ 1.863.404,62

Totais do mes nesse mesmo arquivo: FPM R$ 24.378.718.190,79 | FUNDEB R$ 22.895.616.903,30 | Royalties R$ 2.941.602.416,54 | total geral R$ 50.509.198.298,75 - numeros vieram da soma desse arquivo.

O pulo do gato: Marica nao ta no top por populacao, ta por royalty de petroleo do pre-sal.

## Conceitos

- Transferencia Constitucional: definicao - rateio de receita federal que a Uniao e obrigada a repassar pra estado e municipio por causa da Constituicao. Exemplo BR - FPM que cai todo decendio pra prefeitura. Referencia verificavel: https://www.gov.br/tesouronacional/pt-br/estados-e-municipios/transferencias-a-estados-e-municipios/transferencias-constitucionais-e-legais
- FPM: definicao - Fundo de Participacao dos Municipios, feito de IR e IPI. Exemplo BR - Fortaleza pegou R$ 213.100.681,76 so de FPM em dez/2024 nesse arquivo. Referencia verificavel: https://www.tesourotransparente.gov.br/temas/estados-e-municipios/transferencias-a-estados-e-municipios
- FUNDEB: definicao - fundo da educacao basica, junta ICMS, FPE, FPM, IPVA e devolve por aluno. Exemplo BR - Sao Paulo pegou R$ 741.596.373,59 de FUNDEB em dez/2024 nesse arquivo. Referencia verificavel: mesma pagina acima + https://www.tesourotransparente.gov.br/ckan/dataset/api-de-transferencias-constitucionais
- Royalties: definicao - compensacao por explorar petroleo, agua, minerio. Exemplo BR - Marica/RJ pegou R$ 222.250.623,57 em dez/2024 nesse arquivo. Referencia verificavel: https://www.tesourotransparente.gov.br/ckan/dataset/transferencias-constitucionais-para-municipios

Livro/autor pra ABNT: NAO SEI - nao vou inventar referencia.

## Limitacao declarada

Mano, papo reto: isso aqui e so dezembro/2024, nao e ano fechado. O arquivo de outubro/2024 somou R$ 3.197.392.241.633,00 - numero veio do meu calculo nesse arquivo - ou seja, 3,19 tri, bugado na fonte. Janeiro/2024 nem existe no CKAN. A diferenca CSV x API em Sao Paulo e de R$ 12.183.233,65 por causa do item DEDU do FUNDEB que o CSV soma e a API detalhada nao lista. Se o professor quiser serie anual, tem que baixar outro ano ou esperar corrigirem.
