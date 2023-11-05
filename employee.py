#Create, Read, Update and Delete ‘Employee’ with basic information e.g., name,
#address, branch

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


def create_employee(json,dbSession):
    # Extract employee data from the request's JSON body

    name = json.get("name")
    address = json.get("address")
    branch = json.get("branch")
    id = json.get("id")


    # Validate the received data (ensure all fields are provided)
    if not all([id,name,address,branch]):
        return jsonify({"success": False, "message": "All employee details must be provided"}), 400

    try:
        #with dbSession() as session:
        # Perform a transaction to create a new employee
        result = dbSession.write_transaction(
            lambda tx: tx.run(
                """
                CREATE (employee:Employee {
                    id: $id,
                    name: $name,    
                    address: $address,    
                    branch: $branch
                })
                RETURN employee
                """,
                id=id,
                name=name,
                address=address,
                branch=branch
            ).single()
        )
        # Return a success response with the created employee's details
        created_employee = result.get("employee") if result else None
        if created_employee:
            return jsonify({"success": True, "employee": created_employee}), 201
        else:
            return jsonify({"success": False, "message": "employee could not be created"}), 400
    except exceptions.Neo4jError as e:
        if 'ConstraintValidationFailed' in str(e):
            return jsonify({"success": False, "message": "employee ID already exists"}), 400
        # Handle other potential neo4j exceptions
        abort(500, description=f"Failed to create employee: {e}")

#
#jsons = {
#    "name": "Tester",
#    "address": "nkvlfd",
#    "branch": "C",
#    "id":"employee82"
#}
#create_employee(jsons,get_db_session())
#

def read_employee(dbDriver):
    #Returns list of all employees
    records, summary, keys = dbDriver.execute_query("MATCH (n:Employee) RETURN n LIMIT 25;",database_="neo4j")
    returnList = []
    for record in records:
        returnList.append(record.data())
    return returnList
#print(read_employee(driver))


def update_employee(dbDriver,id, changejson):
    #Update a employees address,name, and age
    #"adress","name" or "age" as key. The new value as value
    try:
        records, summary, keys = dbDriver.execute_query(
            """
            MATCH (n:Employee {id: $id})
            SET n.id = $id
            SET n.name = $name
            SET n.address = $address
            SET n.branch = $branch
            """, 
            id=id,
            name=changejson.get("name"),
            address=changejson.get("address"),
            branch=changejson.get("branch"),
            database_="neo4j",
            )
        print(f"Query counters: {summary.counters}.")
    except exceptions.Neo4jError as e:
        if 'ConstraintValidationFailed' in str(e):
            return jsonify({"success": False, "message": "Employee ID already exists"}), 400
        # Handle other potential neo4j exceptions
        abort(500, description=f"Failed to create employee: {e}")
        
#jsons = {
#    "id":"employee32",
#    "name": "Charlie",
#    "address": "huttiheita 2",
#    "branch": "C"
#}
#update_employee(driver,"employee82",jsons)


def delete_employee(dbDriver,id):
    records, summary, keys = dbDriver.execute_query("""
    MATCH (p:Employee {id: $id})
    DETACH DELETE p
    """, id=id,
    database_="neo4j",
    )
    print(f"Query counters: {summary.counters}.")

#delete_employee(driver,"employee82")