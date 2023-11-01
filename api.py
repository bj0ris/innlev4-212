from flask import Flask
from neo4j import GraphDatabase

URI = "neo4j+ssc://84c9b254.databases.neo4j.io"
USERNAME = "neo4j"
PASSWORD = "9BPTWpu5kp2nWjPyfuhfn5zorZKBrh5jBpKC3uBw908"

driver = GraphDatabase.driver(URI, auth=(USERNAME,PASSWORD))

with driver.session() as session:
    result = session.run("RETURN 1")
    for record in result:
        print(record)

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
