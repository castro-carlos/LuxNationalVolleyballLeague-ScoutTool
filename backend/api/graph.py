from fastapi import APIRouter
from neo4j import GraphDatabase
import os

router = APIRouter()

# Connect using environment variables
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://xxxx.databases.neo4j.io")
NEO4J_AUTH = (os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "secret"))

@router.get("/graph/teammates/{player_name}")
def get_teammates(player_name: str):
    """Find all teammates a player has played with using a Graph DB query."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
    query = """
    MATCH (p:Player {name: $name})-[:PLAYS_FOR]->(t:Team)<-[:PLAYS_FOR]-(teammate:Player)
    RETURN teammate.name AS teammate
    """
    with driver.session() as session:
        result = session.run(query, name=player_name)
        teammates = [record["teammate"] for record in result]
    driver.close()
    return {"player": player_name, "teammates": teammates}