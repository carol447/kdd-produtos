"""Etapa 3 - Transformação: discretização, novos atributos e normalização."""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

FAIXAS = ["Baixo", "Médio", "Alto"]


def transformar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Variável categórica a partir do preço: tercis garantem faixas equilibradas.
    df["Faixa_Preço"] = pd.qcut(df["Preço"], q=3, labels=FAIXAS)

    df["Receita"] = df["Preço"] * df["Vendas"]

    # Preço, vendas e receita são assimétricos à direita; o log evita que poucos
    # produtos caros dominem as distâncias do K-Means. Depois, Min-Max para [0, 1].
    bases = ["Preço", "Vendas", "Receita"]
    escalados = MinMaxScaler().fit_transform(np.log1p(df[bases]))
    for i, coluna in enumerate(bases):
        df[f"{coluna}_norm"] = escalados[:, i]

    return df
