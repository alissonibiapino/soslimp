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
            UPDATE estoque 
            SET quantidade_atual = quantidade_atual + %s, atualizado_em = CURRENT_TIMESTAMP
            WHERE cod_produto = %s AND cod_loja = %s
            RETURNING quantidade_atual
        """, (ajuste["quantidade"], ajuste["cod_produto"], ajuste["cod_loja"]))

        resultado = cur.fetchone()

        if not resultado:
            raise Exception("Produto ou loja não encontrado!")

        cur.execute("""
            INSERT INTO movimentacao_estoque (cod_produto, cod_loja, tipo_movimentacao, quantidade, motivo)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            ajuste["cod_produto"],
            ajuste["cod_loja"],
            'ENTRADA' if ajuste["quantidade"] > 0 else 'AJUSTE',
            abs(ajuste["quantidade"]),
            ajuste["motivo"]
        ))

        conn.commit()
        return "Estoque ajustado com sucesso!"

    except Exception as e:
        conn.rollback()
        return print(f"Erro no banco: {e}")
    
    finally:
        cur.close()
        conn.close()
