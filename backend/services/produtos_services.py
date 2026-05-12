from database.conn_postgres import get_conn
from psycopg2.extras import RealDictCursor

def listar_produtos():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT 
                p.cod_produto,
                p.nome_produto,
                p.marca,
                p.preco_unitario,
                c.cod_categoria,
                c.categoria_produto
            FROM produto p
            INNER JOIN categoria c USING (cod_categoria)
        """)
        produtos = cur.fetchall()
        return produtos

    except Exception as e:
        conn.rollback()
        return print(f"Erro no banco: {e}")
    
    finally:
        cur.close()
        conn.close()

def buscar_produto(produto_id: int):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
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
        return produto
    
    except Exception as e:
        conn.rollback()
        return print(f"Erro no banco: {e}")
    
    finally:
        cur.close()
        conn.close()

def listar_categorias():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:            
        cur.execute("""
            SELECT	
	            c.cod_categoria,
	            c.categoria_produto,
	            COUNT (p.cod_produto) AS total_produtos
            FROM categoria c
            INNER JOIN produto p USING (cod_categoria)
            GROUP BY c.cod_categoria, c.categoria_produto
            ORDER BY total_produtos DESC;
            """)
        categorias = cur.fetchall()
        return categorias

    except Exception as e:
        conn.rollback()
        return print(f"Erro no banco: {e}")
    
    finally:
        cur.close()
        conn.close()

def listar_produtos_por_categoria(categoria_id: int):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:            
        cur.execute("""
            SELECT 
                p.cod_produto,
                p.nome_produto,
                p.marca,
                p.preco_unitario
            FROM produto p
            JOIN categoria c
                ON p.cod_categoria = c.cod_categoria
            WHERE c.cod_categoria = %s
            """, (categoria_id,))
        produtos = cur.fetchall()
        return produtos

    except Exception as e:
        conn.rollback()
        return print(f"Erro no banco: {e}")
    
    finally:
        cur.close()
        conn.close()

def cadastrar_novo_produto(dados_do_produto):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        query = """
            INSERT INTO produto (cod_categoria, nome_produto, descricao, marca, preco_unitario)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING cod_produto;
        """
        
        valores = (
            dados_do_produto.get('cod_categoria'),
            dados_do_produto.get('nome_produto'),
            dados_do_produto.get('descricao'),
            dados_do_produto.get('marca'),
            dados_do_produto.get('preco_unitario')
        )

        cur.execute(query, valores)

        resultado = cur.fetchone()
        novo_id = resultado['cod_produto']

        conn.commit()
        return novo_id

    except Exception as e:
        conn.rollback()
        return print(f"Erro no banco: {e}")
    finally:
        cur.close()
        conn.close()

def editar_produto(cod_produto, dados_novos):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        query = """
            UPDATE produto 
            SET cod_categoria = %s, nome_produto = %s, descricao = %s, marca = %s, preco_unitario = %s
            WHERE cod_produto = %s
            RETURNING cod_produto;
        """
        valores = (
            dados_novos.get('cod_categoria'),
            dados_novos.get('nome_produto'),
            dados_novos.get('descricao'),
            dados_novos.get('marca'),
            dados_novos.get('preco_unitario'),
            cod_produto
        )

        cur.execute(query, valores)
        resultado = cur.fetchone()

        if not resultado:
            return None
        
        conn.commit()
        return resultado['cod_produto']
    
    except Exception as e:
        conn.rollback()
        return print(f"Erro no banco: {e}")
    finally:
        cur.close()
        conn.close()

