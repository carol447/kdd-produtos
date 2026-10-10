"""Etapa 2 - Pré-processamento: limpeza, correção e preenchimento dos dados."""

import unicodedata

import numpy as np
import pandas as pd

# Grafias sem acento que devem voltar à forma canônica.
CANONICAS = {"calca": "calça"}


def normalizar_texto(valor):
    if pd.isna(valor):
        return np.nan
    texto = " ".join(str(valor).split()).lower()
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )
    return CANONICAS.get(sem_acento, texto)


def converter_preco(valor):
    """Converte números e textos como "R$ 1.234,56" para float."""
    if pd.isna(valor):
        return np.nan
    if isinstance(valor, (int, float, np.number)):
        return float(valor)
    texto = str(valor).replace("R$", "").strip()
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return np.nan


def _limite_superior_extremo(serie: pd.Series, fator: float = 3.0) -> float:
    """Cerca superior de Tukey (fator 3 = outlier extremo), em escala log."""
    log = np.log1p(serie.dropna())
    q1, q3 = log.quantile([0.25, 0.75])
    return float(np.expm1(q3 + fator * (q3 - q1)))


def preprocessar(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    df = df.copy()
    relatorio = {"registros_entrada": len(df)}

    # Normalização de textos e conversão de tipos.
    df["Categoria"] = df["Categoria"].map(normalizar_texto)
    df["Preço"] = df["Preço"].map(converter_preco)
    df["Vendas"] = pd.to_numeric(df["Vendas"], errors="coerce")

    # Remoção de duplicatas: só depois de normalizar, para pegar "CAMISA" == "camisa".
    antes = len(df)
    df = df.drop_duplicates(subset="ID_Produto", keep="first")
    relatorio["duplicatas_removidas"] = antes - len(df)

    # Correção de valores inválidos: registros impossíveis não são confiáveis.
    invalidos = (df["Preço"] <= 0) | (df["Vendas"] < 0)
    limite = _limite_superior_extremo(df.loc[~invalidos, "Preço"])
    extremos = df["Preço"] > limite
    relatorio["invalidos_removidos"] = int(invalidos.sum())
    relatorio["extremos_removidos"] = int((extremos & ~invalidos).sum())
    relatorio["limite_preco_extremo"] = round(limite, 2)
    df = df[~(invalidos | extremos)]

    # Sem categoria não há como imputar com segurança nem interpretar o produto.
    relatorio["sem_categoria_removidos"] = int(df["Categoria"].isna().sum())
    df = df.dropna(subset=["Categoria"])

    # Preenchimento com a mediana da categoria (robusta a assimetria).
    relatorio["ausentes_preenchidos"] = {
        c: int(df[c].isna().sum()) for c in ["Preço", "Vendas"]
    }
    for coluna in ["Preço", "Vendas"]:
        df[coluna] = df[coluna].fillna(df.groupby("Categoria")[coluna].transform("median"))

    relatorio["registros_saida"] = len(df)
    return df.reset_index(drop=True), relatorio
