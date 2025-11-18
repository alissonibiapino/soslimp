from database.conn import get_conn
from sessao import SessaoDeLogin

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

    # print(categorias_dict)
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
    # print(produtos_dict)
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
    # print(produtos_dict)
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

def insert_registra_pedido(cod_loja, cod_colaborador, cod_forma_pag, valor_total, cod_produto, quantidade, preco_unitario):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO registro_pedido (cod_loja, cod_colaborador, cod_forma_pag, valor_total, hora_do_registro) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP) RETURNING cod_venda", (cod_loja, cod_colaborador, cod_forma_pag, valor_total))
        cod_pedido = cur.fetchone()[0]
        cur.execute("INSERT INTO detalhes_pedido (cod_produto, quantidade, preco_unitario, cod_venda) VALUES (%s, %s, %s, %s)", (cod_produto, quantidade, preco_unitario, cod_pedido))
        conn.commit()
    except Exception as err:
        print("Erro: ", err)
        conn.rollback()
    else:
        print("Tudo certo!")
    finally:
        print("Fechando conexão")
        conn.close()
   

# def insert_registra_pedido_detalhe (cod_produto, quantidade, preco_unitario, cod_venda):


    
# QUERIES DE TROCO

def get_caixa_atual():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT ROUND(valor_atual, 2) FROM caixa;")
    resultado = cur.fetchall()
    conn.close()

    # print(resultado)
    return resultado


# QUERIES DE LOJA

def get_lojas():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT cod_loja, nome_loja, tipo_loja FROM loja;")
        resultado = cur.fetchall()
        
        lojas_dict = {
            nome_loja: { "cod_loja":cod_loja, "tipo_loja":tipo_loja }
            for cod_loja, nome_loja, tipo_loja in resultado
        }

        return lojas_dict

    except Exception as err:
        print("Erro:", err)
    finally:
        conn.close()


def login(usuario, senha, loja):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT	c.cod_colaborador, c.nome, c.cargo FROM colaborador_login INNER JOIN colaborador c USING (cod_colaborador) WHERE usuario = %s AND senha_hash = %s;", (usuario, senha))
        resultado = cur.fetchall()
        if resultado == []:
            return False
        else:
            SessaoDeLogin.cod_colaborador = resultado[0][0]
            SessaoDeLogin.nome = resultado[0][1]
            SessaoDeLogin.cargo = resultado[0][2]
            SessaoDeLogin.loja_cod = loja
            print(type(loja))
            cur.execute("SELECT nome_loja, endereco, telefone, email FROM loja WHERE cod_loja = %s;", (loja,))
            resultado2 = cur.fetchone()
            SessaoDeLogin.loja_nome = resultado2[0]
            SessaoDeLogin.loja_end = resultado2[1]
            SessaoDeLogin.loja_num = resultado2[2]
            SessaoDeLogin.loja_email = resultado2[3]
            return True
    except Exception as err:
        print("Erro:", err)
    finally:
        conn.close()