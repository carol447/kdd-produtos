"""Executa o pipeline KDD completo.

Uso:
    python main.py                 # usa data/raw/produtos.csv (gera se não existir)
    python main.py --k 4           # força o número de clusters
    python main.py --entrada x.csv # usa outra base com as mesmas colunas
"""

import argparse
import logging
from pathlib import Path

import pandas as pd

from kdd import gerar_dados, pipeline
from kdd.config import DADOS_BRUTOS, SEMENTE


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline KDD de segmentação de produtos")
    parser.add_argument("--entrada", type=Path, default=DADOS_BRUTOS, help="CSV de dados brutos")
    parser.add_argument("--k", type=int, help="número de clusters (padrão: escolhido pela silhueta)")
    parser.add_argument("--semente", type=int, default=SEMENTE)
    parser.add_argument("--regerar-dados", action="store_true", help="recria a base sintética")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if args.regerar_dados or (args.entrada == DADOS_BRUTOS and not DADOS_BRUTOS.exists()):
        gerar_dados.salvar(gerar_dados.gerar(semente=args.semente))
        logging.info("Base sintética gerada em %s", DADOS_BRUTOS)

    brutos = pd.read_csv(args.entrada)
    resultado = pipeline.executar(brutos, k=args.k, semente=args.semente)

    print("\nPerfil dos clusters:")
    print(resultado.perfil.to_string())
    print("\nResultados completos em reports/resultados.md")


if __name__ == "__main__":
    main()
