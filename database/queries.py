from database.conn import get_conn

# QUERIES DE COLABORADOR

def get_colaboradores():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT cod_colaborador, nome FROM colaborador")
    colaboradores = cur.fetchall()
    # colaboradores = [row[0] for row in cur.fetchall()]
    conn.close()
    print(colaboradores)
    return colaboradores

# QUERIES DE COLABORADOR

def get_produtos():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id_produto, nome_produto, marca, preco_unitario FROM produto")
    produtos = cur.fetchall()

    # produtos_dict = {nome: id for }

    conn.close()
    print(produtos)
    return produtos
