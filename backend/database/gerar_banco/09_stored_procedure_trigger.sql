-- 1 stored procedure de taxa de recomendação por loja
-- proporção de itens vendidos por recomendação (is_recomendacao = TRUE) em um período.
CREATE TABLE IF NOT EXISTS dw.estatistica_recomendacao (
    cod_estatistica    SERIAL PRIMARY KEY,
    calculado_em       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_inicio        DATE NOT NULL,
    data_fim           DATE NOT NULL,
    cod_loja           INTEGER NOT NULL,
    total_itens        INTEGER NOT NULL,
    itens_recomendados INTEGER NOT NULL,
    taxa_recomendacao  NUMERIC(6,2) NOT NULL
);

CREATE OR REPLACE PROCEDURE dw.sp_calcular_taxa_recomendacao(
    p_data_inicio DATE,
    p_data_fim    DATE,
    p_cod_loja    INTEGER DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    cur          refcursor;
    v_sql        TEXT;
    v_reg        RECORD;
    v_loja_atual INTEGER := NULL;
    v_total      INTEGER := 0;
    v_recom      INTEGER := 0;
BEGIN
    IF p_data_inicio IS NULL OR p_data_fim IS NULL OR p_data_inicio > p_data_fim THEN
        RAISE EXCEPTION 'Período inválido: % a %', p_data_inicio, p_data_fim;
    END IF;

    v_sql := 'SELECT l.cod_loja, f.is_recomendacao
              FROM dw.fato_venda_item f
              JOIN dw.dim_tempo t ON t.sk_tempo = f.fk_tempo
              JOIN dw.dim_loja  l ON l.sk_loja  = f.fk_loja
              WHERE t.data BETWEEN $1 AND $2';

    IF p_cod_loja IS NOT NULL THEN
        v_sql := v_sql || format(' AND l.cod_loja = %L', p_cod_loja);
    END IF;

    v_sql := v_sql || ' ORDER BY l.cod_loja';

    OPEN cur FOR EXECUTE v_sql USING p_data_inicio, p_data_fim;

    LOOP
        FETCH cur INTO v_reg;
        EXIT WHEN NOT FOUND;

        IF v_loja_atual IS DISTINCT FROM v_reg.cod_loja THEN
            IF v_loja_atual IS NOT NULL THEN
                INSERT INTO dw.estatistica_recomendacao
                    (data_inicio, data_fim, cod_loja, total_itens,
                     itens_recomendados, taxa_recomendacao)
                VALUES (p_data_inicio, p_data_fim, v_loja_atual, v_total,
                        v_recom, ROUND(100.0 * v_recom / v_total, 2));
            END IF;
            v_loja_atual := v_reg.cod_loja;
            v_total := 0;
            v_recom := 0;
        END IF;

        v_total := v_total + 1;
        IF v_reg.is_recomendacao IS TRUE THEN
            v_recom := v_recom + 1;
        END IF;
    END LOOP;

    CLOSE cur;

    IF v_loja_atual IS NOT NULL THEN
        INSERT INTO dw.estatistica_recomendacao
            (data_inicio, data_fim, cod_loja, total_itens,
             itens_recomendados, taxa_recomendacao)
        VALUES (p_data_inicio, p_data_fim, v_loja_atual, v_total,
                v_recom, ROUND(100.0 * v_recom / v_total, 2));
    END IF;

    RAISE NOTICE 'Taxa de recomendação calculada para o período % a %', p_data_inicio, p_data_fim;
END;
$$;


CALL dw.sp_calcular_taxa_recomendacao('2026-10-01', '2026-10-31');
CALL dw.sp_calcular_taxa_recomendacao('2026-10-01', '2026-10-31', 1);
SELECT * FROM dw.estatistica_recomendacao ORDER BY cod_estatistica DESC;


-- 2 trigger de auditoria de alteração de preço em produtos
-- ele roda depois do AFTER UPDATE quando o preço é alterado, daí ele grava o preço anterior e o novo em pct


CREATE TABLE IF NOT EXISTS log_alteracao_preco (
    cod_log             SERIAL PRIMARY KEY,
    cod_produto         INTEGER NOT NULL REFERENCES produto (cod_produto),
    preco_anterior      DECIMAL(10,2) NOT NULL,
    preco_novo          DECIMAL(10,2) NOT NULL,
    variacao_percentual NUMERIC(8,2),
    alterado_em         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    usuario_banco       TEXT NOT NULL DEFAULT current_user
);

CREATE OR REPLACE FUNCTION fn_log_alteracao_preco()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO log_alteracao_preco
        (cod_produto, preco_anterior, preco_novo, variacao_percentual)
    VALUES (
        NEW.cod_produto,
        OLD.preco_unitario,
        NEW.preco_unitario,
        ROUND(100.0 * (NEW.preco_unitario - OLD.preco_unitario)
              / NULLIF(OLD.preco_unitario, 0), 2)
    );
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_log_alteracao_preco ON produto;

CREATE TRIGGER trg_log_alteracao_preco
AFTER UPDATE OF preco_unitario ON produto
FOR EACH ROW
WHEN (OLD.preco_unitario IS DISTINCT FROM NEW.preco_unitario)
EXECUTE FUNCTION fn_log_alteracao_preco();


UPDATE produto SET preco_unitario = preco_unitario + 1 WHERE cod_produto = 1;
SELECT * FROM log_alteracao_preco;
