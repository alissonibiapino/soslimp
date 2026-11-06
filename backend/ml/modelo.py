"""Rede MLP para previsão da demanda semanal e persistência dos artefatos."""
import json
import random
from datetime import date
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

PASTA_ARTEFATOS = Path(__file__).resolve().parent / "artefatos"
CAMINHO_MODELO = PASTA_ARTEFATOS / "modelo.pt"
CAMINHO_SCALER = PASTA_ARTEFATOS / "scaler.json"
SEMENTE = 42
SEMANAS_HOLDOUT = 8


class MLPDemanda(nn.Module):
    def __init__(self, n_features):
        super().__init__()
        self.rede = nn.Sequential(
            nn.Linear(n_features, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.ReLU(),
        )

    def forward(self, x):
        return self.rede(x).squeeze(-1)


def _travar_aleatoriedade():
    random.seed(SEMENTE)
    np.random.seed(SEMENTE)
    torch.manual_seed(SEMENTE)


def _ajustar_escala(X, media=None, desvio=None):
    if media is None:
        media = X.mean(axis=0)
        desvio = X.std(axis=0)
        desvio[desvio == 0] = 1.0
    return (X - media) / desvio, media, desvio


def _treinar_rede(X, y, epochs):
    _travar_aleatoriedade()
    modelo = MLPDemanda(X.shape[1])
    otimizador = torch.optim.Adam(modelo.parameters(), lr=1e-3)
    perda = nn.MSELoss()
    tensor_x = torch.tensor(X, dtype=torch.float32)
    tensor_y = torch.tensor(y, dtype=torch.float32)

    modelo.train()
    for _ in range(epochs):
        otimizador.zero_grad()
        erro = perda(modelo(tensor_x), tensor_y)
        erro.backward()
        otimizador.step()

    return modelo


def _prever(modelo, X):
    modelo.eval()
    with torch.no_grad():
        return modelo(torch.tensor(X, dtype=torch.float32)).numpy()


def treinar(X, y, semanas=None, epochs=200):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)

    if semanas is None:
        corte = int(len(X) * 0.8)
        treino = np.arange(len(X)) < corte
        holdout = ~treino
    else:
        semanas = np.asarray(semanas)
        semanas_unicas = np.sort(np.unique(semanas))
        if len(semanas_unicas) <= SEMANAS_HOLDOUT:
            raise ValueError("Histórico insuficiente para separar o holdout de 8 semanas.")
        holdout = np.isin(semanas, semanas_unicas[-SEMANAS_HOLDOUT:])
        treino = ~holdout

    if not treino.any() or not holdout.any():
        raise ValueError("Divisão treino/holdout vazia.")

    X_treino, media, desvio = _ajustar_escala(X[treino])
    modelo_holdout = _treinar_rede(X_treino, y[treino], epochs)

    X_holdout = (X[holdout] - media) / desvio
    previsto = _prever(modelo_holdout, X_holdout)
    erro = y[holdout] - previsto
    metricas = {
        "mae": float(np.mean(np.abs(erro))),
        "rmse": float(np.sqrt(np.mean(erro ** 2))),
        "semanas_holdout": int(SEMANAS_HOLDOUT),
    }

    # Modelo final usa todo o histórico; as métricas continuam sendo as do holdout.
    X_final, media, desvio = _ajustar_escala(X)
    modelo = _treinar_rede(X_final, y, epochs)

    scaler = {
        "media": [float(v) for v in media],
        "desvio": [float(v) for v in desvio],
        "n_features": int(X.shape[1]),
        "treinado_em": date.today().isoformat(),
        "metricas_holdout": metricas,
    }
    return modelo, scaler


def salvar(modelo, scaler, **metadados):
    PASTA_ARTEFATOS.mkdir(parents=True, exist_ok=True)
    torch.save(modelo.state_dict(), CAMINHO_MODELO)
    with open(CAMINHO_SCALER, "w", encoding="utf-8") as arquivo:
        json.dump({**scaler, **metadados}, arquivo, ensure_ascii=False, indent=2)


def carregar():
    if not CAMINHO_MODELO.exists() or not CAMINHO_SCALER.exists():
        raise FileNotFoundError(
            "Modelo não treinado: execute POST /previsao/treinar antes de prever."
        )

    with open(CAMINHO_SCALER, encoding="utf-8") as arquivo:
        scaler = json.load(arquivo)

    modelo = MLPDemanda(scaler["n_features"])
    modelo.load_state_dict(torch.load(CAMINHO_MODELO, map_location="cpu"))
    modelo.eval()
    return modelo, scaler
