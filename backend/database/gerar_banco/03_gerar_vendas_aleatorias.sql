-- POPULAÇÃO (GERADO POR IA)
-- POPULAÇÃO REALISTA DE VENDAS
-- POPULAÇÃO REALISTA DE VENDAS (com controle de estoque)
DO
$$
DECLARE

    v_cur_date DATE;

    --------------------------------------------------
    -- PERÍODO
    --------------------------------------------------

    v_dt_start DATE := (CURRENT_DATE - INTERVAL '12 months')::DATE;
    v_dt_end   DATE := CURRENT_DATE;

    --------------------------------------------------
    -- PARÂMETROS DE ESTOQUE (ajuste aqui)
    --------------------------------------------------

    v_ponto_reposicao   INTEGER := 15;     -- só repõe se estoque <= este valor
    v_chance_reposicao  NUMERIC := 0.75;   -- chance do fornecedor entregar
    v_repo_min          INTEGER := 20;     -- reposição: mínimo
    v_repo_max          INTEGER := 60;     -- reposição: máximo

    v_n_zerados         INTEGER := 2 + floor(random() * 2)::INT;  -- 2 ou 3 zerados
    v_pct_critico       NUMERIC := 0.10;   -- % com 1 a 5 un.
    v_pct_baixo         NUMERIC := 0.15;   -- % com 6 a 15 un.

    --------------------------------------------------
    -- VARIÁVEIS
    --------------------------------------------------

    v_cod_loja INTEGER;
    v_cod_colab INTEGER;
    v_cod_forma INTEGER;

    v_n_pedidos INTEGER;
    v_new_cod_venda INTEGER;

    v_total NUMERIC(10,2);

    v_n_itens INTEGER;

    v_prod RECORD;

    v_fragrancia INTEGER;

    v_quantidade INTEGER;

    v_estoque_atual INTEGER;

    v_hora TIMESTAMP;

    v_hour_rand FLOAT;

    v_is_weekend BOOLEAN;

    --------------------------------------------------
    -- SAZONALIDADE
    --------------------------------------------------

    v_month_factor NUMERIC(4,2);

    v_target_recommendation_rate NUMERIC(4,2);

    v_current_month INTEGER;

    v_day_of_week INTEGER;

BEGIN

    --------------------------------------------------
    -- LOOP DE DATAS
    --------------------------------------------------

    FOR v_cur_date IN
        SELECT gs::DATE
        FROM generate_series(v_dt_start, v_dt_end, '1 day') AS gs
    LOOP

        --------------------------------------------------
        -- INFO DO DIA
        --------------------------------------------------

        v_is_weekend := EXTRACT(DOW FROM v_cur_date) IN (0,6);
        v_current_month := EXTRACT(MONTH FROM v_cur_date)::INT;
        v_day_of_week := EXTRACT(DOW FROM v_cur_date)::INT;

        --------------------------------------------------
        -- REPOSIÇÃO MENSAL (apenas produtos com estoque baixo)
        --------------------------------------------------

        IF EXTRACT(DAY FROM v_cur_date) = 1 THEN

            WITH repo AS (
                UPDATE estoque e
                SET quantidade_atual = e.quantidade_atual + r.qtd,
                    atualizado_em = v_cur_date
                FROM (
                    SELECT
                        cod_produto,
                        cod_loja,
                        v_repo_min + floor(random() * (v_repo_max - v_repo_min + 1))::INT AS qtd
                    FROM estoque
                    WHERE quantidade_atual <= v_ponto_reposicao
                      AND random() < v_chance_reposicao
                ) r
                WHERE e.cod_produto = r.cod_produto
                  AND e.cod_loja = r.cod_loja
                RETURNING e.cod_produto, e.cod_loja, r.qtd
            )
            INSERT INTO movimentacao_estoque (
                cod_produto, cod_loja, tipo_movimentacao,
                quantidade, motivo, data_movimentacao
            )
            SELECT cod_produto, cod_loja, 'ENTRADA', qtd,
                   'Reposição mensal (fornecedor)', v_cur_date
            FROM repo;

        END IF;

        --------------------------------------------------
        -- SAZONALIDADE MENSAL
        --------------------------------------------------

        CASE v_current_month
            WHEN 1  THEN v_month_factor := 0.85;
            WHEN 2  THEN v_month_factor := 0.90;
            WHEN 3  THEN v_month_factor := 1.00;
            WHEN 4  THEN v_month_factor := 1.00;
            WHEN 5  THEN v_month_factor := 0.95;
            WHEN 6  THEN v_month_factor := 1.05;
            WHEN 7  THEN v_month_factor := 1.08;
            WHEN 8  THEN v_month_factor := 1.00;
            WHEN 9  THEN v_month_factor := 0.92;
            WHEN 10 THEN v_month_factor := 1.02;
            WHEN 11 THEN v_month_factor := 1.10;
            WHEN 12 THEN v_month_factor := 1.15;
            ELSE v_month_factor := 1.00;
        END CASE;

        --------------------------------------------------
        -- IA / RECOMENDAÇÃO
        --------------------------------------------------

        v_target_recommendation_rate := 0.05;

        --------------------------------------------------
        -- LOOP DE LOJAS
        --------------------------------------------------

        FOR v_cod_loja IN 1..2 LOOP

            --------------------------------------------------
            -- QUANTIDADE BASE DE PEDIDOS
            --------------------------------------------------

            IF v_is_weekend THEN
                v_n_pedidos := ((1 + floor(random()*4)::INT) * v_month_factor)::INT;
            ELSE
                v_n_pedidos := ((3 + floor(random()*6)::INT) * v_month_factor)::INT;
            END IF;

            IF v_n_pedidos < 1 THEN
                v_n_pedidos := 1;
            END IF;

            --------------------------------------------------
            -- AJUSTE POR DIA DA SEMANA
            --------------------------------------------------

            CASE v_day_of_week
                WHEN 1 THEN v_n_pedidos := GREATEST(1, (v_n_pedidos * 0.85)::INT);
                WHEN 5 THEN v_n_pedidos := GREATEST(1, (v_n_pedidos * 1.10)::INT);
                WHEN 6 THEN v_n_pedidos := GREATEST(1, (v_n_pedidos * 1.15)::INT);
                WHEN 0 THEN v_n_pedidos := GREATEST(1, (v_n_pedidos * 1.05)::INT);
                ELSE v_n_pedidos := v_n_pedidos;
            END CASE;

            --------------------------------------------------
            -- BLACK FRIDAY
            --------------------------------------------------

            IF EXTRACT(MONTH FROM v_cur_date) = 11
               AND EXTRACT(DAY FROM v_cur_date) >= 20 THEN
                v_n_pedidos := (v_n_pedidos * 1.20)::INT;
            END IF;

            --------------------------------------------------
            -- NATAL
            --------------------------------------------------

            IF EXTRACT(MONTH FROM v_cur_date) = 12
               AND EXTRACT(DAY FROM v_cur_date) >= 15 THEN
                v_n_pedidos := (v_n_pedidos * 1.15)::INT;
            END IF;

            --------------------------------------------------
            -- GERA PEDIDOS
            --------------------------------------------------

            FOR i IN 1..v_n_pedidos LOOP

                --------------------------------------------------
                -- COLABORADOR
                --------------------------------------------------

                SELECT cod_colaborador
                INTO v_cod_colab
                FROM colaborador_trabalha
                WHERE cod_loja = v_cod_loja
                ORDER BY random()
                LIMIT 1;

                --------------------------------------------------
                -- FORMA PAGAMENTO
                --------------------------------------------------

                SELECT cod_forma_pag
                INTO v_cod_forma
                FROM forma_pagamento
                ORDER BY
                    CASE tipo_pagamento
                        WHEN 'PIX' THEN random()*5
                        WHEN 'DÉBITO' THEN random()*4
                        WHEN 'CRÉDITO' THEN random()*3
                        ELSE random()
                    END DESC
                LIMIT 1;

                --------------------------------------------------
                -- HORÁRIOS MAIS REALISTAS
                --------------------------------------------------

                v_hour_rand := random();

                IF v_hour_rand < 0.25 THEN
                    v_hora := v_cur_date + interval '8 hour'  + (random() * interval '3 hour');
                ELSIF v_hour_rand < 0.55 THEN
                    v_hora := v_cur_date + interval '11 hour' + (random() * interval '2 hour');
                ELSIF v_hour_rand < 0.85 THEN
                    v_hora := v_cur_date + interval '14 hour' + (random() * interval '3 hour');
                ELSE
                    v_hora := v_cur_date + interval '18 hour' + (random() * interval '2 hour');
                END IF;

                --------------------------------------------------
                -- INSERE PEDIDO
                --------------------------------------------------

                INSERT INTO registro_pedido (
                    cod_loja, cod_colaborador, cod_forma_pag,
                    valor_total, valor_recebido, troco, hora_do_registro
                )
                VALUES (
                    v_cod_loja, v_cod_colab, v_cod_forma,
                    0, 0, 0, v_hora
                )
                RETURNING cod_venda
                INTO v_new_cod_venda;

                v_total := 0;

                --------------------------------------------------
                -- QUANTIDADE DE ITENS
                --------------------------------------------------

                IF random() < 0.78 THEN
                    v_n_itens := 1;
                ELSIF random() < 0.95 THEN
                    v_n_itens := 2;
                ELSE
                    v_n_itens := 3;
                END IF;

                --------------------------------------------------
                -- INSERE ITENS
                --------------------------------------------------

                FOR j IN 1..v_n_itens LOOP

                    --------------------------------------------------
                    -- PRODUTOS MAIS REALISTAS
                    --------------------------------------------------

                    IF random() < 0.50 THEN

                        -- ALTO GIRO / SOSLIMP
                        SELECT cod_produto, preco_unitario
                        INTO v_prod
                        FROM produto
                        WHERE cod_produto IN (2,3,11,12,13,17,18,29,33,35,36,37,40,43)
                        ORDER BY random()
                        LIMIT 1;

                    ELSIF random() < 0.78 THEN

                        -- GIRO MÉDIO
                        SELECT cod_produto, preco_unitario
                        INTO v_prod
                        FROM produto
                        WHERE (
                            marca = 'SOSLimp'
                            OR cod_categoria IN (1,2,4,5,13,14,15)
                        )
                        AND preco_unitario <= 25
                        ORDER BY random()
                        LIMIT 1;

                    ELSIF random() < 0.93 THEN

                        -- PRODUTOS NORMAIS
                        SELECT cod_produto, preco_unitario
                        INTO v_prod
                        FROM produto
                        WHERE preco_unitario <= 35
                        ORDER BY random()
                        LIMIT 1;

                    ELSE

                        -- BAIXO GIRO
                        SELECT cod_produto, preco_unitario
                        INTO v_prod
                        FROM produto
                        WHERE preco_unitario > 35
                        ORDER BY random()
                        LIMIT 1;

                    END IF;

                    --------------------------------------------------
                    -- QUANTIDADE
                    --------------------------------------------------

                    IF random() < 0.93 THEN
                        v_quantidade := 1;
                    ELSE
                        v_quantidade := 2;
                    END IF;

                    --------------------------------------------------
                    -- VERIFICA ESTOQUE (sem estoque = não vende)
                    --------------------------------------------------

                    SELECT quantidade_atual
                    INTO v_estoque_atual
                    FROM estoque
                    WHERE cod_produto = v_prod.cod_produto
                      AND cod_loja = v_cod_loja;

                    IF COALESCE(v_estoque_atual, 0) < v_quantidade THEN
                        CONTINUE;
                    END IF;

                    --------------------------------------------------
                    -- FRAGRÂNCIA
                    --------------------------------------------------

                    SELECT COALESCE(
                    (
                        SELECT cod_fragrancia
                        FROM produto_fragrancia
                        WHERE cod_produto = v_prod.cod_produto
                        ORDER BY random()
                        LIMIT 1
                    ),
                    18
                    )
                    INTO v_fragrancia;

                    --------------------------------------------------
                    -- INSERE ITEM
                    --------------------------------------------------

                    INSERT INTO detalhes_pedido (
                        cod_produto, cod_fragrancia, quantidade,
                        preco_unitario, cod_venda, is_recomendacao
                    )
                    VALUES (
                        v_prod.cod_produto, v_fragrancia, v_quantidade,
                        v_prod.preco_unitario, v_new_cod_venda,
                        (random() < v_target_recommendation_rate)
                    );

                    UPDATE estoque
                    SET quantidade_atual = quantidade_atual - v_quantidade,
                        atualizado_em = v_hora
                    WHERE cod_produto = v_prod.cod_produto
                      AND cod_loja = v_cod_loja;

                    INSERT INTO movimentacao_estoque (
                        cod_produto, cod_loja, tipo_movimentacao,
                        quantidade, cod_venda, data_movimentacao
                    )
                    VALUES (
                        v_prod.cod_produto, v_cod_loja, 'SAIDA',
                        v_quantidade, v_new_cod_venda, v_hora
                    );

                    --------------------------------------------------
                    -- SOMA TOTAL
                    --------------------------------------------------

                    v_total := v_total + (v_prod.preco_unitario * v_quantidade);

                END LOOP;

                --------------------------------------------------
                -- PEDIDO SEM NENHUM ITEM (tudo sem estoque): descarta
                --------------------------------------------------

                IF v_total = 0 THEN
                    DELETE FROM registro_pedido WHERE cod_venda = v_new_cod_venda;
                    CONTINUE;
                END IF;

                --------------------------------------------------
                -- ATUALIZA PAGAMENTO
                --------------------------------------------------

                UPDATE registro_pedido
                SET
                    valor_total = v_total,
                    valor_recebido =
                        CASE
                            WHEN v_cod_forma = 4 THEN ceil(v_total / 10) * 10
                            ELSE v_total
                        END,
                    troco =
                        CASE
                            WHEN v_cod_forma = 4 THEN (ceil(v_total / 10) * 10) - v_total
                            ELSE 0
                        END
                WHERE cod_venda = v_new_cod_venda;

            END LOOP;

        END LOOP;

    END LOOP;

    --------------------------------------------------
    -- AJUSTE FINAL: CENÁRIO DE TESTE PARA O FRONTEND
    -- (só reduz estoque; registra a diferença como SAIDA)
    --------------------------------------------------

    WITH ranked AS (
        SELECT
            cod_produto,
            cod_loja,
            quantidade_atual,
            row_number() OVER (ORDER BY random()) AS rn,
            count(*) OVER () AS total
        FROM estoque
    ),
    alvo AS (
        SELECT
            cod_produto,
            cod_loja,
            quantidade_atual,
            CASE
                -- zerados
                WHEN rn <= v_n_zerados
                    THEN 0
                -- críticos (1 a 5)
                WHEN rn <= v_n_zerados + ceil(total * v_pct_critico)
                    THEN 1 + floor(random() * 5)::INT
                -- baixos (6 a 15)
                WHEN rn <= v_n_zerados + ceil(total * v_pct_critico) + ceil(total * v_pct_baixo)
                    THEN 6 + floor(random() * 10)::INT
                -- saudáveis (16 a 60)
                ELSE 16 + floor(random() * 45)::INT
            END AS novo
        FROM ranked
    ),
    ajuste AS (
        UPDATE estoque e
        SET quantidade_atual = a.novo,
            atualizado_em = v_dt_end
        FROM alvo a
        WHERE e.cod_produto = a.cod_produto
          AND e.cod_loja = a.cod_loja
          AND a.novo < e.quantidade_atual
        RETURNING e.cod_produto, e.cod_loja, (a.quantidade_atual - a.novo) AS qtd
    )
    INSERT INTO movimentacao_estoque (
        cod_produto, cod_loja, tipo_movimentacao,
        quantidade, motivo, data_movimentacao
    )
    SELECT cod_produto, cod_loja, 'SAIDA', qtd,
           'Ajuste de inventário', v_dt_end
    FROM ajuste;

END
$$;