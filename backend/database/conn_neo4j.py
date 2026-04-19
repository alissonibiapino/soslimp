import os
from neo4j import GraphDatabase

from dotenv import load_dotenv

load_dotenv()

NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

def get_neo4j_session():
    return driver.session()
