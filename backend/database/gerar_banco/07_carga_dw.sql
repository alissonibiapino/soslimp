-- Carga das dimensões e da fato do DW. Executar após 06_carga_staging.sql.

-- =========================================================
-- 3. DW: dimensões e tabela fato
-- =========================================================

INSERT INTO dw.dim_tempo
    (data, dia, dia_semana, semana_do_ano, mes, nome_mes, trimestre, ano, eh_fim_de_semana)
SELECT data, dia, dia_semana, semana_do_ano, mes, nome_mes, trimestre, ano, eh_fim_de_semana
FROM staging.stg_tempo
ON CONFLICT (data) DO NOTHING;

INSERT INTO dw.dim_produto
    (cod_produto, nome_produto, marca, descricao, categoria_produto,
     possui_fragrancia, faixa_preco, ativo)
SELECT cod_produto, nome_produto, marca, descricao, categoria_produto,
       possui_fragrancia, faixa_preco, ativo
FROM staging.stg_produto
ON CONFLICT (cod_produto) DO NOTHING;

INSERT INTO dw.dim_loja
    (cod_loja, nome_loja, endereco, bairro, cidade, cep, tipo_loja)
SELECT cod_loja, nome_loja, endereco, bairro, cidade, cep, tipo_loja
FROM staging.stg_loja
ON CONFLICT (cod_loja) DO NOTHING;

INSERT INTO dw.dim_colaborador
    (cod_colaborador, nome, cargo, data_admissao, tempo_de_casa_meses,
     situacao, loja_principal)
SELECT cod_colaborador, nome, cargo, data_admissao, tempo_de_casa_meses,
       situacao, loja_principal
FROM staging.stg_colaborador
ON CONFLICT (cod_colaborador) DO NOTHING;

INSERT INTO dw.dim_forma_pagamento
    (cod_forma_pag, tipo_pagamento, categoria_pagamento)
SELECT cod_forma_pag, tipo_pagamento, categoria_pagamento
FROM staging.stg_forma_pagamento
ON CONFLICT (cod_forma_pag) DO NOTHING;

INSERT INTO dw.fato_venda_item
    (fk_tempo, fk_produto, fk_loja, fk_colaborador, fk_forma_pagamento,
     cod_venda, cod_detalhes, quantidade, preco_unitario_praticado,
     valor_total_item, is_recomendacao, turno)
SELECT
    t.sk_tempo,
    p.sk_produto,
    l.sk_loja,
    c.sk_colaborador,
    fp.sk_forma_pagamento,
    v.cod_venda,
    v.cod_detalhes,
    v.quantidade,
    v.preco_unitario,
    v.valor_total_item,
    v.is_recomendacao,
    v.turno
FROM staging.stg_venda_item v
JOIN dw.dim_tempo t ON t.data = v.data_venda
JOIN dw.dim_produto p ON p.cod_produto = v.cod_produto
JOIN dw.dim_loja l ON l.cod_loja = v.cod_loja
JOIN dw.dim_colaborador c ON c.cod_colaborador = v.cod_colaborador
JOIN dw.dim_forma_pagamento fp ON fp.cod_forma_pag = v.cod_forma_pag
ON CONFLICT (cod_detalhes) DO NOTHING;



