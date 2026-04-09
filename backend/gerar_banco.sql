-- SOSLIMP - SCRIPT COMPLETO (ESTRUTURA + DADOS)

-- 1. LIMPEZA TOTAL (Ordem inversa às FKs)
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

-- 2. CRIAÇÃO DAS TABELAS
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

-- 3. INSERÇÃO DE DADOS MESTRES (Necessários para o script de população)
INSERT INTO loja (nome_loja, endereco, bairro, cidade, cep, telefone, email, tipo_loja) VALUES 
('SOSLimp - Jd. Patrícia', 'R. José Alexandrino de Morães, 489', 'Jardim Patrícia', 'Itaquaquecetuba', '08584-090', '(11)4646-6464','contatoloja1@soslimp.com', 'MATRIZ'),
('SOSLimp - Jd. América', 'Estr. Pedro da Cunha Albuquerque Lopes, 2473', 'Jardim América', 'Itaquaquecetuba', '08584-584', '(11)94646-4646', 'contatoloja2@soslimp.com', 'FILIAL');

INSERT INTO colaborador (cpf_cnpj, nome, cargo, data_admissao) VALUES 
('348.480.178-66', 'Wellington Magalhães', 'MICROEMPRESARIO', '2000-01-01'),
('525.865.362-45', 'Carol Carvalho', 'VENDEDORA', '2022-07-04'),
('525.865.362-48', 'Arthur Papadopoulos', 'VENDEDOR', '2024-02-10');

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


INSERT INTO produto (cod_categoria, nome_produto, descricao, marca, preco_unitario) VALUES
(1, 'Álcool 70% 1L', 'Álcool para higienização', 'SOSLimp', 10.00),
(2, 'Amaciante 1L - Verão', 'Fragrância de Verão', 'SOSLimp', 25.00),
(4, 'Detergente 5L - Neutro', 'Galão 5L', 'ALCA', 19.00),
(7, 'Desengordurante 400ml', 'Limpador pesado', 'SOSLimp', 30.00),
(1, 'Álcool Gel 500ml', 'Álcool gel antisséptico', 'SOSLimp', 12.00),
(1, 'Álcool 92% 1L', 'Limpeza pesada', 'SOSLimp', 11.50),
(2, 'Amaciante 2L - Lavanda', 'Perfume suave', 'SOSLimp', 32.00),
(2, 'Amaciante 5L - Floral', 'Uso profissional', 'SOSLimp', 65.00),
(4, 'Detergente 500ml - Limão', 'Uso diário', 'Ypê', 3.50),
(4, 'Detergente 500ml - Coco', 'Alta eficiência', 'Ypê', 3.50),
(5, 'Desinfetante 2L - Pinho', 'Elimina bactérias', 'Bombril', 14.00),
(5, 'Desinfetante 5L - Lavanda', 'Uso geral', 'SOSLimp', 28.00),
(7, 'Desengordurante 1L', 'Remove gordura pesada', 'SOSLimp', 18.00),
(7, 'Desengordurante 5L', 'Uso industrial', 'SOSLimp', 70.00),
(8, 'Removedor 1L', 'Remove sujeiras difíceis', 'SOSLimp', 22.00),
(8, 'Limpa Pedra 2L', 'Limpeza externa', 'SOSLimp', 26.00),
(9, 'Limpador Multiuso 500ml', 'Uso geral', 'Veja', 6.50),
(9, 'Limpador Multiuso 1L', 'Alta performance', 'Veja', 9.90),
(10, 'Sabonete Líquido 500ml', 'Higiene pessoal', 'Palmolive', 12.00),
(10, 'Sabonete Antibacteriano', 'Proteção diária', 'Protex', 8.50),
(11, 'Esponja Dupla Face', 'Limpeza geral', 'Scotch-Brite', 4.00),
(11, 'Pano Multiuso', 'Alta absorção', 'Perfex', 6.00),
(11, 'Vassoura', 'Uso doméstico', 'Condor', 18.00),
(11, 'Rodo 40cm', 'Limpeza de pisos', 'Condor', 22.00),
(12, 'Odorizador Spray', 'Ambiente perfumado', 'Glade', 11.00),
(12, 'Odorizador Automático', 'Liberação contínua', 'Bom Ar', 45.00),
(13, 'Sabão em Pó 1kg', 'Limpeza de roupas', 'Omo', 18.00),
(13, 'Sabão em Pó 2kg', 'Alta performance', 'Omo', 32.00),
(14, 'Sabão Líquido 1L', 'Roupas delicadas', 'Omo', 20.00),
(14, 'Sabão Líquido 3L', 'Uso frequente', 'Omo', 45.00),
(15, 'Limpa Vidros 500ml', 'Vidros sem manchas', 'Veja', 8.00),
(15, 'Limpa Vidros 1L', 'Uso profissional', 'Veja', 14.00),
(16, 'Água Sanitária 1L', 'Alvejante comum', 'Qboa', 6.00),
(16, 'Água Sanitária 5L', 'Uso pesado', 'Qboa', 20.00);

-- 4. EXECUÇÃO DO SCRIPT DE POPULAÇÃO AUTOMÁTICA
DO
$$
DECLARE
    v_cur_date date;
    v_dt_start date := '2026-01-01'::date;
    v_dt_end   date := CURRENT_DATE;
    v_n_pedidos integer;
    v_cod_loja integer;
    v_cod_colab integer;
    v_cod_forma integer;
    v_prod_rec record;
    v_new_cod_venda integer;
BEGIN
    FOR v_cur_date IN SELECT generate_series(v_dt_start, v_dt_end, '1 day')::date LOOP
        FOR v_cod_loja IN 1..2 LOOP
            v_n_pedidos := 5 + floor(random()*5)::int; -- 5 a 10 pedidos por loja/dia
            
            FOR i IN 1..v_n_pedidos LOOP
                -- Seleciona colaborador e forma de pag. aleatórios
                SELECT cod_colaborador INTO v_cod_colab FROM colaborador_trabalha WHERE cod_loja = v_cod_loja ORDER BY random() LIMIT 1;
                SELECT cod_forma_pag INTO v_cod_forma FROM forma_pagamento ORDER BY random() LIMIT 1;

                INSERT INTO registro_pedido(cod_loja, cod_colaborador, cod_forma_pag, valor_total, hora_do_registro)
                VALUES (v_cod_loja, v_cod_colab, v_cod_forma, 0, v_cur_date + (random() * interval '9 hours' + interval '9 hours'))
                RETURNING cod_venda INTO v_new_cod_venda;

                -- Adiciona 1 produto aleatório
                SELECT p.cod_produto, p.preco_unitario INTO v_prod_rec FROM produto p ORDER BY random() LIMIT 1;
                INSERT INTO detalhes_pedido(cod_produto, quantidade, preco_unitario, cod_venda)
                VALUES (v_prod_rec.cod_produto, 1, v_prod_rec.preco_unitario, v_new_cod_venda);

                UPDATE registro_pedido SET valor_total = v_prod_rec.preco_unitario WHERE cod_venda = v_new_cod_venda;
            END LOOP;
        END LOOP;
    END LOOP;
END
$$;