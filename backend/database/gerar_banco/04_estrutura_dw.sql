-- schemas do bossini

DROP SCHEMA IF EXISTS raw CASCADE;
DROP SCHEMA IF EXISTS staging CASCADE;
DROP SCHEMA IF EXISTS dw CASCADE;

CREATE SCHEMA raw;
CREATE SCHEMA staging;
CREATE SCHEMA dw;


-- ===================== raw ===================== 
-- ===================== raw ===================== 
-- ===================== raw ===================== 
-- ===================== raw ===================== 

CREATE TABLE raw.loja (
    cod_loja TEXT,
    nome_loja TEXT,
    endereco TEXT,
    bairro TEXT,
    cidade TEXT,
    cep TEXT,
    telefone TEXT,
    email TEXT,
    tipo_loja TEXT,
    dt_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE raw.colaborador (
    cod_colaborador TEXT,
    nome TEXT,
    cargo TEXT,
    data_admissao TEXT,
    data_demissao TEXT,
    dt_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE raw.colaborador_trabalha (
    cod_loja TEXT,
    cod_colaborador TEXT,
    dt_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE raw.forma_pagamento (
    cod_forma_pag TEXT,
    tipo_pagamento TEXT,
    dt_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE raw.categoria (
    cod_categoria TEXT,
    categoria_produto TEXT,
    dt_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE raw.produto (
    cod_produto TEXT,
    cod_categoria TEXT,
    nome_produto TEXT,
    descricao TEXT,
    marca TEXT,
    preco_unitario TEXT,
    url_imagem TEXT,
    ativo TEXT,
    dt_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE raw.produto_fragrancia (
    cod_produto TEXT,
    cod_fragrancia TEXT,
    dt_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE raw.registro_pedido (
    cod_venda TEXT,
    cod_loja TEXT,
    cod_colaborador TEXT,
    cod_forma_pag TEXT,
    valor_total TEXT,
    valor_recebido TEXT,
    troco TEXT,
    hora_do_registro TEXT,
    dt_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE raw.detalhes_pedido (
    cod_detalhes TEXT,
    cod_venda TEXT,
    cod_produto TEXT,
    cod_fragrancia TEXT,
    quantidade TEXT,
    preco_unitario TEXT,
    is_recomendacao TEXT,
    dt_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ===================== staging ===================== 
-- ===================== staging ===================== 
-- ===================== staging ===================== 
-- ===================== staging ===================== 

CREATE TABLE staging.stg_loja (
    cod_loja INTEGER PRIMARY KEY,
    nome_loja VARCHAR(100),
    endereco VARCHAR(100),
    bairro VARCHAR(50),
    cidade VARCHAR(50),
    cep VARCHAR(9),
    tipo_loja VARCHAR(10),
    dt_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE staging.stg_colaborador (
    cod_colaborador INTEGER PRIMARY KEY,
    nome VARCHAR(100),
    cargo VARCHAR(50),
    data_admissao DATE,
    data_demissao DATE,
    tempo_de_casa_meses INTEGER,
    situacao VARCHAR(10),
    cod_loja_principal INTEGER,
    loja_principal VARCHAR(100),
    dt_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE staging.stg_forma_pagamento (
    cod_forma_pag INTEGER PRIMARY KEY,
    tipo_pagamento VARCHAR(15),
    categoria_pagamento VARCHAR(15),
    dt_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE staging.stg_produto (
    cod_produto INTEGER PRIMARY KEY,
    cod_categoria INTEGER,
    categoria_produto VARCHAR(30),
    nome_produto VARCHAR(100),
    descricao VARCHAR(200),
    marca VARCHAR(50),
    preco_unitario DECIMAL(10,2),
    faixa_preco VARCHAR(10),
    possui_fragrancia BOOLEAN,
    ativo BOOLEAN,
    dt_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE staging.stg_tempo (
    data DATE PRIMARY KEY,
    dia INTEGER,
    dia_semana VARCHAR(15),
    semana_do_ano INTEGER,
    mes INTEGER,
    nome_mes VARCHAR(15),
    trimestre INTEGER,
    ano INTEGER,
    eh_fim_de_semana BOOLEAN,
    dt_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE staging.stg_venda_item (
    cod_detalhes INTEGER PRIMARY KEY,
    cod_venda INTEGER,
    cod_produto INTEGER,
    cod_loja INTEGER,
    cod_colaborador INTEGER,
    cod_forma_pag INTEGER,
    data_venda DATE,
    hora_venda TIMESTAMP,
    quantidade INTEGER,
    preco_unitario DECIMAL(10,2),
    valor_total_item DECIMAL(10,2),
    is_recomendacao BOOLEAN,
    turno VARCHAR(10),
    dt_carga TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ===================== tempo ===================== 
-- ===================== tempo ===================== 
-- ===================== tempo ===================== 
-- ===================== tempo ===================== 


CREATE TABLE dw.dim_tempo (
    sk_tempo SERIAL PRIMARY KEY,
    data DATE NOT NULL UNIQUE,
    dia INTEGER,
    dia_semana VARCHAR(15),
    semana_do_ano INTEGER,
    mes INTEGER,
    nome_mes VARCHAR(15),
    trimestre INTEGER,
    ano INTEGER,
    eh_fim_de_semana BOOLEAN
);

CREATE TABLE dw.dim_produto (
    sk_produto SERIAL PRIMARY KEY,
    cod_produto INTEGER NOT NULL UNIQUE,
    nome_produto VARCHAR(100),
    marca VARCHAR(50),
    descricao VARCHAR(200),
    categoria_produto VARCHAR(30),
    possui_fragrancia BOOLEAN,
    faixa_preco VARCHAR(10),
    ativo BOOLEAN
);

CREATE TABLE dw.dim_loja (
    sk_loja SERIAL PRIMARY KEY,
    cod_loja INTEGER NOT NULL UNIQUE,
    nome_loja VARCHAR(100),
    endereco VARCHAR(100),
    bairro VARCHAR(50),
    cidade VARCHAR(50),
    cep VARCHAR(9),
    tipo_loja VARCHAR(10)
);

CREATE TABLE dw.dim_colaborador (
    sk_colaborador SERIAL PRIMARY KEY,
    cod_colaborador INTEGER NOT NULL UNIQUE,
    nome VARCHAR(100),
    cargo VARCHAR(50),
    data_admissao DATE,
    tempo_de_casa_meses INTEGER,
    situacao VARCHAR(10),
    loja_principal VARCHAR(100)
);

CREATE TABLE dw.dim_forma_pagamento (
    sk_forma_pagamento SERIAL PRIMARY KEY,
    cod_forma_pag INTEGER NOT NULL UNIQUE,
    tipo_pagamento VARCHAR(15),
    categoria_pagamento VARCHAR(15)
);

CREATE TABLE dw.fato_venda_item (
    sk_venda_item SERIAL PRIMARY KEY,
    fk_tempo INTEGER REFERENCES dw.dim_tempo(sk_tempo),
    fk_produto INTEGER REFERENCES dw.dim_produto(sk_produto),
    fk_loja INTEGER REFERENCES dw.dim_loja(sk_loja),
    fk_colaborador INTEGER REFERENCES dw.dim_colaborador(sk_colaborador),
    fk_forma_pagamento INTEGER REFERENCES dw.dim_forma_pagamento(sk_forma_pagamento),
    cod_venda INTEGER,
    cod_detalhes INTEGER UNIQUE,
    quantidade INTEGER,
    preco_unitario_praticado DECIMAL(10,2),
    valor_total_item DECIMAL(10,2),
    is_recomendacao BOOLEAN,
    turno VARCHAR(10)
);



























