from database.conn_postgres import get_conn
from psycopg2.extras import RealDictCursor
from fastapi import HTTPException

def abrir_novo_caixa(cod_loja, valor_inicial):
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
        cur.execute(verificar_caixa, (cod_loja,))
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
        """, (valor_inicial, valor_inicial, cod_loja))

        cod_caixa = cur.fetchone()
        conn.commit()
        return {"Caixa aberto: " : cod_caixa}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    finally:
        cur.close()
        conn.close()

def fechar_caixa_dia(cod_caixa, valor_fechamento):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("SELECT valor_atual, status_caixa FROM caixa WHERE cod_caixa = %s", (cod_caixa,))
        caixa = cur.fetchone()

        if not caixa:
            raise Exception("Erro: caixa não encontrado")
        
        if caixa['status_caixa'] == 'FECHADO':
            raise Exception("Este caixa já foi encerrado")

        diferenca = float(valor_fechamento) - float(caixa['valor_atual'])

        cur.execute("""
            UPDATE caixa 
            SET status_caixa = 'FECHADO', 
                valor_final = %s,
                diferenca = %s
            WHERE cod_caixa = %s
        """, (valor_fechamento, diferenca, cod_caixa,))

        conn.commit()
        return {"status": "caixa fechado", "diferenca" : diferenca}

    except Exception as e:
        conn.rollback()
        return print(f"Erro no banco: {e}")
    
    finally:
        cur.close()
        conn.close()

def caixa_atual(cod_loja):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
                    SELECT
                        ROUND(valor_atual, 2)
                    FROM caixa
                    WHERE cod_loja = %s
                    ;""", (cod_loja,))
        caixa = cur.fetchone()
        return caixa

    except Exception as e:
        conn.rollback()
        return print(f"Erro no banco: {e}")
    
    finally:
        cur.close()
        conn.close()