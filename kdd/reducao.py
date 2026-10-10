"""Etapa 4 - Redução de dados: escolhe os atributos usados no agrupamento.

Filtros independentes de modelo, aplicados em ordem:
1. variância mínima (atributos quase constantes não separam grupos);
2. correlação (de um par redundante, mantém o primeiro da lista).

O ANOVA F (SelectKBest/f_classif) contra a Categoria é calculado apenas como
diagnóstico. Ele não decide os atributos porque o agrupamento é não
supervisionado: escolher atributos pelo rótulo faria os clusters apenas
reproduzirem as categorias já conhecidas.
"""

import pandas as pd
from sklearn.feature_selection import f_classif

from kdd.config import ATRIBUTOS_CANDIDATOS


def reduzir(
    df: pd.DataFrame,
    candidatos: list[str] = ATRIBUTOS_CANDIDATOS,
    variancia_minima: float = 0.005,
    correlacao_maxima: float = 0.9,
) -> tuple[pd.DataFrame, list[str], dict]:
    variancias = df[candidatos].var()
    atributos = [c for c in candidatos if variancias[c] >= variancia_minima]

    correlacao = df[atributos].corr()
    removidos_correlacao = []
    for i, a in enumerate(atributos):
        for b in atributos[i + 1:]:
            if b not in removidos_correlacao and abs(correlacao.loc[a, b]) > correlacao_maxima:
                removidos_correlacao.append(b)
    atributos = [a for a in atributos if a not in removidos_correlacao]

    f, p = f_classif(df[candidatos], df["Categoria"])

    relatorio = {
        "variancia": variancias.round(4).to_dict(),
        "correlacao": df[candidatos].corr().round(3).to_dict(),
        "removidos_por_correlacao": removidos_correlacao,
        "anova_f_vs_categoria": dict(zip(candidatos, f.round(1).tolist())),
        "anova_p_vs_categoria": dict(zip(candidatos, p.tolist())),
        "atributos_selecionados": atributos,
    }
    colunas = ["ID_Produto", "Categoria", "Preço", "Vendas", "Receita", "Faixa_Preço"]
    return df[colunas + atributos].copy(), atributos, relatorio
