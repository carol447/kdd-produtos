"""Etapa 6 - Avaliação e interpretação dos clusters."""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)


def metricas(X: np.ndarray, rotulos: np.ndarray) -> dict:
    return {
        "silhueta": round(float(silhouette_score(X, rotulos)), 3),
        "davies_bouldin": round(float(davies_bouldin_score(X, rotulos)), 3),
        "calinski_harabasz": round(float(calinski_harabasz_score(X, rotulos)), 1),
    }


def _nivel(valor: float, referencia: pd.Series) -> str:
    baixo, alto = referencia.quantile([1 / 3, 2 / 3])
    return "baixo" if valor < baixo else "alto" if valor > alto else "médio"


def perfil(df: pd.DataFrame) -> pd.DataFrame:
    """Resumo de cada cluster nas unidades originais, com um nome descritivo.

    O nome compara a mediana do cluster com os tercis de toda a base; não usa
    a categoria, que serve só para validar o resultado depois.
    """
    grupos = df.groupby("Cluster")
    tabela = pd.DataFrame({
        "Produtos": grupos.size(),
        "Preço_mediano": grupos["Preço"].median().round(2),
        "Vendas_medianas": grupos["Vendas"].median().round(0),
        "Receita_total": grupos["Receita"].sum().round(0),
        "Categoria_predominante": grupos["Categoria"].agg(lambda s: s.mode().iat[0]),
        "Pct_predominante": grupos["Categoria"]
        .agg(lambda s: s.value_counts(normalize=True).iat[0] * 100)
        .round(1),
    })
    tabela["Pct_receita"] = (tabela["Receita_total"] / tabela["Receita_total"].sum() * 100).round(1)
    tabela["Segmento"] = [
        f"Preço {_nivel(p, df['Preço'])} · giro {_nivel(v, df['Vendas'])}"
        for p, v in zip(tabela["Preço_mediano"], tabela["Vendas_medianas"])
    ]
    return tabela


def categoria_por_cluster(df: pd.DataFrame) -> pd.DataFrame:
    """Percentual de cada categoria distribuído entre os clusters (linhas somam 100)."""
    return (pd.crosstab(df["Categoria"], df["Cluster"], normalize="index") * 100).round(1)
