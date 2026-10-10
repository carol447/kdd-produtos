"""Etapa 1 - Seleção: mantém apenas os atributos relevantes (redução vertical)."""

import pandas as pd

from kdd.config import COLUNAS_SELECIONADAS


def selecionar(df: pd.DataFrame) -> pd.DataFrame:
    faltando = set(COLUNAS_SELECIONADAS) - set(df.columns)
    if faltando:
        raise ValueError(f"Colunas obrigatórias ausentes: {sorted(faltando)}")
    return df[COLUNAS_SELECIONADAS].copy()
