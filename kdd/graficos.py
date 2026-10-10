"""Figuras do pipeline, com um estilo único e paleta categórica de ordem fixa."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402
from sklearn.metrics import silhouette_samples  # noqa: E402

# Paleta categórica validada para daltonismo; usada sempre na mesma ordem.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
SUPERFICIE = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
TINTA_SUAVE = "#898781"
GRADE = "#e1e0d9"
EIXO = "#c3c2b7"
AZUL_SEQUENCIAL = LinearSegmentedColormap.from_list("azul", ["#f0efec", "#9ec5f4", "#2a78d6", "#0d366b"])

plt.rcParams.update({
    "figure.facecolor": SUPERFICIE,
    "axes.facecolor": SUPERFICIE,
    "savefig.facecolor": SUPERFICIE,
    "axes.edgecolor": EIXO,
    "axes.labelcolor": TINTA_SECUNDARIA,
    "axes.titlecolor": TINTA,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": GRADE,
    "grid.linewidth": 0.6,
    "axes.axisbelow": True,
    "xtick.color": TINTA_SUAVE,
    "ytick.color": TINTA_SUAVE,
    "xtick.labelcolor": TINTA_SECUNDARIA,
    "ytick.labelcolor": TINTA_SECUNDARIA,
    "legend.frameon": False,
    "legend.labelcolor": TINTA_SECUNDARIA,
    "font.size": 10,
})


def _salvar(fig, caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close(fig)


def escolha_k(avaliacao: pd.DataFrame, k_escolhido: int, caminho: Path) -> None:
    """Cotovelo e silhueta lado a lado: duas medidas, dois eixos separados."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.6))
    for ax, coluna, titulo in [
        (ax1, "inercia", "Inércia (método do cotovelo)"),
        (ax2, "silhueta", "Silhueta média"),
    ]:
        ax.plot(avaliacao["k"], avaliacao[coluna], color=SERIES[0], lw=2, marker="o", ms=6)
        linha = avaliacao.set_index("k").loc[k_escolhido, coluna]
        ax.plot(k_escolhido, linha, "o", ms=10, mfc=SERIES[1], mec=SUPERFICIE, mew=2)
        ax.set_title(titulo)
        ax.margins(x=0.06, y=0.12)
        ax.set_xlabel("Número de clusters (k)")
        ax.set_xticks(avaliacao["k"])
    ax2.annotate(
        f"k = {k_escolhido}",
        (k_escolhido, avaliacao.set_index("k").loc[k_escolhido, "silhueta"]),
        xytext=(10, -4), textcoords="offset points", color=TINTA_SECUNDARIA,
    )
    fig.tight_layout()
    _salvar(fig, caminho)


def dispersao_clusters(df: pd.DataFrame, perfil: pd.DataFrame, caminho: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5.5))
    for cluster, grupo in df.groupby("Cluster"):
        ax.scatter(
            grupo["Preço"], grupo["Vendas"], s=16, alpha=0.75, color=SERIES[cluster],
            edgecolors=SUPERFICIE, linewidths=0.5,
            label=f"{cluster} · {perfil.loc[cluster, 'Segmento']}",
        )
    ax.set_xscale("log")
    ax.set_yscale("log")
    # Rotula 1, 2, 3 e 5 de cada década; os demais ticks ficam sem texto.
    rotulo = FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", ".") if f"{v:.0f}"[0] in "1235" else "")
    for eixo in (ax.xaxis, ax.yaxis):
        eixo.set_major_formatter(rotulo)
        eixo.set_minor_formatter(rotulo)
    ax.set_xlabel("Preço (R$, escala log)")
    ax.set_ylabel("Vendas (unidades, escala log)")
    ax.set_title("Segmentos de produtos encontrados pelo K-Means")
    ax.legend(title="Cluster", title_fontsize=9, loc="upper right", markerscale=1.6)
    _salvar(fig, caminho)


def silhueta_por_amostra(X: np.ndarray, rotulos: np.ndarray, media: float, caminho: Path) -> None:
    valores = silhouette_samples(X, rotulos)
    fig, ax = plt.subplots(figsize=(8, 5))
    base = 0
    for cluster in np.unique(rotulos):
        v = np.sort(valores[rotulos == cluster])
        ax.fill_betweenx(np.arange(base, base + len(v)), 0, v, color=SERIES[cluster], lw=0)
        ax.text(-0.04, base + len(v) / 2, str(cluster), va="center", ha="right", color=TINTA_SECUNDARIA)
        base += len(v) + 15
    ax.axvline(media, color=TINTA_SECUNDARIA, ls="--", lw=1)
    ax.text(media, base + 10, f" média = {media:.2f}".replace(".", ","), color=TINTA_SECUNDARIA, va="bottom")
    ax.set_ylim(-10, base + 0.08 * base)
    ax.set_xlim(-0.2, 1)
    ax.set_yticks([])
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Coeficiente de silhueta")
    ax.set_ylabel("Produtos, agrupados por cluster")
    ax.set_title("Silhueta de cada produto")
    _salvar(fig, caminho)


def mapa_categoria_cluster(tabela: pd.DataFrame, caminho: Path) -> None:
    fig, ax = plt.subplots(figsize=(1.3 * tabela.shape[1] + 2.5, 0.55 * tabela.shape[0] + 1.5))
    ax.imshow(tabela.to_numpy(), cmap=AZUL_SEQUENCIAL, vmin=0, vmax=100, aspect="auto")
    for (i, j), valor in np.ndenumerate(tabela.to_numpy()):
        cor = "#ffffff" if valor > 55 else TINTA
        ax.text(j, i, f"{valor:.0f}%", ha="center", va="center", color=cor, fontsize=9)
    ax.set_xticks(range(tabela.shape[1]), [f"Cluster {c}" for c in tabela.columns])
    ax.set_yticks(range(tabela.shape[0]), tabela.index)
    ax.grid(False)
    for lado in ax.spines.values():
        lado.set_visible(False)
    ax.tick_params(length=0)
    ax.set_title("Onde cada categoria caiu (% da categoria)")
    _salvar(fig, caminho)
