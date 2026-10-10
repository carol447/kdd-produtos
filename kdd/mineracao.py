"""Etapa 5 - Mineração de dados: agrupamento com K-Means."""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from kdd.config import FAIXA_K, SEMENTE


def _kmeans(k: int, semente: int) -> KMeans:
    return KMeans(n_clusters=k, n_init=10, random_state=semente)


def avaliar_k(X: np.ndarray, faixa=FAIXA_K, semente: int = SEMENTE) -> pd.DataFrame:
    """Inércia (método do cotovelo) e silhueta para cada k candidato."""
    linhas = []
    for k in faixa:
        modelo = _kmeans(k, semente).fit(X)
        linhas.append({
            "k": k,
            "inercia": modelo.inertia_,
            "silhueta": silhouette_score(X, modelo.labels_),
        })
    return pd.DataFrame(linhas)


def escolher_k(avaliacao: pd.DataFrame) -> int:
    return int(avaliacao.loc[avaliacao["silhueta"].idxmax(), "k"])


def agrupar(
    X: np.ndarray, k: int, ordenar_por: np.ndarray, semente: int = SEMENTE
) -> tuple[np.ndarray, KMeans]:
    """Agrupa e renumera os clusters em ordem crescente da média de `ordenar_por`.

    O K-Means numera os grupos arbitrariamente; a renumeração deixa os rótulos
    estáveis e interpretáveis (com o preço, cluster 0 = segmento mais barato).
    """
    modelo = _kmeans(k, semente).fit(X)
    medias = pd.Series(ordenar_por).groupby(modelo.labels_).mean()
    ordem = medias.sort_values().index.to_numpy()
    mapa = np.empty(k, dtype=int)
    mapa[ordem] = np.arange(k)
    modelo.cluster_centers_ = modelo.cluster_centers_[ordem]
    return mapa[modelo.labels_], modelo
