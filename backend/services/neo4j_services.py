from database.conn_neo4j import get_neo4j_session

def registrar_novo_pedido_neo4j(cod_venda, dados_do_pedido):
    session = get_neo4j_session()

    with session:
        for produto in dados_do_pedido['produtos']:
            session.run("""
                MERGE (v:Venda {cod_venda: $cod_venda})
                    ON CREATE SET v.data = datetime()

                MERGE (p:Produto {cod_produto: $cod_produto})
                    ON CREATE SET
                        p.nome = $nome_produto,
                        p.marca = $marca
                
                MERGE (f:Fragrancia {cod_fragrancia: $cod_fragrancia})
                    ON CREATE SET
                        f.nome = $nome_fragrancia
                        
                MERGE (p)-[:TEM_FRAGRANCIA]->(f)

                MERGE (v)-[r:CONTEM]->(p)
                    ON CREATE SET
                        r.cod_fragrancia = $cod_fragrancia
            """,
            {
                "cod_venda": cod_venda,
                "cod_produto": produto['cod_produto'],
                "cod_fragrancia": produto['cod_fragrancia'],
                "nome_produto": produto['nome_produto'],
                "marca": produto['marca'],
                "nome_fragrancia": produto['nome_fragrancia']
            }
            )