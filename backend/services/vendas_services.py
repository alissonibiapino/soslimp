from database.conn_postgres import get_conn
from psycopg2.extras import RealDictCursor
from fastapi import HTTPException
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

    try:
        valor_total_venda = 0
        produtos_processados = []
        valor_recebido = float(dados_do_pedido.get('valor_recebido', 0))

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

            is_recomendacao = produto.get('is_recomendacao', False)

            cod_frag = produto.get('cod_fragrancia')

            if cod_frag is None:
                cod_frag = 18
                
            # cod_frag = produto.get('cod_fragrancia', 18)
            cur.execute("""
                SELECT nome_fragrancia
                FROM fragrancia
                WHERE cod_fragrancia = %s
            """, (cod_frag, ))
            frag_bd = cur.fetchone()
            
            preco_atual = float(prod_bd['preco_unitario'])
            subtotal = preco_atual * produto['quantidade']
            valor_total_venda += subtotal

            produtos_processados.append({
                'cod_produto': produto['cod_produto'],
                'cod_fragrancia': cod_frag,
                'qtd': produto['quantidade'],
                'preco': preco_atual,
                'nome_produto': prod_bd['nome_produto'],
                'marca': prod_bd['marca'],
                'nome_fragrancia': frag_bd['nome_fragrancia'] if frag_bd and frag_bd['nome_fragrancia'] else 'Sem fragrância',
                'is_recomendacao': is_recomendacao
            })

        troco = 0
        if int(dados_do_pedido['cod_forma_pag']) == 4:
            troco = max(0, valor_recebido - valor_total_venda)

        cur.execute("""
            INSERT INTO
                    registro_pedido (
                        cod_loja,
                    cod_colaborador,
                    cod_forma_pag,
                    valor_total,
                    valor_recebido,
                    troco,
                    hora_do_registro) 
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING cod_venda
        """, (
            dados_do_pedido['cod_loja'], 
            dados_do_pedido['cod_colaborador'], 
            dados_do_pedido['cod_forma_pag'], 
            valor_total_venda,
            valor_recebido,
            troco
        ))

        cod_venda = cur.fetchone()['cod_venda']

        if int(dados_do_pedido['cod_forma_pag']) == 4 and dados_do_pedido.get('cod_caixa'):
            cur.execute("""
                UPDATE caixa SET valor_atual = valor_atual + %s WHERE cod_caixa = %s
            """, (valor_total_venda, dados_do_pedido['cod_caixa']))
            
            cur.execute("""
                INSERT INTO movimentacao_caixa (cod_caixa, valor, cod_venda)
                VALUES (%s, %s, %s)
            """, (dados_do_pedido['cod_caixa'], valor_total_venda, cod_venda))

        for ip in produtos_processados:
                        # parte de estoque

            cur.execute("""
                SELECT quantidade_atual FROM estoque
                WHERE cod_produto = %s AND cod_loja = %s
            """, (ip['cod_produto'], dados_do_pedido['cod_loja']))
            estoque_atual = cur.fetchone()

            if not estoque_atual:
                raise HTTPException(status_code=400, detail="Estoque insuficiente para o produto")

            cur.execute("""
                UPDATE estoque SET quantidade_atual = quantidade_atual - %s, atualizado_em = CURRENT_TIMESTAMP
                WHERE cod_produto = %s AND cod_loja = %s
            """, (ip['qtd'], ip['cod_produto'], dados_do_pedido['cod_loja']))

            # movimentacao do estoque
            cur.execute("""
                INSERT INTO movimentacao_estoque (cod_produto, cod_loja, tipo_movimentacao, quantidade, cod_venda)
                VALUES (%s, %s, 'SAIDA', %s, %s)
            """, (ip['cod_produto'], dados_do_pedido['cod_loja'], ip['qtd'], cod_venda))

            cur.execute("""
                INSERT INTO detalhes_pedido (cod_produto, quantidade, preco_unitario, cod_venda, cod_fragrancia, is_recomendacao)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (ip['cod_produto'], ip['qtd'], ip['preco'], cod_venda, ip['cod_fragrancia'], ip['is_recomendacao']))

        conn.commit()

        registrar_novo_pedido_neo4j(cod_venda, {
            "produtos": produtos_processados
        })

        return cod_venda

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        cur.close()
        conn.close()
