from database.conn_neo4j import get_neo4j_session

def recomendar_produtos(cod_produto: int):
    session = get_neo4j_session()

    cypher = """
        // MATCH (n) RETURN n LIMIT 5
        MATCH (p:Produto {cod_produto: $cod_produto})
        MATCH (v:Venda)-[r1:CONTEM]->(p)
        MATCH (v)-[r2:CONTEM]->(outro:Produto)

        WHERE outro.cod_produto <> p.cod_produto

        WITH 
            outro,
            CASE 
                WHEN r1.cod_fragrancia = r2.cod_fragrancia THEN 3
                ELSE 1
            END AS peso

        RETURN 
            outro.cod_produto AS id,
            outro.nome AS nome,
            sum(peso) AS score
        ORDER BY score DESC
        LIMIT 5
    """
    with session:
        result = session.run(cypher, {"cod_produto": cod_produto})
        return [record.data() for record in result]
