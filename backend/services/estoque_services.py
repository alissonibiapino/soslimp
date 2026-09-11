from database.conn_postgres import get_conn
from psycopg2.extras import RealDictCursor
from fastapi import HTTPException

def listar_estoque():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT * FROM estoque;
        """)
        estoque = cur.fetchall()
        return estoque

    except Exception as e:
        conn.rollback()
        return print(f"Erro no banco: {e}")
    
    finally:
        cur.close()
        conn.close()


def listar_estoque_por_loja(cod_loja: int):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT * FROM estoque WHERE cod_loja = %s;
        """, (cod_loja,))
        estoque = cur.fetchall()
        return estoque

    except Exception as e:
        conn.rollback()
        return print(f"Erro no banco: {e}")
    
    finally:
        cur.close()
        conn.close()
