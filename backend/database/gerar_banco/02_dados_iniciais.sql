-- INSERTS
INSERT INTO loja (nome_loja, endereco, bairro, cidade, cep, telefone, email, tipo_loja) VALUES 
('SOSLimp - Jd. Patrícia', 'R. José Alexandrino de Morães, 489', 'Jardim Patrícia', 'Itaquaquecetuba', '08584-090', '(11)4646-6464','contatoloja1@soslimp.com', 'MATRIZ'),
('SOSLimp - Jd. América', 'Estr. Pedro da Cunha Albuquerque Lopes, 2473', 'Jardim América', 'Itaquaquecetuba', '08584-584', '(11)94646-4646', 'contatoloja2@soslimp.com', 'FILIAL');

INSERT INTO colaborador (cpf_cnpj, nome, cargo, data_admissao) VALUES 
('348.480.178-66', 'Wellington Magalhães', 'MICROEMPRESARIO', '2000-01-01'),
('525.865.362-45', 'Carol Carvalho', 'VENDEDORA', '2022-07-04'),
('525.865.362-48', 'Arthur Papadopoulos', 'VENDEDOR', '2024-02-10');

INSERT INTO colaborador_login (usuario, senha_hash, cod_colaborador) VALUES 
('well', 1234, 1),
('carol', 1234, 2);

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
(4, 'Detergente 500ml alta eficiência', 'Alta eficiência', 'Ypê', 3.50, '/static/products/detergente-ype-2.jpg'),
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
(2, 1), (2, 12),
(7, 1), (7, 15), (7, 11), (7, 10), (7, 9),
(8, 1), (8, 12), (8, 10),
(3, 17),
(9, 3), (9, 9),
(10, 4), (10, 11),
(11, 5), (11, 13),
(12, 1), (12, 2), (12, 5), (12, 6), (12, 7), (12, 8), (12, 9), (12, 13), (12, 15),
(35, 1), (35, 2), (35, 5), (35, 6), (35, 7), (35, 8), (35, 9), (35, 13), (35, 15),
(36, 1), (36, 2), (36, 5), (36, 6), (36, 7), (36, 8), (36, 9), (36, 13), (36, 15),
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



-- população inicial do estoque
INSERT INTO estoque (cod_produto, cod_loja, quantidade_atual, estoque_minimo)
SELECT 
    p.cod_produto,
    l.cod_loja,
    floor(random() * 30 + 10)::INT,  -- entre 50 e 150 unidades
    floor(random() * 10 + 10)::INT    -- mínimo entre 10 e 25
FROM produto p
CROSS JOIN loja l;





