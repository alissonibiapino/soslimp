from database.conn_postgres import get_conn
from psycopg2.extras import RealDictCursor
from typing import Optional

from models.autenticacao import Colaborador, LoginRequest
from models.loja import Loja


def listar_lojas() -> list[Loja]:
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM loja")
        return [Loja(**loja) for loja in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def verificar_credenciais(dados: LoginRequest) -> Optional[Colaborador]:
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        query = """
            SELECT 
                c.cod_colaborador, 
                c.cpf_cnpj,
                c.nome,
                c.cargo,
                c.data_admissao,
                c.data_demissao
            FROM colaborador_login cl
            INNER JOIN colaborador c ON cl.cod_colaborador = c.cod_colaborador
            WHERE cl.usuario = %s AND cl.senha_hash = %s
        """
        cur.execute(query, (dados.usuario, dados.senha))
        resultado = cur.fetchone()
        return Colaborador(**resultado) if resultado else None

    except Exception as e:
        print(f"Erro na autenticação: {e}")
        return None
    
    finally:
        cur.close()
        conn.close()
