from database.conn_postgres import get_conn
from psycopg2.extras import RealDictCursor

def listar_lojas():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT cod_loja, nome_loja FROM loja")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def verificar_credenciais(usuario, senha):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        query = """
            SELECT 
                c.cod_colaborador, 
                c.nome,
                c.cargo
            FROM colaborador_login cl
            INNER JOIN colaborador c ON cl.cod_colaborador = c.cod_colaborador
            WHERE cl.usuario = %s AND cl.senha_hash = %s
        """
        cur.execute(query, (usuario, senha))
        return cur.fetchone()

    except Exception as e:
        print(f"Erro na autenticação: {e}")
        return None
    
    finally:
        cur.close()
        conn.close()
