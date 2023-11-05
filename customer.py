from flask import Flask, jsonify, request, abort
from neo4j import GraphDatabase, exceptions

URI = "neo4j+ssc://84c9b254.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "9BPTWpu5kp2nWjPyfuhfn5zorZKBrh5jBpKC3uBw908"

driver = GraphDatabase.driver(URI, auth=(USERNAME,PASSWORD))

def get_db_session():
    # Creates a database session, handling potential connection errors
    try:
        return driver.session()
    except exceptions.Neo4jError as e:
        # If a database connection error occurs, the API will respond with a 500 error
        abort(500, description=f"Database connection error: {str(e)}")


def create_customer(json,dbSession):
    # Extract car data from the request's JSON body
    
    id = json.get('id')
    address = json.get('address')
    name = json.get('name')
    age = json.get('age')

    # Validate the received data (ensure all fields are provided)
    if not all([id,address,name,age]):
        return jsonify({"success": False, "message": "All customer details must be provided"}), 400

    try:
        #with dbSession() as session:
        # Perform a transaction to create a new customer
        result = dbSession.write_transaction(
            lambda tx: tx.run(
                """
                CREATE (customer:Customer {
                    id: $id, 
                    address: $address, 
                    name: $name, 
                    age: $age
                })
                RETURN customer
                """,
                id=id,
                address=address,
                name=name,
                age=age
            ).single()
        )
        # Return a success response with the created car's details
        created_customer = result.get("customer") if result else None
        if created_customer:
            return jsonify({"success": True, "customer": created_customer}), 201
        else:
            return jsonify({"success": False, "message": "Customer could not be created"}), 400
    except exceptions.Neo4jError as e:
        if 'ConstraintValidationFailed' in str(e):
            return jsonify({"success": False, "message": "Customer ID already exists"}), 400
        # Handle other potential neo4j exceptions
        abort(500, description=f"Failed to create customer: {e}")

def read_customer(dbDriver):
    #Returns list of all customers
    records, summary, keys = dbDriver.execute_query("MATCH (n:Customer) RETURN n LIMIT 25;",database_="neo4j")
    returnList = []
    for record in records:
        returnList.append(record.data())
    return returnList


def update_customer(dbDriver,id, changejson):
    #Update a customers address,name, and age
    #"adress","name" or "age" as key. The new value as value
    try:
        records, summary, keys = dbDriver.execute_query(
            """
            MATCH (p:Customer {id: $id})
            SET p.age = $age
            SET p.name = $name
            SET p.address = $address
            """, 
            id = id,
            address = changejson.get("address"),
            name=changejson.get("name"), 
            age=changejson.get("age"),
            database_="neo4j",
            )
        print(f"Query counters: {summary.counters}.")
    except exceptions.Neo4jError as e:
        if 'ConstraintValidationFailed' in str(e):
            return jsonify({"success": False, "message": "Customer ID already exists"}), 400
        # Handle other potential neo4j exceptions
        abort(500, description=f"Failed to create customer: {e}")
        
#update_customer("customer14", 
#                {"name":"Pjotr",
#                 "age":14,
#                 "address" : "TestVeien2"
#                 })



def delete_customer(dbDriver,id):
    records, summary, keys = dbDriver.execute_query("""
    MATCH (p:Customer {id: $id})
    DETACH DELETE p
    """, id=id,
    database_="neo4j",
    )
    print(f"Query counters: {summary.counters}.")
