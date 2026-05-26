-- SOSLIMP - SCRIPT COMPLETO (ESTRUTURA + DADOS)

-- DROPS
DROP TABLE IF EXISTS movimentacao_caixa CASCADE;
DROP TABLE IF EXISTS caixa CASCADE;
DROP TABLE IF EXISTS detalhes_pedido CASCADE;
DROP TABLE IF EXISTS registro_pedido CASCADE;
DROP TABLE IF EXISTS produto CASCADE;
DROP TABLE IF EXISTS categoria CASCADE;
DROP TABLE IF EXISTS forma_pagamento CASCADE;
DROP TABLE IF EXISTS colaborador_login CASCADE;
DROP TABLE IF EXISTS colaborador_trabalha CASCADE;
DROP TABLE IF EXISTS colaborador CASCADE;
DROP TABLE IF EXISTS loja CASCADE;
DROP TABLE IF EXISTS fragrancia CASCADE;
DROP TABLE IF EXISTS produto_fragrancia CASCADE;

-- CREATES
CREATE TABLE loja(
    cod_loja SERIAL PRIMARY KEY,
    nome_loja VARCHAR(100) NOT NULL,
    endereco VARCHAR(100) NOT NULL,
    bairro VARCHAR(50) NOT NULL,
    cidade VARCHAR(50) NOT NULL,
    cep VARCHAR(9) NOT NULL,
    telefone VARCHAR(14) NOT NULL,
    email VARCHAR(100) NOT NULL,
    tipo_loja VARCHAR(10) NOT NULL CHECK (tipo_loja IN ('MATRIZ', 'FILIAL'))
);

CREATE TABLE colaborador(
    cod_colaborador SERIAL PRIMARY KEY,
    cpf_cnpj VARCHAR(18) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    cargo VARCHAR(50) NOT NULL,
    data_admissao DATE NOT NULL,
    data_demissao DATE NULL
);

CREATE TABLE colaborador_trabalha (
    cod_loja INTEGER REFERENCES loja (cod_loja),
    cod_colaborador INTEGER REFERENCES colaborador (cod_colaborador),
    PRIMARY KEY (cod_loja, cod_colaborador)
);

CREATE TABLE colaborador_login (
    cod_usuario_login SERIAL PRIMARY KEY,
    usuario VARCHAR(20) NOT NULL,
    senha_hash VARCHAR(255),
    ultimo_login TIMESTAMP,
    cod_colaborador INTEGER REFERENCES colaborador (cod_colaborador)
);

CREATE TABLE forma_pagamento(
    cod_forma_pag SERIAL PRIMARY KEY,
    tipo_pagamento VARCHAR(15) NOT NULL
);

CREATE TABLE categoria(
    cod_categoria SERIAL PRIMARY KEY,
    categoria_produto VARCHAR(30) NOT NULL
);

CREATE TABLE produto(
    cod_produto SERIAL PRIMARY KEY,
    cod_categoria INTEGER REFERENCES categoria(cod_categoria),
    nome_produto VARCHAR(100) NOT NULL,
    descricao VARCHAR(200) NOT NULL,
    marca VARCHAR(50) NOT NULL,
    preco_unitario DECIMAL(10,2) NOT NULL
);

CREATE TABLE registro_pedido (
    cod_venda SERIAL PRIMARY KEY,
    cod_loja INTEGER REFERENCES loja (cod_loja),
    cod_colaborador INTEGER REFERENCES colaborador (cod_colaborador),
    cod_forma_pag INTEGER REFERENCES forma_pagamento (cod_forma_pag),
    valor_total DECIMAL(10,2),
    valor_recebido DECIMAL(10,2),
    troco DECIMAL(10,2),
    hora_do_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE detalhes_pedido (
    cod_detalhes SERIAL PRIMARY KEY,
    cod_produto INTEGER REFERENCES produto (cod_produto),
    quantidade INTEGER NOT NULL,
    preco_unitario DECIMAL (10, 2),
    cod_venda INTEGER NOT NULL REFERENCES registro_pedido (cod_venda)
);

CREATE TABLE caixa (
    cod_caixa SERIAL PRIMARY KEY,
    data_abertura TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valor_inicial DECIMAL (10, 2) NOT NULL,
    valor_atual DECIMAL (10, 2) NOT NULL,
    valor_final DECIMAL (10, 2),
    diferenca DECIMAL (10, 2),
    status_caixa VARCHAR(7) NOT NULL CHECK (status_caixa IN ('ABERTO', 'FECHADO')),
    cod_loja INTEGER NOT NULL REFERENCES loja (cod_loja)
);

CREATE TABLE movimentacao_caixa (
    cod_movimentacao SERIAL,
    cod_caixa INTEGER REFERENCES caixa (cod_caixa),
    valor DECIMAL (10, 2),
    data_movimentacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cod_venda INTEGER REFERENCES registro_pedido (cod_venda),
    PRIMARY KEY (cod_movimentacao, cod_caixa)
);

CREATE TABLE fragrancia (
    cod_fragrancia SERIAL PRIMARY KEY,
    nome_fragrancia VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE produto_fragrancia (
    cod_produto INTEGER REFERENCES produto(cod_produto),
    cod_fragrancia INTEGER REFERENCES fragrancia(cod_fragrancia),
    PRIMARY KEY (cod_produto, cod_fragrancia)
);

--ALTER TABLE

ALTER TABLE detalhes_pedido
ADD COLUMN cod_fragrancia INTEGER REFERENCES fragrancia(cod_fragrancia);

ALTER TABLE detalhes_pedido
ADD COLUMN is_recomendacao BOOLEAN DEFAULT FALSE;

-- Suporte a imagens e gestão de status do produto
ALTER TABLE produto
ADD COLUMN url_imagem VARCHAR(255),
ADD COLUMN ativo BOOLEAN DEFAULT TRUE;


-- INSERTS
INSERT INTO loja (nome_loja, endereco, bairro, cidade, cep, telefone, email, tipo_loja) VALUES 
('SOSLimp - Jd. Patrícia', 'R. José Alexandrino de Morães, 489', 'Jardim Patrícia', 'Itaquaquecetuba', '08584-090', '(11)4646-6464','contatoloja1@soslimp.com', 'MATRIZ'),
('SOSLimp - Jd. América', 'Estr. Pedro da Cunha Albuquerque Lopes, 2473', 'Jardim América', 'Itaquaquecetuba', '08584-584', '(11)94646-4646', 'contatoloja2@soslimp.com', 'FILIAL');

INSERT INTO colaborador (cpf_cnpj, nome, cargo, data_admissao) VALUES 
('348.480.178-66', 'Wellington Magalhães', 'MICROEMPRESARIO', '2000-01-01'),
('525.865.362-45', 'Carol Carvalho', 'VENDEDORA', '2022-07-04'),
('525.865.362-48', 'Arthur Papadopoulos', 'VENDEDOR', '2024-02-10');

INSERT INTO colaborador_login (usuario, senha_hash, cod_colaborador) VALUES 
('well', 1234, 1);

INSERT INTO colaborador_trabalha (cod_loja, cod_colaborador) VALUES (1, 1), (1, 2), (2, 3);

INSERT INTO forma_pagamento (tipo_pagamento) VALUES ('DÉBITO'), ('CRÉDITO'), ('PIX'), ('DINHEIRO');

INSERT INTO categoria (categoria_produto) VALUES 
('Álcool'), 
('Amaciante'), 
('Automotivo'), 
('Detergente'), 
('Desinfetante'), 
('Essência'), 
('Desengordurantes'),
('Limpeza Pesada'),
('Limpeza Leve'),
('Higiene Pessoal'),
('Utensílios de Limpeza'),
('Odorizadores'),
('Sabão em Pó'),
('Sabão Líquido'),
('Multiuso'),
('Limpa Vidros'),
('Cloro e Alvejante');

INSERT INTO produto (cod_categoria, nome_produto, descricao, marca, preco_unitario, url_imagem) VALUES
(1, 'Álcool 70% 1L', 'Álcool para higienização', 'SOSLimp', 10.00, '/static/products/alcool-70.jpg'),
(2, 'Amaciante 1L', 'Fragrância de Verão', 'SOSLimp', 25.00, '/static/products/amaciante-1l.jpg'),
(4, 'Detergente 5L', 'Galão 5L', 'ALCA', 19.00, '/static/products/detergente-5l.jpg'),
(7, 'Desengordurante 400ml', 'Limpador pesado', 'SOSLimp', 30.00, '/static/products/desengordurante.jpg'),
(1, 'Álcool Gel 500ml', 'Álcool gel antisséptico', 'SOSLimp', 12.00, '/static/products/alcool-gel.jpg'),
(1, 'Álcool 92% 1L', 'Limpeza pesada', 'SOSLimp', 11.50, '/static/products/alcool-92.jpg'),
(2, 'Amaciante 2L', 'Perfume suave', 'SOSLimp', 32.00, '/static/products/amaciante-2l.jpg'),
(2, 'Amaciante 5L', 'Uso profissional', 'SOSLimp', 65.00, '/static/products/amaciante-5l.jpg'),
(4, 'Detergente 500ml', 'Uso diário', 'Ypê', 3.50, '/static/products/detergente-ype.jpg'),
(4, 'Detergente 500ml', 'Alta eficiência', 'Ypê', 3.50, '/static/products/detergente-ype-2.jpg'),
(5, 'Desinfetante 2L', 'Elimina bactérias', 'Bombril', 14.00, '/static/products/desinfetante-2l.jpg'),
(5, 'Desinfetante 5L', 'Uso geral', 'SOSLimp', 28.00, '/static/products/desinfetante-5l.jpg'),
(7, 'Desengordurante 1L', 'Remove gordura pesada', 'SOSLimp', 18.00, '/static/products/desengordurante-1l.jpg'),
(7, 'Desengordurante 5L', 'Uso industrial', 'SOSLimp', 70.00, '/static/products/desengordurante-5l.jpg'),
(8, 'Removedor 1L', 'Remove sujeiras difíceis', 'SOSLimp', 22.00, '/static/products/removedor.jpg'),
(8, 'Limpa Pedra 2L', 'Limpeza externa', 'SOSLimp', 26.00, '/static/products/limpa-pedra.jpg'),
(9, 'Limpador Multiuso 500ml', 'Uso geral', 'Veja', 6.50, '/static/products/veja-multiuso.jpg'),
(9, 'Limpador Multiuso 1L', 'Alta performance', 'Veja', 9.90, '/static/products/veja-multiuso-1l.jpg'),
(10, 'Sabonete Líquido 500ml', 'Higiene pessoal', 'Palmolive', 12.00, '/static/products/sabonete-palmolive.jpg'),
(10, 'Sabonete Antibacteriano', 'Proteção diária', 'Protex', 8.50, '/static/products/sabonete-protex.jpg'),
(11, 'Esponja Dupla Face', 'Limpeza geral', 'Scotch-Brite', 4.00, '/static/products/esponja.jpg'),
(11, 'Pano Multiuso', 'Alta absorção', 'Perfex', 6.00, '/static/products/pano-multiuso.jpg'),
(11, 'Vassoura', 'Uso doméstico', 'Condor', 18.00, '/static/products/vassoura.jpg'),
(11, 'Rodo 40cm', 'Limpeza de pisos', 'Condor', 22.00, '/static/products/rodo.jpg'),
(12, 'Odorizador Spray', 'Ambiente perfumado', 'Glade', 11.00, '/static/products/odorizador-spray.jpg'),
(12, 'Odorizador Automático', 'Liberação contínua', 'Bom Ar', 45.00, '/static/products/odorizador-automatico.jpg'),
(13, 'Sabão em Pó 1kg', 'Limpeza de roupas', 'Omo', 18.00, '/static/products/sabao-po-1kg.jpg'),
(13, 'Sabão em Pó 2kg', 'Alta performance', 'Omo', 32.00, '/static/products/sabao-po-2kg.jpg'),
(14, 'Sabão Líquido 1L', 'Roupas delicadas', 'Omo', 20.00, '/static/products/sabao-liquido-1l.jpg'),
(14, 'Sabão Líquido 3L', 'Uso frequente', 'Omo', 45.00, '/static/products/sabao-liquido-3l.jpg'),
(15, 'Limpa Vidros 500ml', 'Vidros sem manchas', 'Veja', 8.00, '/static/products/limpa-vidros.jpg'),
(15, 'Limpa Vidros 1L', 'Uso profissional', 'Veja', 14.00, '/static/products/limpa-vidros-1l.jpg'),
(16, 'Água Sanitária 1L', 'Alvejante comum', 'Qboa', 6.00, '/static/products/agua-sanitaria-1l.jpg'),
(16, 'Água Sanitária 5L', 'Uso pesado', 'Qboa', 20.00, '/static/products/agua-sanitaria-5l.jpg'),
(5, 'Desinfetante 1L', 'Uso diário', 'SOSLimp', 9.50, '/static/products/desinfetante-1l.jpg'),
(5, 'Desinfetante 3L', 'Ambientes grandes', 'SOSLimp', 18.00, '/static/products/desinfetante-3l.jpg'),
(9, 'Multiuso 2L', 'Limpeza pesada', 'Veja', 15.00, '/static/products/veja-2l.jpg'),
(9, 'Multiuso Concentrado 500ml', 'Alta eficiência', 'Veja', 12.00, '/static/products/veja-concentrado.jpg'),
(14, 'Sabão Líquido 5L', 'Uso profissional', 'OMO', 65.00, '/static/products/sabao-liquido-5l.jpg'),
(12, 'Odorizador Gel', 'Perfume contínuo', 'Glade', 9.00, '/static/products/odorizador-gel.jpg'),
(2, 'Amaciante Concentrado 500ml', 'Alta performance', 'SOSLimp', 18.00, '/static/products/amaciante-concentrado.jpg'),
(3, 'Shampoo Automotivo 1L', 'Limpeza de veículos', 'Vonixx', 25.00, '/static/products/shampoo-auto.jpg'),
(8, 'Limpa Alumínio 500ml', 'Brilho intenso', 'SOSLimp', 7.00, '/static/products/limpa-aluminio.jpg');

INSERT INTO fragrancia (nome_fragrancia) VALUES
('Lavanda'),
('Floral'),
('Limão Siciliano'),
('Coco'),
('Pinho'),
('Brisa do Mar'),
('Talco'),
('Erva Doce'),
('Capim Limão'),
('Maçã Verde'),
('Frutas Vermelhas'),
('Baunilha'),
('Eucalipto'),
('Algodão'),
('Jasmim'),
('Canela'),
('Neutro'),
('Sem fragrância');

INSERT INTO produto_fragrancia VALUES
(2, 1), (2, 14), (2, 6),
(7, 1), (7, 15), (7, 11),
(8, 2), (8, 12), (8, 10),
(3, 17),
(9, 3), (9, 9),
(10, 4), (10, 11),
(11, 5), (11, 13),
(12, 1), (12, 6),
(35, 13), (35, 5),
(36, 1), (36, 8),
(17, 3), (17, 14),
(18, 3), (18, 9),
(37, 3), (37, 13),
(38, 17),
(25, 11), (25, 6), (25, 15),
(26, 11), (26, 1),
(40, 12), (40, 16),
(29, 14), (29, 1),
(30, 14), (30, 10),
(39, 14), (39, 2),
(1, 18),
(5, 18),
(6, 18),
(4, 18),
(13, 18),
(14, 18),
(15, 18),
(16, 18);

-- SELECTS
SELECT 
    p.cod_produto,
    p.nome_produto,
    f.nome_fragrancia
FROM produto p
LEFT JOIN produto_fragrancia pf ON pf.cod_produto = p.cod_produto
LEFT JOIN fragrancia f ON f.cod_fragrancia = pf.cod_fragrancia
ORDER BY p.cod_produto;

-- POPULAÇÃO (GERADO POR IA)
-- POPULAÇÃO REALISTA DE VENDAS
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
        -- SAZONALIDADE MENSAL
        --------------------------------------------------

        CASE v_current_month

            WHEN 1 THEN
                v_month_factor := 0.85;
                v_target_recommendation_rate := 0.03;

            WHEN 2 THEN
                v_month_factor := 0.95;
                v_target_recommendation_rate := 0.04;

            WHEN 3 THEN
                v_month_factor := 1.05;
                v_target_recommendation_rate := 0.05;

            WHEN 4 THEN
                v_month_factor := 1.10;
                v_target_recommendation_rate := 0.06;

            WHEN 5 THEN
                v_month_factor := 0.92;
                v_target_recommendation_rate := 0.04;

            WHEN 6 THEN
                v_month_factor := 1.18;
                v_target_recommendation_rate := 0.07;

            WHEN 7 THEN
                v_month_factor := 1.25;
                v_target_recommendation_rate := 0.08;

            WHEN 8 THEN
                v_month_factor := 1.08;
                v_target_recommendation_rate := 0.06;

            WHEN 9 THEN
                v_month_factor := 0.90;
                v_target_recommendation_rate := 0.04;

            WHEN 10 THEN
                v_month_factor := 1.12;
                v_target_recommendation_rate := 0.07;

            WHEN 11 THEN
                v_month_factor := 1.35;
                v_target_recommendation_rate := 0.08;

            WHEN 12 THEN
                v_month_factor := 1.50;
                v_target_recommendation_rate := 0.08;

            ELSE
                v_month_factor := 1.00;
                v_target_recommendation_rate := 0.05;

        END CASE;

        --------------------------------------------------
        -- LOOP DE LOJAS
        --------------------------------------------------

        FOR v_cod_loja IN 1..2 LOOP

            --------------------------------------------------
            -- QUANTIDADE BASE DE PEDIDOS
            --------------------------------------------------

            IF v_is_weekend THEN

                v_n_pedidos :=
                (
                    (
                        8 + floor(random()*10)::INT
                    ) * v_month_factor
                )::INT;

            ELSE

                v_n_pedidos :=
                (
                    (
                        25 + floor(random()*30)::INT
                    ) * v_month_factor
                )::INT;

            END IF;

            --------------------------------------------------
            -- AJUSTE POR DIA DA SEMANA
            --------------------------------------------------

            CASE v_day_of_week

                -- Segunda
                WHEN 1 THEN
                    v_n_pedidos := (v_n_pedidos * 0.85)::INT;

                -- Sexta
                WHEN 5 THEN
                    v_n_pedidos := (v_n_pedidos * 1.20)::INT;

                -- Sábado
                WHEN 6 THEN
                    v_n_pedidos := (v_n_pedidos * 1.35)::INT;

                -- Domingo
                WHEN 0 THEN
                    v_n_pedidos := (v_n_pedidos * 1.15)::INT;

                ELSE
                    v_n_pedidos := v_n_pedidos;

            END CASE;

            --------------------------------------------------
            -- BLACK FRIDAY
            --------------------------------------------------

            IF EXTRACT(MONTH FROM v_cur_date) = 11
            AND EXTRACT(DAY FROM v_cur_date) >= 20
            THEN
                v_n_pedidos := (v_n_pedidos * 1.8)::INT;
            END IF;

            --------------------------------------------------
            -- NATAL
            --------------------------------------------------

            IF EXTRACT(MONTH FROM v_cur_date) = 12
            AND EXTRACT(DAY FROM v_cur_date) >= 15
            THEN
                v_n_pedidos := (v_n_pedidos * 1.5)::INT;
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

                    --------------------------------------------------
                    -- MANHÃ
                    --------------------------------------------------

                    v_hora :=
                        v_cur_date
                        + interval '8 hour'
                        + (random() * interval '3 hour');

                ELSIF v_hour_rand < 0.55 THEN

                    --------------------------------------------------
                    -- ALMOÇO
                    --------------------------------------------------

                    v_hora :=
                        v_cur_date
                        + interval '11 hour'
                        + (random() * interval '2 hour');

                ELSIF v_hour_rand < 0.85 THEN

                    --------------------------------------------------
                    -- TARDE
                    --------------------------------------------------

                    v_hora :=
                        v_cur_date
                        + interval '14 hour'
                        + (random() * interval '3 hour');

                ELSE

                    --------------------------------------------------
                    -- NOITE
                    --------------------------------------------------

                    v_hora :=
                        v_cur_date
                        + interval '18 hour'
                        + (random() * interval '2 hour');

                END IF;

                --------------------------------------------------
                -- INSERE PEDIDO
                --------------------------------------------------

                INSERT INTO registro_pedido (
                    cod_loja,
                    cod_colaborador,
                    cod_forma_pag,
                    valor_total,
                    valor_recebido,
                    troco,
                    hora_do_registro
                )
                VALUES (
                    v_cod_loja,
                    v_cod_colab,
                    v_cod_forma,
                    0,
                    0,
                    0,
                    v_hora
                )
                RETURNING cod_venda
                INTO v_new_cod_venda;

                v_total := 0;

                --------------------------------------------------
                -- QUANTIDADE DE ITENS
                --------------------------------------------------

                IF random() < 0.65 THEN

                    v_n_itens := 1 + floor(random()*2)::INT;

                ELSE

                    v_n_itens := 3 + floor(random()*4)::INT;

                END IF;

                --------------------------------------------------
                -- INSERE ITENS
                --------------------------------------------------

                FOR j IN 1..v_n_itens LOOP

                    --------------------------------------------------
                    -- PRODUTOS CAMPEÕES DE VENDA
                    --------------------------------------------------

                    /*
                        70%:
                        produtos mais vendidos

                        30%:
                        produtos aleatórios
                    */

                    IF random() < 0.70 THEN

                        SELECT
                            cod_produto,
                            preco_unitario
                        INTO v_prod
                        FROM produto
                        WHERE cod_produto <= 8
                        ORDER BY random()
                        LIMIT 1;

                    ELSE

                        SELECT
                            cod_produto,
                            preco_unitario
                        INTO v_prod
                        FROM produto
                        ORDER BY random()
                        LIMIT 1;

                    END IF;

                    --------------------------------------------------
                    -- FRAGRÂNCIA
                    --------------------------------------------------

                    SELECT cod_fragrancia
                    INTO v_fragrancia
                    FROM produto_fragrancia
                    WHERE cod_produto = v_prod.cod_produto
                    ORDER BY random()
                    LIMIT 1;

                    --------------------------------------------------
                    -- QUANTIDADE
                    --------------------------------------------------

                    IF random() < 0.75 THEN

                        v_quantidade := 1;

                    ELSIF random() < 0.90 THEN

                        v_quantidade := 2;

                    ELSE

                        v_quantidade := 3;

                    END IF;

                    --------------------------------------------------
                    -- INSERE ITEM
                    --------------------------------------------------

                    INSERT INTO detalhes_pedido (
                        cod_produto,
                        cod_fragrancia,
                        quantidade,
                        preco_unitario,
                        cod_venda,
                        is_recomendacao
                    )
                    VALUES (
                        v_prod.cod_produto,
                        v_fragrancia,
                        v_quantidade,
                        v_prod.preco_unitario,
                        v_new_cod_venda,

                        (
                            j > 1
                            AND random() < v_target_recommendation_rate
                        )
                    );

                    --------------------------------------------------
                    -- SOMA TOTAL
                    --------------------------------------------------

                    v_total :=
                        v_total
                        + (
                            v_prod.preco_unitario
                            * v_quantidade
                        );

                END LOOP;

                --------------------------------------------------
                -- ATUALIZA PAGAMENTO
                --------------------------------------------------

                UPDATE registro_pedido
                SET
                    valor_total = v_total,

                    valor_recebido =
                        CASE
                            WHEN v_cod_forma = 4
                            THEN ceil(v_total / 10) * 10
                            ELSE v_total
                        END,

                    troco =
                        CASE
                            WHEN v_cod_forma = 4
                            THEN (ceil(v_total / 10) * 10) - v_total
                            ELSE 0
                        END

                WHERE cod_venda = v_new_cod_venda;

            END LOOP;

        END LOOP;

    END LOOP;

END
$$;