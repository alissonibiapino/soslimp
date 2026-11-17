"""Monta o dataset semanal (produto x loja) usado para treinar o modelo de demanda."""
from datetime import date

import numpy as np
import pandas as pd

from database.conn_postgres import get_conn

N_LAGS = 4
MIN_PERIODS_MEDIA = 4


def _consultar(sql):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(sql)
        colunas = [desc[0] for desc in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=colunas)
    finally:
        cur.close()
        conn.close()


def carregar_vendas_semanais():
    return _consultar("""
        SELECT date_trunc('week', t.data)::date AS semana_inicio,
               p.cod_produto,
               l.cod_loja,
               SUM(f.quantidade)::float AS quantidade
        FROM dw.fato_venda_item f
        JOIN dw.dim_tempo t ON t.sk_tempo = f.fk_tempo
        JOIN dw.dim_produto p ON p.sk_produto = f.fk_produto
        JOIN dw.dim_loja l ON l.sk_loja = f.fk_loja
        GROUP BY 1, 2, 3
        ORDER BY 1, 2, 3;
    """)


def carregar_calendario():
    return _consultar("""
        SELECT MIN(data) AS min_data,
               MAX(data) AS max_data
        FROM dw.dim_tempo;
    """).iloc[0]


def carregar_primeira_venda_por_loja():
    return _consultar("""
        SELECT l.cod_loja, MIN(t.data) AS primeira_venda
        FROM dw.fato_venda_item f
        JOIN dw.dim_tempo t ON t.sk_tempo = f.fk_tempo
        JOIN dw.dim_loja l ON l.sk_loja = f.fk_loja
        GROUP BY 1;
    """)


def carregar_produtos():
    return _consultar("""
        SELECT cod_produto, nome_produto, categoria_produto
        FROM dw.dim_produto
        ORDER BY cod_produto;
    """)


def carregar_lojas():
    return _consultar("SELECT cod_loja FROM dw.dim_loja ORDER BY cod_loja;")


def carregar_preco_mais_recente():
    return _consultar("""
        SELECT DISTINCT ON (p.cod_produto)
               p.cod_produto,
               f.preco_unitario_praticado::float AS preco
        FROM dw.fato_venda_item f
        JOIN dw.dim_produto p ON p.sk_produto = f.fk_produto
        JOIN dw.dim_tempo t ON t.sk_tempo = f.fk_tempo
        WHERE f.preco_unitario_praticado IS NOT NULL
        ORDER BY p.cod_produto, t.data DESC, f.sk_venda_item DESC;
    """)


def montar_dataset():
    vendas = carregar_vendas_semanais()
    vendas["semana_inicio"] = pd.to_datetime(vendas["semana_inicio"])
    if vendas.empty:
        raise ValueError("DW sem vendas: carregue o banco antes de treinar.")

    calendario = carregar_calendario()
    max_data = pd.Timestamp(calendario["max_data"])
    semana_min = pd.Timestamp(calendario["min_data"]).to_period("W-SUN").start_time

    primeira_venda = pd.to_datetime(
        carregar_primeira_venda_por_loja().set_index("cod_loja")["primeira_venda"]
    )
    produtos = carregar_produtos()
    lojas = carregar_lojas()
    precos = carregar_preco_mais_recente().set_index("cod_produto")["preco"]

    semanas = pd.date_range(semana_min, max_data, freq="7D")
    semanas = semanas[semanas + pd.Timedelta(days=6) <= max_data]
    semana_atual = pd.Timestamp(date.today()).to_period("W-SUN").start_time
    semanas = semanas[semanas < semana_atual]
    if len(semanas) <= N_LAGS:
        raise ValueError("Histórico semanal insuficiente para montar os lags.")

    grade = pd.MultiIndex.from_product(
        [semanas, produtos["cod_produto"], lojas["cod_loja"]],
        names=["semana_inicio", "cod_produto", "cod_loja"],
    ).to_frame(index=False)

    df = grade.merge(vendas, on=["semana_inicio", "cod_produto", "cod_loja"], how="left")
    df["quantidade"] = df["quantidade"].fillna(0.0)

    # Loja sem venda antes da inauguração não tem demanda real: tira os zeros artificiais.
    df["primeira_semana_loja"] = df["cod_loja"].map(primeira_venda).dt.to_period("W-SUN").dt.start_time
    df = df[df["semana_inicio"] >= df["primeira_semana_loja"]].copy()

    df = df.sort_values(["cod_produto", "cod_loja", "semana_inicio"]).reset_index(drop=True)
    chaves = ["cod_produto", "cod_loja"]

    df["qtd_prev"] = df.groupby(chaves)["quantidade"].shift(1)
    for n in range(1, N_LAGS + 1):
        df[f"lag{n}"] = df.groupby(chaves)["qtd_prev"].shift(n - 1)
    for n in (4, 12):
        df[f"media{n}"] = df.groupby(chaves)["qtd_prev"].transform(
            lambda s: s.rolling(n, min_periods=MIN_PERIODS_MEDIA).mean()
        )

    numero_semana = df["semana_inicio"].dt.isocalendar().week.astype(int)
    df["sen_sem"] = np.sin(2 * np.pi * numero_semana / 52)
    df["cos_sem"] = np.cos(2 * np.pi * numero_semana / 52)

    df["categoria_produto"] = df["cod_produto"].map(
        produtos.set_index("cod_produto")["categoria_produto"]
    )
    df["preco"] = df["cod_produto"].map(precos)
    # shortcut: produto sem nenhuma venda recebe preço 0, revisar quando entrar em catálogo sem histórico
    df["preco"] = df["preco"].fillna(0.0)

    df = df.dropna(subset=[f"lag{n}" for n in range(1, N_LAGS + 1)] + ["media4", "media12"])
    df = df.reset_index(drop=True)

    if df.empty:
        raise ValueError("Nenhuma linha sobrou após montar os lags.")

    numericas = [f"lag{n}" for n in range(1, N_LAGS + 1)] + [
        "media4", "media12", "sen_sem", "cos_sem", "preco"
    ]
    categorias = {
        "produto": produtos["cod_produto"].tolist(),
        "loja": lojas["cod_loja"].tolist(),
        "categoria": sorted(produtos["categoria_produto"].dropna().unique().tolist()),
    }

    blocos = [df[numericas].astype(float)]
    nomes = list(numericas)
    for chave, prefixo in (("cod_produto", "prod"), ("cod_loja", "loja"), ("categoria_produto", "cat")):
        dummies = pd.get_dummies(df[chave], prefix=prefixo, dtype=float)
        dummies = dummies.reindex(
            columns=[f"{prefixo}_{valor}" for valor in categorias[
                {"cod_produto": "produto", "cod_loja": "loja", "categoria_produto": "categoria"}[chave]
            ]],
            fill_value=0.0,
        )
        blocos.append(dummies)
        nomes.extend(dummies.columns.tolist())

    X = np.hstack([bloco.to_numpy(dtype=float) for bloco in blocos])
    y = df["quantidade"].to_numpy(dtype=float)
    feature_names = nomes

    assert not np.isnan(X).any(), "features com NaN"
    assert (y >= 0).all(), "target negativo"
    assert df["semana_inicio"].max() < semana_atual, "semana atual incompleta no dataset"
    assert X.shape[1] == len(feature_names), "features e nomes fora de sincronia"

    return {
        "df": df,
        "X": X,
        "y": y,
        "feature_names": feature_names,
        "produtos": categorias["produto"],
        "lojas": categorias["loja"],
        "categorias": produtos.set_index("cod_produto")["categoria_produto"].to_dict(),
        "precos": precos.to_dict(),
        "semana_atual": semana_atual,
    }


if __name__ == "__main__":
    dados = montar_dataset()
    print(f"X={dados['X'].shape} | y={dados['y'].shape} | features={len(dados['feature_names'])}")
    print(f"semanas: {dados['df']['semana_inicio'].min().date()} a {dados['df']['semana_inicio'].max().date()}")
