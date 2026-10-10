# Resultados da execução

> Arquivo gerado automaticamente por `python main.py`.

## Pré-processamento

| Etapa | Registros |
|---|---|
| Entrada | 1246 |
| Duplicatas removidas | 46 |
| Valores inválidos removidos (preço ≤ 0 ou vendas < 0) | 9 |
| Preços extremos removidos (> R$ 1886.5) | 3 |
| Sem categoria removidos | 12 |
| Preços ausentes preenchidos (mediana da categoria) | 47 |
| Vendas ausentes preenchidas (mediana da categoria) | 48 |
| **Saída** | **1176** |

## Redução de dados

- Atributos selecionados para o agrupamento: `Preço_norm, Vendas_norm, Receita_norm`
- Removidos por correlação (|r| > 0,9): `nenhum`
- ANOVA F contra a categoria (diagnóstico): Preço_norm = 1185.5, Vendas_norm = 845.2, Receita_norm = 82.7

## Mineração e avaliação

- k escolhido pela maior silhueta: **2**
- Silhueta: **0.4** (de -1 a 1; maior é melhor)
- Davies-Bouldin: **0.965** (menor é melhor)
- Calinski-Harabasz: **1013.9** (maior é melhor)

### Busca de k

| k | inercia | silhueta |
|---|---|---|
| 2 | 60.811 | 0.4 |
| 3 | 41.668 | 0.374 |
| 4 | 31.548 | 0.378 |
| 5 | 26.146 | 0.352 |
| 6 | 22.181 | 0.347 |
| 7 | 19.127 | 0.349 |
| 8 | 16.619 | 0.356 |

### Perfil dos clusters

| Cluster | Produtos | Preço_mediano | Vendas_medianas | Receita_total | Categoria_predominante | Pct_predominante | Pct_receita | Segmento |
|---|---|---|---|---|---|---|---|---|
| 0 | 659 | 63.51 | 158.0 | 7558878.0 | camisa | 53.9 | 60.4 | Preço baixo · giro alto |
| 1 | 517 | 153.69 | 58.0 | 4952991.0 | vestido | 47.0 | 39.6 | Preço alto · giro baixo |

### Distribuição das categorias entre clusters (%)

| Categoria | 0 | 1 |
|---|---|---|
| calça | 68.0 | 32.0 |
| camisa | 100.0 | 0.0 |
| jaqueta | 0.0 | 100.0 |
| saia | 62.1 | 37.9 |
| vestido | 1.2 | 98.8 |
