import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load environment variables from .env file
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

def seed_database():
    if not NEO4J_URI or not NEO4J_PASSWORD:
        print("[ERROR] NEO4J_URI or NEO4J_PASSWORD are missing from your .env file.")
        return

    print(f"Connecting to Neo4j graph database...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    cypher_seed = """
    // MERGE ensures we don't create duplicate nodes if run multiple times
    MERGE (t1:Team {name: "VC Strassen"})
    MERGE (t2:Team {name: "CH Diekirch"})

    MERGE (p1:Player {name: "Carlos Castro"})
    MERGE (p2:Player {name: "Alex M."})
    MERGE (p3:Player {name: "Ben S."})

    MERGE (p1)-[:PLAYS_FOR]->(t1)
    MERGE (p2)-[:PLAYS_FOR]->(t1)
    MERGE (p3)-[:PLAYS_FOR]->(t2)

    MERGE (t1)-[:PLAYED_AGAINST {score: "3-1", date: "2026-10-15"}]->(t2)
    """

    try:
        with driver.session() as session:
            session.run(cypher_seed)
            print("[SUCCESS] Neo4j graph database successfully seeded with sample volleyball data!")
    except Exception as e:
        print(f"[ERROR] Failed to connect or seed Neo4j: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    seed_database()