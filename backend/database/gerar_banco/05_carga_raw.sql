-- Carga da camada RAW. Executar após 01-04.

-- =========================================================
-- 1. RAW: cópia fiel da origem, convertendo os valores para TEXT
-- =========================================================

INSERT INTO raw.loja
    (cod_loja, nome_loja, endereco, bairro, cidade, cep, telefone, email, tipo_loja)
SELECT cod_loja::text, nome_loja, endereco, bairro, cidade, cep, telefone, email, tipo_loja
FROM loja;

INSERT INTO raw.colaborador
    (cod_colaborador, nome, cargo, data_admissao, data_demissao)
SELECT cod_colaborador::text, nome, cargo, data_admissao::text, data_demissao::text
FROM colaborador;

INSERT INTO raw.colaborador_trabalha (cod_loja, cod_colaborador)
SELECT cod_loja::text, cod_colaborador::text
FROM colaborador_trabalha;

INSERT INTO raw.forma_pagamento (cod_forma_pag, tipo_pagamento)
SELECT cod_forma_pag::text, tipo_pagamento
FROM forma_pagamento;

INSERT INTO raw.categoria (cod_categoria, categoria_produto)
SELECT cod_categoria::text, categoria_produto
FROM categoria;

INSERT INTO raw.produto
    (cod_produto, cod_categoria, nome_produto, descricao, marca,
     preco_unitario, url_imagem, ativo)
SELECT cod_produto::text, cod_categoria::text, nome_produto, descricao, marca,
       preco_unitario::text, url_imagem, ativo::text
FROM produto;

INSERT INTO raw.produto_fragrancia (cod_produto, cod_fragrancia)
SELECT cod_produto::text, cod_fragrancia::text
FROM produto_fragrancia;

INSERT INTO raw.registro_pedido
    (cod_venda, cod_loja, cod_colaborador, cod_forma_pag,
     valor_total, valor_recebido, troco, hora_do_registro)
SELECT cod_venda::text, cod_loja::text, cod_colaborador::text, cod_forma_pag::text,
       valor_total::text, valor_recebido::text, troco::text, hora_do_registro::text
FROM registro_pedido;

INSERT INTO raw.detalhes_pedido
    (cod_detalhes, cod_venda, cod_produto, cod_fragrancia,
     quantidade, preco_unitario, is_recomendacao)
SELECT cod_detalhes::text, cod_venda::text, cod_produto::text,
       cod_fragrancia::text, quantidade::text, preco_unitario::text,
       is_recomendacao::text
FROM detalhes_pedido;

