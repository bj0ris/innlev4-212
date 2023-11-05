#Create, Read, Update and Delete ‘Cars' with basic information e.g., make, model, year,
#location, status (i.e., available, booked, rented, damaged)

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


def create_car(json,dbSession):
    # Extract car data from the request's JSON body

    year = json.get("year")
    location = json.get("location")
    model = json.get("model")
    id = json.get("id")
    make = json.get("make")
    status = json.get("status")


    # Validate the received data (ensure all fields are provided)
    if not all([id,year,location,model,make,status]):
        return jsonify({"success": False, "message": "All car details must be provided"}), 400

    try:
        #with dbSession() as session:
        # Perform a transaction to create a new car
        result = dbSession.write_transaction(
            lambda tx: tx.run(
                """
                CREATE (car:Car {
                    year: $year,    
                    location: $location,    
                    model: $model,    
                    id: $id,                        
                    make: $make,    
                    status: $status
                })
                RETURN car
                """,
                year=year,
                location=location,
                model=model,
                id=id,
                make=make,
                status=status
            ).single()
        )
        # Return a success response with the created car's details
        created_car = result.get("car") if result else None
        if created_car:
            return jsonify({"success": True, "car": created_car}), 201
        else:
            return jsonify({"success": False, "message": "car could not be created"}), 400
    except exceptions.Neo4jError as e:
        if 'ConstraintValidationFailed' in str(e):
            return jsonify({"success": False, "message": "car ID already exists"}), 400
        # Handle other potential neo4j exceptions
        abort(500, description=f"Failed to create car: {e}")

"""
jsons = {
    "year": 1999,
    "location": "C",
    "model": "case",
    "id": "car82",
    "make": "BMW",
    "status":"available"
}
create_car(jsons,get_db_session())
"""

def read_car(dbDriver):
    #Returns list of all cars
    records, summary, keys = dbDriver.execute_query("MATCH (n:Car) RETURN n LIMIT 25;",database_="neo4j")
    returnList = []
    for record in records:
        returnList.append(record.data())
    return returnList
#print(read_car(driver))


def update_car(dbDriver,id, changejson):
    #Update a cars address,name, and age
    #"adress","name" or "age" as key. The new value as value
    try:
        records, summary, keys = dbDriver.execute_query(
            """
            MATCH (c:Car {id: $id})
            SET c.year = $year
            SET c.location = $location
            SET c.model = $model
            SET c.id = $id
            SET c.make = $make
            SET c.status = $status
            """, 
            id = id,
            year = changejson.get("year"),
            location = changejson.get("location"),
            model = changejson.get("model"),
            make = changejson.get("make"),
            status = changejson.get("status"),
            database_="neo4j",
            )
        print(f"Query counters: {summary.counters}.")
    except exceptions.Neo4jError as e:
        if 'ConstraintValidationFailed' in str(e):
            return jsonify({"success": False, "message": "Car ID already exists"}), 400
        # Handle other potential neo4j exceptions
        abort(500, description=f"Failed to create car: {e}")
        
#jsonUpdate = {
#    "year":1987,
#    "location": "B",
#    "model":"dsadsa",
#    "id":"car72",
#    "make":"Mercedes",
#    "status":"booked"
#    }
#update_car(driver,"car82",jsonUpdate)


def delete_car(dbDriver,id):
    records, summary, keys = dbDriver.execute_query("""
    MATCH (p:Car {id: $id})
    DETACH DELETE p
    """, id=id,
    database_="neo4j",
    )
    print(f"Query counters: {summary.counters}.")

#delete_car(driver,"car82")