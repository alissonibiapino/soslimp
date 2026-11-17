"""Serviços de treino do modelo e previsão de ruptura de estoque."""
import threading
from datetime import date, timedelta

import numpy as np
import torch
from fastapi import HTTPException
from psycopg2.extras import RealDictCursor

from database.conn_postgres import get_conn
from database.etl_dw import atualizar_dw
from ml import modelo as ml_modelo
from ml.dataset import montar_dataset
from models.previsao import PrevisaoEstoque

# Evita dois treinos pesados rodando ao mesmo tempo.
treino_em_andamento = threading.Lock()


def treinar_modelo():
    if not treino_em_andamento.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="Treino já em andamento.")

    try:
        try:
            linhas_dw = atualizar_dw()
        except Exception as erro:
            raise HTTPException(
                status_code=500,
                detail=f"Falha ao recarregar o DW: {erro}"
            )

        dados = montar_dataset()

        modelo, scaler = ml_modelo.treinar(
            dados["X"],
            dados["y"],
            dados["df"]["semana_inicio"]
        )

        ultima_semana = dados["df"]["semana_inicio"].max().date().isoformat()

        ml_modelo.salvar(
            modelo,
            scaler,
            feature_names=dados["feature_names"],
            produtos=dados["produtos"],
            lojas=dados["lojas"],
            categorias=dados["categorias"],
            precos=dados["precos"],
            ultima_semana_treino=ultima_semana
        )

        return {
            "linhas_dw": linhas_dw,
            "linhas_treino": len(dados["y"]),
            "ultima_semana_treino": ultima_semana,
            "metricas_holdout": scaler["metricas_holdout"]
        }

    finally:
        treino_em_andamento.release()


def carregar_modelo_treinado():
    try:
        return ml_modelo.carregar()
    except Exception as erro:
        raise HTTPException(
            status_code=503,
            detail=f"Modelo indisponível: {erro}"
        )


def buscar_estoque_da_loja(cod_loja):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT e.cod_produto, p.nome_produto, e.quantidade_atual
            FROM estoque e
            JOIN produto p USING (cod_produto)
            WHERE e.cod_loja = %s;
        """, (cod_loja,))

        estoque_por_produto = {}
        for linha in cur.fetchall():
            estoque_por_produto[linha["cod_produto"]] = linha

        return estoque_por_produto

    finally:
        cur.close()
        conn.close()


def separar_ultima_semana(dados, cod_loja):
    """Pega as features da última semana completa da loja escolhida."""
    tabela = dados["df"]
    ultima_semana = tabela["semana_inicio"].max()

    filtro = (tabela["semana_inicio"] == ultima_semana) & (tabela["cod_loja"] == cod_loja)
    if not filtro.any():
        raise HTTPException(
            status_code=404,
            detail="Loja sem histórico suficiente para previsão."
        )

    produtos = tabela.loc[filtro, "cod_produto"].tolist()

    # X está na mesma ordem das linhas da tabela.
    matriz_entrada = dados["X"][filtro.to_numpy()]

    return produtos, matriz_entrada


def normalizar_entrada(matriz_entrada, scaler):
    media = np.array(scaler["media"])
    desvio = np.array(scaler["desvio"])
    return (matriz_entrada - media) / desvio


def prever_proxima_semana(modelo, matriz_entrada):
    modelo.eval()

    with torch.no_grad():
        entradas = torch.tensor(matriz_entrada, dtype=torch.float32)
        previsoes = modelo(entradas).numpy()

    return previsoes


def classificar_risco(dias_restantes):
    if dias_restantes is None:
        return "OK"
    if dias_restantes <= 7:
        return "CRITICO"
    if dias_restantes <= 15:
        return "ATENCAO"
    return "OK"


def montar_previsao(cod_produto, nome_produto, quantidade_atual, previsao_semana):
    consumo_diario = previsao_semana / 7

    if consumo_diario > 0:
        dias_restantes = quantidade_atual / consumo_diario
        data_ruptura = date.today() + timedelta(days=dias_restantes)
    else:
        dias_restantes = None
        data_ruptura = None

    return PrevisaoEstoque(
        cod_produto=cod_produto,
        nome_produto=nome_produto,
        quantidade_atual=quantidade_atual,
        consumo_previsto_diario=round(consumo_diario, 2),
        dias_restantes=round(dias_restantes, 1) if dias_restantes is not None else None,
        data_ruptura_estimada=data_ruptura,
        risco=classificar_risco(dias_restantes)
    )


def prever_loja(cod_loja):
    modelo, scaler = carregar_modelo_treinado()
    dados = montar_dataset()

    # O modelo só pode receber as mesmas features com que foi treinado.
    if dados["feature_names"] != scaler.get("feature_names"):
        raise HTTPException(
            status_code=503,
            detail="Features do modelo incompatíveis com o DW atual."
        )

    produtos, matriz_entrada = separar_ultima_semana(dados, cod_loja)
    matriz_entrada = normalizar_entrada(matriz_entrada, scaler)
    previsoes_semanais = prever_proxima_semana(modelo, matriz_entrada)
    estoque = buscar_estoque_da_loja(cod_loja)

    resultado = []

    for cod_produto, previsao_semana in zip(produtos, previsoes_semanais):
        produto_em_estoque = estoque.get(int(cod_produto))
        if produto_em_estoque is None:
            continue

        previsao = montar_previsao(
            cod_produto=int(cod_produto),
            nome_produto=produto_em_estoque["nome_produto"],
            quantidade_atual=int(produto_em_estoque["quantidade_atual"]),
            previsao_semana=float(previsao_semana)
        )
        resultado.append(previsao)

    return resultado


def prever_produto(cod_loja, cod_produto):
    previsoes = prever_loja(cod_loja)

    for previsao in previsoes:
        if previsao.cod_produto == cod_produto:
            return previsao

    raise HTTPException(
        status_code=404,
        detail="Produto sem previsão para esta loja."
    )
