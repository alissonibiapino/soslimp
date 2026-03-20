from database.conn_postgres import get_conn
from psycopg2.extras import RealDictCursor

def caixa_atual(cod_loja):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
                    SELECT
                        ROUND(valor_atual, 2)
                    FROM caixa
                    WHERE cod_loja = %s
                    ;""", (cod_loja,))
        caixa = cur.fetchone()
        return caixa

    except Exception as e:
        conn.rollback()
        return print(f"Erro no banco: {e}")
    
    finally:
        cur.close()
        conn.close()