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

@app.route("/order-car", methods=['POST'])
def order_car():
    # Extracting customer and car IDs from the request's JSON body
    data = request.json
    customer_id = data.get('customer_id')
    car_id = data.get('car_id')

    # Input validation to ensure required data is present
    if not customer_id or not car_id:
        return jsonify({"success": False, "message": "Missing customer_id or car_id"}), 400

    try:
        with get_db_session() as session:
            # Perform a transaction to book a car for a customer
            result = session.write_transaction(
                lambda tx: tx.run(
                    """
                    // Find the customer by ID and check if they have already booked a car
                    MATCH (customer:Customer {id: $customer_id})
                    OPTIONAL MATCH (customer)-[r:BOOKED]->(c:Car)
                    // Only proceed with booking if the customer has not booked another car
                    WITH customer, c, CASE WHEN c IS NULL THEN true ELSE false END as canBook
                    // Find the requested car by ID and ensure it is available
                    MATCH (car:Car {id: $car_id})
                    WHERE car.status = 'available' AND canBook
                    // If the car is available and the customer can book, update the car's status and create the booking relationship
                    SET car.status = 'booked'
                    CREATE (customer)-[:BOOKED]->(car)
                    // Return whether the booking was successful
                    RETURN count(car) > 0 as booked
                    """,
                    customer_id=customer_id,
                    car_id=car_id
                ).single()
            )
        # If a car was successfully booked, return a success response
        if result and result["booked"]:
            return jsonify({"success": True, "message": "Car booked successfully."}), 200
        else:
            # If booking was unsuccessful, either due to the car being unavailable or customer already having a booked car
            return jsonify({"success": False, "message": "Car booking failed or customer already has a booked car."}), 400
    except exceptions.Neo4jError as e:
        # If any other Neo4j-related error occurs during the transaction, respond with a 500 error
        abort(500, description=f"Transaction failed: {str(e)}")

@app.route("/cancel-order-car", methods=['POST'])
def cancel_order_car():
    # Extract customer/car IDs from request JSON body
    data = request.json
    customer_id = data.get('customer_id')
    car_id = data.get('car_id')

    # Input validation to ensure needed data is present
    if not customer_id or not car_id:
        return jsonify({"success:" False, "message": "Missing customer_id or car_id"}), 400

    try: 
        with get_db_session() as session:
            #Transaction to cancel car booking for customer
            result = session.write_transaction(
                lambda tx: tx.run(
                    """ 
                    // Find customer by ID
                    MATCH (customer:Customer {id: $customer_id})
                    // Find car by ID, check if booked
                    MATCH (customer)-[r:BOOKED] ->(car:Car {id: $car_id})
                    // If car is booked by customer, mark available and remove booking
                    DELETE r
                    SET car.status = 'available'
                    // RETURN count(r) > 0 as canceled
                    """,
                    customer_id = customer_id,
                    car_id= car_id


                ).single()
            )
        #If booking canceled
        if result and result["canceled"]:
            return jsonify({"success": True, "message": "Booking canceled"}), 200
        else:
            #If cancellation unsuccessful
            return jsonify({"success": False, "message": "Cancellation failed"}), 400
        except exceptions.Neo4jError as e:
            #If neo4j related error with transaction respond with 500 error
            abort(500, description=f"Transaction failed: {str(e)}")
            

if __name__ == '__main__':
    app.run(debug=True)

'''
app = Flask(__name__)
#TEesttdjskfjkldjfksl

@app.route("/order-car")
def orderCar():
    #TODO The system must check that the customer with customer-id has not booked other cars. The system changes the status of the car with car-id from ‘available’ to ‘booked’
    return

@app.route("/cancel-order-car")
def cancelOrder():
    #TODO  The system must check that the customer with customer-id has booked for the car. If the customer has booked the car, the car becomes available.
    return

@app.route("/rent-car")
def rentCar():
    #TODO The system must check that the customer with customer-id has a booking for the car. The car’s status is changed from ‘booked’ to ‘rented’.
    return

@app.route("/return-car")
def returnCar():
    #TODO Car’s status (e.g., ok or damaged) during the return will also be sent as a parameter. The system must check that the customer with customer-id has rented the car. 
    # The car’s status is changed from ‘booked’ to ‘available’ or ‘damaged’.
    return
'''
