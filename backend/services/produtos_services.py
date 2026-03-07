from database.conn_postgres import get_conn
from psycopg2.extras import RealDictCursor

def listar_produtos():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT 
            cod_produto AS id,
            nome_produto AS nome,
            marca,
            preco_unitario AS preco
        FROM produto
    """)

    produtos = cur.fetchall()

    cur.close()
    conn.close()

    return produtos

def buscar_produto(produto_id: int):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT 
            cod_produto AS id,
            nome_produto AS nome,
            marca,
            preco_unitario AS preco
        FROM produto
        WHERE cod_produto = %s
    """, (produto_id,))

    produto = cur.fetchone()

    cur.close()
    conn.close()

    return produto

def listar_produtos_por_categoria(categoria_id: int):
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT 
                p.cod_produto AS id,
                p.nome_produto AS nome,
                p.marca,
                p.preco_unitario AS preco
            FROM produto p
            JOIN categoria c
                ON p.cod_categoria = c.cod_categoria
            WHERE c.cod_categoria = %s
            """, (categoria_id,))
        
        produtos = cur.fetchall()
        
        cur.close()
        conn.close()

        return produtos