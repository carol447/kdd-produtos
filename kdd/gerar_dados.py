"""Gera um conjunto de dados sintético e propositalmente "sujo" de produtos.

Os dados do trabalho original não foram preservados, então este módulo cria uma
base reprodutível com os mesmos atributos e com os problemas que as etapas de
pré-processamento precisam tratar: colunas irrelevantes, texto inconsistente,
preços em formato brasileiro, valores ausentes, inválidos, extremos e duplicatas.
"""

import numpy as np
import pandas as pd

from kdd.config import DADOS_BRUTOS, SEMENTE

# Parâmetros log-normais (média e desvio em escala log) de preço e vendas.
PERFIS = {
    "camisa": {"preco": (4.00, 0.25), "vendas": (5.30, 0.35), "peso": 0.30},
    "calça": {"preco": (4.60, 0.25), "vendas": (4.70, 0.35), "peso": 0.25},
    "saia": {"preco": (4.30, 0.25), "vendas": (4.40, 0.35), "peso": 0.15},
    "vestido": {"preco": (5.10, 0.25), "vendas": (4.10, 0.35), "peso": 0.20},
    "jaqueta": {"preco": (5.50, 0.25), "vendas": (3.60, 0.35), "peso": 0.10},
}

VARIACOES_TEXTO = {
    "calça": ["calça", "Calça", "CALÇA", " calca", "calca "],
    "camisa": ["camisa", "Camisa", "CAMISA ", " camisa"],
    "saia": ["saia", "Saia", "SAIA"],
    "vestido": ["vestido", "Vestido", "VESTIDO", "vestido  "],
    "jaqueta": ["jaqueta", "Jaqueta", "JAQUETA", "jaqueta "],
}


def _formato_brasileiro(valor: float) -> str:
    texto = f"{valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {texto}"


def gerar(n: int = 1200, semente: int = SEMENTE) -> pd.DataFrame:
    rng = np.random.default_rng(semente)

    categorias = list(PERFIS)
    pesos = [PERFIS[c]["peso"] for c in categorias]
    categoria = rng.choice(categorias, size=n, p=pesos)

    preco = np.array([rng.lognormal(*PERFIS[c]["preco"]) for c in categoria]).round(2)
    vendas = np.array([rng.lognormal(*PERFIS[c]["vendas"]) for c in categoria]).round()

    df = pd.DataFrame({
        "ID_Produto": [f"P{i:05d}" for i in range(1, n + 1)],
        "Nome_Produto": [f"{c.title()} modelo {i}" for i, c in enumerate(categoria, 1)],
        "Categoria": [rng.choice(VARIACOES_TEXTO[c]) for c in categoria],
        "Preço": preco.astype(object),
        "Vendas": vendas,
        "Cor": rng.choice(["preto", "branco", "azul", "vermelho", "verde"], size=n),
        "Tamanho": rng.choice(["PP", "P", "M", "G", "GG"], size=n),
        "Fornecedor": rng.choice([f"F{i:02d}" for i in range(1, 16)], size=n),
        "Codigo_Barras": rng.integers(10**12, 10**13, size=n).astype(str),
        "Data_Cadastro": pd.Timestamp("2023-01-01")
        + pd.to_timedelta(rng.integers(0, 600, size=n), unit="D"),
    })

    # Parte dos preços chega como texto no formato "R$ 1.234,56".
    idx = rng.choice(n, size=int(0.10 * n), replace=False)
    df.loc[idx, "Preço"] = [_formato_brasileiro(v) for v in preco[idx]]

    # Valores ausentes.
    for coluna, fracao in [("Preço", 0.04), ("Vendas", 0.04), ("Categoria", 0.01)]:
        idx = rng.choice(n, size=int(fracao * n), replace=False)
        df.loc[idx, coluna] = np.nan

    # Valores inválidos e erros de digitação.
    idx = rng.choice(n, size=12, replace=False)
    df.loc[idx[:4], "Preço"] = -preco[idx[:4]]
    df.loc[idx[4:6], "Preço"] = 0
    df.loc[idx[6:9], "Vendas"] = -5
    df.loc[idx[9:], "Preço"] = 99999.0

    # Duplicatas exatas e registros repetidos com texto diferente.
    duplicadas = df.sample(frac=0.03, random_state=semente)
    repetidas = df.sample(n=10, random_state=semente + 1).assign(
        Categoria=lambda d: d["Categoria"].str.upper()
    )
    df = pd.concat([df, duplicadas, repetidas], ignore_index=True)

    return df.sample(frac=1, random_state=semente).reset_index(drop=True)


def salvar(df: pd.DataFrame, caminho=DADOS_BRUTOS) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho, index=False)


if __name__ == "__main__":
    dados = gerar()
    salvar(dados)
    print(f"{len(dados)} registros salvos em {DADOS_BRUTOS}")
