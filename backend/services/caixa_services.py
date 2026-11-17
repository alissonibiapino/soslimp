from database.conn_postgres import get_conn
from psycopg2.extras import RealDictCursor
from fastapi import HTTPException
from typing import Optional

from models.caixa import AberturaCaixa, Caixa, FechamentoCaixa


def abrir_novo_caixa(dados: AberturaCaixa):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        verificar_caixa = """
            SELECT cod_caixa
            FROM caixa
            WHERE cod_loja = %s
            AND status_caixa = 'ABERTO'
            AND data_abertura::date = CURRENT_DATE
        """
        cur.execute(verificar_caixa, (dados.cod_loja,))
        caixa_existente = cur.fetchone()

        if caixa_existente:
            raise Exception(f"Erro no banco: esse caixa já foi aberto para essa loja!")
        
        cur.execute("""
            INSERT INTO caixa (
                    data_abertura,
                    valor_inicial,
                    valor_atual,
                    status_caixa,
                    cod_loja)
            VALUES (CURRENT_TIMESTAMP, %s, %s, 'ABERTO', %s)
            RETURNING cod_caixa
        """, (dados.valor_inicial, dados.valor_inicial, dados.cod_loja))

        cod_caixa = cur.fetchone()
        conn.commit()
        return cod_caixa['cod_caixa']

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    finally:
        cur.close()
        conn.close()

def fechar_caixa_dia(dados: FechamentoCaixa):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("SELECT valor_atual, status_caixa FROM caixa WHERE cod_caixa = %s", (dados.cod_caixa,))
        caixa = cur.fetchone()

        if not caixa:
            raise Exception("Erro: caixa não encontrado")
        
        if caixa['status_caixa'] == 'FECHADO':
            raise Exception("Este caixa já foi encerrado")

        diferenca = float(dados.valor_fechamento) - float(caixa['valor_atual'])

        cur.execute("""
            UPDATE caixa 
            SET status_caixa = 'FECHADO', 
                valor_final = %s,
                diferenca = %s
            WHERE cod_caixa = %s
        """, (dados.valor_fechamento, diferenca, dados.cod_caixa,))

        conn.commit()
        return {"status": "caixa fechado", "diferenca" : diferenca}

    except Exception as e:
        conn.rollback()
        return print(f"Erro no banco: {e}")
    
    finally:
        cur.close()
        conn.close()

def caixa_atual(cod_loja: int) -> Optional[Caixa]:
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
                    SELECT *
                    FROM caixa
                    WHERE cod_loja = %s
                    AND status_caixa = 'ABERTO'
                    ORDER BY data_abertura DESC LIMIT 1;""", (cod_loja,))
        caixa = cur.fetchone()
        return Caixa(**caixa) if caixa else None

    except Exception as e:
        conn.rollback()
        return print(f"Erro no banco: {e}")
    
    finally:
        cur.close()
        conn.close()

def listar_historico_caixa(cod_loja: int) -> list[Caixa]:
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT *
            FROM caixa
            WHERE cod_loja = %s
            ORDER BY data_abertura DESC;
        """, (cod_loja,))
        return [Caixa(**caixa) for caixa in cur.fetchall()]
    finally:
        cur.close()
        conn.close()
