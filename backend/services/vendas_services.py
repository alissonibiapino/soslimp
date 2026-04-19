from database.conn_postgres import get_conn
from psycopg2.extras import RealDictCursor
from services.neo4j_services import registrar_novo_pedido_neo4j

def listar_vendas_do_dia():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT
                cod_venda, INITCAP(forma_pagamento.tipo_pagamento), rp.hora_do_registro, rp.valor_total
            FROM registro_pedido rp
            INNER JOIN forma_pagamento USING (cod_forma_pag)
            WHERE DATE(hora_do_registro) = CURRENT_DATE
            ORDER BY hora_do_registro DESC;
        """)
        vendas = cur.fetchall()
        return vendas

    except Exception as e:
        conn.rollback()
        return print(f"Erro no banco: {e}")
    
    finally:
        cur.close()
        conn.close()

def listar_vendas_do_dia_por_loja(cod_loja: int):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT
                cod_venda, INITCAP(forma_pagamento.tipo_pagamento), rp.hora_do_registro, rp.valor_total
            FROM registro_pedido rp
            INNER JOIN forma_pagamento USING (cod_forma_pag)
            WHERE DATE(hora_do_registro) = CURRENT_DATE AND cod_loja = %s
            ORDER BY hora_do_registro DESC;
        """, (cod_loja,))
        vendas = cur.fetchall()
        return vendas

    except Exception as e:
        conn.rollback()
        return print(f"Erro no banco: {e}")
    
    finally:
        cur.close()
        conn.close()

def listar_pedidos_do_dia():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT
                dp.cod_detalhes
            FROM detalhes_pedido dp
        """)
        pedidos = cur.fetchall()
        return pedidos

    except Exception as e:
        conn.rollback()
        return print(f"Erro no banco: {e}")
    
    finally:
        cur.close()
        conn.close()

def registrar_novo_pedido(dados_do_pedido):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    print(dados_do_pedido)

    try:
        valor_total_venda = 0
        produtos_processados = []

        for produto in dados_do_pedido['produtos']:
            cur.execute("""
                        SELECT
                            preco_unitario,
                            nome_produto,
                            marca
                        FROM produto
                        WHERE cod_produto = %s""",
                        (produto['cod_produto'],))
            prod_bd = cur.fetchone()

            cur.execute("""
                SELECT nome_fragrancia
                FROM fragrancia
                WHERE cod_fragrancia = %s
            """, (produto['cod_fragrancia'],))
            frag_bd = cur.fetchone()
            
            preco_atual = float(prod_bd['preco_unitario'])
            subtotal = preco_atual * produto['quantidade']
            valor_total_venda += subtotal

            produtos_processados.append({
                'cod_produto': produto['cod_produto'],
                'cod_fragrancia': produto['cod_fragrancia'],
                'qtd': produto['quantidade'],
                'preco': preco_atual,
                'nome_produto': prod_bd['nome_produto'],
                'marca': prod_bd['marca'],
                'nome_fragrancia': frag_bd['nome_fragrancia']
            })

        cur.execute("""
            INSERT INTO
                    registro_pedido (
                        cod_loja,
                    cod_colaborador,
                    cod_forma_pag,
                    valor_total,
                    hora_do_registro) 
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING cod_venda
        """, (dados_do_pedido['cod_loja'], dados_do_pedido['cod_colaborador'], dados_do_pedido['cod_forma_pag'], valor_total_venda))

        cod_venda = cur.fetchone()['cod_venda']

        for ip in produtos_processados:
            cur.execute("""
                INSERT INTO detalhes_pedido (cod_produto, quantidade, preco_unitario, cod_venda, cod_fragrancia)
                VALUES (%s, %s, %s, %s, %s)
            """, (ip['cod_produto'], ip['qtd'], ip['preco'], cod_venda, ip['cod_fragrancia']))

        conn.commit()

        registrar_novo_pedido_neo4j(cod_venda, {
            "produtos": produtos_processados
        })

        return cod_venda

    except Exception as e:
        conn.rollback()
        return print(f"Erro no banco: {e}")
    
    finally:
        cur.close()
        conn.close()
