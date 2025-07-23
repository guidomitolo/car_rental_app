from flask_restx import Namespace, Resource, fields
from src.database import retrieve, select, update, create


customer_ns = Namespace('customer', description='Customer operations')

customer_model = customer_ns.model('Customer', {
    "first_name": fields.String(max_length=50, description="Customer's first name."),
    "last_name": fields.String(max_length=50, description="Customer's last name."),
    "email": fields.String(max_length=100, description="Unique email address of the customer."),
    "phone": fields.String(max_length=20, description="Customer's phone number."),
    "address": fields.String(max_length=255, description="Customer's street address."),
    "city": fields.String(max_length=100, description="Customer's city."),
    "state": fields.String(max_length=100, description="Customer's state."),
    "zip_code": fields.String(max_length=10, description="Customer's zip code."),
})

@customer_ns.route('/<int:customer_id>')
@customer_ns.param('customer_id', 'The customer identifier')
@customer_ns.response(404, 'Customer not found')
class CustomerView(Resource):

    __table = "customer"

    def get_customer(self, id:int):
        try:
            customer = retrieve(self.__table, id)
            return customer
        except:
            raise {'error': 'Not Found'}
    
    @customer_ns.marshal_list_with(customer_model)
    def get(self, customer_id:int):
        return self.get_customer(customer_id)

    @customer_ns.expect(customer_model, validate=True)
    @customer_ns.marshal_with(customer_model, code=200)
    def put(self, customer_id:int):
        customer_updated_data = customer_ns.payload
        customer_data = dict(self.get_customer(customer_id))
        customer_data.update(customer_updated_data)
        customer = update(self.__table, customer_id, customer_data)
        return customer

@customer_ns.route('/')
class CustomerListView(Resource):
    
    __table = "customer"

    @customer_ns.marshal_list_with(customer_model, code=200)
    def get(self):
        return select(self.__table)
    
    @customer_ns.expect(customer_model, validate=True)
    @customer_ns.marshal_with(customer_model, code=200)
    def post(self,):
        new_customer_data = customer_ns.payload
        return create(self.__table, new_customer_data)
        