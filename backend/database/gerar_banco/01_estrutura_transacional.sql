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
DROP TABLE IF EXISTS estoque CASCADE;
DROP TABLE IF EXISTS movimentacao_estoque CASCADE;

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



-- Tabelas de estoque (definições movidas para a etapa de estrutura)

-- criando a nova parte de estoque
CREATE TABLE estoque (
    cod_produto INTEGER REFERENCES produto(cod_produto),
    cod_loja INTEGER REFERENCES loja(cod_loja),
    quantidade_atual INTEGER NOT NULL DEFAULT 0,
    estoque_minimo INTEGER NOT NULL DEFAULT 0,
    atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (cod_produto, cod_loja)
);

CREATE TABLE movimentacao_estoque (
    cod_movimentacao SERIAL PRIMARY KEY,
    cod_produto INTEGER REFERENCES produto(cod_produto),
    cod_loja INTEGER REFERENCES loja(cod_loja),
    tipo_movimentacao VARCHAR(10) NOT NULL CHECK (tipo_movimentacao IN ('ENTRADA','SAIDA','AJUSTE')),
    quantidade INTEGER NOT NULL,
    cod_venda INTEGER REFERENCES registro_pedido(cod_venda),
    motivo VARCHAR(100),
    data_movimentacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

