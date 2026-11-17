-- Carga e transformação da camada STAGING. Executar após 05_carga_raw.sql.

-- =========================================================
-- 2. STAGING: tipagem, enriquecimento e regras de negócio
-- =========================================================

INSERT INTO staging.stg_loja
    (cod_loja, nome_loja, endereco, bairro, cidade, cep, tipo_loja)
SELECT DISTINCT ON (NULLIF(trim(cod_loja), '')::integer)
       NULLIF(trim(cod_loja), '')::integer,
       NULLIF(trim(nome_loja), ''),
       NULLIF(trim(endereco), ''),
       NULLIF(trim(bairro), ''),
       NULLIF(trim(cidade), ''),
       NULLIF(trim(cep), ''),
       upper(NULLIF(trim(tipo_loja), ''))
FROM raw.loja
WHERE NULLIF(trim(cod_loja), '') ~ '^[0-9]+$'
ORDER BY NULLIF(trim(cod_loja), '')::integer, dt_carga DESC;

INSERT INTO staging.stg_colaborador
    (cod_colaborador, nome, cargo, data_admissao, data_demissao,
     tempo_de_casa_meses, situacao, cod_loja_principal, loja_principal)
SELECT
    c.cod_colaborador::integer,
    c.nome,
    c.cargo,
    NULLIF(c.data_admissao, '')::date,
    NULLIF(c.data_demissao, '')::date,
    CASE
      WHEN NULLIF(c.data_admissao, '') IS NULL THEN NULL
      ELSE GREATEST(0, (
        (EXTRACT(YEAR FROM COALESCE(NULLIF(c.data_demissao, '')::date, CURRENT_DATE)) -
         EXTRACT(YEAR FROM c.data_admissao::date)) * 12
        + EXTRACT(MONTH FROM COALESCE(NULLIF(c.data_demissao, '')::date, CURRENT_DATE)) -
          EXTRACT(MONTH FROM c.data_admissao::date)
      )::integer)
    END,
    CASE WHEN c.data_demissao IS NULL OR trim(c.data_demissao) = ''
         THEN 'ATIVO' ELSE 'INATIVO' END,
    ct.cod_loja::integer,
    l.nome_loja
FROM raw.colaborador c
LEFT JOIN raw.colaborador_trabalha ct
       ON ct.cod_colaborador = c.cod_colaborador
LEFT JOIN raw.loja l ON l.cod_loja = ct.cod_loja
WHERE NULLIF(trim(c.cod_colaborador), '') ~ '^[0-9]+$'
  AND NULLIF(trim(c.data_admissao), '') IS NOT NULL
  AND c.data_admissao ~ '^\d{4}-\d{2}-\d{2}$'
  AND NOT EXISTS (
      SELECT 1 FROM staging.stg_colaborador sc
      WHERE sc.cod_colaborador = c.cod_colaborador::integer
  );

INSERT INTO staging.stg_forma_pagamento
    (cod_forma_pag, tipo_pagamento, categoria_pagamento)
SELECT
    NULLIF(trim(cod_forma_pag), '')::integer,
    upper(trim(tipo_pagamento)),
    CASE
      WHEN upper(trim(tipo_pagamento)) IN ('DÉBITO', 'CRÉDITO') THEN 'CARTÃO'
      WHEN upper(trim(tipo_pagamento)) = 'PIX' THEN 'PIX'
      WHEN upper(trim(tipo_pagamento)) = 'DINHEIRO' THEN 'DINHEIRO'
      ELSE 'OUTROS'
    END
FROM raw.forma_pagamento
WHERE NULLIF(trim(cod_forma_pag), '') ~ '^[0-9]+$'
ON CONFLICT (cod_forma_pag) DO NOTHING;

INSERT INTO staging.stg_produto
    (cod_produto, cod_categoria, categoria_produto, nome_produto, descricao,
     marca, preco_unitario, faixa_preco, possui_fragrancia, ativo)
SELECT
    p.cod_produto::integer,
    NULLIF(trim(p.cod_categoria), '')::integer,
    c.categoria_produto,
    p.nome_produto,
    p.descricao,
    p.marca,
    NULLIF(trim(p.preco_unitario), '')::numeric(10,2),
    CASE
      WHEN NULLIF(trim(p.preco_unitario), '')::numeric < 10 THEN 'BAIXO'
      WHEN NULLIF(trim(p.preco_unitario), '')::numeric < 30 THEN 'MÉDIO'
      ELSE 'ALTO'
    END,
    EXISTS (
      SELECT 1 FROM raw.produto_fragrancia pf
      WHERE pf.cod_produto = p.cod_produto
    ),
    CASE
      WHEN lower(trim(COALESCE(p.ativo, 'true'))) IN ('true','t','1','sim','s') THEN TRUE
      WHEN lower(trim(COALESCE(p.ativo, 'true'))) IN ('false','f','0','não','nao','n') THEN FALSE
      ELSE TRUE
    END
FROM raw.produto p
LEFT JOIN raw.categoria c ON c.cod_categoria = p.cod_categoria
WHERE NULLIF(trim(p.cod_produto), '') ~ '^[0-9]+$'
  AND NULLIF(trim(p.preco_unitario), '') ~ '^[0-9]+([.][0-9]+)?$'
ON CONFLICT (cod_produto) DO NOTHING;

-- A dimensão tempo é derivada das datas de venda existentes.
INSERT INTO staging.stg_tempo
    (data, dia, dia_semana, semana_do_ano, mes, nome_mes, trimestre, ano, eh_fim_de_semana)
SELECT DISTINCT
    d::date,
    EXTRACT(DAY FROM d)::integer,
    CASE EXTRACT(ISODOW FROM d)::integer
      WHEN 1 THEN 'Segunda-feira' WHEN 2 THEN 'Terça-feira'
      WHEN 3 THEN 'Quarta-feira' WHEN 4 THEN 'Quinta-feira'
      WHEN 5 THEN 'Sexta-feira' WHEN 6 THEN 'Sábado' WHEN 7 THEN 'Domingo'
    END,
    EXTRACT(WEEK FROM d)::integer,
    EXTRACT(MONTH FROM d)::integer,
    CASE EXTRACT(MONTH FROM d)::integer
      WHEN 1 THEN 'Janeiro' WHEN 2 THEN 'Fevereiro' WHEN 3 THEN 'Março'
      WHEN 4 THEN 'Abril' WHEN 5 THEN 'Maio' WHEN 6 THEN 'Junho'
      WHEN 7 THEN 'Julho' WHEN 8 THEN 'Agosto' WHEN 9 THEN 'Setembro'
      WHEN 10 THEN 'Outubro' WHEN 11 THEN 'Novembro' WHEN 12 THEN 'Dezembro'
    END,
    EXTRACT(QUARTER FROM d)::integer,
    EXTRACT(YEAR FROM d)::integer,
    EXTRACT(ISODOW FROM d)::integer IN (6,7)
FROM (
    SELECT DISTINCT NULLIF(trim(hora_do_registro), '')::timestamp::date AS d
    FROM raw.registro_pedido
    WHERE NULLIF(trim(hora_do_registro), '') IS NOT NULL
      AND trim(hora_do_registro) ~ '^\d{4}-\d{2}-\d{2}'
) datas
WHERE d IS NOT NULL
ON CONFLICT (data) DO NOTHING;

INSERT INTO staging.stg_venda_item
    (cod_detalhes, cod_venda, cod_produto, cod_loja, cod_colaborador,
     cod_forma_pag, data_venda, hora_venda, quantidade, preco_unitario,
     valor_total_item, is_recomendacao, turno)
SELECT
    dp.cod_detalhes::integer,
    rp.cod_venda::integer,
    dp.cod_produto::integer,
    rp.cod_loja::integer,
    rp.cod_colaborador::integer,
    rp.cod_forma_pag::integer,
    rp.hora_do_registro::timestamp::date,
    rp.hora_do_registro::timestamp,
    dp.quantidade::integer,
    NULLIF(trim(dp.preco_unitario), '')::numeric(10,2),
    dp.quantidade::integer * NULLIF(trim(dp.preco_unitario), '')::numeric(10,2),
    CASE WHEN lower(trim(COALESCE(dp.is_recomendacao, 'false'))) IN ('true','t','1','sim','s')
         THEN TRUE ELSE FALSE END,
    CASE
      WHEN EXTRACT(HOUR FROM rp.hora_do_registro::timestamp) BETWEEN 5 AND 11 THEN 'MANHÃ'
      WHEN EXTRACT(HOUR FROM rp.hora_do_registro::timestamp) BETWEEN 12 AND 17 THEN 'TARDE'
      ELSE 'NOITE'
    END
FROM raw.detalhes_pedido dp
JOIN raw.registro_pedido rp ON rp.cod_venda = dp.cod_venda
WHERE dp.cod_detalhes ~ '^[0-9]+$'
  AND dp.cod_venda ~ '^[0-9]+$'
  AND dp.cod_produto ~ '^[0-9]+$'
  AND rp.cod_loja ~ '^[0-9]+$'
  AND rp.cod_colaborador ~ '^[0-9]+$'
  AND rp.cod_forma_pag ~ '^[0-9]+$'
  AND dp.quantidade ~ '^[0-9]+$'
  AND NULLIF(trim(dp.preco_unitario), '') ~ '^[0-9]+([.][0-9]+)?$'
  AND rp.hora_do_registro ~ '^\d{4}-\d{2}-\d{2}'
ON CONFLICT (cod_detalhes) DO NOTHING;

