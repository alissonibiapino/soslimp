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

def ajustar_estoque_manualmente(ajuste):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    print(ajuste)
    print(ajuste["quantidade"])
    print(ajuste["cod_produto"])
    print(ajuste["cod_loja"])

    try:
        cur.execute("""
            UPDATE estoque SET quantidade_atual = %s WHERE cod_produto = %s AND cod_loja = %s;
        """, (ajuste["quantidade"], ajuste["cod_produto"], ajuste["cod_loja"]))
        conn.commit()
        return "Estoque ajustado com sucesso!"

    except Exception as e:
        conn.rollback()
        return print(f"Erro no banco: {e}")
    
    finally:
        cur.close()
        conn.close()
