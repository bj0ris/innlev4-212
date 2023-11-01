from neo4j import GraphDatabase

URI = "neo4j+s://84c9b254.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "9BPTWpu5kp2nWjPyfuhfn5zorZKBrh5jBpKC3uBw908"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

with driver.session() as session:
    result = session.run("RETURN 1")
    for record in result:
        print(record)
