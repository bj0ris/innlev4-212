from flask import Flask, jsonify, request, abort
from neo4j import GraphDatabase, exceptions


def create_car(json,dbSession):
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
        # Perform a transaction to create a new car
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