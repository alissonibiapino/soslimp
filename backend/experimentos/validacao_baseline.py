"""Passo 8 - MAE/RMSE do baseline de 30 dias vs. modelo MLP, no mesmo holdout."""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.dataset import montar_dataset
from ml.modelo import SEMANAS_HOLDOUT

CAMINHO_SCALER = Path(__file__).resolve().parent.parent / "ml" / "artefatos" / "scaler.json"


def metricas(y, previsto):
    erro = y - previsto
    return float(np.mean(np.abs(erro))), float(np.sqrt(np.mean(erro ** 2)))


def main():
    dados = montar_dataset()
    df = dados["df"]
    y = dados["y"]

    semanas = df["semana_inicio"].to_numpy()
    unicas = np.sort(np.unique(semanas))
    holdout = np.isin(semanas, unicas[-SEMANAS_HOLDOUT:])

    # Baseline "30 dias" = media das ultimas 4 semanas completas (28 dias).
    baseline = df["media4"].to_numpy()
    mae_b, rmse_b = metricas(y[holdout], baseline[holdout])

    scaler = json.loads(CAMINHO_SCALER.read_text(encoding="utf-8"))
    m = scaler["metricas_holdout"]

    print(f"linhas holdout: {holdout.sum()} | semanas: {unicas[-SEMANAS_HOLDOUT:].tolist()}")
    print(f"baseline (media 4 semanas ~ 30 dias): MAE={mae_b:.4f} RMSE={rmse_b:.4f}")
    print(f"modelo MLP:                           MAE={m['mae']:.4f} RMSE={m['rmse']:.4f}")
    ganho_mae = 100 * (mae_b - m["mae"]) / mae_b
    ganho_rmse = 100 * (rmse_b - m["rmse"]) / rmse_b
    print(f"ganho do modelo sobre o baseline: MAE {ganho_mae:.1f}% | RMSE {ganho_rmse:.1f}%")


if __name__ == "__main__":
    main()
