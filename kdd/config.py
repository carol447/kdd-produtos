"""Caminhos e parâmetros compartilhados por todas as etapas do pipeline."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

DADOS_BRUTOS = RAIZ / "data" / "raw" / "produtos.csv"
DIR_PROCESSADOS = RAIZ / "data" / "processed"
DIR_RELATORIOS = RAIZ / "reports"
DIR_FIGURAS = DIR_RELATORIOS / "figures"

SEMENTE = 42

# Etapa de seleção: atributos relevantes para o problema (redução vertical).
COLUNAS_SELECIONADAS = ["ID_Produto", "Categoria", "Preço", "Vendas"]

# Atributos candidatos ao agrupamento, gerados na transformação.
ATRIBUTOS_CANDIDATOS = ["Preço_norm", "Vendas_norm", "Receita_norm"]

# Busca do número de clusters.
FAIXA_K = range(2, 9)
