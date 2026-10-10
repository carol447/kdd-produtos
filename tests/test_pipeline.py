import numpy as np
import pandas as pd
import pytest

from kdd import gerar_dados, pipeline
from kdd.preprocessamento import converter_preco, normalizar_texto, preprocessar
from kdd.selecao import selecionar
from kdd.transformacao import transformar


@pytest.mark.parametrize("entrada, esperado", [
    ("R$ 1.234,56", 1234.56),
    ("R$ 89,90", 89.90),
    ("89.9", 89.9),
    (45, 45.0),
    ("abc", None),
    (None, None),
])
def test_converter_preco(entrada, esperado):
    resultado = converter_preco(entrada)
    if esperado is None:
        assert np.isnan(resultado)
    else:
        assert resultado == pytest.approx(esperado)


@pytest.mark.parametrize("entrada", ["calça", " CALÇA ", "calca", "Calca  "])
def test_normalizar_texto_unifica_grafias(entrada):
    assert normalizar_texto(entrada) == "calça"


def test_selecao_exige_colunas():
    with pytest.raises(ValueError, match="Vendas"):
        selecionar(pd.DataFrame(columns=["ID_Produto", "Categoria", "Preço"]))


def test_preprocessamento_limpa_os_dados():
    brutos = pd.DataFrame({
        "ID_Produto": ["A", "A", "B", "C", "D", "E", "F", "G"],
        "Categoria": ["camisa", "CAMISA", "Camisa ", "camisa", None, "calca", "calça", "calça"],
        "Preço": [50, 50, "R$ 60,00", -10, 70, np.nan, 100, 120],
        "Vendas": [10, 10, 20, 30, 40, 50, np.nan, 70],
    })
    df, relatorio = preprocessar(brutos)

    assert relatorio["duplicatas_removidas"] == 1
    assert relatorio["invalidos_removidos"] == 1
    assert relatorio["sem_categoria_removidos"] == 1
    assert set(df["Categoria"]) == {"camisa", "calça"}
    assert not df[["Preço", "Vendas"]].isna().any().any()
    # Preço ausente de "E" recebe a mediana da categoria calça (100 e 120).
    assert df.set_index("ID_Produto").loc["E", "Preço"] == 110


def test_transformacao_normaliza_e_discretiza():
    df = pd.DataFrame({
        "Categoria": ["a"] * 6,
        "Preço": [10, 20, 30, 40, 50, 60],
        "Vendas": [5, 4, 3, 2, 1, 0],
    })
    df = transformar(df)
    for coluna in ["Preço_norm", "Vendas_norm", "Receita_norm"]:
        assert df[coluna].between(0, 1).all()
    assert list(df["Faixa_Preço"].cat.categories) == ["Baixo", "Médio", "Alto"]
    assert df["Faixa_Preço"].value_counts().eq(2).all()


def test_pipeline_completo(tmp_path):
    brutos = gerar_dados.gerar(n=400, semente=7)
    r = pipeline.executar(brutos, k=3, dir_processados=tmp_path / "proc", dir_relatorios=tmp_path / "rep")

    assert r.dados["Cluster"].nunique() == 3
    assert -1 <= r.metricas["silhueta"] <= 1
    # Clusters numerados em ordem crescente de preço.
    medianas = r.dados.groupby("Cluster")["Preço"].mean()
    assert medianas.is_monotonic_increasing
    for arquivo in ["metricas.json", "resultados.md", "figures/clusters.png"]:
        assert (tmp_path / "rep" / arquivo).exists()
