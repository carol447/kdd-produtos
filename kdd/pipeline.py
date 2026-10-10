"""Orquestra as seis etapas do KDD e grava dados intermediários, métricas e figuras."""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from kdd import avaliacao, graficos, mineracao
from kdd.config import DIR_FIGURAS, DIR_PROCESSADOS, DIR_RELATORIOS, SEMENTE
from kdd.preprocessamento import preprocessar
from kdd.reducao import reduzir
from kdd.selecao import selecionar
from kdd.transformacao import transformar

log = logging.getLogger("kdd")


@dataclass
class Resultado:
    dados: pd.DataFrame
    atributos: list[str]
    k: int
    avaliacao_k: pd.DataFrame
    metricas: dict
    perfil: pd.DataFrame
    categoria_cluster: pd.DataFrame
    relatorios: dict = field(default_factory=dict)


def executar(
    brutos: pd.DataFrame,
    k: int | None = None,
    semente: int = SEMENTE,
    dir_processados: Path = DIR_PROCESSADOS,
    dir_relatorios: Path = DIR_RELATORIOS,
    salvar: bool = True,
) -> Resultado:
    relatorios = {}

    log.info("1/6 Seleção")
    df = selecionar(brutos)

    log.info("2/6 Pré-processamento")
    df, relatorios["preprocessamento"] = preprocessar(df)
    log.info("    %s", relatorios["preprocessamento"])

    log.info("3/6 Transformação")
    df = transformar(df)

    log.info("4/6 Redução de dados")
    df, atributos, relatorios["reducao"] = reduzir(df)
    log.info("    atributos selecionados: %s", atributos)

    log.info("5/6 Mineração (K-Means)")
    X = df[atributos].to_numpy()
    avaliacao_k = mineracao.avaliar_k(X, semente=semente)
    k = k or mineracao.escolher_k(avaliacao_k)
    rotulos, _ = mineracao.agrupar(X, k, ordenar_por=df["Preço"].to_numpy(), semente=semente)
    df["Cluster"] = rotulos

    log.info("6/6 Avaliação")
    resultado = Resultado(
        dados=df,
        atributos=atributos,
        k=k,
        avaliacao_k=avaliacao_k,
        metricas=avaliacao.metricas(X, rotulos),
        perfil=avaliacao.perfil(df),
        categoria_cluster=avaliacao.categoria_por_cluster(df),
        relatorios=relatorios,
    )
    log.info("    k=%d %s", k, resultado.metricas)

    if salvar:
        _salvar_saidas(resultado, X, dir_processados, dir_relatorios)
    return resultado


def _salvar_saidas(r: Resultado, X, dir_processados: Path, dir_relatorios: Path) -> None:
    dir_processados.mkdir(parents=True, exist_ok=True)
    figuras = dir_relatorios / DIR_FIGURAS.name
    figuras.mkdir(parents=True, exist_ok=True)

    r.dados.to_csv(dir_processados / "produtos_clusterizados.csv", index=False)
    r.perfil.to_csv(dir_relatorios / "perfil_clusters.csv")
    r.avaliacao_k.round(4).to_csv(dir_relatorios / "avaliacao_k.csv", index=False)

    with open(dir_relatorios / "metricas.json", "w", encoding="utf-8") as f:
        json.dump(
            {"k": r.k, "atributos": r.atributos, **r.metricas, "etapas": r.relatorios},
            f, ensure_ascii=False, indent=2,
        )

    graficos.escolha_k(r.avaliacao_k, r.k, figuras / "escolha_k.png")
    graficos.dispersao_clusters(r.dados, r.perfil, figuras / "clusters.png")
    graficos.silhueta_por_amostra(X, r.dados["Cluster"].to_numpy(), r.metricas["silhueta"], figuras / "silhueta.png")
    graficos.mapa_categoria_cluster(r.categoria_cluster, figuras / "categoria_por_cluster.png")

    (dir_relatorios / "resultados.md").write_text(_markdown(r), encoding="utf-8")


def _tabela_md(df: pd.DataFrame) -> str:
    df = df.reset_index()
    linhas = ["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
    linhas += ["| " + " | ".join(map(str, linha)) + " |" for linha in df.itertuples(index=False)]
    return "\n".join(linhas)


def _markdown(r: Resultado) -> str:
    pre = r.relatorios["preprocessamento"]
    red = r.relatorios["reducao"]
    return f"""# Resultados da execução

> Arquivo gerado automaticamente por `python main.py`.

## Pré-processamento

| Etapa | Registros |
|---|---|
| Entrada | {pre['registros_entrada']} |
| Duplicatas removidas | {pre['duplicatas_removidas']} |
| Valores inválidos removidos (preço ≤ 0 ou vendas < 0) | {pre['invalidos_removidos']} |
| Preços extremos removidos (> R$ {pre['limite_preco_extremo']}) | {pre['extremos_removidos']} |
| Sem categoria removidos | {pre['sem_categoria_removidos']} |
| Preços ausentes preenchidos (mediana da categoria) | {pre['ausentes_preenchidos']['Preço']} |
| Vendas ausentes preenchidas (mediana da categoria) | {pre['ausentes_preenchidos']['Vendas']} |
| **Saída** | **{pre['registros_saida']}** |

## Redução de dados

- Atributos selecionados para o agrupamento: `{', '.join(r.atributos)}`
- Removidos por correlação (|r| > 0,9): `{', '.join(red['removidos_por_correlacao']) or 'nenhum'}`
- ANOVA F contra a categoria (diagnóstico): {', '.join(f'{k} = {v}' for k, v in red['anova_f_vs_categoria'].items())}

## Mineração e avaliação

- k escolhido pela maior silhueta: **{r.k}**
- Silhueta: **{r.metricas['silhueta']}** (de -1 a 1; maior é melhor)
- Davies-Bouldin: **{r.metricas['davies_bouldin']}** (menor é melhor)
- Calinski-Harabasz: **{r.metricas['calinski_harabasz']}** (maior é melhor)

### Busca de k

{_tabela_md(r.avaliacao_k.round(3).set_index('k'))}

### Perfil dos clusters

{_tabela_md(r.perfil)}

### Distribuição das categorias entre clusters (%)

{_tabela_md(r.categoria_cluster)}
"""
