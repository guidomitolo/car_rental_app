from flask import Flask
from flask_restx  import Api
from src.database import init_app_db
from src.resources.customer import customer_ns
from src.resources.vehicle import vehicle_ns
from src.resources.order import order_ns


app = Flask(__name__)

init_app_db(app)

api = Api(
    app, 
    version='1.0',
    title='Car Rental API',
    description='A simple car rental API',
)

# https://flask-restx.readthedocs.io/en/latest/scaling.html
api.add_namespace(customer_ns)
api.add_namespace(vehicle_ns)
api.add_namespace(order_ns)


