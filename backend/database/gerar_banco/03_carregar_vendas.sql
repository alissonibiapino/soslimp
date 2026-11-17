-- CARGA DAS VENDAS SINTÉTICAS (substitui 03_gerar_vendas_aleatorias.sql)
--
-- Os dados vêm dos CSVs gerados por backend/database/gerador/gerar_vendas.py
-- (semente fixa: todo mundo carrega exatamente a mesma base).
-- Os CSVs ficam em gerar_banco/dados/, a única pasta montada pelo docker-compose
-- no container (/docker-entrypoint-initdb.d). Executar após 01 e 02.

BEGIN;

COPY registro_pedido
    (cod_venda, cod_loja, cod_colaborador, cod_forma_pag,
     valor_total, valor_recebido, troco, hora_do_registro)
FROM '/docker-entrypoint-initdb.d/dados/registro_pedido.csv'
WITH (FORMAT csv, HEADER true);

COPY detalhes_pedido
    (cod_detalhes, cod_produto, quantidade, preco_unitario,
     cod_venda, cod_fragrancia, is_recomendacao)
FROM '/docker-entrypoint-initdb.d/dados/detalhes_pedido.csv'
WITH (FORMAT csv, HEADER true);

COPY movimentacao_estoque
    (cod_movimentacao, cod_produto, cod_loja, tipo_movimentacao,
     quantidade, cod_venda, motivo, data_movimentacao)
FROM '/docker-entrypoint-initdb.d/dados/movimentacao_estoque.csv'
WITH (FORMAT csv, HEADER true);

-- Estado final do estoque (saldo, mínimo e data da última movimentação).
-- O 02 já criou as linhas de estoque com valores aleatórios; aqui elas são sobrescritas.
CREATE TEMP TABLE estoque_final (
    cod_produto      INTEGER,
    cod_loja         INTEGER,
    quantidade_atual INTEGER,
    estoque_minimo   INTEGER,
    atualizado_em    TIMESTAMP
) ON COMMIT DROP;

COPY estoque_final
FROM '/docker-entrypoint-initdb.d/dados/estoque_final.csv'
WITH (FORMAT csv, HEADER true);

UPDATE estoque e
SET quantidade_atual = f.quantidade_atual,
    estoque_minimo   = f.estoque_minimo,
    atualizado_em    = f.atualizado_em
FROM estoque_final f
WHERE e.cod_produto = f.cod_produto
  AND e.cod_loja = f.cod_loja;

-- Como os códigos vieram dos CSVs, as sequences precisam continuar depois do último código.
SELECT setval(pg_get_serial_sequence('registro_pedido', 'cod_venda'),
              (SELECT MAX(cod_venda) FROM registro_pedido));
SELECT setval(pg_get_serial_sequence('detalhes_pedido', 'cod_detalhes'),
              (SELECT MAX(cod_detalhes) FROM detalhes_pedido));
SELECT setval(pg_get_serial_sequence('movimentacao_estoque', 'cod_movimentacao'),
              (SELECT MAX(cod_movimentacao) FROM movimentacao_estoque));

COMMIT;
