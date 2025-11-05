from database.conn import get_conn

def get_morador():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT cod_pessoa, nome_pessoa FROM morador")
    moradores = cur.fetchall()
    # moradores = [row[0] for row in cur.fetchall()]
    conn.close()
    print(moradores)
    return moradores