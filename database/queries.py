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


# QUERIES DE VENDAS

def get_ultimas_vendas():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id_reg_venda, INITCAP(forma_pagamento.tipo_pagamento), data_reg_venda, preco_unitario FROM registro_venda INNER JOIN forma_pagamento ON( registro_venda.cod_forma_pag = forma_pagamento.cod_forma_pag) WHERE data_reg_venda >= current_date - INTERVAL '7 days';")
    resultado = cur.fetchall()
    conn.close()

    ultimas_vendas_dict = {
        id_reg_venda: {"id":id_reg_venda, "forma_pagamento":tipo_pagamento, "data":data_reg_venda, "preco_unitario":preco_unitario}
        for id_reg_venda, tipo_pagamento, data_reg_venda, preco_unitario in resultado
    }

    return ultimas_vendas_dict
    
