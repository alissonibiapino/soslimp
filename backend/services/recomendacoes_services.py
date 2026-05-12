from database.conn_neo4j import get_neo4j_session

def recomendar_produto(cod_produto: int):
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


def recomendar_produtos_carrinho(produtos_carrinho: list):
    session = get_neo4j_session()

    cypher = """
        MATCH (p:Produto)
        WHERE p.cod_produto IN $ids_carrinho

        MATCH (p1)<-[:CONTEM]-(v:Venda)-[:CONTEM]->(p2:Produto)
        WHERE NOT p2.cod_produto IN $ids_carrinho

        OPTIONAL MATCH (p1)-[:TEM_FRAGRANCIA]->(f:Fragrancia)<-[:TEM_FRAGRANCIA]-(p2)

        WITH p2, 
             count(DISTINCT v) * 10 AS peso_venda, 
             count(DISTINCT f) * 2 AS peso_fragrancia

        RETURN 
            p2.cod_produto AS id,
            p2.nome AS nome,
            (peso_venda + peso_fragrancia) AS score
        ORDER BY score DESC
        LIMIT 3
    """
    with session:
        result = session.run(cypher, ids_carrinho=produtos_carrinho)
        return [record.data() for record in result]

