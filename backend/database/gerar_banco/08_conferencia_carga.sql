-- =========================================================
-- 4. Conferência da carga
-- =========================================================
SELECT 'raw.loja' AS tabela, COUNT(*) AS registros FROM raw.loja
UNION ALL SELECT 'raw.colaborador', COUNT(*) FROM raw.colaborador
UNION ALL SELECT 'raw.produto', COUNT(*) FROM raw.produto
UNION ALL SELECT 'raw.registro_pedido', COUNT(*) FROM raw.registro_pedido
UNION ALL SELECT 'raw.detalhes_pedido', COUNT(*) FROM raw.detalhes_pedido
UNION ALL SELECT 'staging.stg_loja', COUNT(*) FROM staging.stg_loja
UNION ALL SELECT 'staging.stg_colaborador', COUNT(*) FROM staging.stg_colaborador
UNION ALL SELECT 'staging.stg_produto', COUNT(*) FROM staging.stg_produto
UNION ALL SELECT 'staging.stg_tempo', COUNT(*) FROM staging.stg_tempo
UNION ALL SELECT 'staging.stg_venda_item', COUNT(*) FROM staging.stg_venda_item
UNION ALL SELECT 'dw.dim_tempo', COUNT(*) FROM dw.dim_tempo
UNION ALL SELECT 'dw.dim_produto', COUNT(*) FROM dw.dim_produto
UNION ALL SELECT 'dw.dim_loja', COUNT(*) FROM dw.dim_loja
UNION ALL SELECT 'dw.dim_colaborador', COUNT(*) FROM dw.dim_colaborador
UNION ALL SELECT 'dw.dim_forma_pagamento', COUNT(*) FROM dw.dim_forma_pagamento
UNION ALL SELECT 'dw.fato_venda_item', COUNT(*) FROM dw.fato_venda_item
ORDER BY tabela;

-- LIMITAÇÕES IDENTIFICADAS NO DDL ENVIADO:
-- 1) raw não possui tabelas para fragrancia, estoque, caixa e movimentacao_estoque.
-- 2) staging/DW não possuem dimensões para fragrância/estoque.
-- 3) raw.colaborador não tem cpf_cnpj; o DDL da origem possui esse campo, mas ele não é necessário para o DW.
-- 4) Se o mesmo colaborador estiver associado a mais de uma loja, stg_colaborador pode ter mais de uma linha candidata
--    para o mesmo cod_colaborador. O modelo atual exige uma única loja principal; defina um critério de negócio.
-- 5) O código original não insere vendas/detalhes; sem elas, stg_venda_item e dw.fato_venda_item ficam vazias.
