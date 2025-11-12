from database.conn import get_conn

# QUERIES DE COLABORADOR

def get_colaboradores():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT cod_colaborador, nome FROM colaborador")
    colaboradores = cur.fetchall()
    # colaboradores = [row[0] for row in cur.fetchall()]
    conn.close()
    # print(colaboradores)
    return colaboradores


# QUERIES DE PRODUTOS

def get_categorias():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT cod_categoria, categoria_produto FROM categoria")
    resultado = cur.fetchall()

    categorias_dict = {
        linha[1]: linha[0] for linha in resultado
    }

    print(categorias_dict)
    conn.close()
    return categorias_dict

def get_produtos():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id_produto, nome_produto, marca, preco_unitario FROM produto")
    resultado = cur.fetchall()
    conn.close()

    produtos_dict = {
        nome_produto: {"id":id, "marca":marca, "preco":preco}
        for id, nome_produto, marca, preco in resultado
    }
    print(produtos_dict)
    return produtos_dict

def get_produtos_por_categoria(categoria):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""SELECT cod_produto, nome_produto, descricao, marca, preco_unitario FROM produto WHERE cod_categoria = %s;""", (categoria,))
    resultado = cur.fetchall()
    conn.close()

    produtos_dict = {
        nome_produto: {"cod_produto":cod_produto, "descricao":descricao, "marca":marca, "preco":preco}
        for cod_produto, descricao, nome_produto, marca, preco in resultado
    }
    print(produtos_dict)
    return produtos_dict



# QUERIES DE VENDAS

def get_ultimas_vendas():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT cod_venda, INITCAP(forma_pagamento.tipo_pagamento), hora_do_registro, valor_total FROM registro_pedido rp INNER JOIN forma_pagamento USING (cod_forma_pag) WHERE hora_do_registro >= current_date - INTERVAL '7 days';")
    resultado = cur.fetchall()
    conn.close()

    ultimas_vendas_dict = {
        id_reg_venda: {"id":id_reg_venda, "forma_pagamento":tipo_pagamento, "data":data_reg_venda, "preco_unitario":preco_unitario}
        for id_reg_venda, tipo_pagamento, data_reg_venda, preco_unitario in resultado
    }

    return ultimas_vendas_dict
    
# QUERIES DE TROCO

def get_caixa_atual():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT ROUND(valor_atual, 2) FROM caixa;")
    resultado = cur.fetchall()
    conn.close()

    print(resultado)
    return resultado
