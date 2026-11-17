"""Recarrega o DW a partir do OLTP, reaproveitando os scripts de ETL originais."""
from pathlib import Path

from database.conn_postgres import get_conn

PASTA_SQL = Path(__file__).resolve().parent / "gerar_banco"
SCRIPTS = ("05_carga_raw.sql", "06_carga_staging.sql", "07_carga_dw.sql")

TABELAS_RAW = [
    "raw.loja", "raw.colaborador", "raw.colaborador_trabalha",
    "raw.forma_pagamento", "raw.categoria", "raw.produto",
    "raw.produto_fragrancia", "raw.registro_pedido", "raw.detalhes_pedido",
]
TABELAS_STAGING = [
    "staging.stg_loja", "staging.stg_colaborador", "staging.stg_forma_pagamento",
    "staging.stg_produto", "staging.stg_tempo", "staging.stg_venda_item",
]


def atualizar_dw():
    """Trunca raw/staging e refaz a carga 05->07. Retorna o total de itens na fato."""
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute(f"TRUNCATE {', '.join(TABELAS_RAW)};")
        cur.execute(f"TRUNCATE {', '.join(TABELAS_STAGING)};")

        for nome in SCRIPTS:
            cur.execute((PASTA_SQL / nome).read_text(encoding="utf-8"))

        cur.execute("ANALYZE dw.fato_venda_item;")
        cur.execute("SELECT COUNT(*) AS total_fato FROM dw.fato_venda_item;")
        total = cur.fetchone()["total_fato"]

        conn.commit()
        return total

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()
